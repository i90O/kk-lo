"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatPL } from "@/lib/format";

export default function PositionsTable() {
  const positions = useAppStore((s) => s.positionsData);

  if (!positions || positions.length === 0 || positions[0]?.error) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-6 text-center">
        <div className="text-[var(--text-muted)] text-sm">No open positions</div>
      </div>
    );
  }

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4 overflow-x-auto">
      <table className="table-compact w-full">
        <thead>
          <tr className="text-[var(--text-muted)] text-left text-[11px] uppercase border-b border-[var(--border)]">
            <th className="py-2 px-3">Symbol</th>
            <th className="py-2 px-3">Qty</th>
            <th className="py-2 px-3">Side</th>
            <th className="py-2 px-3 text-right">Avg Entry</th>
            <th className="py-2 px-3 text-right">Current</th>
            <th className="py-2 px-3 text-right">Mkt Value</th>
            <th className="py-2 px-3 text-right">P&amp;L</th>
            <th className="py-2 px-3 text-right">P&amp;L %</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((p, i) => {
            const pl = formatPL(p.unrealized_pl);
            const plPct = parseFloat(p.unrealized_plpc || "0");
            const pctColor = plPct > 0 ? "text-[var(--bullish)]" : plPct < 0 ? "text-[var(--bearish)]" : "text-[var(--text-secondary)]";
            return (
              <tr key={i} className="border-b border-[var(--border)]/30 hover:bg-[var(--bg-tertiary)]/50">
                <td className="py-2 px-3 font-semibold text-[var(--text-primary)]">{p.symbol}</td>
                <td className="py-2 px-3 font-mono text-[var(--text-secondary)]">{p.qty}</td>
                <td className="py-2 px-3 text-[var(--text-muted)]">{p.side}</td>
                <td className="py-2 px-3 text-right font-mono text-[var(--text-secondary)]">{formatCurrency(p.avg_entry_price)}</td>
                <td className="py-2 px-3 text-right font-mono text-[var(--text-secondary)]">{formatCurrency(p.current_price)}</td>
                <td className="py-2 px-3 text-right font-mono text-[var(--text-secondary)]">{formatCurrency(p.market_value)}</td>
                <td className={`py-2 px-3 text-right font-mono font-semibold ${pl.color}`}>{pl.text}</td>
                <td className={`py-2 px-3 text-right font-mono ${pctColor}`}>
                  {plPct > 0 ? "+" : ""}{(plPct * 100).toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
