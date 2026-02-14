"use client";

export default function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const s = size === "sm" ? "w-4 h-4" : size === "lg" ? "w-8 h-8" : "w-6 h-6";
  return (
    <div className={`inline-block ${s} border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin`} />
  );
}
