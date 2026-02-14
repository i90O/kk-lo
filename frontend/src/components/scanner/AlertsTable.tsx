"use client";

import type { UnusualAlert } from "@/lib/types";
import { formatCurrency, formatCompact } from "@/lib/format";
import { useAppStore } from "@/lib/store";

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    "VOL/OI_SURGE": "bg-purple-500/20 text-purple-400",
    "HIGH_VOLUME": "bg-blue-500/20 text-blue-400",
    "INSTITUTIONAL_FAR_MONTH": "bg-cyan-500/20 text-cyan-400",
    "ATM_OI_MAGNET": "bg-orange-500/20 text-orange-400",
    "EXTREME_PC_RATIO": "bg-pink-500/20 text-pink-400",
  };
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${colors[type] || "bg-gray-700 text-gray-400"}`}>
      {type.replace(/_/g, " ")}
    </span>
  );
}

export default function AlertsTable({ alerts }: { alerts: UnusualAlert[] }) {
  const selectTicker = useAppStore((s) => s.selectTicker);

  if (alerts.length === 0) {
    return <div className="text-xs text-gray-600 py-4">No alerts found</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr className="text-gray-500 text-left border-b border-gray-800">
            <th className="py-2 px-2">Ticker</th>
            <th className="py-2 px-2">Type</th>
            <th className="py-2 px-2">Side</th>
            <th className="py-2 px-2 text-right">Strike</th>
            <th className="py-2 px-2">Expiry</th>
            <th className="py-2 px-2 text-right">Volume</th>
            <th className="py-2 px-2 text-right">OI</th>
            <th className="py-2 px-2 text-right">Premium Flow</th>
            <th className="py-2 px-2">Interpretation</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((a, i) => (
            <tr key={i} className="border-b border-gray-800/30 hover:bg-gray-800/30">
              <td className="py-2 px-2">
                <button
                  onClick={() => selectTicker(a.ticker)}
                  className="font-semibold text-green-400 hover:text-green-300"
                >
                  {a.ticker}
                </button>
              </td>
              <td className="py-2 px-2"><TypeBadge type={a.type} /></td>
              <td className={`py-2 px-2 font-semibold ${a.side === "CALL" ? "text-green-400" : a.side === "PUT" ? "text-red-400" : "text-gray-400"}`}>
                {a.side || "-"}
              </td>
              <td className="py-2 px-2 text-right font-mono text-gray-300">
                {a.strike ? formatCurrency(a.strike) : "-"}
              </td>
              <td className="py-2 px-2 text-gray-400">{a.expiration || "-"}</td>
              <td className="py-2 px-2 text-right font-mono text-gray-300">
                {a.volume ? formatCompact(a.volume) : "-"}
              </td>
              <td className="py-2 px-2 text-right font-mono text-gray-300">
                {a.open_interest ? formatCompact(a.open_interest) : "-"}
              </td>
              <td className="py-2 px-2 text-right font-mono text-yellow-400 font-semibold">
                {formatCompact(a.premium_flow)}
              </td>
              <td className="py-2 px-2 text-gray-500 max-w-xs truncate" title={a.interpretation}>
                {a.interpretation}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
