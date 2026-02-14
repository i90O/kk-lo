"""
OptionsAgent FastAPI Backend.
Provides REST API + WebSocket for the frontend.

Run: uvicorn api.main:app --reload --port 8000
"""

import json
import time
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from log import setup_logging

setup_logging()

ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]

app = FastAPI(title="OptionsAgent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple in-memory rate limiter (30 req/min/IP) ---
_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 30
RATE_WINDOW = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    timestamps = _rate_store[client_ip]
    # Evict old entries
    _rate_store[client_ip] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(_rate_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Max 30 requests per minute."},
        )
    _rate_store[client_ip].append(now)
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
            "/ws/alerts",
        ],
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """Full AI analysis for a ticker."""
    from agents.options_agent import invoke

    question = request.question or f"Analyze options opportunities for {request.ticker}"
    result = invoke(question)
    return {"ticker": request.ticker, "response": result}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Free-form AI chat."""
    from agents.options_agent import invoke

    result = invoke(request.message)
    return {"response": result}


@app.get("/api/scanner/unusual")
async def unusual_activity(tickers: str = Query(None)):
    """Scan for unusual options activity."""
    from tools.unusual_activity import scan_unusual
    from config import WATCHLIST

    ticker_list = tickers.split(",") if tickers else WATCHLIST
    results = scan_unusual(ticker_list)
    return {
        "scan_time": datetime.now().isoformat(),
        "total_alerts": len(results),
        "alerts": results[:20],
    }


@app.get("/api/iv/{ticker}")
async def iv_data(ticker: str):
    """Get IV percentile and rank for a ticker."""
    from tools.iv_tracker import get_iv_percentile, record_daily_iv

    record_daily_iv(ticker)
    data = get_iv_percentile(ticker)
    return data


@app.get("/api/technical/{ticker}")
async def technical_analysis(ticker: str):
    """Get technical analysis for a ticker."""
    from tools.technical import full_technical_analysis

    result = full_technical_analysis(ticker)
    return result


@app.get("/api/news/{ticker}")
async def news(ticker: str, limit: int = Query(10)):
    """Get news for a ticker."""
    from tools.news_sentiment import analyze_news_sentiment

    result = analyze_news_sentiment.invoke({"ticker": ticker, "limit": limit})
    return result


@app.get("/api/account")
async def account():
    """Get Alpaca paper trading account info."""
    from tools.trade_executor import get_account_info

    result = get_account_info.invoke({})
    return result


@app.get("/api/positions")
async def positions():
    """Get current positions."""
    from tools.trade_executor import get_positions

    result = get_positions.invoke({})
    return result


@app.get("/api/chain/{ticker}")
async def options_chain(
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


# --- WebSocket for real-time alerts ---

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass


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
