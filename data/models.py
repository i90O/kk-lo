"""
SQLAlchemy database models for OptionsAgent.
Supports both PostgreSQL (production) and SQLite (local dev).
"""

from datetime import datetime, date, timezone
from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime, Text, Boolean,
    create_engine, Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL, DB_PATH

Base = declarative_base()


class IVHistory(Base):
    """Daily IV snapshots for tracking IV percentile/rank over time.
    Schema matches iv_tracker.py raw SQLite table."""
    __tablename__ = "iv_history"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    atm_iv = Column(Float)          # ATM implied volatility (~30 DTE)
    hv20 = Column(Float)            # 20-day historical volatility
    hv60 = Column(Float)            # 60-day historical volatility
    close_price = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Database initialization ---

_engine = None
_SessionFactory = None


def get_engine():
    """Get SQLAlchemy engine (singleton). Try PostgreSQL if configured, fall back to SQLite."""
    global _engine
    if _engine is not None:
        return _engine

    if DATABASE_URL and "postgresql" in DATABASE_URL:
        try:
            _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with _engine.connect():
                pass  # Connection test
            return _engine
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "PostgreSQL connection failed, falling back to SQLite: %s", e
            )
            _engine = None

    sqlite_url = f"sqlite:///{DB_PATH}"
    _engine = create_engine(sqlite_url)
    return _engine


def get_session():
    """Get a new database session."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory()


def init_db():
    """Create all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    from log import get_logger
    get_logger(__name__).info("Database initialized: %s", engine.url)


if __name__ == "__main__":
    init_db()
