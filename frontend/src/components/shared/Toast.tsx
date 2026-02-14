"use client";

import { useAppStore } from "@/lib/store";
import type { ToastMessage } from "@/lib/types";

const ICONS: Record<string, string> = {
  success: "\u2713",
  error: "\u2715",
  warning: "\u26A0",
  info: "\u2139",
};

const COLORS: Record<string, string> = {
  success: "border-[var(--bullish)]/40 bg-[var(--bullish)]/10 text-[var(--bullish)]",
  error: "border-[var(--bearish)]/40 bg-[var(--bearish)]/10 text-[var(--bearish)]",
  warning: "border-[var(--neutral)]/40 bg-[var(--neutral)]/10 text-[var(--neutral)]",
  info: "border-[var(--accent)]/40 bg-[var(--accent)]/10 text-[var(--accent)]",
};

function ToastItem({ toast }: { toast: ToastMessage }) {
  const removeToast = useAppStore((s) => s.removeToast);

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm shadow-lg animate-slide-in ${COLORS[toast.type]}`}
    >
      <span className="text-sm font-bold">{ICONS[toast.type]}</span>
      <span className="text-xs flex-1">{toast.message}</span>
      <button
        onClick={() => removeToast(toast.id)}
        className="text-[var(--text-muted)] hover:text-[var(--text-secondary)] text-xs"
      >
        \u2715
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const toasts = useAppStore((s) => s.toasts);
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}
