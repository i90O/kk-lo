"use client";

import { useEffect, useMemo } from "react";
import { useAppStore, WATCHLIST } from "@/lib/store";
import { formatPercent, formatCurrency, formatCompact } from "@/lib/format";
import SortableTable, { type Column } from "@/components/shared/SortableTable";
import SignalBadge from "@/components/shared/SignalBadge";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import type { TechnicalData } from "@/lib/types";
import { RefreshCw } from "lucide-react";

export default function WatchlistGrid() {
  const watchlistData = useAppStore((s) => s.watchlistData);
  const watchlistLoading = useAppStore((s) => s.watchlistLoading);
  const loadWatchlist = useAppStore((s) => s.loadWatchlist);
  const selectTicker = useAppStore((s) => s.selectTicker);

  useEffect(() => {
    if (Object.keys(watchlistData).length === 0) {
      loadWatchlist();
    }
    const interval = setInterval(loadWatchlist, 5 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const data: TechnicalData[] = useMemo(
    () => WATCHLIST.map((t) => watchlistData[t]).filter(Boolean),
    [watchlistData]
  );

  const columns: Column<TechnicalData>[] = useMemo(() => [
    {
      key: "ticker",
      label: "Ticker",
      render: (row) => <span className="font-mono font-semibold text-[var(--text-primary)]">{row.ticker}</span>,
      sortValue: (row) => row.ticker,
    },
    {
      key: "price",
      label: "Price",
      align: "right",
      render: (row) => <span className="font-mono text-[var(--text-primary)]">{formatCurrency(row.current_price)}</span>,
      sortValue: (row) => row.current_price,
    },
    {
      key: "change",
      label: "Chg%",
      align: "right",
      render: (row) => (
        <span className={`font-mono ${row.change_pct >= 0 ? "text-[var(--bullish)]" : "text-[var(--bearish)]"}`}>
          {formatPercent(row.change_pct)}
        </span>
      ),
      sortValue: (row) => row.change_pct,
    },
    {
      key: "rsi",
      label: "RSI",
      align: "right",
      render: (row) => {
        const color = row.rsi !== null
          ? row.rsi > 70 ? "text-[var(--bearish)]" : row.rsi < 30 ? "text-[var(--bullish)]" : "text-[var(--text-secondary)]"
          : "text-[var(--text-muted)]";
        return <span className={`font-mono ${color}`}>{row.rsi !== null ? row.rsi.toFixed(1) : "N/A"}</span>;
      },
      sortValue: (row) => row.rsi || 0,
    },
    {
      key: "signal",
      label: "Signal",
      align: "center",
      render: (row) => <SignalBadge signal={row.signal} size="sm" />,
    },
    {
      key: "strength",
      label: "Str",
      align: "center",
      render: (row) => <span className="font-mono text-[var(--text-secondary)]">{row.strength}/5</span>,
      sortValue: (row) => row.strength,
    },
    {
      key: "volume",
      label: "Vol Ratio",
      align: "right",
      render: (row) => (
        <span className={`font-mono ${row.volume_ratio > 1.5 ? "text-[var(--bullish)]" : "text-[var(--text-muted)]"}`}>
          {row.volume_ratio.toFixed(2)}x
        </span>
      ),
      sortValue: (row) => row.volume_ratio,
    },
  ], []);

  const loaded = Object.keys(watchlistData).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Watchlist</h2>
        <div className="flex items-center gap-3">
          {watchlistLoading && <LoadingSpinner size="sm" />}
          <span className="text-xs text-[var(--text-muted)]">{loaded}/{WATCHLIST.length}</span>
          <button
            onClick={loadWatchlist}
            disabled={watchlistLoading}
            className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-secondary)] disabled:opacity-50 transition"
          >
            <RefreshCw size={14} className={watchlistLoading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {data.length > 0 ? (
        <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-3">
          <SortableTable
            columns={columns}
            data={data}
            onRowClick={(row) => selectTicker(row.ticker)}
            emptyMessage="Loading watchlist..."
          />
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
          {WATCHLIST.map((t) => (
            <div key={t} className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4 animate-shimmer">
              <div className="text-sm font-bold text-[var(--text-muted)] mb-2">{t}</div>
              <div className="h-6 bg-[var(--bg-tertiary)] rounded mb-2" />
              <div className="h-4 bg-[var(--bg-tertiary)] rounded w-1/2" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
