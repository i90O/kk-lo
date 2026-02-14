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
      <AccountCards />
      <PositionsTable />
    </div>
  );
}
