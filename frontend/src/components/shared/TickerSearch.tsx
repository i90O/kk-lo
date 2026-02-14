"use client";

import { useState, useRef, useEffect } from "react";
import { useAppStore, WATCHLIST } from "@/lib/store";
import { Search, X } from "lucide-react";

export default function TickerSearch() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const searchAndSelectTicker = useAppStore((s) => s.searchAndSelectTicker);
  const selectedTicker = useAppStore((s) => s.selectedTicker);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const filtered = query
    ? WATCHLIST.filter((t) => t.includes(query.toUpperCase()))
    : WATCHLIST;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchAndSelectTicker(query);
      setQuery("");
      setOpen(false);
    }
  };

  const handleSelect = (ticker: string) => {
    searchAndSelectTicker(ticker);
    setQuery("");
    setOpen(false);
  };

  return (
    <div ref={wrapperRef} className="relative w-[280px]">
      <form onSubmit={handleSubmit}>
        <div className="flex items-center gap-2 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg px-3 py-1.5 focus-within:border-[var(--accent)] transition">
          <Search size={14} className="text-[var(--text-muted)] flex-shrink-0" />
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value.toUpperCase());
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            placeholder="Search ticker..."
            className="bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none w-full font-mono"
          />
          {query && (
            <button
              type="button"
              onClick={() => { setQuery(""); setOpen(false); }}
              className="text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
            >
              <X size={14} />
            </button>
          )}
        </div>
      </form>

      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto">
          {query && !WATCHLIST.includes(query.toUpperCase()) && (
            <button
              onClick={() => handleSelect(query)}
              className="w-full text-left px-3 py-2 text-xs text-[var(--accent)] hover:bg-[var(--bg-tertiary)] border-b border-[var(--border)]"
            >
              Search &quot;{query.toUpperCase()}&quot;
            </button>
          )}
          {filtered.map((t) => (
            <button
              key={t}
              onClick={() => handleSelect(t)}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-[var(--bg-tertiary)] transition ${
                t === selectedTicker ? "text-[var(--accent)] bg-[var(--accent)]/5" : "text-[var(--text-secondary)]"
              }`}
            >
              <span className="font-mono">{t}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
