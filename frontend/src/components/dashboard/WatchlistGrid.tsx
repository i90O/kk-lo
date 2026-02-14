"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import TickerCard from "./TickerCard";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

const WATCHLIST = [
  "SPY", "QQQ", "TSLA", "AAPL", "NVDA", "META",
  "AMZN", "AMD", "MSFT", "GOOGL", "NFLX", "COIN",
];

export default function WatchlistGrid() {
  const watchlistData = useAppStore((s) => s.watchlistData);
  const watchlistLoading = useAppStore((s) => s.watchlistLoading);
  const loadWatchlist = useAppStore((s) => s.loadWatchlist);
  const selectTicker = useAppStore((s) => s.selectTicker);

  useEffect(() => {
    if (Object.keys(watchlistData).length === 0) {
      loadWatchlist();
    }
    // Auto refresh every 5 minutes
    const interval = setInterval(loadWatchlist, 5 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loaded = Object.keys(watchlistData).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-200">Watchlist</h2>
        <div className="flex items-center gap-3">
          {watchlistLoading && <LoadingSpinner size="sm" />}
          <span className="text-xs text-gray-500">{loaded}/12 loaded</span>
          <button
            onClick={loadWatchlist}
            disabled={watchlistLoading}
            className="text-xs text-green-500 hover:text-green-400 disabled:text-gray-600"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
        {WATCHLIST.map((t) => {
          const data = watchlistData[t];
          if (!data) {
            return (
              <div key={t} className="bg-[#111] border border-gray-800 rounded-lg p-4 animate-pulse">
                <div className="text-sm font-bold text-gray-600 mb-2">{t}</div>
                <div className="h-6 bg-gray-800 rounded mb-2" />
                <div className="h-4 bg-gray-800 rounded w-1/2" />
              </div>
            );
          }
          return (
            <TickerCard key={t} data={data} onClick={() => selectTicker(t)} />
          );
        })}
      </div>
    </div>
  );
}
