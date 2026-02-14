import { create } from "zustand";
import { api } from "./api";
import type {
  TabId, TechnicalData, IVData, ChainResponse,
  NewsResponse, ScannerResponse, AccountData, Position,
  StrategyResponse, ChatMessage, ToastMessage, PriceBar,
} from "./types";

export const WATCHLIST = [
  "SPY", "QQQ", "TSLA", "AAPL", "NVDA", "META",
  "AMZN", "AMD", "MSFT", "GOOGL", "NFLX", "COIN",
];

let toastIdCounter = 0;

interface AppState {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  selectedTicker: string;

  // Dashboard
  watchlistData: Record<string, TechnicalData>;
  watchlistLoading: boolean;

  // Analysis
  technicalData: TechnicalData | null;
  ivData: IVData | null;
  chainData: ChainResponse | null;
  newsData: NewsResponse | null;
  strategyData: StrategyResponse | null;
  priceHistory: PriceBar[] | null;

  // Scanner
  scannerData: ScannerResponse | null;

  // Account
  accountData: AccountData | null;
  positionsData: Position[] | null;

  // Chat
  chatMessages: ChatMessage[];
  chatLoading: boolean;

  // Toasts
  toasts: ToastMessage[];

  // Loading
  loading: Record<string, boolean>;

  // Actions
  loadWatchlist: () => Promise<void>;
  selectTicker: (ticker: string) => Promise<void>;
  searchAndSelectTicker: (ticker: string) => Promise<void>;
  fetchPriceHistory: (ticker: string, period?: string) => Promise<void>;
  fetchTechnical: (ticker: string) => Promise<void>;
  fetchIV: (ticker: string) => Promise<void>;
  fetchChain: (ticker: string) => Promise<void>;
  fetchNews: (ticker: string) => Promise<void>;
  fetchStrategy: (ticker: string) => Promise<void>;
  fetchScanner: () => Promise<void>;
  fetchAccount: () => Promise<void>;
  fetchPositions: () => Promise<void>;
  sendChat: (message: string) => Promise<void>;
  clearChat: () => void;
  addToast: (type: ToastMessage["type"], message: string) => void;
  removeToast: (id: string) => void;
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
  strategyData: null,
  priceHistory: null,
  scannerData: null,
  accountData: null,
  positionsData: null,
  chatMessages: [],
  chatLoading: false,
  toasts: [],
  loading: {},

  loadWatchlist: async () => {
    set({ watchlistLoading: true });
    try {
      const results = await Promise.allSettled(
        WATCHLIST.map((t) => api.technical(t))
      );
      const data: Record<string, TechnicalData> = {};
      results.forEach((r, i) => {
        if (r.status === "fulfilled") data[WATCHLIST[i]] = r.value;
      });
      set({ watchlistData: data, watchlistLoading: false });
    } catch {
      set({ watchlistLoading: false });
      get().addToast("error", "Failed to load watchlist data");
    }
  },

  selectTicker: async (ticker) => {
    set({
      selectedTicker: ticker,
      activeTab: "analysis",
      technicalData: null,
      ivData: null,
      chainData: null,
      newsData: null,
      strategyData: null,
      priceHistory: null,
    });
    const store = get();
    await Promise.allSettled([
      store.fetchTechnical(ticker),
      store.fetchIV(ticker),
      store.fetchNews(ticker),
      store.fetchPriceHistory(ticker),
    ]);
    store.fetchStrategy(ticker);
  },

  searchAndSelectTicker: async (ticker) => {
    const t = ticker.trim().toUpperCase();
    if (!t) return;
    get().selectTicker(t);
  },

  fetchPriceHistory: async (ticker, period = "6mo") => {
    set((s) => ({ loading: { ...s.loading, priceHistory: true } }));
    try {
      const data = await api.priceHistory(ticker, period);
      set({ priceHistory: data.data || [] });
    } catch {
      // Price history optional, fail silently
    }
    set((s) => ({ loading: { ...s.loading, priceHistory: false } }));
  },

  fetchTechnical: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, technical: true } }));
    try {
      const data = await api.technical(ticker);
      set({ technicalData: data });
    } catch {
      get().addToast("error", `Failed to load technical data for ${ticker}`);
    }
    set((s) => ({ loading: { ...s.loading, technical: false } }));
  },

  fetchIV: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, iv: true } }));
    try {
      const data = await api.iv(ticker);
      set({ ivData: data });
    } catch {
      get().addToast("error", `Failed to load IV data for ${ticker}`);
    }
    set((s) => ({ loading: { ...s.loading, iv: false } }));
  },

  fetchChain: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, chain: true } }));
    try {
      const data = await api.chain(ticker);
      set({ chainData: data });
    } catch {
      get().addToast("error", `Failed to load options chain for ${ticker}`);
    }
    set((s) => ({ loading: { ...s.loading, chain: false } }));
  },

  fetchNews: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, news: true } }));
    try {
      const data = await api.news(ticker);
      set({ newsData: data });
    } catch {
      get().addToast("error", `Failed to load news for ${ticker}`);
    }
    set((s) => ({ loading: { ...s.loading, news: false } }));
  },

  fetchStrategy: async (ticker) => {
    set((s) => ({ loading: { ...s.loading, strategy: true } }));
    try {
      const data = await api.strategy(ticker);
      set({ strategyData: data });
    } catch {
      // Strategy endpoint may not exist yet, silently fail
    }
    set((s) => ({ loading: { ...s.loading, strategy: false } }));
  },

  fetchScanner: async () => {
    set((s) => ({ loading: { ...s.loading, scanner: true } }));
    try {
      const data = await api.unusual();
      set({ scannerData: data });
      get().addToast("success", `Scan complete: ${data.total_alerts} alerts found`);
    } catch {
      get().addToast("error", "Scanner failed. Is the backend running?");
    }
    set((s) => ({ loading: { ...s.loading, scanner: false } }));
  },

  fetchAccount: async () => {
    try {
      const data = await api.account();
      set({ accountData: data });
    } catch { /* Backend not running */ }
  },

  fetchPositions: async () => {
    try {
      const data = await api.positions();
      set({ positionsData: data });
    } catch { /* Backend not running */ }
  },

  sendChat: async (message) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}-user`,
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };
    const loadingMsg: ChatMessage = {
      id: `msg-${Date.now()}-loading`,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      loading: true,
    };
    set((s) => ({
      chatMessages: [...s.chatMessages, userMsg, loadingMsg],
      chatLoading: true,
    }));

    try {
      const data = await api.chat(message);
      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: "assistant",
        content: data.response || "No response",
        timestamp: new Date().toISOString(),
      };
      set((s) => ({
        chatMessages: s.chatMessages
          .filter((m) => !m.loading)
          .concat(assistantMsg),
        chatLoading: false,
      }));
    } catch {
      set((s) => ({
        chatMessages: s.chatMessages.filter((m) => !m.loading).concat({
          id: `msg-${Date.now()}-error`,
          role: "assistant",
          content: "⚠️ Failed to get response. Make sure the backend is running (`uvicorn api.main:app --port 8000`) and ANTHROPIC_API_KEY is set in `.env`.",
          timestamp: new Date().toISOString(),
        }),
        chatLoading: false,
      }));
    }
  },

  clearChat: () => set({ chatMessages: [] }),

  addToast: (type, message) => {
    const id = `toast-${++toastIdCounter}`;
    const toast: ToastMessage = { id, type, message, duration: 4000 };
    set((s) => ({ toasts: [...s.toasts, toast] }));
    setTimeout(() => get().removeToast(id), toast.duration);
  },

  removeToast: (id) => {
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
  },
}));
