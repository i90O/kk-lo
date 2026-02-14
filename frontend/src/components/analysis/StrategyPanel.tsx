"use client";

import { useAppStore } from "@/lib/store";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import StrategyCard from "./StrategyCard";
import { RefreshCw } from "lucide-react";

export default function StrategyPanel() {
  const data = useAppStore((s) => s.strategyData);
  const loading = useAppStore((s) => s.loading.strategy);
  const ticker = useAppStore((s) => s.selectedTicker);
  const fetchStrategy = useAppStore((s) => s.fetchStrategy);

  if (loading && !data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Strategy</div>
        <div className="flex items-center justify-center py-8"><LoadingSpinner /></div>
      </div>
    );
  }

  if (!data || !data.strategies || data.strategies.length === 0) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-[var(--text-secondary)]">Strategy</div>
          <button
            onClick={() => fetchStrategy(ticker)}
            className="px-3 py-1.5 text-xs bg-[var(--accent)] text-white rounded hover:bg-[var(--accent-hover)] transition"
          >
            Get Recommendations
          </button>
        </div>
      </div>
    );
  }

  const trendColors: Record<string, string> = {
    bullish: "text-[var(--bullish)]",
    bearish: "text-[var(--bearish)]",
    neutral: "text-[var(--neutral)]",
  };

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-medium text-[var(--text-secondary)]">Strategy</div>
          <div className="flex items-center gap-3 mt-0.5">
            <span className={`text-xs font-mono ${trendColors[data.trend] || "text-[var(--text-muted)]"}`}>
              {data.trend?.toUpperCase()}
            </span>
            {data.iv_percentile !== null && (
              <span className="text-[10px] text-[var(--text-muted)]">
                IV: {data.iv_percentile?.toFixed(0)}%
              </span>
            )}
          </div>
        </div>
        <button
          onClick={() => fetchStrategy(ticker)}
          disabled={loading}
          className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="space-y-2">
        {data.strategies.map((s, i) => (
          <StrategyCard key={i} strategy={s} rank={i + 1} />
        ))}
      </div>
    </div>
  );
}
