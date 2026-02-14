"""
SQLAlchemy database models for OptionsAgent.
Supports both PostgreSQL (production) and SQLite (local dev).
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime, Text, Boolean,
    create_engine, Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL, DB_PATH

Base = declarative_base()


class IVHistory(Base):
    """Daily IV snapshots for tracking IV percentile/rank over time."""
    __tablename__ = "iv_history"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    atm_iv_30d = Column(Float)      # 30-day ATM implied volatility
    atm_iv_60d = Column(Float)      # 60-day ATM implied volatility
    hv_20d = Column(Float)          # 20-day historical volatility
    hv_60d = Column(Float)          # 60-day historical volatility
    iv_hv_spread = Column(Float)    # IV - HV spread
    put_call_ratio = Column(Float)
    total_options_volume = Column(Integer)
    close_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_iv_ticker_date", "ticker", "date", unique=True),
    )


class UnusualActivity(Base):
    """Unusual options activity alerts."""
    __tablename__ = "unusual_activity"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    alert_type = Column(String(50))        # VOL_OI_SURGE, HIGH_VOLUME, etc.
    contract_symbol = Column(String(50))
    contract_type = Column(String(4))      # call / put
    strike = Column(Float)
    expiration = Column(Date)
    volume = Column(Integer)
    open_interest = Column(Integer)
    vol_oi_ratio = Column(Float)
    iv = Column(Float)
    premium_flow = Column(Float)
    interpretation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisReport(Base):
    """Cached analysis reports."""
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    report_type = Column(String(20))       # full / quick / daily
    trend = Column(String(10))
    signal_strength = Column(Integer)
    iv_percentile = Column(Float)
    recommended_strategy = Column(String(50))
    report_json = Column(Text)             # full report as JSON
    created_at = Column(DateTime, default=datetime.utcnow)


class TradeLog(Base):
    """Paper/live trade execution log."""
    __tablename__ = "trade_log"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True)
    ticker = Column(String(10), index=True)
    contract_symbol = Column(String(50))
    side = Column(String(4))               # buy / sell
    qty = Column(Integer)
    order_type = Column(String(10))        # market / limit
    limit_price = Column(Float)
    fill_price = Column(Float)
    status = Column(String(20))
    strategy_name = Column(String(50))
    paper = Column(Boolean, default=True)
    submitted_at = Column(DateTime)
    filled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Database initialization ---

def get_engine():
    """Get SQLAlchemy engine. Try PostgreSQL if configured, fall back to SQLite."""
    if DATABASE_URL and "postgresql" in DATABASE_URL:
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect():
                pass  # Connection test
            return engine
        except Exception:
            pass  # PostgreSQL not available, fall back to SQLite
    sqlite_url = f"sqlite:///{DB_PATH}"
    return create_engine(sqlite_url)


def get_session():
    """Get a new database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Create all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    from log import get_logger
    get_logger(__name__).info("Database initialized: %s", engine.url)


if __name__ == "__main__":
    init_db()
