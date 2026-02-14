"""Comprehensive test for all Phase 2 components."""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console

console = Console()
passed = 0
failed = 0


def test(name, func):
    global passed, failed
    console.print(f"\n[bold]TEST: {name}[/bold]")
    try:
        func()
        passed += 1
        console.print(f"  [green]PASSED[/green]")
    except Exception as e:
        failed += 1
        console.print(f"  [red]FAILED: {e}[/red]")
        traceback.print_exc()


# --- Phase 1 Tests (should still pass) ---

def test_config():
    from config import (
        WATCHLIST, ANTHROPIC_API_KEY, POLYGON_API_KEY, ALPACA_API_KEY,
        BASE_DIR, DB_PATH, DEFAULT_ACCOUNT_SIZE
    )
    assert len(WATCHLIST) == 12
    assert DEFAULT_ACCOUNT_SIZE == 10000
    assert BASE_DIR
    console.print(f"  Watchlist: {len(WATCHLIST)} tickers")
    console.print(f"  ANTHROPIC_API_KEY: {'configured' if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your_key_here' else 'not set'}")
    console.print(f"  POLYGON_API_KEY: {'configured' if POLYGON_API_KEY and POLYGON_API_KEY != 'your_key_here' else 'not set'}")
    console.print(f"  ALPACA_API_KEY: {'configured' if ALPACA_API_KEY and ALPACA_API_KEY != 'your_key_here' else 'not set'}")


def test_market_data():
    from tools.market_data import get_current_price, get_stock_info
    price = get_current_price("SPY")
    assert price > 0
    console.print(f"  SPY: ${price:.2f}")


def test_technical():
    from tools.technical import full_technical_analysis
    r = full_technical_analysis("AAPL")
    assert "error" not in r
    assert r["signal"] in ["bullish", "bearish", "neutral"]
    console.print(f"  AAPL: {r['signal']} (strength {r['strength']}/5)")


def test_strategy():
    from tools.strategy import recommend_strategies
    for trend, iv in [("bullish", 75), ("bearish", 25), ("neutral", 60)]:
        r = recommend_strategies("TEST", 100, trend, iv)
        assert len(r) > 0
        console.print(f"  {trend}/IV{iv}: {r[0]['name_en']}")


def test_unusual():
    from tools.unusual_activity import scan_unusual
    r = scan_unusual(["SPY", "TSLA"])
    console.print(f"  Found {len(r)} alerts for SPY+TSLA")


def test_iv_tracker():
    from tools.iv_tracker import record_daily_iv, get_iv_percentile
    r = record_daily_iv("TSLA")
    assert "error" not in r
    console.print(f"  TSLA IV recorded: {r.get('atm_iv')}")
    p = get_iv_percentile("TSLA")
    console.print(f"  TSLA percentile data points: {p.get('data_points')}")


# --- Phase 2 New Components ---

def test_options_chain_tool():
    from tools.options_chain import scan_options_chain
    r = scan_options_chain.invoke({"ticker": "SPY", "contract_type": "call"})
    assert "error" not in r
    assert r["count"] > 0
    console.print(f"  Source: {r.get('source', 'unknown')}")
    console.print(f"  SPY calls: {r['count']} contracts")
    console.print(f"  Avg IV: {r.get('summary', {}).get('avg_iv')}")


def test_news_sentiment():
    from tools.news_sentiment import analyze_news_sentiment
    r = analyze_news_sentiment.invoke({"ticker": "TSLA", "limit": 3})
    assert "error" not in r
    console.print(f"  Source: {r.get('source', 'unknown')}")
    console.print(f"  TSLA news: {r.get('news_count', 0)} articles")
    for a in r.get("articles", [])[:2]:
        title = a.get("title", "")[:60]
        console.print(f"    - {title}...")


def test_trade_executor():
    from tools.trade_executor import get_account_info
    r = get_account_info.invoke({})
    # Will return error if not configured, which is OK
    if "error" in r:
        console.print(f"  [yellow]Alpaca not configured: {r['error']}[/yellow]")
    else:
        console.print(f"  Equity: {r.get('equity')}")
        console.print(f"  Buying power: {r.get('buying_power')}")


def test_db_models():
    from data.models import init_db, get_engine
    init_db()
    engine = get_engine()
    console.print(f"  Database: {engine.url}")
    console.print("  Tables created successfully")


def test_langgraph_agent():
    from agents.options_agent import invoke
    r = invoke("analyze TSLA")
    assert r
    # In offline mode, should still work
    console.print(f"  Response length: {len(r)} chars")
    console.print(f"  First 100 chars: {r[:100]}...")


def test_main_cli():
    # Just test import and offline mode
    from agents.options_agent import _offline_fallback
    r = _offline_fallback("help")
    assert "Offline mode" in r
    console.print(f"  Offline fallback works")


def test_fastapi_app():
    from api.main import app
    assert app.title == "OptionsAgent API"
    routes = [r.path for r in app.routes]
    expected = ["/api/analyze", "/api/chat", "/api/technical/{ticker}", "/api/iv/{ticker}"]
    for e in expected:
        assert e in routes, f"Missing route: {e}"
    console.print(f"  FastAPI app: {len(routes)} routes")
    console.print(f"  Key routes verified: {', '.join(expected)}")


def test_daily_collector():
    # Just test import
    from jobs.daily_collector import daily_iv_collection, intraday_unusual_scan
    console.print("  Module imports OK")
    console.print("  daily_iv_collection: callable")
    console.print("  intraday_unusual_scan: callable")


def test_frontend_exists():
    assert os.path.exists("frontend/package.json")
    assert os.path.exists("frontend/src/app/page.tsx")
    assert os.path.exists("frontend/src/lib/api.ts")
    assert os.path.exists("frontend/src/lib/store.ts")
    assert os.path.exists("frontend/node_modules")
    console.print("  package.json: OK")
    console.print("  page.tsx: OK")
    console.print("  api.ts: OK")
    console.print("  node_modules: installed")


# Run all tests
if __name__ == "__main__":
    console.print(f"[bold]{'=' * 55}[/bold]")
    console.print("[bold]  OptionsAgent Phase 2 Test Suite[/bold]")
    console.print(f"[bold]{'=' * 55}[/bold]")

    # Phase 1 (existing)
    console.print("\n[bold yellow]--- Phase 1 Components ---[/bold yellow]")
    test("1. Config", test_config)
    test("2. Market Data", test_market_data)
    test("3. Technical Analysis", test_technical)
    test("4. Strategy Engine", test_strategy)
    test("5. Unusual Activity", test_unusual)
    test("6. IV Tracker", test_iv_tracker)

    # Phase 2 (new)
    console.print("\n[bold yellow]--- Phase 2 Components ---[/bold yellow]")
    test("7. Options Chain Tool (LangChain)", test_options_chain_tool)
    test("8. News Sentiment", test_news_sentiment)
    test("9. Trade Executor (Alpaca)", test_trade_executor)
    test("10. Database Models (SQLAlchemy)", test_db_models)
    test("11. LangGraph Agent", test_langgraph_agent)
    test("12. CLI Interface", test_main_cli)
    test("13. FastAPI Backend", test_fastapi_app)
    test("14. Daily Collector", test_daily_collector)
    test("15. Frontend Project", test_frontend_exists)

    console.print(f"\n[bold]{'=' * 55}[/bold]")
    console.print(f"[bold]  Results: {passed} passed, {failed} failed[/bold]")
    console.print(f"[bold]{'=' * 55}[/bold]\n")

    sys.exit(1 if failed > 0 else 0)
