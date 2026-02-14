"use client";

import { useAppStore } from "@/lib/store";
import type { TabId } from "@/lib/types";
import {
  LayoutDashboard,
  BarChart3,
  ScanSearch,
  Wallet,
  MessageSquare,
} from "lucide-react";

const TABS: { id: TabId; label: string; icon: React.ElementType; shortcut: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, shortcut: "1" },
  { id: "analysis", label: "Analysis", icon: BarChart3, shortcut: "2" },
  { id: "scanner", label: "Scanner", icon: ScanSearch, shortcut: "3" },
  { id: "account", label: "Account", icon: Wallet, shortcut: "4" },
  { id: "chat", label: "AI Chat", icon: MessageSquare, shortcut: "5" },
];

export default function TabNav() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);

  return (
    <nav className="flex items-center px-4 border-b border-[var(--border)] bg-[var(--bg-secondary)]">
      <div className="flex gap-0.5">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`relative flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium transition ${
                active
                  ? "text-white"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
              title={`${t.label} (${t.shortcut})`}
            >
              <Icon size={15} />
              {t.label}
              <span className="text-[9px] text-[var(--text-muted)] ml-0.5 hidden lg:inline opacity-50">{t.shortcut}</span>
              {active && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--accent)]" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
