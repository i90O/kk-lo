"use client";

import { useAppStore } from "@/lib/store";
import { formatCurrency } from "@/lib/format";
import StatCard from "@/components/shared/StatCard";

export default function AccountCards() {
  const acc = useAppStore((s) => s.accountData);

  if (!acc || acc.error) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-6 text-center">
        <div className="text-[var(--text-muted)] text-sm">
          {acc?.error || "Account data not available"}
        </div>
        <div className="text-[var(--text-muted)] text-xs mt-2 opacity-60">
          Configure ALPACA_API_KEY in .env to enable paper trading
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard label="Portfolio Value" value={formatCurrency(acc.portfolio_value)} />
      <StatCard label="Equity" value={formatCurrency(acc.equity)} />
      <StatCard label="Cash" value={formatCurrency(acc.cash)} />
      <StatCard label="Buying Power" value={formatCurrency(acc.buying_power)} color="text-[var(--bullish)]" />
    </div>
  );
}
