import { create } from "zustand";
import { api } from "./api";
import type {
  TabId, TechnicalData, IVData, ChainResponse,
  NewsResponse, ScannerResponse, AccountData, Position,
} from "./types";

const WATCHLIST = [
  "SPY", "QQQ", "TSLA", "AAPL", "NVDA", "META",
  "AMZN", "AMD", "MSFT", "GOOGL", "NFLX", "COIN",
];

interface AppState {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  selectedTicker: string;

  watchlistData: Record<string, TechnicalData>;
  watchlistLoading: boolean;

  technicalData: TechnicalData | null;
  ivData: IVData | null;
  chainData: ChainResponse | null;
  newsData: NewsResponse | null;
  scannerData: ScannerResponse | null;
  accountData: AccountData | null;
  positionsData: Position[] | null;

  loading: Record<string, boolean>;

  loadWatchlist: () => Promise<void>;
  selectTicker: (ticker: string) => Promise<void>;
  fetchTechnical: (ticker: string) => Promise<void>;
  fetchIV: (ticker: string) => Promise<void>;
  fetchChain: (ticker: string) => Promise<void>;
  fetchNews: (ticker: string) => Promise<void>;
  fetchScanner: () => Promise<void>;
  fetchAccount: () => Promise<void>;
  fetchPositions: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  activeTab: "dashboard",
  setActiveTab: (tab) => set({ activeTab: tab }),
  selectedTicker: "TSLA",

  watchlistData: {},
  watchlistLoading: false,
  technicalData: null,
  ivData: null,
  chainData: null,
  newsData: null,
  scannerData: null,
  accountData: null,
  positionsData: null,
  loading: {},

  loadWatchlist: async () => {
    set({ watchlistLoading: true });
    const results = await Promise.allSettled(
      WATCHLIST.map((t) => api.technical(t))
    );
    const data: Record<string, TechnicalData> = {};
    results.forEach((r, i) => {
      if (r.status === "fulfilled") data[WATCHLIST[i]] = r.value;
    });
    set({ watchlistData: data, watchlistLoading: false });
  },

  selectTicker: async (ticker) => {
    set({
      selectedTicker: ticker,
      activeTab: "analysis",
      technicalData: null,
      ivData: null,
      chainData: null,
      newsData: null,
    });
    const store = get();
    await Promise.allSettled([
      store.fetchTechnical(ticker),
      store.fetchIV(ticker),
      store.fetchNews(ticker),
    ]);
  },

  fetchTechnical: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, technical: true } }));
    try {
      const data = await api.technical(ticker);
      set({ technicalData: data });
    } catch { /* ignore */ }
    set((s) => ({ loading: { ...s.loading, technical: false } }));
  },

  fetchIV: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, iv: true } }));
    try {
      const data = await api.iv(ticker);
      set({ ivData: data });
    } catch { /* ignore */ }
    set((s) => ({ loading: { ...s.loading, iv: false } }));
  },

  fetchChain: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, chain: true } }));
    try {
      const data = await api.chain(ticker);
      set({ chainData: data });
    } catch { /* ignore */ }
    set((s) => ({ loading: { ...s.loading, chain: false } }));
  },

  fetchNews: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, news: true } }));
    try {
      const data = await api.news(ticker);
      set({ newsData: data });
    } catch { /* ignore */ }
    set((s) => ({ loading: { ...s.loading, news: false } }));
  },

  fetchScanner: async () => {
    set((s) => ({ loading: { ...s.loading, scanner: true } }));
    try {
      const data = await api.unusual();
      set({ scannerData: data });
    } catch { /* ignore */ }
    set((s) => ({ loading: { ...s.loading, scanner: false } }));
  },

  fetchAccount: async () => {
    try {
      const data = await api.account();
      set({ accountData: data });
    } catch { /* ignore */ }
  },

  fetchPositions: async () => {
    try {
      const data = await api.positions();
      set({ positionsData: data });
    } catch { /* ignore */ }
  },
}));
