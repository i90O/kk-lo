"""Market data tools using Polygon.io API."""

import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from tools import polygon_client as _client
from config import REQUEST_DELAY
from log import get_logger

logger = get_logger(__name__)


def get_current_price(ticker: str) -> float:
    """Get current/latest stock price via Polygon snapshot."""
    try:
        snapshot = _client.get_snapshot_ticker("stocks", ticker)
        # Try last trade price first, then day close, then prev day close
        if snapshot.last_trade and snapshot.last_trade.price:
            return float(snapshot.last_trade.price)
        if snapshot.day and snapshot.day.close:
            return float(snapshot.day.close)
        if snapshot.prev_day and snapshot.prev_day.close:
            return float(snapshot.prev_day.close)
    except Exception as e:
        logger.warning("Snapshot price error for %s: %s", ticker, e)

    # Fallback: previous close agg
    try:
        aggs = _client.get_previous_close_agg(ticker)
        if aggs and len(aggs) > 0:
            return float(aggs[0].close)
    except Exception as e:
        logger.warning("Previous close error for %s: %s", ticker, e)

    return 0.0


def get_stock_info(ticker: str) -> dict:
    """Get basic stock info: name, market cap, sector, etc."""
    try:
        details = _client.get_ticker_details(ticker)
    except Exception as e:
        return {
            "ticker": ticker, "name": ticker, "sector": "N/A",
            "industry": "N/A", "market_cap": 0, "pe_ratio": None,
            "forward_pe": None, "beta": None, "52w_high": None,
            "52w_low": None, "avg_volume": None, "earnings_date": None,
        }

    # 52-week high/low from daily aggs
    w52_high, w52_low, avg_volume = None, None, None
    try:
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        aggs = _client.get_aggs(
            ticker, 1, "day", from_date, to_date,
            adjusted=True, sort="asc", limit=50000,
        )
        if aggs:
            highs = [a.high for a in aggs if a.high is not None]
            lows = [a.low for a in aggs if a.low is not None]
            vols = [a.volume for a in aggs if a.volume is not None]
            if highs:
                w52_high = max(highs)
            if lows:
                w52_low = min(lows)
            if vols and len(vols) >= 20:
                avg_volume = int(sum(vols[-20:]) / 20)
    except Exception as e:
        logger.warning("52-week data error for %s: %s", ticker, e)

    return {
        "ticker": ticker,
        "name": getattr(details, "name", ticker) or ticker,
        "sector": getattr(details, "sic_description", "N/A") or "N/A",
        "industry": getattr(details, "sic_description", "N/A") or "N/A",
        "market_cap": getattr(details, "market_cap", 0) or 0,
        "pe_ratio": None,  # Polygon basic tier doesn't include P/E
        "forward_pe": None,
        "beta": None,
        "52w_high": w52_high,
        "52w_low": w52_low,
        "avg_volume": avg_volume,
        "earnings_date": None,  # Would need separate financials API
    }


def get_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    Get OHLCV data as pandas DataFrame for technical analysis.
    Compatible with ta library (columns: Open, High, Low, Close, Volume).
    """
    # Convert period string to days
    period_days = {
        "1mo": 30, "3mo": 90, "6mo": 180,
        "1y": 365, "2y": 730, "5y": 1825,
    }
    days = period_days.get(period, 180)

    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        aggs = _client.get_aggs(
            ticker, 1, "day", from_date, to_date,
            adjusted=True, sort="asc", limit=50000,
        )
    except Exception as e:
        logger.warning("Polygon aggs error for %s: %s", ticker, e)
        return pd.DataFrame()

    if not aggs:
        return pd.DataFrame()

    # Build DataFrame matching yfinance format (capitalized columns)
    data = []
    for a in aggs:
        ts = datetime.fromtimestamp(a.timestamp / 1000) if a.timestamp else None
        data.append({
            "Date": ts,
            "Open": a.open,
            "High": a.high,
            "Low": a.low,
            "Close": a.close,
            "Volume": a.volume or 0,
        })

    df = pd.DataFrame(data)
    if not df.empty and "Date" in df.columns:
        df.set_index("Date", inplace=True)
        df.index = pd.DatetimeIndex(df.index)

    return df


def get_options_chain(ticker: str) -> dict:
    """
    Get full options chain for a ticker using Polygon snapshot.
    Returns structured data with calls/puts, OI, volume, IV,
    ATM options, and put/call ratios.
    """
    current_price = get_current_price(ticker)

    # Scan 3-60 DTE range (skip 0-2 DTE where Greeks are often None)
    exp_gte = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    exp_lte = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    all_calls = []
    all_puts = []
    total_call_vol = 0
    total_put_vol = 0
    total_call_oi = 0
    total_put_oi = 0
    expirations_set = set()

    try:
        for o in _client.list_snapshot_options_chain(
            ticker,
            params={
                "expiration_date.gte": exp_gte,
                "expiration_date.lte": exp_lte,
            },
        ):
            details = o.details
            if not details:
                continue

            ctype = details.contract_type  # "call" or "put"
            strike = details.strike_price or 0
            expiry = details.expiration_date or ""
            expirations_set.add(expiry)

            iv = o.implied_volatility or 0
            vol = o.day.volume if o.day else 0
            vol = vol or 0
            oi = o.open_interest or 0
            bid = o.last_quote.bid if o.last_quote else 0
            ask = o.last_quote.ask if o.last_quote else 0
            bid = bid or 0
            ask = ask or 0

            contract = {
                "expiration": expiry,
                "type": ctype,
                "strike": float(strike),
                "lastPrice": float((bid + ask) / 2) if bid and ask else 0,
                "bid": float(bid),
                "ask": float(ask),
                "volume": int(vol),
                "openInterest": int(oi),
                "impliedVolatility": float(iv),
                "contractSymbol": details.ticker if details else "",
                "inTheMoney": (ctype == "call" and strike < current_price) or
                              (ctype == "put" and strike > current_price),
            }

            if ctype == "call":
                all_calls.append(contract)
                total_call_vol += contract["volume"]
                total_call_oi += contract["openInterest"]
            else:
                all_puts.append(contract)
                total_put_vol += contract["volume"]
                total_put_oi += contract["openInterest"]

    except Exception as e:
        return {"error": f"Polygon options error: {e}", "ticker": ticker}

    expirations = sorted(expirations_set)

    # Find ATM options for nearest expiration
    atm_call = None
    atm_put = None
    if expirations:
        nearest_exp = expirations[0]
        nearest_calls = [c for c in all_calls if c["expiration"] == nearest_exp]
        nearest_puts = [p for p in all_puts if p["expiration"] == nearest_exp]
        if nearest_calls:
            atm_call = min(nearest_calls, key=lambda c: abs(c["strike"] - current_price))
        if nearest_puts:
            atm_put = min(nearest_puts, key=lambda p: abs(p["strike"] - current_price))

    # Ratios
    pc_vol_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else None
    pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else None

    return {
        "ticker": ticker,
        "current_price": current_price,
        "expirations": expirations,
        "total_contracts": len(all_calls) + len(all_puts),
        "calls": all_calls,
        "puts": all_puts,
        "atm_call": atm_call,
        "atm_put": atm_put,
        "total_call_volume": total_call_vol,
        "total_put_volume": total_put_vol,
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "put_call_volume_ratio": pc_vol_ratio,
        "put_call_oi_ratio": pc_oi_ratio,
    }


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("[bold]Testing market_data.py (Polygon) with TSLA...[/bold]\n")

    price = get_current_price("TSLA")
    console.print(f"TSLA Current Price: ${price:.2f}\n")

    info = get_stock_info("TSLA")
    console.print("[bold]Stock Info:[/bold]")
    for k, v in info.items():
        console.print(f"  {k}: {v}")

    console.print("\n[bold]OHLCV Data (last 5 days):[/bold]")
    df = get_stock_data("TSLA", "1mo")
    if not df.empty:
        console.print(str(df.tail()))

    console.print("\n[bold]Fetching options chain...[/bold]")
    chain = get_options_chain("TSLA")

    if "error" in chain:
        console.print(f"[red]{chain['error']}[/red]")
    else:
        console.print(f"Expirations: {len(chain['expirations'])}")
        console.print(f"Total contracts: {chain['total_contracts']}")
        console.print(f"Put/Call Vol Ratio: {chain['put_call_volume_ratio']:.3f}" if chain['put_call_volume_ratio'] else "Put/Call Vol Ratio: N/A")
        console.print(f"Put/Call OI Ratio: {chain['put_call_oi_ratio']:.3f}" if chain['put_call_oi_ratio'] else "Put/Call OI Ratio: N/A")
