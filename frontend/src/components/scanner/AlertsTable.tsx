"use client";

import { useMemo } from "react";
import type { UnusualAlert } from "@/lib/types";
import { formatCurrency, formatCompact, timeAgo } from "@/lib/format";
import { useAppStore } from "@/lib/store";
import SortableTable, { type Column } from "@/components/shared/SortableTable";

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    "VOL/OI_SURGE": "bg-purple-500/20 text-purple-400",
    "HIGH_VOLUME": "bg-[var(--accent)]/20 text-[var(--accent)]",
    "INSTITUTIONAL_FAR_MONTH": "bg-cyan-500/20 text-cyan-400",
    "ATM_OI_MAGNET": "bg-orange-500/20 text-orange-400",
    "EXTREME_PC_RATIO": "bg-pink-500/20 text-pink-400",
  };
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${colors[type] || "bg-[var(--bg-tertiary)] text-[var(--text-muted)]"}`}>
      {type.replace(/_/g, " ")}
    </span>
  );
}

function PremiumFlowBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-mono text-[var(--neutral)] font-semibold whitespace-nowrap">
        {formatCompact(value)}
      </span>
      <div className="w-16 h-1.5 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
        <div
          className="h-full bg-[var(--neutral)] rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function AlertsTable({ alerts }: { alerts: UnusualAlert[] }) {
  const selectTicker = useAppStore((s) => s.selectTicker);
  const maxFlow = useMemo(() => Math.max(...alerts.map((a) => a.premium_flow || 0), 1), [alerts]);

  const columns: Column<UnusualAlert>[] = useMemo(() => [
    {
      key: "ticker",
      label: "Ticker",
      render: (row) => (
        <button
          onClick={(e) => { e.stopPropagation(); selectTicker(row.ticker); }}
          className="font-semibold font-mono text-[var(--accent)] hover:text-white transition"
        >
          {row.ticker}
        </button>
      ),
    },
    {
      key: "type",
      label: "Type",
      render: (row) => <TypeBadge type={row.type} />,
    },
    {
      key: "side",
      label: "C/P",
      render: (row) => (
        <span className={`font-semibold ${
          row.side === "CALL" ? "text-[var(--bullish)]" : row.side === "PUT" ? "text-[var(--bearish)]" : "text-[var(--text-muted)]"
        }`}>
          {row.side || "-"}
        </span>
      ),
    },
    {
      key: "strike",
      label: "Strike",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--text-secondary)]">{row.strike ? formatCurrency(row.strike) : "-"}</span>,
      sortValue: (row) => row.strike || 0,
    },
    {
      key: "expiry",
      label: "Exp",
      render: (row) => <span className="text-[var(--text-muted)]">{row.expiration || "-"}</span>,
    },
    {
      key: "dte",
      label: "DTE",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--text-muted)]">{row.dte ?? "-"}</span>,
      sortValue: (row) => row.dte || 0,
    },
    {
      key: "volume",
      label: "Vol",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--text-secondary)]">{row.volume ? formatCompact(row.volume) : "-"}</span>,
      sortValue: (row) => row.volume || 0,
    },
    {
      key: "oi",
      label: "OI",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--text-muted)]">{row.open_interest ? formatCompact(row.open_interest) : "-"}</span>,
      sortValue: (row) => row.open_interest || 0,
    },
    {
      key: "vol_oi",
      label: "V/OI",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--text-secondary)]">{row.vol_oi_ratio ? row.vol_oi_ratio.toFixed(1) : "-"}</span>,
      sortValue: (row) => row.vol_oi_ratio || 0,
    },
    {
      key: "iv",
      label: "IV",
      align: "right" as const,
      render: (row) => <span className="font-mono text-[var(--neutral)]">{row.iv ? (row.iv * 100).toFixed(0) + "%" : "-"}</span>,
      sortValue: (row) => row.iv || 0,
    },
    {
      key: "flow",
      label: "Flow $",
      align: "right" as const,
      render: (row) => <PremiumFlowBar value={row.premium_flow} max={maxFlow} />,
      sortValue: (row) => row.premium_flow || 0,
    },
    {
      key: "signal",
      label: "Signal",
      render: (row) => (
        <span className="text-[var(--text-muted)] max-w-[200px] truncate block text-[11px]" title={row.interpretation}>
          {row.interpretation}
        </span>
      ),
    },
  ], [selectTicker, maxFlow]);

  return (
    <SortableTable
      columns={columns}
      data={alerts}
      rowClassName={(row) =>
        row.side === "CALL" ? "bg-[var(--bullish-bg)]" : row.side === "PUT" ? "bg-[var(--bearish-bg)]" : ""
      }
      maxHeight="500px"
      emptyMessage="No alerts found"
    />
  );
}
