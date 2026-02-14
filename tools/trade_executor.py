"""
Trade executor using Alpaca API (Paper Trading).
API docs: https://docs.alpaca.markets/docs/options-trading
Default: Paper Trading mode - no real money involved.
"""

from langchain.tools import tool
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY


def _get_client():
    """Get Alpaca trading client. Returns None if not configured."""
    if not ALPACA_API_KEY or ALPACA_API_KEY == "your_key_here":
        return None
    from alpaca.trading.client import TradingClient
    return TradingClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=True,
    )


@tool
def get_account_info() -> dict:
    """Get Alpaca paper trading account info: balance, buying power, portfolio value."""
    client = _get_client()
    if not client:
        return {"error": "Alpaca API not configured. Set ALPACA_API_KEY in .env"}

    try:
        account = client.get_account()
        return {
            "equity": str(account.equity),
            "cash": str(account.cash),
            "buying_power": str(account.buying_power),
            "portfolio_value": str(account.portfolio_value),
            "status": account.status,
        }
    except Exception as e:
        return {"error": f"Alpaca API error: {e}"}


@tool
def search_option_contracts(
    underlying: str,
    expiration_date: str = None,
    strike_price: float = None,
    contract_type: str = None,
) -> list:
    """
    Search tradeable option contracts on Alpaca.

    Args:
        underlying: Stock symbol e.g. "AAPL"
        expiration_date: Expiry date "2026-03-20"
        strike_price: Strike price
        contract_type: "call" or "put"
    """
    client = _get_client()
    if not client:
        return [{"error": "Alpaca API not configured"}]

    try:
        from alpaca.trading.requests import GetOptionContractsRequest
        req = GetOptionContractsRequest(
            underlying_symbols=[underlying],
            expiration_date=expiration_date,
            strike_price_gte=str(strike_price - 1) if strike_price else None,
            strike_price_lte=str(strike_price + 1) if strike_price else None,
            type=contract_type,
        )
        contracts = client.get_option_contracts(req)
        return [{
            "symbol": c.symbol,
            "name": c.name,
            "type": c.type,
            "strike": str(c.strike_price),
            "expiry": str(c.expiration_date),
            "status": c.status,
        } for c in contracts.option_contracts[:20]]
    except Exception as e:
        return [{"error": f"Search error: {e}"}]


@tool
def place_option_order(
    symbol: str,
    qty: int,
    side: str,
    order_type: str = "market",
    limit_price: float = None,
    confirm: bool = False,
) -> dict:
    """
    Place an option order on Alpaca Paper Trading.

    Args:
        symbol: Option contract symbol (from search_option_contracts)
        qty: Number of contracts
        side: "buy" or "sell"
        order_type: "market" or "limit"
        limit_price: Required if order_type is "limit"
        confirm: Must be True to actually place the order. First call returns order preview.
    """
    client = _get_client()
    if not client:
        return {"error": "Alpaca API not configured"}

    if not confirm:
        return {
            "status": "confirmation_required",
            "message": "Review order details and call again with confirm=True to execute.",
            "order_preview": {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "order_type": order_type,
                "limit_price": limit_price,
            },
        }

    try:
        from alpaca.trading.requests import OptionOrderRequest
        from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

        order_data = OptionOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            type=OrderType.MARKET if order_type == "market" else OrderType.LIMIT,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price if order_type == "limit" else None,
        )
        order = client.submit_order(order_data)
        return {
            "order_id": str(order.id),
            "status": str(order.status),
            "symbol": order.symbol,
            "qty": str(order.qty),
            "side": str(order.side),
            "type": str(order.type),
            "submitted_at": str(order.submitted_at),
        }
    except Exception as e:
        return {"error": f"Order error: {e}"}


@tool
def get_positions() -> list:
    """Get all current positions in the Alpaca paper account."""
    client = _get_client()
    if not client:
        return [{"error": "Alpaca API not configured"}]

    try:
        positions = client.get_all_positions()
        return [{
            "symbol": p.symbol,
            "qty": str(p.qty),
            "side": str(p.side),
            "avg_entry_price": str(p.avg_entry_price),
            "current_price": str(p.current_price),
            "unrealized_pl": str(p.unrealized_pl),
            "unrealized_plpc": str(p.unrealized_plpc),
            "market_value": str(p.market_value),
        } for p in positions]
    except Exception as e:
        return [{"error": f"Positions error: {e}"}]


if __name__ == "__main__":
    result = get_account_info.invoke({})
    print(f"Account: {result}")
