"""IV (Implied Volatility) tracking system with SQLite storage.
Uses Polygon.io API for price history and ATM IV."""

import sqlite3
import time
from datetime import datetime, timedelta
import numpy as np
from tools import polygon_client as _client
from config import DB_PATH, REQUEST_DELAY
from log import get_logger

logger = get_logger(__name__)


def _get_db():
    """Get SQLite connection and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS iv_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            atm_iv REAL,
            hv20 REAL,
            hv60 REAL,
            close_price REAL,
            UNIQUE(ticker, date)
        )
    """)
    conn.commit()
    return conn


def record_daily_iv(ticker: str) -> dict:
    """
    Record today's IV and HV data for a ticker.
    - ATM IV from ~30 DTE options via Polygon snapshot
    - HV20 and HV60 from historical close prices via Polygon aggs
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Get 3 months of daily close prices from Polygon
    to_date = today
    from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    try:
        aggs = _client.get_aggs(
            ticker, 1, "day", from_date, to_date,
            adjusted=True, sort="asc", limit=50000,
        )
    except Exception as e:
        return {"error": f"Polygon aggs error for {ticker}: {e}"}

    if not aggs or len(aggs) < 5:
        return {"error": f"Insufficient price data for {ticker}"}

    closes = np.array([float(a.close) for a in aggs if a.close is not None])
    if len(closes) < 5:
        return {"error": f"Insufficient close data for {ticker}"}

    close_price = float(closes[-1])

    # Calculate Historical Volatility (annualized)
    log_returns = np.diff(np.log(closes))
    hv20 = float(np.std(log_returns[-20:]) * np.sqrt(252)) if len(log_returns) >= 20 else None
    hv60 = float(np.std(log_returns[-60:]) * np.sqrt(252)) if len(log_returns) >= 60 else None

    # Get ATM IV from ~30 DTE options via Polygon
    atm_iv = _get_atm_iv(ticker, close_price)
    time.sleep(REQUEST_DELAY)

    # Store in database
    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO iv_history (ticker, date, atm_iv, hv20, hv60, close_price) VALUES (?, ?, ?, ?, ?, ?)",
            (ticker, today, atm_iv, hv20, hv60, close_price)
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "ticker": ticker,
        "date": today,
        "atm_iv": atm_iv,
        "hv20": hv20,
        "hv60": hv60,
        "close_price": close_price,
    }


def _get_atm_iv(ticker: str, current_price: float) -> float | None:
    """Get ATM IV from the nearest ~30 DTE expiration via Polygon snapshot."""
    # Target ~30 DTE window
    exp_gte = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
    exp_lte = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")

    best_iv = None
    best_dist = float("inf")

    try:
        for o in _client.list_snapshot_options_chain(
            ticker,
            params={
                "expiration_date.gte": exp_gte,
                "expiration_date.lte": exp_lte,
                "contract_type": "call",
            },
        ):
            details = o.details
            if not details:
                continue

            strike = float(details.strike_price or 0)
            iv = o.implied_volatility

            if iv is None or iv <= 0:
                continue

            dist = abs(strike - current_price)
            if dist < best_dist:
                best_dist = dist
                best_iv = float(iv)

    except Exception:
        return None

    return best_iv


def get_iv_percentile(ticker: str, lookback: int = 252) -> dict:
    """
    Calculate IV Percentile and IV Rank from historical data.

    IV Percentile: % of days in lookback where IV was LOWER than current
    IV Rank: (current - min) / (max - min) over lookback period
    """
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT atm_iv FROM iv_history WHERE ticker = ? AND atm_iv IS NOT NULL ORDER BY date DESC LIMIT ?",
            (ticker, lookback)
        ).fetchall()
    finally:
        conn.close()

    if len(rows) < 2:
        return {
            "ticker": ticker,
            "iv_percentile": None,
            "iv_rank": None,
            "current_iv": None,
            "data_points": len(rows),
            "message": f"Need more data ({len(rows)} days collected, recommend 30+ for meaningful percentile)",
        }

    ivs = [r[0] for r in rows]
    current_iv = ivs[0]
    historical = ivs[1:]

    # IV Percentile: % of days where IV was lower
    below_count = sum(1 for iv in historical if iv < current_iv)
    iv_percentile = (below_count / len(historical)) * 100

    # IV Rank: (current - min) / (max - min)
    iv_min = min(historical)
    iv_max = max(historical)
    iv_rank = ((current_iv - iv_min) / (iv_max - iv_min) * 100) if iv_max != iv_min else 50

    return {
        "ticker": ticker,
        "current_iv": round(current_iv * 100, 1),
        "iv_percentile": round(iv_percentile, 1),
        "iv_rank": round(iv_rank, 1),
        "iv_min": round(iv_min * 100, 1),
        "iv_max": round(iv_max * 100, 1),
        "data_points": len(rows),
    }


def batch_record(tickers: list[str]) -> list[dict]:
    """Record IV data for all tickers in watchlist."""
    results = []
    for ticker in tickers:
        try:
            result = record_daily_iv(ticker)
            results.append(result)
            status = "OK" if "error" not in result else result["error"]
            logger.info("%s: %s", ticker, status)
        except Exception as e:
            results.append({"ticker": ticker, "error": str(e)})
            logger.warning("%s: ERROR - %s", ticker, e)
        time.sleep(REQUEST_DELAY)
    return results


def iv_dashboard(tickers: list[str]) -> list[dict]:
    """
    Generate IV dashboard data for all tickers.
    Columns: ticker, current_iv, iv_percentile, iv_rank, hv20, iv_hv_diff
    """
    conn = _get_db()
    dashboard = []

    for ticker in tickers:
        try:
            # Get latest record
            row = conn.execute(
                "SELECT atm_iv, hv20, hv60, close_price FROM iv_history WHERE ticker = ? ORDER BY date DESC LIMIT 1",
                (ticker,)
            ).fetchone()

            if row is None:
                dashboard.append({"ticker": ticker, "status": "no data"})
                continue

            atm_iv, hv20, hv60, close_price = row
            iv_data = get_iv_percentile(ticker)

            entry = {
                "ticker": ticker,
                "close": close_price,
                "current_iv": round(atm_iv * 100, 1) if atm_iv else None,
                "iv_percentile": iv_data.get("iv_percentile"),
                "iv_rank": iv_data.get("iv_rank"),
                "hv20": round(hv20 * 100, 1) if hv20 else None,
                "hv60": round(hv60 * 100, 1) if hv60 else None,
                "iv_hv_diff": round((atm_iv - hv20) * 100, 1) if atm_iv and hv20 else None,
                "data_points": iv_data.get("data_points", 0),
            }
            dashboard.append(entry)
        except Exception as e:
            dashboard.append({"ticker": ticker, "status": f"error: {e}"})

    conn.close()
    return dashboard


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    from config import WATCHLIST

    console = Console()

    # Batch record
    console.print("[bold]Recording IV data for watchlist (Polygon)...[/bold]\n")
    batch_record(WATCHLIST)

    # Dashboard
    console.print("\n[bold]IV Dashboard[/bold]\n")
    data = iv_dashboard(WATCHLIST)

    table = Table(title="IV Dashboard")
    table.add_column("Ticker", style="bold")
    table.add_column("Close")
    table.add_column("IV%")
    table.add_column("IV %ile")
    table.add_column("IV Rank")
    table.add_column("HV20%")
    table.add_column("IV-HV")
    table.add_column("Data Pts")

    for d in data:
        if "status" in d:
            table.add_row(d["ticker"], "", "", "", "", "", "", d["status"])
        else:
            iv_hv = d.get("iv_hv_diff")
            iv_hv_str = f"{iv_hv:+.1f}" if iv_hv is not None else "N/A"
            table.add_row(
                d["ticker"],
                f"${d['close']:.2f}" if d.get("close") else "N/A",
                f"{d['current_iv']:.1f}" if d.get("current_iv") else "N/A",
                f"{d['iv_percentile']:.0f}" if d.get("iv_percentile") is not None else "N/A",
                f"{d['iv_rank']:.0f}" if d.get("iv_rank") is not None else "N/A",
                f"{d['hv20']:.1f}" if d.get("hv20") else "N/A",
                iv_hv_str,
                str(d.get("data_points", 0)),
            )

    console.print(table)
