"""Daily market scanner and quick analysis tool."""

import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table

from config import WATCHLIST, DEFAULT_ACCOUNT_SIZE, DEFAULT_RISK_LEVEL, DEFAULT_DTE
from tools.iv_tracker import batch_record, iv_dashboard
from tools.unusual_activity import scan_unusual
from tools.technical import full_technical_analysis
from tools.strategy import recommend_strategies
from tools.market_data import get_current_price
from agent import full_analysis

console = Console()


def daily_scan():
    """
    Daily market scan workflow:
    1. Print date and market status
    2. Batch collect IV data
    3. Scan all watchlist for unusual activity
    4. Run full analysis on top 3 tickers with most unusual activity
    5. Print daily summary
    """
    now = datetime.now()
    console.print(f"\n[bold]{'=' * 55}[/bold]")
    console.print(f"[bold]  OptionsAgent Daily Scan - {now.strftime('%Y-%m-%d %H:%M')}[/bold]")
    console.print(f"[bold]{'=' * 55}[/bold]\n")

    # Check if market is open (rough check - weekday)
    weekday = now.weekday()
    if weekday >= 5:
        console.print("[yellow]  Note: Weekend - using last trading day's data.[/yellow]\n")

    # Step 1: Batch record IV data
    console.print("[bold cyan]Step 1: Collecting IV data for watchlist...[/bold cyan]")
    iv_results = batch_record(WATCHLIST)
    console.print()

    # Step 2: IV Dashboard
    console.print("[bold cyan]Step 2: IV Dashboard[/bold cyan]")
    dash = iv_dashboard(WATCHLIST)
    _print_iv_dashboard(dash)

    # Step 3: Quick technical overview
    console.print("[bold cyan]Step 3: Technical Overview[/bold cyan]")
    tech_summary = []
    for ticker in WATCHLIST:
        try:
            ta = full_technical_analysis(ticker)
            tech_summary.append(ta)
        except Exception as e:
            console.print(f"  [red]{ticker}: Error - {e}[/red]")
    _print_tech_overview(tech_summary)

    # Step 4: Scan unusual activity
    console.print("[bold cyan]Step 4: Scanning unusual options activity...[/bold cyan]")
    unusual = scan_unusual(WATCHLIST)
    if unusual:
        _print_unusual_summary(unusual)
    else:
        console.print("  [dim]No significant unusual activity detected across watchlist.[/dim]\n")

    # Step 5: Full analysis on top tickers
    # Count unusual alerts per ticker
    ticker_alert_count = {}
    for u in unusual:
        t = u.get("ticker", "")
        ticker_alert_count[t] = ticker_alert_count.get(t, 0) + 1

    top_tickers = sorted(ticker_alert_count.keys(), key=lambda t: ticker_alert_count[t], reverse=True)[:3]

    if top_tickers:
        console.print(f"[bold cyan]Step 5: Full analysis on top movers: {', '.join(top_tickers)}[/bold cyan]\n")
        for ticker in top_tickers:
            try:
                full_analysis(ticker)
            except Exception as e:
                console.print(f"  [red]Error analyzing {ticker}: {e}[/red]")
    else:
        # If no unusual activity, analyze top 2 by volume ratio
        console.print("[bold cyan]Step 5: Full analysis on highest volume tickers...[/bold cyan]\n")
        vol_sorted = sorted(tech_summary, key=lambda t: t.get("volume_ratio", 0), reverse=True)
        for ta in vol_sorted[:2]:
            ticker = ta.get("ticker", "")
            if ticker:
                try:
                    full_analysis(ticker)
                except Exception as e:
                    console.print(f"  [red]Error analyzing {ticker}: {e}[/red]")

    # Summary
    console.print(f"\n[bold]{'=' * 55}[/bold]")
    console.print(f"[bold]  Daily Scan Complete - {datetime.now().strftime('%H:%M')}[/bold]")
    console.print(f"  Tickers scanned: {len(WATCHLIST)}")
    console.print(f"  Unusual alerts: {len(unusual)}")
    console.print(f"  Full analyses: {len(top_tickers) or 2}")
    console.print(f"[bold]{'=' * 55}[/bold]\n")


def quick_scan(ticker: str):
    """Quick analysis: key data + strategy suggestion, no full report."""
    ticker = ticker.upper()
    console.print(f"\n[bold]Quick Scan: {ticker}[/bold]\n")

    # Price
    price = get_current_price(ticker)
    console.print(f"  Price: ${price:.2f}")

    # Technical
    ta = full_technical_analysis(ticker)
    trend = ta.get("trend", "unknown")
    strength = ta.get("strength", 0)
    rsi = ta.get("rsi")

    console.print(f"  Trend: {trend.upper()} (strength {strength}/5)")
    console.print(f"  RSI: {rsi:.1f}" if rsi else "  RSI: N/A")
    console.print(f"  MACD: {ta.get('macd_cross', 'neutral')}")
    console.print(f"  BB: {ta.get('bb_position', 'N/A')}")
    console.print(f"  ATR: ${ta.get('atr', 0):.2f} ({ta.get('atr_pct', 0):.1f}%)")
    console.print(f"  Volume: {ta.get('volume_ratio', 0):.2f}x avg")
    console.print(f"  Support: ${ta.get('support_20d', 0):.2f} | Resistance: ${ta.get('resistance_20d', 0):.2f}")

    # IV
    iv_data = _safe_iv(ticker)
    iv_pct = iv_data.get("iv_percentile")
    console.print(f"  IV Percentile: {iv_pct:.0f}" if iv_pct is not None else "  IV Percentile: N/A")

    # Strategy
    strategies = recommend_strategies(
        ticker=ticker,
        current_price=price,
        trend=trend,
        iv_percentile=iv_pct,
        days_to_expiry=DEFAULT_DTE,
        risk_level=DEFAULT_RISK_LEVEL,
        account_size=DEFAULT_ACCOUNT_SIZE,
        atr=ta.get("atr"),
    )

    if strategies:
        s = strategies[0]
        console.print(f"\n  [bold]Suggested: {s['name_en']}[/bold]")
        for leg in s.get("legs", []):
            console.print(f"    {leg['action']} ${leg['strike']:.0f} {leg['type']}")
        console.print(f"    Max Profit: {s.get('max_profit', 'N/A')}")
        console.print(f"    Max Loss: {s.get('max_loss', 'N/A')}")
    else:
        console.print("\n  [dim]No strategy recommended for current conditions.[/dim]")

    console.print()


def _safe_iv(ticker):
    """Get IV data without crashing."""
    try:
        from tools.iv_tracker import get_iv_percentile
        return get_iv_percentile(ticker)
    except Exception:
        return {}


def _print_iv_dashboard(data):
    """Print IV dashboard table."""
    table = Table(title="IV Dashboard")
    table.add_column("Ticker", style="bold")
    table.add_column("Close")
    table.add_column("IV%")
    table.add_column("HV20%")
    table.add_column("IV-HV")

    for d in data:
        if "status" in d:
            table.add_row(d["ticker"], "", "", "", d["status"])
        else:
            iv_hv = d.get("iv_hv_diff")
            table.add_row(
                d["ticker"],
                f"${d['close']:.2f}" if d.get("close") else "N/A",
                f"{d['current_iv']:.1f}" if d.get("current_iv") else "N/A",
                f"{d['hv20']:.1f}" if d.get("hv20") else "N/A",
                f"{iv_hv:+.1f}" if iv_hv is not None else "N/A",
            )

    console.print(table)
    console.print()


def _print_tech_overview(summaries):
    """Print quick technical overview table."""
    table = Table(title="Technical Overview")
    table.add_column("Ticker", style="bold")
    table.add_column("Price")
    table.add_column("Chg%")
    table.add_column("Trend")
    table.add_column("RSI")
    table.add_column("MACD")
    table.add_column("Vol Ratio")

    for ta in summaries:
        if "error" in ta:
            continue
        chg = ta.get("change_pct", 0)
        chg_style = "green" if chg > 0 else "red" if chg < 0 else "white"
        table.add_row(
            ta.get("ticker", ""),
            f"${ta.get('current_price', 0):.2f}",
            f"[{chg_style}]{chg:+.2f}%[/{chg_style}]",
            ta.get("trend", "?"),
            f"{ta.get('rsi', 0):.0f}" if ta.get("rsi") else "N/A",
            ta.get("macd_cross", "neutral")[:8],
            f"{ta.get('volume_ratio', 0):.2f}x",
        )

    console.print(table)
    console.print()


def _print_unusual_summary(unusual):
    """Print unusual activity summary."""
    table = Table(title=f"Unusual Activity ({len(unusual)} alerts)")
    table.add_column("Ticker", style="bold")
    table.add_column("Type")
    table.add_column("Side")
    table.add_column("Strike")
    table.add_column("Exp")
    table.add_column("Flow $")
    table.add_column("Note", max_width=40)

    for u in unusual[:15]:
        table.add_row(
            u.get("ticker", ""),
            u.get("type", ""),
            u.get("side", ""),
            f"${u['strike']:.0f}" if "strike" in u else "",
            str(u.get("expiration", ""))[:10],
            f"${u.get('premium_flow', 0):,.0f}",
            u.get("interpretation", "")[:40],
        )

    console.print(table)
    console.print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # quick_scan mode
        quick_scan(sys.argv[1])
    else:
        daily_scan()
