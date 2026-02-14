"""
OptionsAgent FastAPI Backend.
Provides REST API + WebSocket for the frontend.

Run: uvicorn api.main:app --reload --port 8000
"""

import time
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from log import setup_logging

setup_logging()

import os

_extra_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
ALLOWED_ORIGINS = [
    "http://localhost:3000", "http://localhost:3002",
    "http://localhost:3003", "http://localhost:5173",
    "https://frontend-pi-five-89.vercel.app",
    "https://frontend-d4ufefh6r-kks-projects-19b0a2b5.vercel.app",
] + [o.strip() for o in _extra_origins if o.strip()]

app = FastAPI(title="OptionsAgent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple in-memory rate limiter (30 req/min/IP) ---
_rate_store: dict[str, list[float]] = defaultdict(list)
_last_prune: float = 0.0
RATE_LIMIT = 30
RATE_WINDOW = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    # Evict old entries for this IP
    _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < RATE_WINDOW]
    if len(_rate_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Max 30 requests per minute."},
        )
    _rate_store[client_ip].append(now)
    # Prune stale IPs every 5 minutes
    global _last_prune
    if now - _last_prune > 300:
        _last_prune = now
        stale = [ip for ip, ts in _rate_store.items() if not ts or now - ts[-1] > RATE_WINDOW]
        for ip in stale:
            del _rate_store[ip]
    return await call_next(request)


# --- Request/Response Models ---

class AnalyzeRequest(BaseModel):
    ticker: str
    question: str | None = None
    account_size: float = 10000
    risk_level: str = "moderate"


class ChatRequest(BaseModel):
    message: str


# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "name": "OptionsAgent API",
        "version": "0.2.0",
        "status": "running",
        "endpoints": [
            "/api/analyze",
            "/api/chat",
            "/api/scanner/unusual",
            "/api/iv/{ticker}",
            "/api/technical/{ticker}",
            "/api/news/{ticker}",
            "/api/account",
            "/api/positions",
            "/api/strategy/{ticker}",
            "/ws/alerts",
        ],
    }


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    """Full AI analysis for a ticker."""
    from agents.options_agent import invoke

    question = request.question or f"Analyze options opportunities for {request.ticker}"
    result = invoke(question)
    return {"ticker": request.ticker, "response": result}


@app.post("/api/chat")
def chat(request: ChatRequest):
    """Free-form AI chat."""
    from agents.options_agent import invoke

    result = invoke(request.message)
    return {"response": result}


@app.get("/api/scanner/unusual")
def unusual_activity(tickers: str = Query(None)):
    """Scan for unusual options activity."""
    from tools.unusual_activity import scan_unusual
    from config import WATCHLIST

    ticker_list = tickers.split(",")[:20] if tickers else WATCHLIST
    results = scan_unusual(ticker_list)
    return {
        "scan_time": datetime.now().isoformat(),
        "total_alerts": len(results),
        "alerts": results[:20],
    }


@app.get("/api/iv/{ticker}")
def iv_data(ticker: str):
    """Get IV percentile and rank for a ticker."""
    from tools.iv_tracker import get_iv_percentile, record_daily_iv

    record_daily_iv(ticker)
    data = get_iv_percentile(ticker)
    return data


@app.get("/api/technical/{ticker}")
def technical_analysis(ticker: str):
    """Get technical analysis for a ticker."""
    from tools.technical import full_technical_analysis

    result = full_technical_analysis(ticker)
    return result


@app.get("/api/news/{ticker}")
def news(ticker: str, limit: int = Query(10)):
    """Get news for a ticker."""
    from tools.news_sentiment import analyze_news_sentiment

    result = analyze_news_sentiment.invoke({"ticker": ticker, "limit": limit})
    return result


@app.get("/api/account")
def account():
    """Get Alpaca paper trading account info."""
    from tools.trade_executor import get_account_info

    result = get_account_info.invoke({})
    return result


@app.get("/api/positions")
def positions():
    """Get current positions."""
    from tools.trade_executor import get_positions

    result = get_positions.invoke({})
    return result


@app.get("/api/price-history/{ticker}")
def price_history(ticker: str, period: str = Query("6mo")):
    """Get OHLCV price history for charts."""
    from tools.market_data import get_stock_data

    df = get_stock_data(ticker, period)
    if df.empty:
        return {"ticker": ticker, "period": period, "data": []}

    records = []
    for date, row in df.iterrows():
        records.append({
            "time": date.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2) if row["Open"] is not None else None,
            "high": round(row["High"], 2) if row["High"] is not None else None,
            "low": round(row["Low"], 2) if row["Low"] is not None else None,
            "close": round(row["Close"], 2) if row["Close"] is not None else None,
            "volume": int(row["Volume"]) if row["Volume"] is not None else 0,
        })
    return {"ticker": ticker, "period": period, "count": len(records), "data": records}


@app.get("/api/chain/{ticker}")
def options_chain(
    ticker: str,
    contract_type: str = Query(None),
    expiration_gte: str = Query(None),
    expiration_lte: str = Query(None),
):
    """Get options chain for a ticker."""
    from tools.options_chain import scan_options_chain

    params = {"ticker": ticker}
    if contract_type:
        params["contract_type"] = contract_type
    if expiration_gte:
        params["expiration_gte"] = expiration_gte
    if expiration_lte:
        params["expiration_lte"] = expiration_lte

    result = scan_options_chain.invoke(params)
    return result


@app.get("/api/strategy/{ticker}")
def strategy_recommendation(
    ticker: str,
    risk_level: str = Query("moderate"),
    account_size: float = Query(10000),
    dte: int = Query(30),
):
    """Get strategy recommendations based on technical + IV analysis."""
    from tools.technical import full_technical_analysis
    from tools.iv_tracker import get_iv_percentile, record_daily_iv
    from tools.strategy import recommend_strategies

    # Get current analysis
    tech = full_technical_analysis(ticker)
    record_daily_iv(ticker)
    iv = get_iv_percentile(ticker)

    current_price = tech.get("current_price", 0)
    trend = tech.get("trend", "neutral")
    iv_percentile = iv.get("iv_percentile")
    atr = tech.get("atr")

    strategies = recommend_strategies(
        ticker=ticker,
        current_price=current_price,
        trend=trend,
        iv_percentile=iv_percentile,
        days_to_expiry=dte,
        risk_level=risk_level,
        account_size=account_size,
        atr=atr,
    )

    return {
        "ticker": ticker,
        "trend": trend,
        "iv_percentile": iv_percentile,
        "strategies": strategies,
    }


# --- WebSocket for real-time alerts ---

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        try:
            self.active.remove(ws)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@app.websocket("/ws/alerts")
async def alerts_websocket(ws: WebSocket):
    """Real-time alerts WebSocket."""
    # Basic origin check
    origin = ws.headers.get("origin", "")
    if origin and origin not in ALLOWED_ORIGINS:
        await ws.close(code=1008)
        return
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Client can send commands like {"action": "subscribe", "tickers": ["TSLA"]}
            await ws.send_json({"status": "received", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
