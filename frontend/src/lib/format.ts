// Number formatting utilities

export function formatCurrency(val: number | string | null | undefined): string {
  if (val === null || val === undefined) return "N/A";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "N/A";
  const prefix = num < 0 ? "-$" : "$";
  return prefix + Math.abs(num).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatPercent(val: number | null | undefined, decimals = 2): string {
  if (val === null || val === undefined) return "N/A";
  const sign = val > 0 ? "+" : "";
  return sign + val.toFixed(decimals) + "%";
}

export function formatCompact(val: number | null | undefined): string {
  if (val === null || val === undefined) return "N/A";
  if (Math.abs(val) >= 1e9) return (val / 1e9).toFixed(1) + "B";
  if (Math.abs(val) >= 1e6) return (val / 1e6).toFixed(1) + "M";
  if (Math.abs(val) >= 1e3) return (val / 1e3).toFixed(1) + "K";
  return val.toLocaleString("en-US");
}

export function formatNumber(val: number | null | undefined, decimals = 2): string {
  if (val === null || val === undefined) return "N/A";
  return val.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPL(val: number | string | null | undefined): { text: string; color: string } {
  if (val === null || val === undefined) return { text: "N/A", color: "text-gray-500" };
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return { text: "N/A", color: "text-gray-500" };
  if (num > 0) return { text: "+$" + Math.abs(num).toFixed(2), color: "text-green-400" };
  if (num < 0) return { text: "-$" + Math.abs(num).toFixed(2), color: "text-red-400" };
  return { text: "$0.00", color: "text-gray-400" };
}

export function timeAgo(dateStr: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return diffMin + "m ago";
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return diffHr + "h ago";
  const diffDay = Math.floor(diffHr / 24);
  return diffDay + "d ago";
}

export function signalColor(signal: string): string {
  switch (signal) {
    case "bullish": return "text-green-400";
    case "bearish": return "text-red-400";
    default: return "text-yellow-400";
  }
}

export function signalBg(signal: string): string {
  switch (signal) {
    case "bullish": return "bg-green-500/20 text-green-400 border-green-500/30";
    case "bearish": return "bg-red-500/20 text-red-400 border-red-500/30";
    default: return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
  }
}
