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
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-[var(--text-secondary)]">Options Chain</div>
          <button
            onClick={() => fetchChain(ticker)}
            className="px-3 py-1.5 text-xs bg-[var(--accent)] text-white rounded hover:bg-[var(--accent-hover)] transition"
          >
            Load Chain
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">Options Chain</div>
        <div className="flex items-center justify-center py-6"><LoadingSpinner /></div>
      </div>
    );
  }

  if (!chainData || chainData.error) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm text-[var(--bearish)]">Error: {chainData?.error}</div>
      </div>
    );
  }

  const calls = chainData.contracts.filter((c) => c.type === "call");
  const puts = chainData.contracts.filter((c) => c.type === "put");

  // Get unique strikes sorted
  const allStrikes = [...new Set(chainData.contracts.map((c) => c.strike))].sort((a, b) => a - b);
  const strikes = filter === "call" ? [...new Set(calls.map((c) => c.strike))].sort((a, b) => a - b)
    : filter === "put" ? [...new Set(puts.map((c) => c.strike))].sort((a, b) => a - b)
    : allStrikes;

  // For split view, build lookup maps
  const callMap = new Map(calls.map((c) => [c.strike, c]));
  const putMap = new Map(puts.map((c) => [c.strike, c]));

  const showSplit = filter === "all";

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="text-sm font-medium text-[var(--text-secondary)]">Options Chain</div>
          <span className="text-[10px] text-[var(--text-muted)]">
            {chainData.count} contracts | Avg IV: {chainData.summary.avg_iv ? (chainData.summary.avg_iv * 100).toFixed(1) + "%" : "N/A"}
          </span>
        </div>
        <div className="flex gap-1">
          {(["all", "call", "put"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 text-[11px] rounded transition ${
                filter === f ? "bg-[var(--bg-tertiary)] text-[var(--text-primary)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
            >
              {f.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
        {showSplit ? (
          /* Split view: Calls | Strike | Puts */
          <table className="table-compact w-full text-[12px]">
            <thead className="sticky top-0 bg-[var(--bg-secondary)] z-10">
              <tr>
                <th className="py-2 px-2 text-right text-[var(--text-muted)] text-[10px]">IV</th>
                <th className="py-2 px-2 text-right text-[var(--text-muted)] text-[10px]">OI</th>
                <th className="py-2 px-2 text-right text-[var(--text-muted)] text-[10px]">Vol</th>
                <th className="py-2 px-2 text-right text-[var(--text-muted)] text-[10px]">Ask</th>
                <th className="py-2 px-2 text-right text-[var(--text-muted)] text-[10px]">Bid</th>
                <th className="py-2 px-2 text-center font-semibold text-[var(--text-secondary)] text-[10px] bg-[var(--bg-tertiary)]">Strike</th>
                <th className="py-2 px-2 text-left text-[var(--text-muted)] text-[10px]">Bid</th>
                <th className="py-2 px-2 text-left text-[var(--text-muted)] text-[10px]">Ask</th>
                <th className="py-2 px-2 text-left text-[var(--text-muted)] text-[10px]">Vol</th>
                <th className="py-2 px-2 text-left text-[var(--text-muted)] text-[10px]">OI</th>
                <th className="py-2 px-2 text-left text-[var(--text-muted)] text-[10px]">IV</th>
              </tr>
            </thead>
            <tbody>
              {strikes.slice(0, 50).map((strike) => {
                const call = callMap.get(strike);
                const put = putMap.get(strike);
                const isATM = price ? Math.abs(strike - price) === Math.min(...strikes.map((s) => Math.abs(s - price!))) : false;
                const callITM = price ? strike < price : false;
                const putITM = price ? strike > price : false;

                return (
                  <tr
                    key={strike}
                    className={`border-b border-[var(--border)]/20 ${isATM ? "bg-[var(--accent)]/10" : ""}`}
                  >
                    {/* Call side */}
                    <td className={`py-1 px-2 text-right font-mono text-[var(--neutral)] ${callITM ? "bg-[var(--bullish-bg)]" : ""}`}>
                      {call?.iv ? (call.iv * 100).toFixed(0) + "%" : "-"}
                    </td>
                    <td className={`py-1 px-2 text-right font-mono text-[var(--text-muted)] ${callITM ? "bg-[var(--bullish-bg)]" : ""}`}>
                      {call ? formatCompact(call.open_interest) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-right font-mono text-[var(--text-secondary)] ${callITM ? "bg-[var(--bullish-bg)]" : ""}`}>
                      {call ? formatCompact(call.volume) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-right font-mono text-[var(--text-secondary)] ${callITM ? "bg-[var(--bullish-bg)]" : ""}`}>
                      {call ? formatNumber(call.ask) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-right font-mono text-[var(--text-secondary)] ${callITM ? "bg-[var(--bullish-bg)]" : ""}`}>
                      {call ? formatNumber(call.bid) : "-"}
                    </td>
                    {/* Strike */}
                    <td className="py-1 px-2 text-center font-mono font-semibold text-[var(--text-primary)] bg-[var(--bg-tertiary)]">
                      {formatCurrency(strike)}
                    </td>
                    {/* Put side */}
                    <td className={`py-1 px-2 text-left font-mono text-[var(--text-secondary)] ${putITM ? "bg-[var(--bearish-bg)]" : ""}`}>
                      {put ? formatNumber(put.bid) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-left font-mono text-[var(--text-secondary)] ${putITM ? "bg-[var(--bearish-bg)]" : ""}`}>
                      {put ? formatNumber(put.ask) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-left font-mono text-[var(--text-secondary)] ${putITM ? "bg-[var(--bearish-bg)]" : ""}`}>
                      {put ? formatCompact(put.volume) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-left font-mono text-[var(--text-muted)] ${putITM ? "bg-[var(--bearish-bg)]" : ""}`}>
                      {put ? formatCompact(put.open_interest) : "-"}
                    </td>
                    <td className={`py-1 px-2 text-left font-mono text-[var(--neutral)] ${putITM ? "bg-[var(--bearish-bg)]" : ""}`}>
                      {put?.iv ? (put.iv * 100).toFixed(0) + "%" : "-"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          /* Single side view */
          <table className="table-compact w-full text-[12px]">
            <thead className="sticky top-0 bg-[var(--bg-secondary)]">
              <tr className="text-[var(--text-muted)] text-[10px]">
                <th className="py-2 px-2 text-left">Type</th>
                <th className="py-2 px-2">Strike</th>
                <th className="py-2 px-2">Expiry</th>
                <th className="py-2 px-2 text-right">Bid</th>
                <th className="py-2 px-2 text-right">Ask</th>
                <th className="py-2 px-2 text-right">Vol</th>
                <th className="py-2 px-2 text-right">OI</th>
                <th className="py-2 px-2 text-right">IV</th>
                <th className="py-2 px-2 text-right">Delta</th>
              </tr>
            </thead>
            <tbody>
              {chainData.contracts.filter((c) => c.type === filter).slice(0, 50).map((c, i) => {
                const isITM = price ? (c.type === "call" && c.strike < price) || (c.type === "put" && c.strike > price) : false;
                return (
                  <tr key={i} className={`border-b border-[var(--border)]/20 hover:bg-[var(--bg-tertiary)]/50 ${isITM ? "bg-[var(--bg-tertiary)]/30" : ""}`}>
                    <td className={`py-1 px-2 font-semibold ${c.type === "call" ? "text-[var(--bullish)]" : "text-[var(--bearish)]"}`}>
                      {c.type.toUpperCase()}
                    </td>
                    <td className="py-1 px-2 font-mono text-[var(--text-primary)]">{formatCurrency(c.strike)}</td>
                    <td className="py-1 px-2 text-[var(--text-muted)]">{c.expiry}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--text-secondary)]">{formatNumber(c.bid)}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--text-secondary)]">{formatNumber(c.ask)}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--text-muted)]">{formatCompact(c.volume)}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--text-muted)]">{formatCompact(c.open_interest)}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--neutral)]">{c.iv !== null ? (c.iv * 100).toFixed(1) + "%" : "N/A"}</td>
                    <td className="py-1 px-2 text-right font-mono text-[var(--text-secondary)]">{c.delta !== null ? c.delta.toFixed(3) : "N/A"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
