"""Options strategy recommendation engine."""


def recommend_strategies(
    ticker: str,
    current_price: float,
    trend: str,
    iv_percentile: float | None,
    days_to_expiry: int = 30,
    risk_level: str = "moderate",
    account_size: float = 10000,
    atr: float | None = None,
) -> list[dict]:
    """
    Recommend options strategies based on market conditions.

    Args:
        ticker: Stock symbol
        current_price: Current stock price
        trend: "bullish" / "bearish" / "neutral"
        iv_percentile: 0-100, None if unknown
        days_to_expiry: Target DTE
        risk_level: "conservative" / "moderate" / "aggressive"
        account_size: Total account size in dollars
        atr: Average True Range (for stop loss calculation)

    Returns:
        List of strategy recommendation dicts.
    """
    # Default IV percentile to 50 if unknown
    iv_pct = iv_percentile if iv_percentile is not None else 50
    high_iv = iv_pct >= 50
    low_iv = iv_pct < 50

    # Position sizing: max risk per trade
    risk_multiplier = {"conservative": 0.02, "moderate": 0.05, "aggressive": 0.10}
    max_risk = account_size * risk_multiplier.get(risk_level, 0.05)

    strategies = []

    # --- Strategy Selection Matrix ---

    if trend == "bullish" and high_iv:
        strategies.append(_bull_put_spread(current_price, days_to_expiry, max_risk, atr))
        if risk_level != "conservative":
            strategies.append(_short_put(current_price, days_to_expiry, max_risk, atr))

    elif trend == "bullish" and low_iv:
        strategies.append(_bull_call_spread(current_price, days_to_expiry, max_risk, atr))
        if risk_level == "aggressive":
            strategies.append(_long_call(current_price, days_to_expiry, max_risk, atr))

    elif trend == "bearish" and high_iv:
        strategies.append(_bear_call_spread(current_price, days_to_expiry, max_risk, atr))

    elif trend == "bearish" and low_iv:
        strategies.append(_bear_put_spread(current_price, days_to_expiry, max_risk, atr))
        if risk_level == "aggressive":
            strategies.append(_long_put(current_price, days_to_expiry, max_risk, atr))

    elif trend == "neutral" and high_iv:
        strategies.append(_iron_condor(current_price, days_to_expiry, max_risk, atr))
        if risk_level != "conservative":
            strategies.append(_short_strangle(current_price, days_to_expiry, max_risk, atr))

    elif trend == "neutral" and low_iv:
        strategies.append(_long_straddle(current_price, days_to_expiry, max_risk, atr))
        strategies.append(_calendar_spread(current_price, days_to_expiry, max_risk, atr))

    # Add context to each strategy
    for s in strategies:
        s["ticker"] = ticker
        s["current_price"] = current_price
        s["iv_environment"] = "high" if high_iv else "low"
        s["trend_used"] = trend
        s["risk_level"] = risk_level
        s["account_size"] = account_size
        s["max_risk_per_trade"] = max_risk

    return strategies


# --- Individual Strategy Builders ---

def _strike_step(price):
    """Choose strike increment based on price level."""
    if price < 5:
        return 0.5
    if price < 25:
        return 1
    if price < 200:
        return 5
    return 10


def _round_strike(price, step=None):
    """Round to nearest strike price increment."""
    if step is None:
        step = _strike_step(price)
    return round(price / step) * step


def _bull_put_spread(price, dte, max_risk, atr):
    atr_val = atr or price * 0.03
    sell_strike = _round_strike(price - atr_val)
    wing = _strike_step(price)
    buy_strike = _round_strike(sell_strike - wing)
    spread_width = sell_strike - buy_strike
    # NOTE: credit is estimated, not from live quotes
    est_credit = spread_width * 0.35
    max_loss = (spread_width - est_credit) * 100
    contracts = max(1, int(max_risk / max_loss))

    return {
        "name_en": "Bull Put Spread",
        "name_cn": "Bull Put Spread (看涨卖出看跌价差)",
        "direction": "bullish",
        "legs": [
            {"action": "SELL", "type": "PUT", "strike": sell_strike},
            {"action": "BUY", "type": "PUT", "strike": buy_strike},
        ],
        "dte_range": f"{max(dte - 10, 20)}-{dte + 15} days",
        "max_profit": f"${est_credit * 100 * contracts:.0f} (credit received)",
        "max_loss": f"${max_loss * contracts:.0f}",
        "win_rate_est": "65-70%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of max profit",
            "Stop loss: Close if loss reaches 200% of credit received",
            "Time exit: Close at 21 DTE if not already profitable",
        ],
        "position_size": f"{contracts} contract(s), risking ${max_loss * contracts:.0f}",
    }


def _short_put(price, dte, max_risk, atr):
    atr_val = atr or price * 0.03
    strike = _round_strike(price - atr_val * 1.5)
    est_premium = price * 0.02
    max_loss = (strike - est_premium) * 100  # assignment risk
    contracts = max(1, int(max_risk / (strike * 100) * 5))  # conservative

    return {
        "name_en": "Short Put (Cash-Secured)",
        "name_cn": "Short Put (现金担保卖出看跌)",
        "direction": "bullish",
        "legs": [
            {"action": "SELL", "type": "PUT", "strike": strike},
        ],
        "dte_range": f"{max(dte - 10, 20)}-{dte + 15} days",
        "max_profit": f"~${est_premium * 100 * contracts:.0f} (premium received)",
        "max_loss": f"${strike * 100 * contracts:.0f} (if stock goes to $0, requires cash collateral)",
        "win_rate_est": "70-80%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of premium received",
            "Stop loss: Close if loss reaches 2x premium",
            "Assignment: Accept shares if willing to own at strike price",
        ],
        "position_size": f"{contracts} contract(s), collateral needed: ${strike * 100 * contracts:,.0f}",
    }


def _long_call(price, dte, max_risk, atr):
    strike = _round_strike(price * 1.02)  # slightly OTM
    est_premium = price * 0.04
    contracts = max(1, int(max_risk / (est_premium * 100)))

    return {
        "name_en": "Long Call",
        "name_cn": "Long Call (买入看涨期权)",
        "direction": "bullish",
        "legs": [
            {"action": "BUY", "type": "CALL", "strike": strike},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 30} days",
        "max_profit": "Unlimited",
        "max_loss": f"~${est_premium * 100 * contracts:.0f} (premium paid)",
        "win_rate_est": "35-45%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50-100% gain on premium",
            "Stop loss: Close if premium drops 50%",
            "Time exit: Close at 14 DTE to avoid theta decay",
        ],
        "position_size": f"{contracts} contract(s), cost ~${est_premium * 100 * contracts:.0f}",
    }


def _bull_call_spread(price, dte, max_risk, atr):
    buy_strike = _round_strike(price)  # ATM
    sell_strike = _round_strike(price + (atr or price * 0.03) * 2)
    spread_width = sell_strike - buy_strike
    # NOTE: debit is estimated, not from live quotes
    est_debit = spread_width * 0.55
    max_loss = est_debit * 100
    contracts = max(1, int(max_risk / max_loss))

    return {
        "name_en": "Bull Call Spread",
        "name_cn": "Bull Call Spread (看涨买入看涨价差)",
        "direction": "bullish",
        "legs": [
            {"action": "BUY", "type": "CALL", "strike": buy_strike},
            {"action": "SELL", "type": "CALL", "strike": sell_strike},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 30} days",
        "max_profit": f"${(spread_width - est_debit) * 100 * contracts:.0f}",
        "max_loss": f"${max_loss * contracts:.0f} (debit paid)",
        "win_rate_est": "45-55%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of max profit",
            "Stop loss: Close if debit drops 50%",
            "Time exit: Close at 14 DTE",
        ],
        "position_size": f"{contracts} contract(s), cost ~${max_loss * contracts:.0f}",
    }


def _bear_call_spread(price, dte, max_risk, atr):
    atr_val = atr or price * 0.03
    sell_strike = _round_strike(price + atr_val)
    wing = _strike_step(price)
    buy_strike = _round_strike(sell_strike + wing)
    spread_width = buy_strike - sell_strike
    # NOTE: credit is estimated, not from live quotes
    est_credit = spread_width * 0.35
    max_loss = (spread_width - est_credit) * 100
    contracts = max(1, int(max_risk / max_loss))

    return {
        "name_en": "Bear Call Spread",
        "name_cn": "Bear Call Spread (看跌卖出看涨价差)",
        "direction": "bearish",
        "legs": [
            {"action": "SELL", "type": "CALL", "strike": sell_strike},
            {"action": "BUY", "type": "CALL", "strike": buy_strike},
        ],
        "dte_range": f"{max(dte - 10, 20)}-{dte + 15} days",
        "max_profit": f"${est_credit * 100 * contracts:.0f} (credit received)",
        "max_loss": f"${max_loss * contracts:.0f}",
        "win_rate_est": "65-70%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of max profit",
            "Stop loss: Close if loss reaches 200% of credit",
            "Time exit: Close at 21 DTE",
        ],
        "position_size": f"{contracts} contract(s), risking ${max_loss * contracts:.0f}",
    }


def _bear_put_spread(price, dte, max_risk, atr):
    buy_strike = _round_strike(price)  # ATM
    sell_strike = _round_strike(price - (atr or price * 0.03) * 2)
    spread_width = buy_strike - sell_strike
    # NOTE: debit is estimated, not from live quotes
    est_debit = spread_width * 0.55
    max_loss = est_debit * 100
    contracts = max(1, int(max_risk / max_loss))

    return {
        "name_en": "Bear Put Spread",
        "name_cn": "Bear Put Spread (看跌买入看跌价差)",
        "direction": "bearish",
        "legs": [
            {"action": "BUY", "type": "PUT", "strike": buy_strike},
            {"action": "SELL", "type": "PUT", "strike": sell_strike},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 30} days",
        "max_profit": f"${(spread_width - est_debit) * 100 * contracts:.0f}",
        "max_loss": f"${max_loss * contracts:.0f} (debit paid)",
        "win_rate_est": "45-55%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of max profit",
            "Stop loss: Close if debit drops 50%",
            "Time exit: Close at 14 DTE",
        ],
        "position_size": f"{contracts} contract(s), cost ~${max_loss * contracts:.0f}",
    }


def _long_put(price, dte, max_risk, atr):
    strike = _round_strike(price * 0.98)  # slightly OTM
    est_premium = price * 0.035
    contracts = max(1, int(max_risk / (est_premium * 100)))

    return {
        "name_en": "Long Put",
        "name_cn": "Long Put (买入看跌期权)",
        "direction": "bearish",
        "legs": [
            {"action": "BUY", "type": "PUT", "strike": strike},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 30} days",
        "max_profit": f"${(strike - est_premium) * 100 * contracts:,.0f} (if stock goes to $0)",
        "max_loss": f"~${est_premium * 100 * contracts:.0f} (premium paid)",
        "win_rate_est": "35-45%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50-100% gain on premium",
            "Stop loss: Close if premium drops 50%",
            "Time exit: Close at 14 DTE",
        ],
        "position_size": f"{contracts} contract(s), cost ~${est_premium * 100 * contracts:.0f}",
    }


def _iron_condor(price, dte, max_risk, atr):
    atr_val = atr or price * 0.03
    wing = _strike_step(price)
    # Call side
    sell_call = _round_strike(price + atr_val * 1.5)
    buy_call = _round_strike(sell_call + wing)
    # Put side
    sell_put = _round_strike(price - atr_val * 1.5)
    buy_put = _round_strike(sell_put - wing)
    wing_width = wing
    # NOTE: credit is estimated, not from live quotes
    est_credit = wing_width * 0.30  # total credit from both sides
    max_loss = (wing_width - est_credit) * 100
    contracts = max(1, int(max_risk / max_loss))

    return {
        "name_en": "Iron Condor",
        "name_cn": "Iron Condor (铁鹰价差)",
        "direction": "neutral",
        "legs": [
            {"action": "SELL", "type": "CALL", "strike": sell_call},
            {"action": "BUY", "type": "CALL", "strike": buy_call},
            {"action": "SELL", "type": "PUT", "strike": sell_put},
            {"action": "BUY", "type": "PUT", "strike": buy_put},
        ],
        "dte_range": f"{max(dte - 5, 25)}-{dte + 15} days",
        "max_profit": f"${est_credit * 100 * contracts:.0f} (total credit)",
        "max_loss": f"${max_loss * contracts:.0f} (one side breached)",
        "win_rate_est": "60-70%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 50% of max profit",
            "Stop loss: Close if loss = 2x credit received",
            "Adjust: Roll tested side if price approaches short strike",
            "Time exit: Close at 21 DTE",
        ],
        "position_size": f"{contracts} contract(s), risking ${max_loss * contracts:.0f}",
    }


def _short_strangle(price, dte, max_risk, atr):
    atr_val = atr or price * 0.03
    sell_call = _round_strike(price + atr_val * 2)
    sell_put = _round_strike(price - atr_val * 2)
    est_credit = price * 0.03

    return {
        "name_en": "Short Strangle",
        "name_cn": "Short Strangle (卖出宽跨式)",
        "direction": "neutral",
        "legs": [
            {"action": "SELL", "type": "CALL", "strike": sell_call},
            {"action": "SELL", "type": "PUT", "strike": sell_put},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 15} days",
        "max_profit": f"~${est_credit * 100:.0f}/contract (credit received)",
        "max_loss": "Unlimited (naked position, requires margin)",
        "win_rate_est": "70-80%",
        "contracts": "Size based on margin requirements",
        "exit_rules": [
            "Take profit: Close at 50% of credit",
            "Stop loss: Close if loss = 2x credit received",
            "Adjustment: Roll tested side out in time",
        ],
        "position_size": "Requires significant margin, use caution",
    }


def _long_straddle(price, dte, max_risk, atr):
    strike = _round_strike(price)
    est_debit = price * 0.06  # call + put premium
    contracts = max(1, int(max_risk / (est_debit * 100)))

    return {
        "name_en": "Long Straddle",
        "name_cn": "Long Straddle (买入跨式)",
        "direction": "neutral (expecting big move)",
        "legs": [
            {"action": "BUY", "type": "CALL", "strike": strike},
            {"action": "BUY", "type": "PUT", "strike": strike},
        ],
        "dte_range": f"{max(dte, 30)}-{dte + 30} days",
        "max_profit": "Unlimited (if stock moves significantly)",
        "max_loss": f"~${est_debit * 100 * contracts:.0f} (total premium paid)",
        "win_rate_est": "30-40% (needs big move to profit)",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 25-50% gain (take profits early)",
            "Stop loss: Close if total premium drops 40%",
            "Time exit: Close at 21 DTE, theta accelerates",
        ],
        "position_size": f"{contracts} contract(s), cost ~${est_debit * 100 * contracts:.0f}",
    }


def _calendar_spread(price, dte, max_risk, atr):
    strike = _round_strike(price)
    est_debit = price * 0.015
    contracts = max(1, int(max_risk / (est_debit * 100)))

    return {
        "name_en": "Calendar Spread",
        "name_cn": "Calendar Spread (日历价差)",
        "direction": "neutral (betting on IV increase)",
        "legs": [
            {"action": "SELL", "type": "CALL", "strike": strike, "note": f"~{dte} DTE"},
            {"action": "BUY", "type": "CALL", "strike": strike, "note": f"~{dte + 30} DTE"},
        ],
        "dte_range": f"Front: {dte} DTE, Back: {dte + 30} DTE",
        "max_profit": "Variable (max when stock at strike at front expiry)",
        "max_loss": f"~${est_debit * 100 * contracts:.0f} (net debit)",
        "win_rate_est": "45-55%",
        "contracts": contracts,
        "exit_rules": [
            "Take profit: Close at 25-50% gain",
            "Stop loss: Close if debit drops 40%",
            "Close before front month expiration",
        ],
        "position_size": f"{contracts} contract(s), cost ~${est_debit * 100 * contracts:.0f}",
    }


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("[bold]Strategy Test: TSLA Bullish + High IV[/bold]\n")

    results = recommend_strategies(
        ticker="TSLA",
        current_price=417.0,
        trend="bullish",
        iv_percentile=75,
        days_to_expiry=30,
        risk_level="moderate",
        account_size=10000,
        atr=16.0,
    )

    for i, s in enumerate(results, 1):
        console.print(f"\n[bold cyan]Strategy {i}: {s['name_en']}[/bold cyan]")
        console.print(f"  {s['name_cn']}")
        console.print(f"  Direction: {s['direction']}")

        table = Table()
        table.add_column("Leg", style="white")
        for leg in s["legs"]:
            note = f" ({leg['note']})" if "note" in leg else ""
            table.add_row(f"{leg['action']} {leg['type']} ${leg['strike']:.0f}{note}")
        console.print(table)

        console.print(f"  DTE: {s['dte_range']}")
        console.print(f"  Max Profit: {s['max_profit']}")
        console.print(f"  Max Loss: {s['max_loss']}")
        console.print(f"  Win Rate Est: {s['win_rate_est']}")
        console.print(f"  Position: {s['position_size']}")
        console.print("  Exit Rules:")
        for rule in s["exit_rules"]:
            console.print(f"    - {rule}")
