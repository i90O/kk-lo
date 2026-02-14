"""
Daily data collection job.
Run via cron, Task Scheduler, or leave running with built-in scheduler.

Usage:
    python -m jobs.daily_collector          # Run once now
    python -m jobs.daily_collector --loop   # Run on schedule (keep alive)
"""

import sys
import time
from datetime import datetime

import schedule
from rich.console import Console
from log import setup_logging

setup_logging()

from config import WATCHLIST
from tools.iv_tracker import batch_record, iv_dashboard
from tools.unusual_activity import scan_unusual
from log import get_logger

console = Console()
logger = get_logger(__name__)


def daily_iv_collection():
    """After-market IV data collection. Run after 4:30 PM ET."""
    console.print(f"\n[bold]IV Collection - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/bold]")

    results = batch_record(WATCHLIST)
    success = sum(1 for r in results if "error" not in r)
    console.print(f"  Collected: {success}/{len(WATCHLIST)} tickers")

    # Print dashboard
    dash = iv_dashboard(WATCHLIST)
    for d in dash:
        if "status" not in d:
            ticker = d.get("ticker", "")
            iv = d.get("current_iv")
            hv = d.get("hv20")
            console.print(
                f"  {ticker}: IV={iv:.1f}%" if iv else f"  {ticker}: IV=N/A",
                end=""
            )
            console.print(f" HV20={hv:.1f}%" if hv else " HV20=N/A")


def intraday_unusual_scan():
    """Intraday unusual activity scan. Run every 30 minutes during market hours."""
    now = datetime.now()
    # Skip weekends
    if now.weekday() >= 5:
        return
    # Skip outside market hours (rough check: 9:30-16:00 ET)
    hour = now.hour
    if hour < 9 or hour >= 16:
        return

    console.print(f"\n[bold]Unusual Activity Scan - {now.strftime('%H:%M')}[/bold]")

    results = scan_unusual(WATCHLIST)
    if results:
        console.print(f"  Found {len(results)} alerts")
        for r in results[:5]:
            console.print(
                f"  {r.get('ticker')} {r.get('type')} "
                f"{r.get('side', '')} ${r.get('strike', 0):.0f} "
                f"Flow: ${r.get('premium_flow', 0):,.0f}"
            )
    else:
        console.print("  No unusual activity detected")


def run_once():
    """Run all collection tasks once."""
    console.print("[bold]Running one-time data collection...[/bold]")
    daily_iv_collection()
    console.print()

    console.print("[bold]Running unusual activity scan...[/bold]")
    results = scan_unusual(WATCHLIST)
    console.print(f"Found {len(results)} unusual activity alerts")
    for r in results[:10]:
        console.print(
            f"  {r.get('ticker')} {r.get('type')} "
            f"{r.get('side', '')} ${r.get('strike', 0):.0f} "
            f"Flow: ${r.get('premium_flow', 0):,.0f}"
        )

    # Store unusual activity in DB
    try:
        from data.models import init_db, get_session, UnusualActivity
        init_db()
        session = get_session()
        today = datetime.now().date()
        saved = 0
        for r in results:
            try:
                exp_str = r.get("expiration", "")
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date() if exp_str else None
            except (ValueError, TypeError):
                exp_date = None
            entry = UnusualActivity(
                ticker=r.get("ticker", ""),
                date=today,
                alert_type=r.get("type", ""),
                contract_symbol=r.get("contract", ""),
                contract_type=r.get("side", "").lower() or None,
                strike=r.get("strike"),
                expiration=exp_date,
                volume=r.get("volume"),
                open_interest=r.get("open_interest"),
                vol_oi_ratio=r.get("vol_oi_ratio"),
                iv=r.get("iv"),
                premium_flow=r.get("premium_flow"),
                interpretation=r.get("interpretation"),
            )
            session.add(entry)
            saved += 1
        session.commit()
        session.close()
        console.print(f"\n[dim]Saved {saved} alerts to database.[/dim]")
    except Exception as e:
        logger.warning("DB save error: %s", e)
        console.print(f"\n[dim]DB note: {e}[/dim]")


def run_scheduler():
    """Run on schedule. Keep process alive."""
    console.print("[bold]Starting scheduled data collector...[/bold]")
    console.print("  IV collection: daily at 17:00")
    console.print("  Unusual scan: every 30 minutes during market hours")
    console.print("  Press Ctrl+C to stop\n")

    # Schedule tasks
    schedule.every().day.at("17:00").do(daily_iv_collection)
    schedule.every(30).minutes.do(intraday_unusual_scan)

    # Run IV collection immediately on first start
    daily_iv_collection()

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        console.print("\n[bold]Scheduler stopped.[/bold]")


if __name__ == "__main__":
    if "--loop" in sys.argv:
        run_scheduler()
    else:
        run_once()
