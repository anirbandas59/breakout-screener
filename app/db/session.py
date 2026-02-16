import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Connection pool configuration
# For 4 Celery workers + 1 main process = ~5 processes
# Each process needs max 5 concurrent connections
POOL_SIZE = 10           # Normal pool size (2x processes)
MAX_OVERFLOW = 20        # Burst capacity for spikes
POOL_TIMEOUT = 30        # Wait 30s for connection before error
POOL_RECYCLE = 3600      # Recycle connections every hour (prevents stale connections)
POOL_PRE_PING = True     # Verify connection health before use

# SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,
    echo=False,  # Set to True for SQL query debugging
    # Connection arguments for PostgreSQL
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

# Add connection pool event listeners for monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when new connection is created"""
    logging.debug("Database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool"""
    logging.debug(f"Connection checked out from pool")

# Session Local for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get database session.
    Ensures connection is properly closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pool_stats():
    """
    Get current connection pool statistics for monitoring.
    Useful for /health endpoint.

    Returns:
        dict: Pool statistics including size, checked in/out, overflow
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow()
    }
