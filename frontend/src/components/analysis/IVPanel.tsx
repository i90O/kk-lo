"use client";

import { useAppStore } from "@/lib/store";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

function ProgressBar({ value, label }: { value: number | null; label: string }) {
  const pct = value !== null ? Math.min(100, Math.max(0, value)) : 0;
  const color = value === null
    ? "bg-gray-700"
    : value < 25
      ? "bg-green-500"
      : value < 75
        ? "bg-yellow-500"
        : "bg-red-500";
  const textColor = value === null
    ? "text-gray-600"
    : value < 25
      ? "text-green-400"
      : value < 75
        ? "text-yellow-400"
        : "text-red-400";

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-500">{label}</span>
        <span className={`text-sm font-mono font-semibold ${textColor}`}>
          {value !== null ? value.toFixed(1) + "%" : "N/A"}
        </span>
      </div>
      <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <div className="flex justify-between text-[9px] text-gray-600 mt-0.5">
        <span>0 (Cheap)</span><span>50</span><span>100 (Expensive)</span>
      </div>
    </div>
  );
}

export default function IVPanel() {
  const data = useAppStore((s) => s.ivData);
  const loading = useAppStore((s) => s.loading.iv);

  if (loading && !data) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm font-semibold text-gray-400 mb-3">Implied Volatility</div>
        <div className="flex items-center justify-center py-8"><LoadingSpinner /></div>
      </div>
    );
  }
  if (!data) return null;

  const ivEnv = data.iv_percentile !== null
    ? data.iv_percentile > 75 ? "HIGH IV - Sell Premium" : data.iv_percentile < 25 ? "LOW IV - Buy Premium" : "MODERATE IV"
    : "Insufficient Data";
  const envColor = data.iv_percentile !== null
    ? data.iv_percentile > 75 ? "text-red-400" : data.iv_percentile < 25 ? "text-green-400" : "text-yellow-400"
    : "text-gray-500";

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
      <div className="text-sm font-semibold text-gray-400 mb-4">Implied Volatility</div>

      {/* Current IV */}
      <div className="text-center mb-4">
        <div className="text-3xl font-mono font-bold text-white">
          {data.current_iv !== null ? data.current_iv.toFixed(1) + "%" : "N/A"}
        </div>
        <div className="text-xs text-gray-500 mt-1">Current ATM IV</div>
      </div>

      <ProgressBar value={data.iv_percentile} label="IV Percentile" />
      <ProgressBar value={data.iv_rank} label="IV Rank" />

      {/* Environment */}
      <div className={`text-center text-sm font-semibold ${envColor} mt-2 py-2 rounded bg-gray-800/50`}>
        {ivEnv}
      </div>

      {/* Data info */}
      <div className="text-[10px] text-gray-600 text-center mt-3">
        {data.data_points} data points collected
        {data.message && <div className="mt-1">{data.message}</div>}
      </div>
    </div>
  );
}
