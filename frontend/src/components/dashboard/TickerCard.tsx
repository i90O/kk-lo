"use client";

import type { TechnicalData } from "@/lib/types";
import { formatPercent, formatCurrency } from "@/lib/format";
import SignalBadge from "@/components/shared/SignalBadge";
import StrengthMeter from "@/components/shared/StrengthMeter";

export default function TickerCard({ data, onClick }: {
  data: TechnicalData;
  onClick: () => void;
}) {
  const changePct = data.change_pct;
  const changeColor = changePct > 0 ? "text-green-400" : changePct < 0 ? "text-red-400" : "text-gray-400";
  const rsiColor = data.rsi !== null
    ? data.rsi > 70 ? "text-red-400" : data.rsi < 30 ? "text-green-400" : "text-gray-400"
    : "text-gray-600";

  return (
    <div
      onClick={onClick}
      className="bg-[#111] border border-gray-800 rounded-lg p-4 cursor-pointer hover:border-green-600/50 hover:bg-[#151515] transition group"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-bold text-white group-hover:text-green-400 transition">
          {data.ticker}
        </span>
        <SignalBadge signal={data.signal} size="sm" />
      </div>

      <div className="font-mono text-lg text-white mb-1">
        {formatCurrency(data.current_price)}
      </div>

      <div className={`text-sm font-mono ${changeColor}`}>
        {formatPercent(changePct)}
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-500">RSI</span>
          <span className={`text-xs font-mono ${rsiColor}`}>
            {data.rsi !== null ? data.rsi.toFixed(1) : "N/A"}
          </span>
        </div>
        <StrengthMeter strength={data.strength} signal={data.signal} />
      </div>
    </div>
  );
}
