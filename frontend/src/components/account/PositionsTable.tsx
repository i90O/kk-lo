"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency, formatPL } from "@/lib/format";

export default function PositionsTable() {
  const positions = useAppStore((s) => s.positionsData);

  if (!positions || positions.length === 0 || positions[0]?.error) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-6 text-center">
        <div className="text-gray-600 text-sm">No open positions</div>
      </div>
    );
  }

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4 overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr className="text-gray-500 text-left border-b border-gray-800">
            <th className="py-2 px-2">Symbol</th>
            <th className="py-2 px-2">Qty</th>
            <th className="py-2 px-2">Side</th>
            <th className="py-2 px-2 text-right">Avg Entry</th>
            <th className="py-2 px-2 text-right">Current</th>
            <th className="py-2 px-2 text-right">Mkt Value</th>
            <th className="py-2 px-2 text-right">P&L</th>
            <th className="py-2 px-2 text-right">P&L %</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((p, i) => {
            const pl = formatPL(p.unrealized_pl);
            const plPct = parseFloat(p.unrealized_plpc || "0");
            const pctColor = plPct > 0 ? "text-green-400" : plPct < 0 ? "text-red-400" : "text-gray-400";
            return (
              <tr key={i} className="border-b border-gray-800/30 hover:bg-gray-800/30">
                <td className="py-2 px-2 font-semibold text-gray-200">{p.symbol}</td>
                <td className="py-2 px-2 font-mono text-gray-300">{p.qty}</td>
                <td className="py-2 px-2 text-gray-400">{p.side}</td>
                <td className="py-2 px-2 text-right font-mono text-gray-300">{formatCurrency(p.avg_entry_price)}</td>
                <td className="py-2 px-2 text-right font-mono text-gray-300">{formatCurrency(p.current_price)}</td>
                <td className="py-2 px-2 text-right font-mono text-gray-300">{formatCurrency(p.market_value)}</td>
                <td className={`py-2 px-2 text-right font-mono font-semibold ${pl.color}`}>{pl.text}</td>
                <td className={`py-2 px-2 text-right font-mono ${pctColor}`}>
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
