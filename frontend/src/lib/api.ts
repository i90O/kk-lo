const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  analyze: (ticker: string, question?: string) =>
    fetchAPI("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ ticker, question }),
    }),

  chat: (message: string) =>
    fetchAPI("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  technical: (ticker: string) => fetchAPI(`/api/technical/${ticker}`),

  iv: (ticker: string) => fetchAPI(`/api/iv/${ticker}`),

  news: (ticker: string) => fetchAPI(`/api/news/${ticker}`),

  unusual: (tickers?: string) =>
    fetchAPI(`/api/scanner/unusual${tickers ? `?tickers=${tickers}` : ""}`),

  priceHistory: (ticker: string, period: string = "6mo") =>
    fetchAPI(`/api/price-history/${ticker}?period=${period}`),

  chain: (ticker: string, type?: string) =>
    fetchAPI(`/api/chain/${ticker}${type ? `?contract_type=${type}` : ""}`),

  account: () => fetchAPI("/api/account"),

  positions: () => fetchAPI("/api/positions"),

  strategy: (ticker: string, riskLevel?: string, accountSize?: number) =>
    fetchAPI(
      `/api/strategy/${ticker}?risk_level=${riskLevel || "moderate"}&account_size=${accountSize || 10000}`
    ),
};

export function getWSUrl(): string {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ws/alerts`;
}
