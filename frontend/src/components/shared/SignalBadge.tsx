"use client";

import { signalBg } from "@/lib/format";

export default function SignalBadge({ signal, size = "md" }: {
  signal: string;
  size?: "sm" | "md";
}) {
  const label = signal.toUpperCase();
  const cls = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-1";
  return (
    <span className={`inline-block rounded border font-semibold ${cls} ${signalBg(signal)}`}>
      {label}
    </span>
  );
}
