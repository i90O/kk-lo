"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { formatCurrency, formatCompact, formatNumber } from "@/lib/format";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

export default function OptionsChainTable() {
  const chainData = useAppStore((s) => s.chainData);
  const loading = useAppStore((s) => s.loading.chain);
  const fetchChain = useAppStore((s) => s.fetchChain);
  const ticker = useAppStore((s) => s.selectedTicker);
  const price = useAppStore((s) => s.technicalData?.current_price);
  const [filter, setFilter] = useState<"all" | "call" | "put">("all");

  if (!chainData && !loading) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold text-gray-400">Options Chain</div>
          <button
            onClick={() => fetchChain(ticker)}
            className="px-3 py-1.5 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition"
          >
            Load Options Chain
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm font-semibold text-gray-400 mb-3">Options Chain</div>
        <div className="flex items-center justify-center py-6"><LoadingSpinner /></div>
      </div>
    );
  }

  if (!chainData || chainData.error) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm text-red-400">Error loading chain: {chainData?.error}</div>
      </div>
    );
  }

  const contracts = chainData.contracts.filter((c) => filter === "all" || c.type === filter);

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="text-sm font-semibold text-gray-400">Options Chain</div>
          <span className="text-[10px] text-gray-600">
            {chainData.count} contracts | Source: {chainData.source} | Avg IV: {chainData.summary.avg_iv ? (chainData.summary.avg_iv * 100).toFixed(1) + "%" : "N/A"}
          </span>
        </div>
        <div className="flex gap-1">
          {(["all", "call", "put"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-0.5 text-[11px] rounded transition ${
                filter === f ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"
              }`}
            >
              {f.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="text-xs">
          <thead className="sticky top-0 bg-[#111]">
            <tr className="text-gray-500 text-left">
              <th className="py-2 px-2">Type</th>
              <th className="py-2 px-2">Strike</th>
              <th className="py-2 px-2">Expiry</th>
              <th className="py-2 px-2 text-right">Bid</th>
              <th className="py-2 px-2 text-right">Ask</th>
              <th className="py-2 px-2 text-right">Volume</th>
              <th className="py-2 px-2 text-right">OI</th>
              <th className="py-2 px-2 text-right">IV</th>
              <th className="py-2 px-2 text-right">Delta</th>
              <th className="py-2 px-2 text-right">Theta</th>
            </tr>
          </thead>
          <tbody>
            {contracts.slice(0, 50).map((c, i) => {
              const isITM = price
                ? (c.type === "call" && c.strike < price) || (c.type === "put" && c.strike > price)
                : false;
              return (
                <tr
                  key={i}
                  className={`border-b border-gray-800/30 hover:bg-gray-800/30 ${isITM ? "bg-gray-800/20" : ""}`}
                >
                  <td className={`py-1.5 px-2 font-semibold ${c.type === "call" ? "text-green-400" : "text-red-400"}`}>
                    {c.type.toUpperCase()}
                  </td>
                  <td className="py-1.5 px-2 font-mono text-gray-200">{formatCurrency(c.strike)}</td>
                  <td className="py-1.5 px-2 text-gray-400">{c.expiry}</td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-300">{formatNumber(c.bid)}</td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-300">{formatNumber(c.ask)}</td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-400">{formatCompact(c.volume)}</td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-400">{formatCompact(c.open_interest)}</td>
                  <td className="py-1.5 px-2 text-right font-mono text-yellow-400">
                    {c.iv !== null ? (c.iv * 100).toFixed(1) + "%" : "N/A"}
                  </td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-300">
                    {c.delta !== null ? c.delta.toFixed(3) : "N/A"}
                  </td>
                  <td className="py-1.5 px-2 text-right font-mono text-gray-300">
                    {c.theta !== null ? c.theta.toFixed(3) : "N/A"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
