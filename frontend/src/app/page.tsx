"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import TopBar from "@/components/layout/TopBar";
import TabNav from "@/components/layout/TabNav";
import WatchlistGrid from "@/components/dashboard/WatchlistGrid";
import AnalysisView from "@/components/analysis/AnalysisView";
import ScannerView from "@/components/scanner/ScannerView";
import AccountView from "@/components/account/AccountView";

export default function Home() {
  const activeTab = useAppStore((s) => s.activeTab);
  const fetchAccount = useAppStore((s) => s.fetchAccount);

  useEffect(() => {
    fetchAccount();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <TopBar />
      <TabNav />
      <main className="px-4 py-4 max-w-[1600px] mx-auto">
        {activeTab === "dashboard" && <WatchlistGrid />}
        {activeTab === "analysis" && <AnalysisView />}
        {activeTab === "scanner" && <ScannerView />}
        {activeTab === "account" && <AccountView />}
      </main>
    </div>
  );
}
