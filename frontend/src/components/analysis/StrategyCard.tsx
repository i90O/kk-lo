"use client";

import { useState } from "react";
import type { Strategy } from "@/lib/types";

export default function StrategyCard({ strategy, rank }: { strategy: Strategy; rank: number }) {
  const [expanded, setExpanded] = useState(rank === 1);

  // Direction from strategy name
  const isBullish = strategy.name_en.toLowerCase().includes("bull") || strategy.name_en.toLowerCase().includes("long") || strategy.name_en.toLowerCase().includes("call");
  const isBearish = strategy.name_en.toLowerCase().includes("bear") || strategy.name_en.toLowerCase().includes("short") || strategy.name_en.toLowerCase().includes("put");
  const borderColor = isBullish ? "border-l-[var(--bullish)]" : isBearish ? "border-l-[var(--bearish)]" : "border-l-[var(--neutral)]";

  return (
    <div className={`border border-[var(--border)] rounded-lg border-l-[3px] ${borderColor} transition`}>
      {/* Header - horizontal layout */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-3 px-3 py-2.5 cursor-pointer hover:bg-[var(--bg-tertiary)]/30 transition"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-[var(--text-primary)]">{strategy.name_en}</span>
            {isBullish && <span className="text-[9px] px-1.5 py-0.5 rounded bg-[var(--bullish-bg)] text-[var(--bullish)]">BULL</span>}
            {isBearish && <span className="text-[9px] px-1.5 py-0.5 rounded bg-[var(--bearish-bg)] text-[var(--bearish)]">BEAR</span>}
          </div>
          {/* Legs as pill tags */}
          {strategy.legs && strategy.legs.length > 0 && (
            <div className="flex gap-1 mt-1 flex-wrap">
              {strategy.legs.map((leg, i) => (
                <span
                  key={i}
                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                    leg.action.toLowerCase().includes("sell")
                      ? "bg-[var(--bearish-bg)] text-[var(--bearish)]"
                      : "bg-[var(--bullish-bg)] text-[var(--bullish)]"
                  }`}
                >
                  {leg.action} {leg.type} ${leg.strike}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right: key metrics compact */}
        <div className="flex items-center gap-4 text-xs font-mono flex-shrink-0">
          <div className="text-[var(--bullish)]">{strategy.max_profit}</div>
          <div className="text-[var(--bearish)]">{strategy.max_loss}</div>
          <div className="text-[var(--text-secondary)]">{strategy.win_rate_est}</div>
        </div>

        <svg
          className={`w-4 h-4 text-[var(--text-muted)] transition-transform flex-shrink-0 ${expanded ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="px-3 pb-3 pt-0 border-t border-[var(--border)]/50 animate-fade-in">
          <div className="grid grid-cols-4 gap-2 my-2">
            <div className="bg-[var(--bg-primary)] rounded px-2 py-1.5">
              <div className="text-[9px] text-[var(--text-muted)]">MAX PROFIT</div>
              <div className="text-xs font-mono text-[var(--bullish)]">{strategy.max_profit}</div>
            </div>
            <div className="bg-[var(--bg-primary)] rounded px-2 py-1.5">
              <div className="text-[9px] text-[var(--text-muted)]">MAX LOSS</div>
              <div className="text-xs font-mono text-[var(--bearish)]">{strategy.max_loss}</div>
            </div>
            <div className="bg-[var(--bg-primary)] rounded px-2 py-1.5">
              <div className="text-[9px] text-[var(--text-muted)]">R/R</div>
              <div className="text-xs font-mono text-[var(--text-secondary)]">{strategy.risk_reward}</div>
            </div>
            <div className="bg-[var(--bg-primary)] rounded px-2 py-1.5">
              <div className="text-[9px] text-[var(--text-muted)]">WIN RATE</div>
              <div className="text-xs font-mono text-[var(--text-secondary)]">{strategy.win_rate_est}</div>
            </div>
          </div>

          {strategy.position_size && (
            <div className="text-[11px] text-[var(--text-muted)] mb-1.5">
              Position: {strategy.position_size}
            </div>
          )}

          {strategy.exit_rules && strategy.exit_rules.length > 0 && (
            <div className="text-[10px] text-[var(--text-muted)] space-y-0.5">
              {strategy.exit_rules.map((rule, i) => (
                <div key={i} className="flex gap-1.5">
                  <span className="text-[var(--neutral)]/50">&#8226;</span>
                  {rule}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
