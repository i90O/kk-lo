"""OptionsAgent - Main analysis workflow."""

import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from tools.market_data import get_current_price, get_stock_info, get_options_chain
from tools.technical import full_technical_analysis
from tools.strategy import recommend_strategies
from tools.unusual_activity import scan_unusual
from tools.iv_tracker import get_iv_percentile, record_daily_iv
from config import DEFAULT_ACCOUNT_SIZE, DEFAULT_RISK_LEVEL, DEFAULT_DTE

console = Console()


def full_analysis(
    ticker: str,
    account_size: float = DEFAULT_ACCOUNT_SIZE,
    risk: str = DEFAULT_RISK_LEVEL,
    dte: int = DEFAULT_DTE,
):
    """
    Run full options analysis pipeline for a ticker.

    Steps:
    1. Basic stock info
    2. Technical analysis
    3. Options chain data
    4. IV percentile
    5. Unusual activity scan
    6. Strategy recommendation
    7. Generate formatted report
    """
    ticker = ticker.upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    console.print(f"\n[bold]Analyzing {ticker}...[/bold]\n")

    # Step 1: Basic info
    console.print("  [dim]1/6 Fetching stock info...[/dim]")
    info = get_stock_info(ticker)
    price = get_current_price(ticker)

    # Step 2: Technical analysis
    console.print("  [dim]2/6 Running technical analysis...[/dim]")
    ta_result = full_technical_analysis(ticker)

    # Step 3: Options chain (just summary, not full chain to save time)
    console.print("  [dim]3/6 Fetching options chain...[/dim]")
    chain = get_options_chain(ticker)

    # Step 4: IV data
    console.print("  [dim]4/6 Checking IV data...[/dim]")
    record_daily_iv(ticker)
    iv_data = get_iv_percentile(ticker)

    # Step 5: Unusual activity
    console.print("  [dim]5/6 Scanning unusual activity...[/dim]")
    unusual = scan_unusual([ticker])

    # Step 6: Strategy recommendation
    console.print("  [dim]6/6 Generating strategy recommendations...[/dim]")
    iv_pct = iv_data.get("iv_percentile") if iv_data.get("iv_percentile") is not None else None
    strategies = recommend_strategies(
        ticker=ticker,
        current_price=price,
        trend=ta_result.get("trend", "neutral"),
        iv_percentile=iv_pct,
        days_to_expiry=dte,
        risk_level=risk,
        account_size=account_size,
        atr=ta_result.get("atr"),
    )

    # === Generate Report ===
    _print_report(ticker, now, price, info, ta_result, chain, iv_data, unusual, strategies, account_size, risk)

    return {
        "ticker": ticker,
        "price": price,
        "info": info,
        "technical": ta_result,
        "chain_summary": {
            "expirations": len(chain.get("expirations", [])),
            "total_contracts": chain.get("total_contracts", 0),
            "pc_vol_ratio": chain.get("put_call_volume_ratio"),
            "pc_oi_ratio": chain.get("put_call_oi_ratio"),
            "atm_call": chain.get("atm_call"),
            "atm_put": chain.get("atm_put"),
        },
        "iv_data": iv_data,
        "unusual": unusual,
        "strategies": strategies,
    }


def _print_report(ticker, now, price, info, ta, chain, iv_data, unusual, strategies, account_size, risk):
    """Print formatted analysis report."""

    # Header
    header = Text()
    header.append(f"\n{'=' * 55}\n", style="bold cyan")
    header.append(f"       {ticker} Options Analysis Report\n", style="bold white")
    header.append(f"       {now} | Price: ${price:.2f}\n", style="white")
    header.append(f"{'=' * 55}", style="bold cyan")
    console.print(header)

    # Section 1: Market Overview
    console.print("\n[bold cyan]I. Market Overview[/bold cyan]")
    trend = ta.get("trend", "unknown")
    strength = ta.get("strength", 0)
    stars = "*" * strength + "." * (5 - strength)

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Name", info.get("name", ""))
    table.add_row("Sector", info.get("sector", "N/A"))
    mc = info.get("market_cap", 0)
    mc_str = f"${mc/1e9:.1f}B" if mc > 1e9 else f"${mc/1e6:.0f}M" if mc > 1e6 else str(mc)
    table.add_row("Market Cap", mc_str)
    table.add_row("P/E", f"{info.get('pe_ratio', 'N/A')}")
    table.add_row("Beta", f"{info.get('beta', 'N/A')}")
    table.add_row("Next Earnings", info.get("earnings_date", "N/A") or "N/A")
    table.add_row("Trend", f"{trend.upper()} | Strength: {stars}")
    table.add_row("Change", f"{ta.get('change_pct', 0):+.2f}%")
    console.print(table)

    # Section 2: Technical Analysis
    console.print("\n[bold cyan]II. Technical Analysis[/bold cyan]")
    ta_table = Table(show_header=True, box=None, padding=(0, 2))
    ta_table.add_column("Indicator", style="dim")
    ta_table.add_column("Value")
    ta_table.add_column("Signal")

    rsi = ta.get("rsi")
    ta_table.add_row("RSI(14)", f"{rsi:.1f}" if rsi else "N/A", ta.get("rsi_signal", ""))
    ta_table.add_row("MACD", f"{ta.get('macd', 0):.3f}" if ta.get("macd") else "N/A", ta.get("macd_cross", ""))
    ta_table.add_row("MACD Hist", f"{ta.get('macd_histogram', 0):.3f}" if ta.get("macd_histogram") else "N/A", "")
    ta_table.add_row("Bollinger", ta.get("bb_position", "N/A"), "")
    ta_table.add_row("Stoch K/D", f"{ta.get('stoch_k', 0):.1f}/{ta.get('stoch_d', 0):.1f}" if ta.get("stoch_k") else "N/A", "")
    ta_table.add_row("ATR(14)", f"${ta.get('atr', 0):.2f} ({ta.get('atr_pct', 0):.1f}%)" if ta.get("atr") else "N/A", "")
    ta_table.add_row("Volume", f"{ta.get('volume', 0):,}", f"{ta.get('volume_ratio', 0):.2f}x avg")
    sma200_str = f"${ta['sma200']:.2f}" if ta.get("sma200") else "N/A"
    ta_table.add_row("SMA 20/50/200", f"${ta.get('sma20', 0):.2f} / ${ta.get('sma50', 0):.2f} / {sma200_str}", "")
    ta_table.add_row("Support (20d)", f"${ta.get('support_20d', 0):.2f}", "")
    ta_table.add_row("Resistance (20d)", f"${ta.get('resistance_20d', 0):.2f}", "")
    console.print(ta_table)

    # Section 3: Volatility Environment
    console.print("\n[bold cyan]III. Volatility Environment[/bold cyan]")
    vol_table = Table(show_header=False, box=None, padding=(0, 2))
    vol_table.add_column("Key", style="dim")
    vol_table.add_column("Value")

    current_iv = iv_data.get("current_iv")
    iv_pct = iv_data.get("iv_percentile")
    iv_rank = iv_data.get("iv_rank")
    hv20 = ta.get("atr_pct")  # approximate

    vol_table.add_row("ATM IV (30d)", f"{current_iv:.1f}%" if current_iv else "N/A (need more data)")
    vol_table.add_row("IV Percentile", f"{iv_pct:.0f}" if iv_pct is not None else "N/A (need 30+ days)")
    vol_table.add_row("IV Rank", f"{iv_rank:.0f}" if iv_rank is not None else "N/A")
    vol_table.add_row("Data Points", str(iv_data.get("data_points", 0)))

    # P/C ratios from chain
    pc_vol = chain.get("put_call_volume_ratio")
    pc_oi = chain.get("put_call_oi_ratio")
    vol_table.add_row("P/C Volume Ratio", f"{pc_vol:.3f}" if pc_vol else "N/A")
    vol_table.add_row("P/C OI Ratio", f"{pc_oi:.3f}" if pc_oi else "N/A")
    vol_table.add_row("Expirations", str(len(chain.get("expirations", []))))
    vol_table.add_row("Total Contracts", f"{chain.get('total_contracts', 0):,}")

    iv_env = "HIGH" if (iv_pct is not None and iv_pct >= 50) else "LOW" if (iv_pct is not None and iv_pct < 50) else "UNKNOWN"
    vol_table.add_row("IV Environment", iv_env)
    console.print(vol_table)

    # Section 4: Unusual Activity
    console.print("\n[bold cyan]IV. Unusual Options Activity[/bold cyan]")
    if not unusual:
        console.print("  [dim]No significant unusual activity detected.[/dim]")
    else:
        for i, u in enumerate(unusual[:5], 1):
            console.print(f"  {i}. [{u.get('type', '')}] {u.get('side', '')} ${u.get('strike', 0):.0f} {u.get('expiration', '')}")
            console.print(f"     Vol: {u.get('volume', 0):,} | OI: {u.get('open_interest', 0):,} | Flow: ${u.get('premium_flow', 0):,.0f}")
            console.print(f"     {u.get('interpretation', '')}")

    # Section 5: Strategy Recommendations
    console.print(f"\n[bold cyan]V. Strategy Recommendations[/bold cyan]")
    console.print(f"  [dim]Account: ${account_size:,.0f} | Risk: {risk} | Target DTE: ~30 days[/dim]\n")

    if not strategies:
        console.print("  [yellow]No strategies recommended for current conditions.[/yellow]")
    else:
        for i, s in enumerate(strategies, 1):
            console.print(f"  [bold]Strategy {i}: {s['name_en']}[/bold]")
            console.print(f"  {s.get('name_cn', '')}")

            # Legs
            for leg in s.get("legs", []):
                note = f" ({leg['note']})" if "note" in leg else ""
                console.print(f"    - {leg['action']} ${leg['strike']:.0f} {leg['type']}{note}")

            console.print(f"    DTE: {s.get('dte_range', 'N/A')}")
            console.print(f"    Max Profit: {s.get('max_profit', 'N/A')}")
            console.print(f"    Max Loss: {s.get('max_loss', 'N/A')}")
            console.print(f"    Est Win Rate: {s.get('win_rate_est', 'N/A')}")
            console.print(f"    Position: {s.get('position_size', 'N/A')}")
            console.print("    Exit Rules:")
            for rule in s.get("exit_rules", []):
                console.print(f"      - {rule}")
            console.print()

    # Section 6: Risk Warning
    console.print("[bold cyan]VI. Risk Warnings[/bold cyan]")
    warnings = []
    if info.get("earnings_date"):
        warnings.append(f"Earnings on {info['earnings_date']} - elevated IV risk around this date.")
    if ta.get("atr_pct") and ta["atr_pct"] > 3:
        warnings.append(f"High ATR ({ta['atr_pct']:.1f}%) - stock is volatile, size positions accordingly.")
    if pc_vol and pc_vol > 1.5:
        warnings.append(f"Elevated P/C ratio ({pc_vol:.2f}) - heavy put activity may signal bearish pressure.")
    if ta.get("rsi_signal") == "overbought":
        warnings.append("RSI overbought - consider waiting for pullback before bullish entries.")
    elif ta.get("rsi_signal") == "oversold":
        warnings.append("RSI oversold - may bounce, but don't catch falling knives without confirmation.")
    warnings.append("This is for educational purposes only. Not financial advice.")
    warnings.append("Polygon data has ~15min delay (Options Starter plan). Verify with your broker before trading.")

    for w in warnings:
        console.print(f"  ! {w}")

    console.print(f"\n{'=' * 55}\n")


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    full_analysis(ticker)
