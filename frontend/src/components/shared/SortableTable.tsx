"use client";

import { useState, useCallback } from "react";

export interface Column<T> {
  key: string;
  label: string;
  align?: "left" | "right" | "center";
  render: (row: T, index: number) => React.ReactNode;
  sortValue?: (row: T) => number | string;
  width?: string;
}

interface SortableTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowClassName?: (row: T, index: number) => string;
  onRowClick?: (row: T) => void;
  stickyHeader?: boolean;
  maxHeight?: string;
  emptyMessage?: string;
}

export default function SortableTable<T>({
  columns,
  data,
  rowClassName,
  onRowClick,
  stickyHeader = true,
  maxHeight,
  emptyMessage = "No data",
}: SortableTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const handleSort = useCallback((key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }, [sortKey]);

  const sortedData = (() => {
    if (!sortKey) return data;
    const col = columns.find((c) => c.key === sortKey);
    if (!col?.sortValue) return data;
    const sorted = [...data].sort((a, b) => {
      const va = col.sortValue!(a);
      const vb = col.sortValue!(b);
      if (typeof va === "number" && typeof vb === "number") return va - vb;
      return String(va).localeCompare(String(vb));
    });
    return sortDir === "desc" ? sorted.reverse() : sorted;
  })();

  if (data.length === 0) {
    return <div className="text-sm text-[var(--text-muted)] py-6 text-center">{emptyMessage}</div>;
  }

  return (
    <div className={`overflow-x-auto ${maxHeight ? `max-h-[${maxHeight}] overflow-y-auto` : ""}`} style={maxHeight ? { maxHeight } : undefined}>
      <table className="table-compact w-full">
        <thead className={stickyHeader ? "sticky top-0 z-10 bg-[var(--bg-secondary)]" : ""}>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => col.sortValue && handleSort(col.key)}
                className={`py-2 px-3 text-[11px] font-medium uppercase tracking-wider text-[var(--text-muted)] border-b border-[var(--border)] ${
                  col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                } ${col.sortValue ? "cursor-pointer hover:text-[var(--text-secondary)] select-none" : ""}`}
                style={col.width ? { width: col.width } : undefined}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {sortKey === col.key && (
                    <span className="text-[var(--accent)]">{sortDir === "asc" ? "\u25B2" : "\u25BC"}</span>
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, i) => (
            <tr
              key={i}
              onClick={() => onRowClick?.(row)}
              className={`border-b border-[var(--border)]/30 hover:bg-[var(--bg-tertiary)]/50 transition-colors ${
                onRowClick ? "cursor-pointer" : ""
              } ${rowClassName?.(row, i) || ""}`}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`py-2 px-3 ${col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"}`}
                >
                  {col.render(row, i)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
