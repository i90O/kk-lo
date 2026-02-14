"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatPercent, formatCompact } from "@/lib/format";
import SignalBadge from "@/components/shared/SignalBadge";
import StrengthMeter from "@/components/shared/StrengthMeter";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

const WATCHLIST = [
  "SPY", "QQQ", "TSLA", "AAPL", "NVDA", "META",
  "AMZN", "AMD", "MSFT", "GOOGL", "NFLX", "COIN",
];

export default function StockHeader() {
  const data = useAppStore((s) => s.technicalData);
  const loading = useAppStore((s) => s.loading.technical);
  const selectTicker = useAppStore((s) => s.selectTicker);
  const selectedTicker = useAppStore((s) => s.selectedTicker);

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
      {/* Quick ticker selector */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {WATCHLIST.map((t) => (
          <button
            key={t}
            onClick={() => selectTicker(t)}
            className={`px-2 py-0.5 rounded text-[11px] font-mono transition ${
              selectedTicker === t
                ? "bg-green-600/20 text-green-400 border border-green-600"
                : "bg-gray-800/50 text-gray-500 hover:text-gray-300 border border-transparent"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading && !data ? (
        <div className="flex items-center gap-2 py-4">
          <LoadingSpinner size="sm" />
          <span className="text-gray-500 text-sm">Loading {selectedTicker}...</span>
        </div>
      ) : data ? (
        <div className="flex items-center gap-6">
          <div>
            <div className="text-2xl font-bold text-white">{data.ticker}</div>
            <div className="text-[11px] text-gray-500">{data.trend.toUpperCase()} trend</div>
          </div>
          <div>
            <div className="text-2xl font-mono font-semibold text-white">
              {formatCurrency(data.current_price)}
            </div>
            <div className={`text-sm font-mono ${data.change_pct >= 0 ? "text-green-400" : "text-red-400"}`}>
              {data.change >= 0 ? "+" : ""}{formatCurrency(data.change)} ({formatPercent(data.change_pct)})
            </div>
          </div>
          <div className="flex items-center gap-3">
            <SignalBadge signal={data.signal} />
            <StrengthMeter strength={data.strength} signal={data.signal} />
          </div>
          <div className="ml-auto text-right text-xs text-gray-500">
            <div>Vol: {formatCompact(data.volume)} ({data.volume_ratio.toFixed(2)}x avg)</div>
            <div>ATR: {data.atr ? formatCurrency(data.atr) : "N/A"} ({data.atr_pct ? formatPercent(data.atr_pct, 1) : "N/A"})</div>
          </div>
        </div>
      ) : (
        <div className="text-gray-500 text-sm py-4">Select a ticker to analyze</div>
      )}
    </div>
  );
}
