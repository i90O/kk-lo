"use client";

import { useAppStore } from "@/lib/store";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

function CircularGauge({ value, label }: { value: number | null; label: string }) {
  const pct = value !== null ? Math.min(100, Math.max(0, value)) : 0;
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;
  const color = value === null ? "var(--text-muted)" : value > 75 ? "var(--bearish)" : value < 25 ? "var(--bullish)" : "var(--neutral)";

  return (
    <div className="flex flex-col items-center">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="var(--bg-tertiary)" strokeWidth="6" />
        <circle
          cx="50" cy="50" r={radius}
          fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          className="transition-all duration-500"
        />
        <text x="50" y="46" textAnchor="middle" className="text-lg font-mono font-bold" fill={color}>
          {value !== null ? value.toFixed(0) : "N/A"}
        </text>
        <text x="50" y="62" textAnchor="middle" className="text-[10px]" fill="var(--text-muted)">
          {label}
        </text>
      </svg>
    </div>
  );
}

export default function IVPanel() {
  const data = useAppStore((s) => s.ivData);
  const loading = useAppStore((s) => s.loading.iv);

  if (loading && !data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Implied Volatility</div>
        <div className="flex items-center justify-center py-8"><LoadingSpinner /></div>
      </div>
    );
  }
  if (!data) return null;

  const ivEnv = data.iv_percentile !== null
    ? data.iv_percentile > 75 ? "HIGH IV - Sell Premium" : data.iv_percentile < 25 ? "LOW IV - Buy Premium" : "MODERATE IV"
    : "Insufficient Data";
  const envColor = data.iv_percentile !== null
    ? data.iv_percentile > 75 ? "text-[var(--bearish)] bg-[var(--bearish-bg)]" : data.iv_percentile < 25 ? "text-[var(--bullish)] bg-[var(--bullish-bg)]" : "text-[var(--neutral)] bg-[var(--neutral-bg)]"
    : "text-[var(--text-muted)] bg-[var(--bg-tertiary)]";

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Implied Volatility</div>

      {/* Current IV */}
      <div className="text-center mb-3">
        <div className="text-3xl font-mono font-bold text-[var(--text-primary)]">
          {data.current_iv !== null ? data.current_iv.toFixed(1) + "%" : "N/A"}
        </div>
        <div className="text-[10px] text-[var(--text-muted)] mt-1">Current ATM IV</div>
      </div>

      {/* Gauges */}
      <div className="flex justify-center gap-4 mb-3">
        <CircularGauge value={data.iv_percentile} label="Percentile" />
        <CircularGauge value={data.iv_rank} label="Rank" />
      </div>

      {/* IV vs HV */}
      {data.hv20 && (
        <div className="flex items-center gap-2 mb-3">
          <div className="flex-1">
            <div className="text-[10px] text-[var(--text-muted)] mb-1">IV</div>
            <div className="h-2 bg-[var(--accent)]/30 rounded-full" style={{ width: `${Math.min(100, (data.current_iv || 0))}%` }} />
          </div>
          <div className="flex-1">
            <div className="text-[10px] text-[var(--text-muted)] mb-1">HV20</div>
            <div className="h-2 bg-[var(--neutral)]/30 rounded-full" style={{ width: `${Math.min(100, (data.hv20 || 0))}%` }} />
          </div>
        </div>
      )}

      {/* Environment badge */}
      <div className={`text-center text-sm font-semibold py-2 rounded-lg ${envColor}`}>
        {ivEnv}
      </div>

      {/* Data info */}
      <div className="text-[10px] text-[var(--text-muted)] text-center mt-3">
        {data.data_points} data points
        {data.message && <div className="mt-1">{data.message}</div>}
      </div>
    </div>
  );
}
