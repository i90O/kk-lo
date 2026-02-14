"use client";

import { useState, useMemo } from "react";
import { useAppStore } from "@/lib/store";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  ReferenceLine, CartesianGrid, Bar, ComposedChart,
} from "recharts";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

const PERIODS = ["1mo", "3mo", "6mo", "1y"] as const;

export default function PriceChart() {
  const data = useAppStore((s) => s.technicalData);
  const priceHistory = useAppStore((s) => s.priceHistory);
  const loading = useAppStore((s) => s.loading.priceHistory);
  const fetchPriceHistory = useAppStore((s) => s.fetchPriceHistory);
  const ticker = useAppStore((s) => s.selectedTicker);
  const [period, setPeriod] = useState<string>("6mo");
  const [showVolume, setShowVolume] = useState(true);

  const handlePeriodChange = (p: string) => {
    setPeriod(p);
    fetchPriceHistory(ticker, p);
  };

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!priceHistory || priceHistory.length === 0) return [];
    return priceHistory.map((bar) => ({
      time: bar.time,
      price: bar.close,
      open: bar.open,
      high: bar.high,
      low: bar.low,
      volume: bar.volume,
    }));
  }, [priceHistory]);

  if (!data) return null;

  const isUp = data.change_pct >= 0;
  const color = isUp ? "var(--bullish)" : "var(--bearish)";
  const hasData = chartData.length > 0;

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-[var(--text-secondary)]">Price Chart</div>
        <div className="flex items-center gap-2">
          {/* Timeframe selector */}
          <div className="flex gap-0.5 bg-[var(--bg-primary)] rounded-lg p-0.5">
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => handlePeriodChange(p)}
                className={`px-2.5 py-1 text-[11px] rounded font-mono transition ${
                  period === p
                    ? "bg-[var(--bg-tertiary)] text-[var(--text-primary)]"
                    : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                }`}
              >
                {p.toUpperCase()}
              </button>
            ))}
          </div>
          {/* Volume toggle */}
          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`px-2 py-1 text-[10px] rounded transition ${
              showVolume ? "bg-[var(--bg-tertiary)] text-[var(--text-secondary)]" : "text-[var(--text-muted)]"
            }`}
          >
            Vol
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 text-[10px] text-[var(--text-muted)] mb-2">
        {data.support_20d && (
          <span className="flex items-center gap-1">
            <span className="w-3 h-0.5 inline-block" style={{ background: "var(--bullish)", opacity: 0.5 }} /> Support ${data.support_20d.toFixed(2)}
          </span>
        )}
        {data.resistance_20d && (
          <span className="flex items-center gap-1">
            <span className="w-3 h-0.5 inline-block" style={{ background: "var(--bearish)", opacity: 0.5 }} /> Resistance ${data.resistance_20d.toFixed(2)}
          </span>
        )}
        {data.sma20 && (
          <span className="flex items-center gap-1">
            <span className="w-3 h-0.5 inline-block" style={{ background: "var(--neutral)", opacity: 0.5 }} /> SMA20
          </span>
        )}
      </div>

      {loading && !hasData ? (
        <div className="flex items-center justify-center" style={{ height: 400 }}>
          <LoadingSpinner />
        </div>
      ) : !hasData ? (
        <div className="flex items-center justify-center text-[var(--text-muted)] text-sm" style={{ height: 400 }}>
          No price data available
        </div>
      ) : (
        <div style={{ height: 400 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 5, right: 5, bottom: showVolume ? 30 : 5, left: 5 }}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 10, fill: "var(--text-muted)" }}
                axisLine={{ stroke: "var(--border)" }}
                tickLine={false}
                tickFormatter={(v: string) => {
                  const d = new Date(v);
                  return `${d.getMonth() + 1}/${d.getDate()}`;
                }}
                interval="preserveStartEnd"
                minTickGap={40}
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 10, fill: "var(--text-muted)" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => `$${v.toFixed(0)}`}
                width={50}
                yAxisId="price"
              />
              {showVolume && (
                <YAxis
                  yAxisId="volume"
                  orientation="right"
                  tick={false}
                  axisLine={false}
                  tickLine={false}
                  width={0}
                />
              )}
              <Tooltip
                contentStyle={{
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontFamily: "JetBrains Mono, monospace",
                  color: "var(--text-primary)",
                }}
                formatter={(val: number, name: string) => {
                  if (name === "volume") return [val.toLocaleString(), "Volume"];
                  return [`$${val.toFixed(2)}`, name === "price" ? "Close" : name];
                }}
                labelFormatter={(label: string) => {
                  const d = new Date(label);
                  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
                }}
              />
              {data.support_20d && (
                <ReferenceLine yAxisId="price" y={data.support_20d} stroke="var(--bullish)" strokeDasharray="3 3" strokeOpacity={0.4} />
              )}
              {data.resistance_20d && (
                <ReferenceLine yAxisId="price" y={data.resistance_20d} stroke="var(--bearish)" strokeDasharray="3 3" strokeOpacity={0.4} />
              )}
              {data.sma20 && (
                <ReferenceLine yAxisId="price" y={data.sma20} stroke="var(--neutral)" strokeDasharray="2 2" strokeOpacity={0.3} />
              )}
              {showVolume && (
                <Bar
                  yAxisId="volume"
                  dataKey="volume"
                  fill="var(--accent)"
                  opacity={0.15}
                  isAnimationActive={false}
                />
              )}
              <Area
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke={color}
                strokeWidth={2}
                fill="url(#priceGradient)"
                animationDuration={800}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* SMA Legend */}
      <div className="flex gap-4 mt-2 text-[10px] text-[var(--text-muted)] font-mono">
        {data.sma20 && <span>SMA20: ${data.sma20.toFixed(2)}</span>}
        {data.sma50 && <span>SMA50: ${data.sma50.toFixed(2)}</span>}
        {data.sma200 && <span>SMA200: ${data.sma200.toFixed(2)}</span>}
      </div>
    </div>
  );
}
