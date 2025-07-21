"""
Database connection and session management for Breakout Screener V2
Using SQLAlchemy 2.0 with async support
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.sql import text

from .config import config
from .logging import get_logger

logger = get_logger(__name__)

# Create declarative base for models
Base = declarative_base()


class DatabaseManager:
    """Database connection manager with async support"""

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

    async def initialize(self) -> None:
        """Initialize database engine and session factory"""
        try:
            # Create async engine with appropriate pool settings
            engine_kwargs = {
                "echo": config.DEBUG,  # Log SQL queries in debug mode
                "future": True,
            }

            # Add pool settings only for production (QueuePool)
            if config.is_production():
                engine_kwargs.update(
                    {
                        "pool_size": config.CONNECTION_POOL_SIZE,
                        "max_overflow": config.CONNECTION_POOL_MAX_OVERFLOW,
                        "pool_timeout": config.CONNECTION_POOL_TIMEOUT,
                        "pool_recycle": config.CONNECTION_POOL_RECYCLE,
                        "pool_pre_ping": True,
                        "poolclass": QueuePool,
                    }
                )
            else:
                # Development uses NullPool (no connection pooling)
                engine_kwargs["poolclass"] = NullPool

            self._engine = create_async_engine(config.DATABASE_URL, **engine_kwargs)

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Test connection
            await self.health_check()

            logger.info(
                "Database connection initialized successfully",
                url=config.DATABASE_URL.split("@")[1]
                if "@" in config.DATABASE_URL
                else config.DATABASE_URL,
            )

        except Exception as e:
            logger.error("Failed to initialize database connection", error=str(e))
            raise

    async def close(self) -> None:
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")

    @property
    def engine(self) -> AsyncEngine:
        """Get database engine"""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker:
        """Get session factory"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory

    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False

    def get_session(self) -> AsyncSession:
        """Get database session"""
        return self.session_factory()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session for FastAPI
    """
    session = db_manager.session_factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        await session.close()


def get_db_session() -> AsyncSession:
    """Get database session for direct use"""
    return db_manager.get_session()


# Note: Async engine event listeners are not supported in SQLAlchemy 2.0
# Event listeners would need to be added to the sync_engine if needed
# For now, we'll handle SQL logging through other means


class DatabaseSession:
    """Context manager for database sessions"""

    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self.session = db_manager.get_session()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
                logger.error(
                    "Session rolled back due to exception",
                    exception_type=exc_type.__name__ if exc_type else None,
                )
            else:
                await self.session.commit()

            await self.session.close()


class TransactionSession:
    """Context manager for database transactions"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transaction = None

    async def __aenter__(self) -> AsyncSession:
        self.transaction = await self.session.begin()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.transaction.rollback()
            logger.error(
                "Transaction rolled back",
                exception_type=exc_type.__name__ if exc_type else None,
            )
        else:
            await self.transaction.commit()
            logger.debug("Transaction committed")


# Database utilities
async def execute_raw_sql(query: str, parameters: dict = None) -> any:
    """Execute raw SQL query"""
    async with DatabaseSession() as session:
        result = await session.execute(text(query), parameters or {})
        return result


async def check_table_exists(table_name: str) -> bool:
    """Check if table exists in database"""
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = :table_name
    );
    """
    try:
        result = await execute_raw_sql(query, {"table_name": table_name})
        return result.scalar()
    except Exception as e:
        logger.error("Failed to check table existence", table=table_name, error=str(e))
        return False


async def get_table_row_count(table_name: str) -> int:
    """Get row count for table"""
    query = f"SELECT COUNT(*) FROM {table_name}"
    try:
        result = await execute_raw_sql(query)
        return result.scalar()
    except Exception as e:
        logger.error("Failed to get table row count", table=table_name, error=str(e))
        return 0
