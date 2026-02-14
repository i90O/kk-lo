"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatNumber } from "@/lib/format";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

function RSIBar({ value }: { value: number | null }) {
  if (value === null) return <span className="text-gray-600">N/A</span>;
  const pct = Math.min(100, Math.max(0, value));
  const color = value > 70 ? "bg-red-500" : value < 30 ? "bg-green-500" : "bg-yellow-500";
  const textColor = value > 70 ? "text-red-400" : value < 30 ? "text-green-400" : "text-yellow-400";

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-500">RSI(14)</span>
        <span className={`text-sm font-mono font-semibold ${textColor}`}>{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full relative">
        {/* Color zones */}
        <div className="absolute inset-0 flex rounded-full overflow-hidden">
          <div className="w-[30%] bg-green-900/30" />
          <div className="w-[40%] bg-gray-800" />
          <div className="w-[30%] bg-red-900/30" />
        </div>
        {/* Needle */}
        <div
          className={`absolute top-0 h-2 w-1 ${color} rounded-full`}
          style={{ left: `${pct}%`, transform: "translateX(-50%)" }}
        />
      </div>
      <div className="flex justify-between text-[9px] text-gray-600 mt-0.5">
        <span>0</span><span>30</span><span>50</span><span>70</span><span>100</span>
      </div>
    </div>
  );
}

function Row({ label, value, signal }: { label: string; value: string; signal?: string }) {
  const sigColor = signal === "bullish" || signal === "bullish_crossover"
    ? "text-green-400"
    : signal === "bearish" || signal === "bearish_crossover"
      ? "text-red-400"
      : "";
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-800/50">
      <span className="text-xs text-gray-500">{label}</span>
      <span className={`text-xs font-mono ${sigColor || "text-gray-300"}`}>{value}</span>
    </div>
  );
}

export default function TechnicalPanel() {
  const data = useAppStore((s) => s.technicalData);
  const loading = useAppStore((s) => s.loading.technical);

  if (loading && !data) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm font-semibold text-gray-400 mb-3">Technical Analysis</div>
        <div className="flex items-center justify-center py-8"><LoadingSpinner /></div>
      </div>
    );
  }
  if (!data) return null;

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
      <div className="text-sm font-semibold text-gray-400 mb-4">Technical Analysis</div>

      <RSIBar value={data.rsi} />

      <div className="mt-4 space-y-0">
        <Row label="MACD" value={data.macd !== null ? data.macd.toFixed(3) : "N/A"} signal={data.macd_cross} />
        <Row label="MACD Signal" value={data.macd_signal !== null ? data.macd_signal.toFixed(3) : "N/A"} />
        <Row
          label="MACD Histogram"
          value={data.macd_histogram !== null ? data.macd_histogram.toFixed(3) : "N/A"}
          signal={data.macd_histogram !== null ? (data.macd_histogram > 0 ? "bullish" : "bearish") : undefined}
        />
        <Row label="Bollinger Position" value={data.bb_position.replace(/_/g, " ")} />
        <Row label="BB Upper / Lower" value={`${formatCurrency(data.bb_upper)} / ${formatCurrency(data.bb_lower)}`} />
        <Row label="Stochastic K / D" value={`${formatNumber(data.stoch_k, 1)} / ${formatNumber(data.stoch_d, 1)}`} />
        <Row label="SMA 20" value={formatCurrency(data.sma20)} />
        <Row label="SMA 50" value={formatCurrency(data.sma50)} />
        <Row label="SMA 200" value={formatCurrency(data.sma200)} />
        <Row label="Support (20d)" value={formatCurrency(data.support_20d)} />
        <Row label="Resistance (20d)" value={formatCurrency(data.resistance_20d)} />
      </div>
    </div>
  );
}
