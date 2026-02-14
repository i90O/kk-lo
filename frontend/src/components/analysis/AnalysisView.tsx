"use client";

import StockHeader from "./StockHeader";
import PriceChart from "./PriceChart";
import TechnicalPanel from "./TechnicalPanel";
import IVPanel from "./IVPanel";
import StrategyPanel from "./StrategyPanel";
import OptionsChainTable from "./OptionsChainTable";
import NewsFeed from "./NewsFeed";

export default function AnalysisView() {
  return (
    <div className="space-y-4">
      <StockHeader />

      {/* Price Chart - full width */}
      <PriceChart />

      {/* Row: Technical + IV + Strategy */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <TechnicalPanel />
        <IVPanel />
        <StrategyPanel />
      </div>

      {/* Options Chain - full width */}
      <OptionsChainTable />

      {/* News - 3 column compact */}
      <NewsFeed />
    </div>
  );
}
