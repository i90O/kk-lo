"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency } from "@/lib/format";
import TickerSearch from "@/components/shared/TickerSearch";

export default function TopBar() {
  const acc = useAppStore((s) => s.accountData);

  return (
    <header className="flex items-center justify-between px-4 h-12 border-b border-[var(--border)] bg-[var(--bg-secondary)]">
      <div className="flex items-center gap-2">
        <span className="text-base font-bold text-[var(--text-primary)] tracking-tight">OA</span>
        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-tertiary)] text-[var(--text-muted)]">v0.1</span>
      </div>

      <div className="flex-1 flex justify-center">
        <TickerSearch />
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--bullish)] animate-pulse-glow" />
          <span className="text-[11px] text-[var(--text-muted)]">Connected</span>
        </div>
        {acc && !acc.error && (
          <div className="text-right">
            <span className="text-xs font-mono text-[var(--text-secondary)]">{formatCurrency(acc.equity)}</span>
          </div>
        )}
      </div>
    </header>
  );
}
