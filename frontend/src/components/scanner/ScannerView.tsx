"use client";

import { useState, useEffect, useRef } from "react";
import { useAppStore } from "@/lib/store";
import AlertsTable from "./AlertsTable";
import StatCard from "@/components/shared/StatCard";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import { formatCompact } from "@/lib/format";
import { Activity, Filter } from "lucide-react";

const SCANNER_TABS: { key: string; label: string; types: string[] }[] = [
  { key: "all", label: "All Flow", types: [] },
  { key: "sweep", label: "Sweep", types: ["VOL/OI_SURGE"] },
  { key: "block", label: "Block", types: ["HIGH_VOLUME"] },
  { key: "golden", label: "Golden Sweep", types: ["INSTITUTIONAL_FAR_MONTH"] },
  { key: "magnets", label: "Magnets", types: ["ATM_OI_MAGNET"] },
  { key: "pcratio", label: "P/C Ratio", types: ["EXTREME_PC_RATIO"] },
];

export default function ScannerView() {
  const scannerData = useAppStore((s) => s.scannerData);
  const loading = useAppStore((s) => s.loading.scanner);
  const fetchScanner = useAppStore((s) => s.fetchScanner);
  const [activeTab, setActiveTab] = useState("all");
  const [sideFilter, setSideFilter] = useState<"all" | "CALL" | "PUT">("all");
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchScanner, 30000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [autoRefresh, fetchScanner]);

  const alerts = scannerData?.alerts || [];
  const tab = SCANNER_TABS.find((t) => t.key === activeTab)!;
  let filtered = tab.types.length > 0
    ? alerts.filter((a) => tab.types.includes(a.type))
    : alerts;
  if (sideFilter !== "all") {
    filtered = filtered.filter((a) => a.side === sideFilter);
  }

  // Stats
  const totalFlow = alerts.reduce((sum, a) => sum + (a.premium_flow || 0), 0);
  const callAlerts = alerts.filter((a) => a.side === "CALL").length;
  const putAlerts = alerts.filter((a) => a.side === "PUT").length;
  const callPct = alerts.length > 0 ? ((callAlerts / alerts.length) * 100).toFixed(0) : "0";
  const topTicker = (() => {
    const counts: Record<string, number> = {};
    alerts.forEach((a) => { counts[a.ticker] = (counts[a.ticker] || 0) + 1; });
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    return sorted[0]?.[0] || "-";
  })();

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity size={20} className="text-[var(--accent)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Unusual Activity Scanner</h2>
        </div>
        <button
          onClick={fetchScanner}
          disabled={loading}
          className="px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-lg font-medium hover:bg-[var(--accent-hover)] disabled:opacity-50 transition"
        >
          {loading ? (
            <span className="flex items-center gap-2"><LoadingSpinner size="sm" /> Scanning...</span>
          ) : "Scan Now"}
        </button>
      </div>

      {/* Tab filters */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          {SCANNER_TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-3 py-1.5 text-xs rounded-lg font-medium transition ${
                activeTab === t.key
                  ? "bg-[var(--accent)] text-white"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-[var(--text-muted)]" />
          {(["all", "CALL", "PUT"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setSideFilter(f)}
              className={`px-2 py-1 text-[11px] rounded transition ${
                sideFilter === f
                  ? f === "CALL" ? "bg-[var(--bullish)]/20 text-[var(--bullish)]"
                  : f === "PUT" ? "bg-[var(--bearish)]/20 text-[var(--bearish)]"
                  : "bg-[var(--bg-tertiary)] text-[var(--text-primary)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
            >
              {f === "all" ? "All" : f + "s"}
            </button>
          ))}
        </div>
      </div>

      {scannerData && (
        <>
          {/* Quick stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard label="Total Flow" value={"$" + formatCompact(totalFlow)} />
            <StatCard
              label="Call / Put"
              value={`${callPct}% / ${100 - Number(callPct)}%`}
              sub={`${callAlerts}C / ${putAlerts}P`}
            />
            <StatCard label="Top Ticker" value={topTicker} />
            <StatCard label="Alert Count" value={String(filtered.length)} sub={`of ${alerts.length} total`} />
          </div>

          {/* Table */}
          <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
            <AlertsTable alerts={filtered} />
          </div>
        </>
      )}

      {!scannerData && !loading && (
        <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-8 text-center">
          <div className="text-[var(--text-muted)] text-sm">Click &quot;Scan Now&quot; to detect unusual options activity across all watchlist tickers.</div>
          <div className="text-[var(--text-muted)] text-xs mt-2 opacity-60">Scans Vol/OI surges, high volume, institutional flow, ATM magnets, and P/C ratios.</div>
        </div>
      )}

      {/* Bottom bar */}
      {scannerData && (
        <div className="flex items-center justify-between text-xs text-[var(--text-muted)]">
          <span>Last scan: {scannerData.scan_time}</span>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="accent-[var(--accent)]"
            />
            Auto-refresh (30s)
          </label>
        </div>
      )}
    </div>
  );
}
