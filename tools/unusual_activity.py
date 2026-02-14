"""Unusual options activity detection using Polygon.io API."""

import time
import math
from datetime import datetime, timedelta
from tools import polygon_client as _client
from tools.market_data import get_current_price
from config import REQUEST_DELAY
from log import get_logger

logger = get_logger(__name__)


def scan_unusual(tickers: list[str]) -> list[dict]:
    """
    Scan tickers for unusual options activity.

    Detects:
    1. Volume/OI ratio > 3 (new position surge)
    2. Single-day volume > 5000 with significant above-average volume
    3. Large OI accumulation near ATM (magnet levels)
    4. Extreme Put/Call volume ratios (>1.5 or <0.5)
    5. Unusual large orders in far-month contracts (institutional positioning)

    Returns results sorted by premium flow (volume * midprice * 100) descending.
    """
    all_unusual = []

    for ticker in tickers:
        try:
            alerts = _scan_ticker(ticker)
            all_unusual.extend(alerts)
        except Exception as e:
            logger.warning("Error scanning %s: %s", ticker, e)
        time.sleep(REQUEST_DELAY)

    # Sort by premium flow descending
    all_unusual.sort(key=lambda x: x.get("premium_flow", 0), reverse=True)
    return all_unusual


def _scan_ticker(ticker: str) -> list[dict]:
    """Scan a single ticker for unusual activity using Polygon snapshot."""
    price = get_current_price(ticker)
    if price <= 0:
        return []

    # Scan all expirations from 0 to 180 DTE
    exp_gte = datetime.now().strftime("%Y-%m-%d")
    exp_lte = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")

    alerts = []
    total_call_vol = 0
    total_put_vol = 0

    # Track ATM OI for magnet detection
    atm_oi_data = []

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

            side = "CALL" if details.contract_type == "call" else "PUT"
            strike = float(details.strike_price or 0)
            exp_date = details.expiration_date or ""
            contract_symbol = details.ticker or ""

            # Calculate DTE
            try:
                exp_dt = datetime.strptime(exp_date, "%Y-%m-%d").date()
                dte = (exp_dt - datetime.now().date()).days
            except (ValueError, TypeError):
                dte = 0
            is_far_month = dte > 90

            vol = int(o.day.volume) if o.day and o.day.volume else 0
            oi = int(o.open_interest) if o.open_interest else 0
            iv = float(o.implied_volatility) if o.implied_volatility else 0
            bid = float(o.last_quote.bid) if o.last_quote and o.last_quote.bid else 0
            ask = float(o.last_quote.ask) if o.last_quote and o.last_quote.ask else 0
            mid_price = (bid + ask) / 2
            premium_flow = vol * mid_price * 100

            if side == "CALL":
                total_call_vol += vol
            else:
                total_put_vol += vol

            # Track near-ATM OI
            if price > 0 and abs(strike - price) / price < 0.05:
                atm_oi_data.append({
                    "strike": strike, "oi": oi, "type": side,
                    "expiration": exp_date,
                })

            # --- Detection Rules ---

            # Rule 1: Volume/OI > 3
            if oi > 0 and vol / oi > 3 and vol > 100:
                alerts.append({
                    "ticker": ticker,
                    "type": "VOL/OI_SURGE",
                    "contract": contract_symbol,
                    "side": side,
                    "strike": strike,
                    "expiration": exp_date,
                    "dte": dte,
                    "volume": vol,
                    "open_interest": oi,
                    "vol_oi_ratio": round(vol / oi, 1),
                    "iv": round(iv * 100, 1),
                    "mid_price": round(mid_price, 2),
                    "premium_flow": round(premium_flow, 0),
                    "interpretation": f"New positions surging: {vol/oi:.1f}x OI traded today. "
                                      f"{'Bullish' if side == 'CALL' else 'Bearish'} signal.",
                })

            # Rule 2: High absolute volume
            if vol > 5000 and mid_price > 0.10:
                alerts.append({
                    "ticker": ticker,
                    "type": "HIGH_VOLUME",
                    "contract": contract_symbol,
                    "side": side,
                    "strike": strike,
                    "expiration": exp_date,
                    "dte": dte,
                    "volume": vol,
                    "open_interest": oi,
                    "iv": round(iv * 100, 1),
                    "mid_price": round(mid_price, 2),
                    "premium_flow": round(premium_flow, 0),
                    "interpretation": f"Heavy {side} activity: {vol:,} contracts traded, "
                                      f"${premium_flow:,.0f} premium flow.",
                })

            # Rule 5: Far-month large orders (institutional)
            if is_far_month and vol > 1000 and premium_flow > 100000:
                alerts.append({
                    "ticker": ticker,
                    "type": "INSTITUTIONAL_FAR_MONTH",
                    "contract": contract_symbol,
                    "side": side,
                    "strike": strike,
                    "expiration": exp_date,
                    "dte": dte,
                    "volume": vol,
                    "open_interest": oi,
                    "iv": round(iv * 100, 1),
                    "mid_price": round(mid_price, 2),
                    "premium_flow": round(premium_flow, 0),
                    "interpretation": f"Possible institutional positioning: {dte} DTE, "
                                      f"${premium_flow:,.0f} flow in far-month {side}.",
                })

    except Exception as e:
        logger.warning("Polygon scan error for %s: %s", ticker, e)
        return []

    # Rule 3: ATM OI accumulation (magnet levels)
    if atm_oi_data:
        max_oi_entry = max(atm_oi_data, key=lambda x: x["oi"])
        if max_oi_entry["oi"] > 10000:
            alerts.append({
                "ticker": ticker,
                "type": "ATM_OI_MAGNET",
                "side": max_oi_entry["type"],
                "strike": max_oi_entry["strike"],
                "expiration": max_oi_entry["expiration"],
                "open_interest": max_oi_entry["oi"],
                "premium_flow": 0,
                "interpretation": f"Large OI at ${max_oi_entry['strike']:.0f} "
                                  f"({max_oi_entry['oi']:,} contracts) - potential price magnet.",
            })

    # Rule 4: Extreme P/C volume ratio
    if total_call_vol > 0:
        pc_ratio = total_put_vol / total_call_vol
        if pc_ratio > 1.5 or pc_ratio < 0.5:
            sentiment = "bearish (heavy put buying)" if pc_ratio > 1.5 else "bullish (heavy call buying)"
            alerts.append({
                "ticker": ticker,
                "type": "EXTREME_PC_RATIO",
                "put_volume": total_put_vol,
                "call_volume": total_call_vol,
                "pc_ratio": round(pc_ratio, 2),
                "premium_flow": 0,
                "interpretation": f"Put/Call ratio {pc_ratio:.2f} - {sentiment}.",
            })

    # Deduplicate: keep highest premium_flow per contract
    seen = {}
    for a in alerts:
        key = a.get("contract", "") or f"{a['ticker']}_{a['type']}_{a.get('strike', '')}"
        if key not in seen or a.get("premium_flow", 0) > seen[key].get("premium_flow", 0):
            seen[key] = a
    unique_alerts = list(seen.values())

    return unique_alerts


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("[bold]Scanning for unusual options activity (Polygon)...[/bold]")
    console.print("Tickers: TSLA, NVDA, AAPL, SPY\n")

    results = scan_unusual(["TSLA", "NVDA", "AAPL", "SPY"])

    if not results:
        console.print("[yellow]No unusual activity detected.[/yellow]")
    else:
        table = Table(title=f"Top 10 Unusual Activity ({len(results)} total)")
        table.add_column("Ticker", style="bold")
        table.add_column("Type")
        table.add_column("Side")
        table.add_column("Strike")
        table.add_column("Exp")
        table.add_column("Vol")
        table.add_column("OI")
        table.add_column("Flow $")
        table.add_column("Interpretation", max_width=50)

        for r in results[:10]:
            table.add_row(
                r.get("ticker", ""),
                r.get("type", ""),
                r.get("side", ""),
                f"${r['strike']:.0f}" if "strike" in r else "",
                r.get("expiration", "")[:10] if "expiration" in r else "",
                f"{r.get('volume', ''):,}" if isinstance(r.get("volume"), int) else "",
                f"{r.get('open_interest', ''):,}" if isinstance(r.get("open_interest"), int) else "",
                f"${r.get('premium_flow', 0):,.0f}",
                r.get("interpretation", ""),
            )

        console.print(table)
