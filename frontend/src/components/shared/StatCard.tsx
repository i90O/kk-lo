"use client";

export default function StatCard({ label, value, sub, color }: {
  label: string;
  value: string;
  sub?: string;
  color?: string;
}) {
  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="text-[11px] text-[var(--text-muted)] uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-xl font-mono font-semibold ${color || "text-[var(--text-primary)]"}`}>{value}</div>
      {sub && <div className="text-xs text-[var(--text-muted)] mt-1">{sub}</div>}
    </div>
  );
}
