"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { useWebSocket } from "@/lib/websocket";
import TopBar from "@/components/layout/TopBar";
import TabNav from "@/components/layout/TabNav";
import WatchlistGrid from "@/components/dashboard/WatchlistGrid";
import AnalysisView from "@/components/analysis/AnalysisView";
import ScannerView from "@/components/scanner/ScannerView";
import AccountView from "@/components/account/AccountView";
import ChatView from "@/components/chat/ChatView";
import ToastContainer from "@/components/shared/Toast";

export default function Home() {
  const activeTab = useAppStore((s) => s.activeTab);
  const fetchAccount = useAppStore((s) => s.fetchAccount);

  useWebSocket();

  useEffect(() => {
    fetchAccount();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;

      const setTab = useAppStore.getState().setActiveTab;
      switch (e.key) {
        case "1": setTab("dashboard"); break;
        case "2": setTab("analysis"); break;
        case "3": setTab("scanner"); break;
        case "4": setTab("account"); break;
        case "5": setTab("chat"); break;
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <TopBar />
      <TabNav />
      <main className="px-4 py-4 max-w-[1600px] mx-auto">
        {activeTab === "dashboard" && <WatchlistGrid />}
        {activeTab === "analysis" && <AnalysisView />}
        {activeTab === "scanner" && <ScannerView />}
        {activeTab === "account" && <AccountView />}
        {activeTab === "chat" && <ChatView />}
      </main>
      <ToastContainer />
    </div>
  );
}
