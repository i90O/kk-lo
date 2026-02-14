"""
Options chain scanner using Polygon.io API.
API docs: https://polygon.io/docs/options/get_v3_snapshot_options__underlyingasset
"""

from datetime import datetime, timedelta
from langchain.tools import tool
from tools import polygon_client as _client


@tool
def scan_options_chain(
    ticker: str,
    expiration_gte: str = None,
    expiration_lte: str = None,
    strike_price_gte: float = None,
    strike_price_lte: float = None,
    contract_type: str = None,
) -> dict:
    """
    Scan options chain snapshot for a given ticker.
    Returns contracts with price, Greeks (delta/gamma/theta/vega),
    implied volatility, open interest, and bid-ask spread.

    Args:
        ticker: Stock symbol e.g. "AAPL", "TSLA", "SPY"
        expiration_gte: Earliest expiry date "2026-03-01"
        expiration_lte: Latest expiry date
        strike_price_gte: Minimum strike price
        strike_price_lte: Maximum strike price
        contract_type: "call" or "put", None for all
    """
    # Skip 0-2 DTE by default (Greeks often None for near-expiry)
    if not expiration_gte:
        expiration_gte = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    if not expiration_lte:
        expiration_lte = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    params = {
        "expiration_date.gte": expiration_gte,
        "expiration_date.lte": expiration_lte,
    }
    if strike_price_gte:
        params["strike_price.gte"] = strike_price_gte
    if strike_price_lte:
        params["strike_price.lte"] = strike_price_lte
    if contract_type:
        params["contract_type"] = contract_type

    options = []
    try:
        for o in _client.list_snapshot_options_chain(ticker, params=params):
            iv = o.implied_volatility
            g = o.greeks
            options.append({
                "ticker": o.details.ticker if o.details else None,
                "type": o.details.contract_type if o.details else None,
                "strike": o.details.strike_price if o.details else None,
                "expiry": o.details.expiration_date if o.details else None,
                "bid": o.last_quote.bid if o.last_quote else None,
                "ask": o.last_quote.ask if o.last_quote else None,
                "mid": o.last_quote.midpoint if o.last_quote else None,
                "volume": o.day.volume if o.day else 0,
                "open_interest": o.open_interest,
                "iv": round(iv, 4) if iv is not None else None,
                "delta": round(g.delta, 4) if g and g.delta is not None else None,
                "gamma": round(g.gamma, 6) if g and g.gamma is not None else None,
                "theta": round(g.theta, 4) if g and g.theta is not None else None,
                "vega": round(g.vega, 4) if g and g.vega is not None else None,
                "break_even": o.break_even_price,
            })
    except Exception as e:
        return {"error": f"Polygon API error: {e}", "underlying": ticker}

    # Summary
    calls = [o for o in options if o["type"] == "call"]
    puts = [o for o in options if o["type"] == "put"]
    ivs = [o["iv"] for o in options if o["iv"]]

    return {
        "underlying": ticker,
        "source": "polygon",
        "count": len(options),
        "scan_time": datetime.now().isoformat(),
        "contracts": options[:50],
        "summary": {
            "total_contracts": len(options),
            "avg_iv": round(sum(ivs) / len(ivs), 4) if ivs else None,
            "highest_oi_call": max(calls, key=lambda x: x["open_interest"] or 0, default=None),
            "highest_oi_put": max(puts, key=lambda x: x["open_interest"] or 0, default=None),
        },
    }


if __name__ == "__main__":
    result = scan_options_chain.invoke({
        "ticker": "SPY",
        "contract_type": "call",
    })
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"Contracts: {result.get('count', 0)}")
    print(f"Avg IV: {result.get('summary', {}).get('avg_iv')}")
