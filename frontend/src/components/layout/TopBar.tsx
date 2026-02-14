"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency } from "@/lib/format";

export default function TopBar() {
  const acc = useAppStore((s) => s.accountData);

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-[#0d0d0d]">
      <div>
        <h1 className="text-xl font-bold text-green-500 tracking-tight">OptionsAgent</h1>
        <p className="text-[11px] text-gray-600">Options Trading Dashboard</p>
      </div>
      {acc && !acc.error ? (
        <div className="flex gap-6 text-right">
          {[
            { label: "Equity", val: acc.equity },
            { label: "Cash", val: acc.cash },
            { label: "Buying Power", val: acc.buying_power },
          ].map((item) => (
            <div key={item.label}>
              <div className="text-[10px] text-gray-500 uppercase">{item.label}</div>
              <div className="text-sm font-mono text-gray-200">{formatCurrency(item.val)}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-xs text-gray-600">Paper Trading</div>
      )}
    </header>
  );
}
