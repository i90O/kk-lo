"""
OptionsAgent - LangGraph multi-tool Agent.
Architecture: LangGraph StateGraph + tool-calling loop.
Flow: User input -> Agent reasons -> calls tools -> synthesizes report.

Requires ANTHROPIC_API_KEY in .env.
Falls back to offline mode (Phase 1 tools only) if not configured.
"""

import sys

from typing import TypedDict, Annotated
from config import ANTHROPIC_API_KEY

# Import LangChain tools
from tools.options_chain import scan_options_chain
from tools.news_sentiment import analyze_news_sentiment
from tools.trade_executor import (
    get_account_info, search_option_contracts,
    place_option_order, get_positions,
)

# Import Phase 1 tools as LangChain tools
from langchain.tools import tool as lc_tool


@lc_tool
def analyze_technicals(ticker: str, period: str = "6mo") -> dict:
    """
    Run full technical analysis on a stock.
    Returns: price, trend, RSI, MACD, Bollinger Bands, Stochastic, ATR,
    volume analysis, support/resistance, and composite signal.

    Args:
        ticker: Stock symbol e.g. "TSLA"
        period: Data period "1mo", "3mo", "6mo", "1y"
    """
    from tools.technical import full_technical_analysis
    return full_technical_analysis(ticker, period=period)


@lc_tool
def recommend_strategy(
    ticker: str,
    outlook: str,
    iv_percentile: float,
    days_to_expiry: int = 30,
    risk_tolerance: str = "moderate",
    account_size: float = 10000,
) -> dict:
    """
    Recommend options strategies based on market conditions.

    Args:
        ticker: Stock symbol
        outlook: "bullish" / "bearish" / "neutral"
        iv_percentile: IV percentile 0-100
        days_to_expiry: Target DTE
        risk_tolerance: "conservative" / "moderate" / "aggressive"
        account_size: Account size in USD
    """
    from tools.strategy import recommend_strategies
    from tools.market_data import get_current_price

    price = get_current_price(ticker)
    strategies = recommend_strategies(
        ticker=ticker,
        current_price=price,
        trend=outlook,
        iv_percentile=iv_percentile,
        days_to_expiry=days_to_expiry,
        risk_level=risk_tolerance,
        account_size=account_size,
    )
    return {
        "ticker": ticker,
        "current_price": price,
        "outlook": outlook,
        "iv_environment": "high" if iv_percentile >= 50 else "low",
        "recommended_strategies": strategies,
    }


@lc_tool
def scan_unusual_activity(tickers: list[str] = None) -> dict:
    """
    Scan for unusual options activity across tickers.
    Detects: Vol/OI surges, high volume, ATM OI magnets,
    extreme P/C ratios, institutional far-month positioning.

    Args:
        tickers: List of stock symbols to scan. Defaults to watchlist.
    """
    from tools.unusual_activity import scan_unusual
    from config import WATCHLIST

    tickers = tickers or WATCHLIST
    results = scan_unusual(tickers)
    return {
        "total_alerts": len(results),
        "top_alerts": results[:15],
    }


@lc_tool
def get_iv_data(ticker: str) -> dict:
    """
    Get IV percentile, IV rank, and historical volatility data for a ticker.

    Args:
        ticker: Stock symbol
    """
    from tools.iv_tracker import get_iv_percentile, record_daily_iv
    record_daily_iv(ticker)
    return get_iv_percentile(ticker)


# All tools available to the agent
ALL_TOOLS = [
    scan_options_chain,
    analyze_technicals,
    recommend_strategy,
    scan_unusual_activity,
    get_iv_data,
    analyze_news_sentiment,
    get_account_info,
    search_option_contracts,
    place_option_order,
    get_positions,
]


# System prompt
SYSTEM_PROMPT = """You are a professional options trading analysis Agent with these capabilities:

1. **Options Chain Scanning**: Fetch real-time options chain data including Greeks, IV, open interest
2. **Technical Analysis**: Analyze price trends with RSI, MACD, Bollinger Bands, and more
3. **Strategy Recommendation**: Recommend optimal options strategies based on market conditions
4. **Unusual Activity Detection**: Detect institutional-level options flow and anomalies
5. **IV Tracking**: Track implied volatility percentile and rank over time
6. **News Sentiment**: Analyze news for market sentiment signals
7. **Trade Execution**: Execute paper trades via Alpaca (simulation only)
8. **Portfolio Management**: Check account balance and positions

Analysis Framework (based on 10 years options trading experience):

Step 1: Determine overall trend (technical analysis + news sentiment)
Step 2: Evaluate IV environment (current IV vs historical IV percentile)
Step 3: Select strategy (sell premium in high IV, buy premium in low IV)
Step 4: Size position (max 2-5% account risk per trade)
Step 5: Set entry/exit rules

Key Principles:
- Take profit at 50% for credit spreads
- Stop loss at 50% for debit strategies
- Never hold naked short positions through earnings
- Watch for unusual OI changes and Vol/OI ratios
- Skip contracts with bid-ask spread > 10% of mid price
- Prefer liquid weekly and monthly options

IMPORTANT: Always respond in Chinese (Mandarin).
Structure each analysis as:
1. Market overview (trend + sentiment)
2. IV environment assessment
3. Strategy suggestion (with specific strikes and expiry)
4. Risk warnings
5. Entry/exit rules
"""


def _build_graph():
    """Build LangGraph agent graph."""
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    from langchain_anthropic import ChatAnthropic

    class AgentState(TypedDict):
        messages: Annotated[list, add_messages]

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250514",
        api_key=ANTHROPIC_API_KEY,
        max_tokens=4096,
    )
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()


def invoke(user_message: str) -> str:
    """
    Convenience function: send a message to the agent and get the response text.
    Falls back to Phase 1 offline analysis if API key not set.
    Builds a new graph per call (lightweight) for thread safety.
    """
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_key_here":
        return _offline_fallback(user_message)

    agent = _build_graph()

    result = agent.invoke({
        "messages": [{"role": "user", "content": user_message}],
    })

    last_msg = result["messages"][-1]
    if hasattr(last_msg, "content") and last_msg.content:
        return last_msg.content
    return str(last_msg)


def _offline_fallback(user_message: str) -> str:
    """
    Offline mode: use Phase 1 tools directly without LLM.
    Parses simple commands like "analyze TSLA" or "scan".
    """
    msg = user_message.upper().strip()

    # Extract ticker
    import re
    tickers = re.findall(r'\b([A-Z]{1,5})\b', msg)
    # Filter common words
    skip = {"THE", "FOR", "AND", "ALL", "GET", "RUN", "WHAT", "HOW", "CAN",
            "HELP", "SCAN", "ANALYZE", "QUICK", "NEWS", "FAST", "DAILY",
            "ACCOUNT", "BALANCE", "PORTFOLIO"}
    tickers = [t for t in tickers if t not in skip]

    if any(w in msg for w in ["SCAN", "DAILY"]):
        from scanner import daily_scan
        daily_scan()
        return "[Offline mode] Daily scan completed. See output above."

    if any(w in msg for w in ["ACCOUNT", "BALANCE", "PORTFOLIO"]):
        from tools.trade_executor import get_account_info, get_positions
        acct = get_account_info.invoke({})
        pos = get_positions.invoke({})
        lines = [f"Equity: ${acct.get('equity', 'N/A')}",
                 f"Cash: ${acct.get('cash', 'N/A')}",
                 f"Buying Power: ${acct.get('buying_power', 'N/A')}",
                 f"Positions: {len(pos)}"]
        return "[Offline mode] Account Info:\n  " + "\n  ".join(lines)

    if any(w in msg for w in ["NEWS"]) and tickers:
        from tools.news_sentiment import analyze_news_sentiment
        result = analyze_news_sentiment.invoke({"ticker": tickers[0], "limit": 5})
        if "error" in result:
            return f"[Offline mode] News error: {result['error']}"
        lines = [f"{a['title']}" for a in result.get("articles", [])]
        return f"[Offline mode] News for {tickers[0]}:\n  " + "\n  ".join(lines)

    if tickers:
        ticker = tickers[0]
        if any(w in msg for w in ["QUICK", "FAST"]):
            from scanner import quick_scan
            quick_scan(ticker)
            return f"[Offline mode] Quick scan for {ticker} completed."
        else:
            from agent import full_analysis
            full_analysis(ticker)
            return f"[Offline mode] Full analysis for {ticker} completed."

    return (
        "[Offline mode] ANTHROPIC_API_KEY not configured.\n"
        "Available commands:\n"
        "  - 'analyze TSLA' - full analysis\n"
        "  - 'quick NVDA' - quick scan\n"
        "  - 'scan' - daily scan all watchlist\n"
        "  - 'news AAPL' - news sentiment\n"
        "  - 'account' - Alpaca paper account info\n"
        "\nSet ANTHROPIC_API_KEY in .env to enable AI conversation mode."
    )


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "analyze TSLA"
    print(invoke(query))
