"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatNumber } from "@/lib/format";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

function IndicatorCard({ label, value, sub, color }: {
  label: string;
  value: string;
  sub?: string;
  color?: string;
}) {
  return (
    <div className="bg-[var(--bg-primary)] rounded-lg p-3 h-[120px] flex flex-col justify-between">
      <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">{label}</div>
      <div className={`text-lg font-mono font-semibold ${color || "text-[var(--text-primary)]"}`}>{value}</div>
      {sub && <div className="text-[10px] text-[var(--text-muted)]">{sub}</div>}
    </div>
  );
}

export default function TechnicalPanel() {
  const data = useAppStore((s) => s.technicalData);
  const loading = useAppStore((s) => s.loading.technical);

  if (loading && !data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Technical</div>
        <div className="flex items-center justify-center py-8"><LoadingSpinner /></div>
      </div>
    );
  }
  if (!data) return null;

  const rsiColor = data.rsi !== null
    ? data.rsi > 70 ? "text-[var(--bearish)]" : data.rsi < 30 ? "text-[var(--bullish)]" : "text-[var(--neutral)]"
    : "text-[var(--text-muted)]";

  const rsiZone = data.rsi !== null
    ? data.rsi > 70 ? "Overbought" : data.rsi < 30 ? "Oversold" : "Neutral"
    : "";

  const macdColor = data.macd_histogram !== null
    ? data.macd_histogram > 0 ? "text-[var(--bullish)]" : "text-[var(--bearish)]"
    : "text-[var(--text-muted)]";

  const stochColor = data.stoch_k !== null
    ? data.stoch_k > 80 ? "text-[var(--bearish)]" : data.stoch_k < 20 ? "text-[var(--bullish)]" : "text-[var(--text-secondary)]"
    : "text-[var(--text-muted)]";

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Technical</div>
      <div className="grid grid-cols-2 gap-2">
        <IndicatorCard
          label="RSI (14)"
          value={data.rsi !== null ? data.rsi.toFixed(1) : "N/A"}
          sub={rsiZone}
          color={rsiColor}
        />
        <IndicatorCard
          label="MACD"
          value={data.macd !== null ? data.macd.toFixed(3) : "N/A"}
          sub={data.macd_cross?.replace(/_/g, " ")}
          color={macdColor}
        />
        <IndicatorCard
          label="Stochastic %K/%D"
          value={`${formatNumber(data.stoch_k, 1)} / ${formatNumber(data.stoch_d, 1)}`}
          color={stochColor}
        />
        <IndicatorCard
          label="Bollinger"
          value={data.bb_position?.replace(/_/g, " ") || "N/A"}
          sub={`${formatCurrency(data.bb_lower)} - ${formatCurrency(data.bb_upper)}`}
        />
        <IndicatorCard
          label="Volume Ratio"
          value={data.volume_ratio.toFixed(2) + "x"}
          sub="vs 20d avg"
          color={data.volume_ratio > 1.5 ? "text-[var(--bullish)]" : "text-[var(--text-secondary)]"}
        />
        <IndicatorCard
          label="ATR"
          value={data.atr ? formatCurrency(data.atr) : "N/A"}
          sub={data.atr_pct ? data.atr_pct.toFixed(1) + "% of price" : ""}
        />
      </div>
    </div>
  );
}
