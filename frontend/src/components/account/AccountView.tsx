"use client";

import { useEffect } from "react";
import { useAppStore } from "@/lib/store";
import AccountCards from "./AccountCards";
import PositionsTable from "./PositionsTable";

export default function AccountView() {
  const fetchAccount = useAppStore((s) => s.fetchAccount);
  const fetchPositions = useAppStore((s) => s.fetchPositions);

  useEffect(() => {
    fetchAccount();
    fetchPositions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-200">Paper Trading Account</h2>
      <AccountCards />
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Open Positions</h3>
        <PositionsTable />
      </div>
    </div>
  );
}
