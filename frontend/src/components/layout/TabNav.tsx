"use client";

import { useAppStore } from "@/lib/store";
import type { TabId } from "@/lib/types";

const TABS: { id: TabId; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "analysis", label: "Analysis" },
  { id: "scanner", label: "Scanner" },
  { id: "account", label: "Account" },
];

export default function TabNav() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);

  return (
    <nav className="flex gap-1 px-6 py-2 border-b border-gray-800 bg-[#0d0d0d]">
      {TABS.map((t) => (
        <button
          key={t.id}
          onClick={() => setActiveTab(t.id)}
          className={`px-4 py-2 text-sm font-medium rounded-t transition ${
            activeTab === t.id
              ? "text-green-400 border-b-2 border-green-500 bg-green-500/5"
              : "text-gray-500 hover:text-gray-300"
          }`}
        >
          {t.label}
        </button>
      ))}
    </nav>
  );
}
