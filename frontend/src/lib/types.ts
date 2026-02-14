// API response types matching backend exactly

export interface TechnicalData {
  ticker: string;
  current_price: number;
  change: number;
  change_pct: number;
  sma20: number | null;
  sma50: number | null;
  sma200: number | null;
  trend: "bullish" | "bearish" | "neutral" | "unknown";
  rsi: number | null;
  rsi_signal: "overbought" | "oversold" | "neutral";
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  macd_cross: "bullish_crossover" | "bearish_crossover" | "neutral";
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  bb_position: string;
  stoch_k: number | null;
  stoch_d: number | null;
  atr: number | null;
  atr_pct: number | null;
  volume: number;
  volume_sma20: number;
  volume_ratio: number;
  support_20d: number;
  resistance_20d: number;
  signal: "bullish" | "bearish" | "neutral";
  strength: number;
}

export interface IVData {
  ticker: string;
  current_iv: number | null;
  iv_percentile: number | null;
  iv_rank: number | null;
  iv_min?: number | null;
  iv_max?: number | null;
  data_points: number;
  message?: string;
}

export interface UnusualAlert {
  ticker: string;
  type: string;
  contract?: string;
  side?: string;
  strike?: number;
  expiration?: string;
  dte?: number;
  volume?: number;
  open_interest?: number;
  vol_oi_ratio?: number;
  iv?: number;
  mid_price?: number;
  premium_flow: number;
  interpretation: string;
  put_volume?: number;
  call_volume?: number;
  pc_ratio?: number;
}

export interface ScannerResponse {
  scan_time: string;
  total_alerts: number;
  alerts: UnusualAlert[];
}

export interface OptionContract {
  ticker: string;
  type: "call" | "put";
  strike: number;
  expiry: string;
  bid: number | null;
  ask: number | null;
  mid: number | null;
  volume: number;
  open_interest: number;
  iv: number | null;
  delta: number | null;
  gamma: number | null;
  theta: number | null;
  vega: number | null;
  break_even: number | null;
}

export interface ChainResponse {
  underlying: string;
  source: string;
  count: number;
  contracts: OptionContract[];
  summary: {
    total_contracts: number;
    avg_iv: number | null;
  };
  error?: string;
}

export interface NewsArticle {
  title: string;
  published: string;
  source: string;
  url: string;
  description?: string | null;
}

export interface NewsResponse {
  ticker: string;
  news_count: number;
  articles: NewsArticle[];
}

export interface AccountData {
  equity: string;
  cash: string;
  buying_power: string;
  portfolio_value: string;
  status: string;
  error?: string;
}

export interface Position {
  symbol: string;
  qty: string;
  side: string;
  avg_entry_price: string;
  current_price: string;
  unrealized_pl: string;
  unrealized_plpc: string;
  market_value: string;
  error?: string;
}

export type TabId = "dashboard" | "analysis" | "scanner" | "account";
