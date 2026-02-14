"""Technical analysis engine using ta library."""

import pandas as pd
import numpy as np
import ta
from tools.market_data import get_stock_data, get_current_price


def full_technical_analysis(ticker: str, period: str = "6mo") -> dict:
    """
    Run full technical analysis on a ticker.
    Returns dict with all indicators and a composite signal summary.
    """
    df = get_stock_data(ticker, period=period)
    if df.empty:
        return {"error": f"No data for {ticker}"}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    current = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) > 1 else current

    # Price change
    change = current - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0

    # --- Moving Averages ---
    sma20 = ta.trend.sma_indicator(close, window=20)
    sma50 = ta.trend.sma_indicator(close, window=50)
    sma200 = ta.trend.sma_indicator(close, window=200)
    sma20_val = float(sma20.iloc[-1]) if pd.notna(sma20.iloc[-1]) else None
    sma50_val = float(sma50.iloc[-1]) if pd.notna(sma50.iloc[-1]) else None
    sma200_val = float(sma200.iloc[-1]) if pd.notna(sma200.iloc[-1]) else None

    # Trend determination
    trend = _determine_trend(current, sma20_val, sma50_val, sma200_val)

    # --- RSI ---
    rsi_series = ta.momentum.rsi(close, window=14)
    rsi = float(rsi_series.iloc[-1]) if pd.notna(rsi_series.iloc[-1]) else None
    rsi_signal = "neutral"
    if rsi is not None:
        if rsi > 70:
            rsi_signal = "overbought"
        elif rsi < 30:
            rsi_signal = "oversold"

    # --- MACD ---
    macd_ind = ta.trend.MACD(close)
    macd_val = float(macd_ind.macd().iloc[-1]) if pd.notna(macd_ind.macd().iloc[-1]) else None
    macd_signal_val = float(macd_ind.macd_signal().iloc[-1]) if pd.notna(macd_ind.macd_signal().iloc[-1]) else None
    macd_hist = float(macd_ind.macd_diff().iloc[-1]) if pd.notna(macd_ind.macd_diff().iloc[-1]) else None

    macd_cross = "neutral"
    if macd_val is not None and macd_signal_val is not None:
        prev_macd = float(macd_ind.macd().iloc[-2]) if pd.notna(macd_ind.macd().iloc[-2]) else None
        prev_signal = float(macd_ind.macd_signal().iloc[-2]) if pd.notna(macd_ind.macd_signal().iloc[-2]) else None
        if prev_macd is not None and prev_signal is not None:
            if prev_macd <= prev_signal and macd_val > macd_signal_val:
                macd_cross = "bullish_crossover"
            elif prev_macd >= prev_signal and macd_val < macd_signal_val:
                macd_cross = "bearish_crossover"

    # --- Bollinger Bands ---
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    bb_upper = float(bb.bollinger_hband().iloc[-1]) if pd.notna(bb.bollinger_hband().iloc[-1]) else None
    bb_middle = float(bb.bollinger_mavg().iloc[-1]) if pd.notna(bb.bollinger_mavg().iloc[-1]) else None
    bb_lower = float(bb.bollinger_lband().iloc[-1]) if pd.notna(bb.bollinger_lband().iloc[-1]) else None
    bb_position = _bb_position(current, bb_upper, bb_middle, bb_lower)

    # --- Stochastic ---
    stoch = ta.momentum.StochasticOscillator(high, low, close, window=14, smooth_window=3)
    stoch_k = float(stoch.stoch().iloc[-1]) if pd.notna(stoch.stoch().iloc[-1]) else None
    stoch_d = float(stoch.stoch_signal().iloc[-1]) if pd.notna(stoch.stoch_signal().iloc[-1]) else None

    # --- ATR ---
    atr_series = ta.volatility.average_true_range(high, low, close, window=14)
    atr = float(atr_series.iloc[-1]) if pd.notna(atr_series.iloc[-1]) else None
    atr_pct = (atr / current * 100) if atr and current else None

    # --- Volume analysis ---
    vol_current = int(volume.iloc[-1])
    vol_sma20 = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else float(volume.mean())
    vol_ratio = vol_current / vol_sma20 if vol_sma20 > 0 else 1.0

    # --- Support / Resistance (20-day) ---
    recent = df.tail(20)
    support = float(recent["Low"].min())
    resistance = float(recent["High"].max())

    # --- Composite signal ---
    signal, strength = _composite_signal(
        trend, rsi, rsi_signal, macd_cross, macd_hist, bb_position,
        stoch_k, stoch_d, vol_ratio
    )

    return {
        "ticker": ticker,
        "current_price": current,
        "change": change,
        "change_pct": change_pct,
        # Trend
        "sma20": sma20_val,
        "sma50": sma50_val,
        "sma200": sma200_val,
        "trend": trend,
        # RSI
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        # MACD
        "macd": macd_val,
        "macd_signal": macd_signal_val,
        "macd_histogram": macd_hist,
        "macd_cross": macd_cross,
        # Bollinger Bands
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "bb_position": bb_position,
        # Stochastic
        "stoch_k": stoch_k,
        "stoch_d": stoch_d,
        # ATR
        "atr": atr,
        "atr_pct": atr_pct,
        # Volume
        "volume": vol_current,
        "volume_sma20": vol_sma20,
        "volume_ratio": vol_ratio,
        # Support / Resistance
        "support_20d": support,
        "resistance_20d": resistance,
        # Composite
        "signal": signal,
        "strength": strength,
    }


def _determine_trend(price, sma20, sma50, sma200):
    """Determine trend based on SMA alignment."""
    if sma20 is None or sma50 is None:
        return "unknown"

    bullish_count = 0
    bearish_count = 0

    if price > sma20:
        bullish_count += 1
    else:
        bearish_count += 1

    if sma20 > sma50:
        bullish_count += 1
    else:
        bearish_count += 1

    if sma200 is not None:
        if price > sma200:
            bullish_count += 1
        else:
            bearish_count += 1
        if sma50 > sma200:
            bullish_count += 1
        else:
            bearish_count += 1

    if bullish_count >= 3:
        return "bullish"
    elif bearish_count >= 3:
        return "bearish"
    return "neutral"


def _bb_position(price, upper, middle, lower):
    """Describe price position relative to Bollinger Bands."""
    if upper is None or lower is None:
        return "unknown"
    band_width = upper - lower
    if band_width == 0:
        return "unknown"
    position = (price - lower) / band_width
    if position > 0.9:
        return "near_upper"
    elif position < 0.1:
        return "near_lower"
    elif 0.4 < position < 0.6:
        return "near_middle"
    elif position >= 0.6:
        return "upper_half"
    else:
        return "lower_half"


def _composite_signal(trend, rsi, rsi_signal, macd_cross, macd_hist, bb_pos, stoch_k, stoch_d, vol_ratio):
    """Calculate composite signal and strength (1-5)."""
    score = 0  # positive = bullish, negative = bearish

    # Trend weight: 2
    if trend == "bullish":
        score += 2
    elif trend == "bearish":
        score -= 2

    # RSI weight: 1
    if rsi_signal == "oversold":
        score += 1  # potential bounce
    elif rsi_signal == "overbought":
        score -= 1

    # MACD weight: 1.5
    if macd_cross == "bullish_crossover":
        score += 1.5
    elif macd_cross == "bearish_crossover":
        score -= 1.5
    elif macd_hist is not None:
        if macd_hist > 0:
            score += 0.5
        else:
            score -= 0.5

    # BB position weight: 1
    if bb_pos == "near_lower":
        score += 1
    elif bb_pos == "near_upper":
        score -= 1

    # Stochastic weight: 1
    if stoch_k is not None:
        if stoch_k < 20:
            score += 1
        elif stoch_k > 80:
            score -= 1

    # Volume confirmation: 0.5
    if vol_ratio > 1.5:
        if score > 0:
            score += 0.5
        elif score < 0:
            score -= 0.5

    # Convert to signal and strength
    if score > 1:
        signal = "bullish"
    elif score < -1:
        signal = "bearish"
    else:
        signal = "neutral"

    # Strength 1-5
    abs_score = abs(score)
    if abs_score >= 5:
        strength = 5
    elif abs_score >= 3.5:
        strength = 4
    elif abs_score >= 2:
        strength = 3
    elif abs_score >= 1:
        strength = 2
    else:
        strength = 1

    return signal, strength


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("[bold]Technical Analysis: TSLA[/bold]\n")

    result = full_technical_analysis("TSLA")
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
    else:
        table = Table(title=f"TSLA Technical Analysis")
        table.add_column("Indicator", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Signal", style="bold")

        table.add_row("Price", f"${result['current_price']:.2f}", f"{result['change_pct']:+.2f}%")
        table.add_row("SMA 20", f"${result['sma20']:.2f}" if result['sma20'] else "N/A", "")
        table.add_row("SMA 50", f"${result['sma50']:.2f}" if result['sma50'] else "N/A", "")
        table.add_row("SMA 200", f"${result['sma200']:.2f}" if result['sma200'] else "N/A", "")
        trend_icon = "[green]+[/green]" if result['trend'] == 'bullish' else "[red]-[/red]" if result['trend'] == 'bearish' else "~"
        table.add_row("Trend", result['trend'], trend_icon)
        table.add_row("RSI(14)", f"{result['rsi']:.1f}" if result['rsi'] else "N/A", result['rsi_signal'])
        table.add_row("MACD", f"{result['macd']:.3f}" if result['macd'] else "N/A", result['macd_cross'])
        table.add_row("MACD Hist", f"{result['macd_histogram']:.3f}" if result['macd_histogram'] else "N/A", "")
        table.add_row("BB Position", result['bb_position'], "")
        table.add_row("BB Upper", f"${result['bb_upper']:.2f}" if result['bb_upper'] else "N/A", "")
        table.add_row("BB Lower", f"${result['bb_lower']:.2f}" if result['bb_lower'] else "N/A", "")
        table.add_row("Stoch K/D", f"{result['stoch_k']:.1f}/{result['stoch_d']:.1f}" if result['stoch_k'] else "N/A", "")
        table.add_row("ATR(14)", f"${result['atr']:.2f} ({result['atr_pct']:.1f}%)" if result['atr'] else "N/A", "")
        table.add_row("Volume", f"{result['volume']:,}", f"{result['volume_ratio']:.2f}x avg")
        table.add_row("Support (20d)", f"${result['support_20d']:.2f}", "")
        table.add_row("Resistance (20d)", f"${result['resistance_20d']:.2f}", "")
        table.add_row("", "", "")

        signal_color = "green" if result['signal'] == 'bullish' else "red" if result['signal'] == 'bearish' else "yellow"
        stars = "*" * result['strength'] + "." * (5 - result['strength'])
        table.add_row("[bold]SIGNAL[/bold]", f"[{signal_color}]{result['signal'].upper()}[/{signal_color}]", stars)

        console.print(table)
