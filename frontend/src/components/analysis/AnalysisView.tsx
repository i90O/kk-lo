"use client";

import StockHeader from "./StockHeader";
import TechnicalPanel from "./TechnicalPanel";
import IVPanel from "./IVPanel";
import OptionsChainTable from "./OptionsChainTable";
import NewsFeed from "./NewsFeed";

export default function AnalysisView() {
  return (
    <div className="space-y-4">
      <StockHeader />
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3">
          <TechnicalPanel />
        </div>
        <div className="lg:col-span-2">
          <IVPanel />
        </div>
      </div>
      <OptionsChainTable />
      <NewsFeed />
    </div>
  );
}
