"""OptionsAgent configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
DATABASE_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# --- Watchlist ---
WATCHLIST = [
    "SPY", "QQQ", "TSLA", "AAPL", "NVDA", "META",
    "AMZN", "AMD", "MSFT", "GOOGL", "NFLX", "COIN",
]

# --- Default analysis parameters ---
DEFAULT_ACCOUNT_SIZE = 10000
DEFAULT_RISK_LEVEL = "moderate"  # conservative / moderate / aggressive
DEFAULT_DTE = 30  # days to expiry target

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DB_PATH = os.path.join(DATA_DIR, "iv_history.db")
WATCHLIST_PATH = os.path.join(DATA_DIR, "watchlist.json")

# --- Request settings ---
REQUEST_DELAY = 0.5
