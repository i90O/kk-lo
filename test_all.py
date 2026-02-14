"""Comprehensive test for all OptionsAgent components."""

import sys
import traceback
from rich.console import Console

console = Console()
passed = 0
failed = 0


def run_test(name, func):
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


# Test 1: market_data - SPY options chain
def test_market_data():
    from tools.market_data import get_options_chain, get_current_price, get_stock_info, get_stock_data

    price = get_current_price("SPY")
    assert price > 0, f"Price should be positive, got {price}"
    console.print(f"  SPY price: ${price:.2f}")

    info = get_stock_info("SPY")
    assert "ticker" in info, "Missing ticker in info"
    console.print(f"  Info keys: {list(info.keys())}")

    df = get_stock_data("SPY", period="1mo")
    assert len(df) > 0, "No stock data returned"
    console.print(f"  Stock data: {len(df)} rows")

    chain = get_options_chain("SPY")
    assert "error" not in chain, f"Chain error: {chain.get('error')}"
    assert chain["total_contracts"] > 0, "No contracts found"
    assert chain["expirations"], "No expirations"
    console.print(f"  Expirations: {len(chain['expirations'])}")
    console.print(f"  Total contracts: {chain['total_contracts']}")
    console.print(f"  P/C Vol Ratio: {chain.get('put_call_volume_ratio')}")
    console.print(f"  P/C OI Ratio: {chain.get('put_call_oi_ratio')}")

    if chain.get("atm_call"):
        c = chain["atm_call"]
        console.print(f"  ATM Call: strike={c['strike']}, IV={c['impliedVolatility']:.4f}")


# Test 2: technical - AAPL analysis
def test_technical():
    from tools.technical import full_technical_analysis

    result = full_technical_analysis("AAPL")
    assert "error" not in result, f"Error: {result.get('error')}"

    required = ["current_price", "sma20", "sma50", "rsi", "macd", "macd_signal",
                "macd_histogram", "bb_upper", "bb_lower", "stoch_k", "stoch_d",
                "atr", "volume", "support_20d", "resistance_20d", "signal", "strength"]

    for key in required:
        assert key in result, f"Missing key: {key}"
        console.print(f"  {key}: {result[key]}")


# Test 3: strategy - 6 market scenarios
def test_strategy():
    from tools.strategy import recommend_strategies

    scenarios = [
        ("bullish", 75, "Bullish + High IV"),
        ("bullish", 25, "Bullish + Low IV"),
        ("bearish", 75, "Bearish + High IV"),
        ("bearish", 25, "Bearish + Low IV"),
        ("neutral", 75, "Neutral + High IV"),
        ("neutral", 25, "Neutral + Low IV"),
    ]

    for trend, iv_pct, label in scenarios:
        result = recommend_strategies(
            ticker="TEST", current_price=100, trend=trend,
            iv_percentile=iv_pct, days_to_expiry=30,
            risk_level="moderate", account_size=10000, atr=3.0,
        )
        assert len(result) > 0, f"No strategies for {label}"
        names = [s["name_en"] for s in result]
        console.print(f"  {label}: {', '.join(names)}")


# Test 4: unusual_activity - scan 10 stocks
def test_unusual_activity():
    from tools.unusual_activity import scan_unusual

    tickers = ["TSLA", "NVDA", "AAPL", "SPY", "QQQ", "META", "AMZN", "AMD", "MSFT", "GOOGL"]
    results = scan_unusual(tickers)
    console.print(f"  Scanned {len(tickers)} tickers, found {len(results)} alerts")
    for r in results[:5]:
        console.print(f"  - {r.get('ticker')} {r.get('type')} {r.get('side', '')} ${r.get('strike', 0):.0f} Flow: ${r.get('premium_flow', 0):,.0f}")


# Test 5: iv_tracker - record + percentile
def test_iv_tracker():
    from tools.iv_tracker import record_daily_iv, get_iv_percentile, batch_record, iv_dashboard
    from config import WATCHLIST

    # Single record
    result = record_daily_iv("TSLA")
    assert "error" not in result, f"Error: {result.get('error')}"
    console.print(f"  TSLA IV record: IV={result.get('atm_iv')}, HV20={result.get('hv20')}")

    # Percentile (will be N/A with only 1 data point)
    pct = get_iv_percentile("TSLA")
    console.print(f"  TSLA IV percentile: {pct}")
    assert "ticker" in pct

    # Dashboard
    dash = iv_dashboard(WATCHLIST[:3])
    console.print(f"  Dashboard entries: {len(dash)}")
    for d in dash:
        console.print(f"  - {d.get('ticker')}: IV={d.get('current_iv')}, HV20={d.get('hv20')}")


# Test 6: agent - full TSLA analysis
def test_agent():
    from agent import full_analysis

    result = full_analysis("TSLA")
    assert result["ticker"] == "TSLA"
    assert result["price"] > 0
    assert "technical" in result
    assert "strategies" in result
    console.print(f"  Full analysis completed. Price: ${result['price']:.2f}")
    console.print(f"  Strategies: {len(result['strategies'])}")
    console.print(f"  Unusual alerts: {len(result['unusual'])}")


# Test 7: scanner - daily_scan
def test_scanner():
    from scanner import quick_scan
    # Only test quick_scan (daily_scan already tested and takes too long)
    quick_scan("NVDA")
    console.print("  Quick scan completed successfully.")


# Run all tests
if __name__ == "__main__":
    console.print("[bold]=" * 55)
    console.print("[bold]  OptionsAgent Comprehensive Test Suite[/bold]")
    console.print("[bold]=" * 55)

    run_test("1. Market Data (SPY options chain)", test_market_data)
    run_test("2. Technical Analysis (AAPL)", test_technical)
    run_test("3. Strategy Engine (6 scenarios)", test_strategy)
    run_test("4. Unusual Activity (10 stocks)", test_unusual_activity)
    run_test("5. IV Tracker (record + percentile)", test_iv_tracker)
    run_test("6. Agent (full TSLA analysis)", test_agent)
    run_test("7. Scanner (quick scan)", test_scanner)

    console.print(f"\n[bold]{'=' * 55}[/bold]")
    console.print(f"[bold]  Results: {passed} passed, {failed} failed[/bold]")
    console.print(f"[bold]{'=' * 55}[/bold]\n")

    sys.exit(1 if failed > 0 else 0)
