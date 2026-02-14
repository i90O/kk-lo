"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatPercent, formatCompact } from "@/lib/format";
import SignalBadge from "@/components/shared/SignalBadge";
import StrengthMeter from "@/components/shared/StrengthMeter";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function StockHeader() {
  const data = useAppStore((s) => s.technicalData);
  const loading = useAppStore((s) => s.loading.technical);
  const selectedTicker = useAppStore((s) => s.selectedTicker);

  if (loading && !data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="flex items-center gap-2">
          <LoadingSpinner size="sm" />
          <span className="text-[var(--text-muted)] text-sm">Loading {selectedTicker}...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-[var(--text-muted)] text-sm">Select a ticker to analyze</div>
      </div>
    );
  }

  const TrendIcon = data.trend === "bullish" ? TrendingUp : data.trend === "bearish" ? TrendingDown : Minus;
  const trendColor = data.trend === "bullish" ? "text-[var(--bullish)]" : data.trend === "bearish" ? "text-[var(--bearish)]" : "text-[var(--neutral)]";

  // 52-week range bar (approximate using support/resistance)
  const rangeMin = data.support_20d;
  const rangeMax = data.resistance_20d;
  const rangeSpan = rangeMax - rangeMin;
  const pricePos = rangeSpan > 0 ? ((data.current_price - rangeMin) / rangeSpan) * 100 : 50;
  const clampedPos = Math.max(2, Math.min(98, pricePos));

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg px-5 py-3">
      <div className="flex flex-wrap items-center gap-6">
        {/* Ticker + Trend */}
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold text-[var(--text-primary)]">{data.ticker}</div>
          <TrendIcon size={18} className={trendColor} />
        </div>

        {/* Price + Change */}
        <div>
          <div className="text-2xl font-mono font-semibold text-[var(--text-primary)]">
            {formatCurrency(data.current_price)}
          </div>
          <div className={`text-sm font-mono ${data.change_pct >= 0 ? "text-[var(--bullish)]" : "text-[var(--bearish)]"}`}>
            {data.change >= 0 ? "+" : ""}{formatCurrency(data.change)} ({formatPercent(data.change_pct)})
          </div>
        </div>

        {/* Signal + Strength */}
        <div className="flex items-center gap-3">
          <SignalBadge signal={data.signal} />
          <StrengthMeter strength={data.strength} signal={data.signal} />
        </div>

        {/* 20d Range Bar */}
        <div className="ml-auto min-w-[200px]">
          <div className="flex items-center justify-between text-[10px] text-[var(--text-muted)] mb-1">
            <span>${rangeMin.toFixed(0)}</span>
            <span className="text-[var(--text-secondary)]">20d Range</span>
            <span>${rangeMax.toFixed(0)}</span>
          </div>
          <div className="relative h-1.5 bg-[var(--bg-tertiary)] rounded-full">
            <div
              className="absolute top-0 h-1.5 w-2 bg-[var(--accent)] rounded-full"
              style={{ left: `${clampedPos}%`, transform: "translateX(-50%)" }}
            />
          </div>
        </div>

        {/* Volume + ATR compact */}
        <div className="text-right text-xs text-[var(--text-muted)]">
          <div>Vol: {formatCompact(data.volume)} ({data.volume_ratio.toFixed(1)}x)</div>
          <div>ATR: {data.atr ? formatCurrency(data.atr) : "N/A"}</div>
        </div>
      </div>
    </div>
  );
}
