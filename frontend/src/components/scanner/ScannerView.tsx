"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import AlertsTable from "./AlertsTable";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

const ALERT_TYPES = [
  "VOL/OI_SURGE", "HIGH_VOLUME", "INSTITUTIONAL_FAR_MONTH",
  "ATM_OI_MAGNET", "EXTREME_PC_RATIO",
];

export default function ScannerView() {
  const scannerData = useAppStore((s) => s.scannerData);
  const loading = useAppStore((s) => s.loading.scanner);
  const fetchScanner = useAppStore((s) => s.fetchScanner);
  const [typeFilter, setTypeFilter] = useState<string>("all");

  const alerts = scannerData?.alerts || [];
  const filtered = typeFilter === "all" ? alerts : alerts.filter((a) => a.type === typeFilter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-200">Unusual Activity Scanner</h2>
        <button
          onClick={fetchScanner}
          disabled={loading}
          className="px-4 py-2 text-sm bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 disabled:opacity-50 transition"
        >
          {loading ? (
            <span className="flex items-center gap-2"><LoadingSpinner size="sm" /> Scanning...</span>
          ) : "Scan Now"}
        </button>
      </div>

      {scannerData && (
        <>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-500">
              {scannerData.total_alerts} alerts | {scannerData.scan_time}
            </span>
            <div className="flex gap-1">
              <button
                onClick={() => setTypeFilter("all")}
                className={`px-2 py-0.5 text-[10px] rounded ${typeFilter === "all" ? "bg-gray-700 text-white" : "text-gray-500"}`}
              >
                ALL
              </button>
              {ALERT_TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => setTypeFilter(t)}
                  className={`px-2 py-0.5 text-[10px] rounded ${typeFilter === t ? "bg-gray-700 text-white" : "text-gray-500"}`}
                >
                  {t.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
            <AlertsTable alerts={filtered.slice(0, 20)} />
          </div>
        </>
      )}

      {!scannerData && !loading && (
        <div className="bg-[#111] border border-gray-800 rounded-lg p-8 text-center">
          <div className="text-gray-600 text-sm">Click "Scan Now" to detect unusual options activity across all watchlist tickers.</div>
          <div className="text-gray-700 text-xs mt-2">Scans Vol/OI surges, high volume, institutional flow, ATM magnets, and P/C ratios.</div>
        </div>
      )}
    </div>
  );
}
