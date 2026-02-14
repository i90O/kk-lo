"""
OptionsAgent CLI - Interactive command-line interface.
Supports both AI conversation mode (with API key) and offline mode.
"""

import sys
import io

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.markdown import Markdown
from log import setup_logging

setup_logging()
from config import ANTHROPIC_API_KEY

console = Console()


def main():
    console.print("[bold green]OptionsAgent v0.2[/bold green]")

    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_key_here":
        console.print("[green]AI mode: ON[/green] (Claude API connected)")
    else:
        console.print("[yellow]Offline mode[/yellow] (set ANTHROPIC_API_KEY in .env for AI chat)")

    console.print(
        "Commands:\n"
        "  'analyze TSLA'     - Full options analysis\n"
        "  'quick NVDA'       - Quick scan\n"
        "  'scan'             - Daily scan all watchlist\n"
        "  'news AAPL'        - News sentiment\n"
        "  'account'          - Alpaca paper account info\n"
        "  Or ask any question in natural language (AI mode)\n"
        "  'quit' to exit\n"
    )

    from agents.options_agent import invoke

    while True:
        try:
            user_input = console.input("[bold cyan]> [/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.strip().lower() in ["quit", "exit", "q"]:
            break

        if not user_input.strip():
            continue

        console.print("\n[dim]Analyzing...[/dim]\n")

        try:
            result = invoke(user_input)
            # Try to render as markdown if it looks like AI output
            if result and not result.startswith("[Offline"):
                try:
                    console.print(Markdown(result))
                except Exception:
                    console.print(result)
            else:
                console.print(result)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        console.print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single command mode
        from agents.options_agent import invoke
        query = " ".join(sys.argv[1:])
        result = invoke(query)
        if result and not result.startswith("[Offline"):
            Console().print(Markdown(result))
        else:
            print(result)
    else:
        main()
