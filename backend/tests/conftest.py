"""
Test configuration and fixtures for Breakout Screener V2
"""

import asyncio
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from breakout_screener.core.database import Base
from breakout_screener.models.analysis import AnalysisSession, PerformanceMetrics
from breakout_screener.models.breakout_data import BreakoutData
from breakout_screener.models.enums import (
    AnalysisStatusEnum,
    BreakoutStatusEnum,
    PerformanceMetricTypeEnum,
    PivotTypeEnum,
)
from breakout_screener.models.master_data import MasterBreakoutData
from breakout_screener.models.stock import Stock
from breakout_screener.repositories.analysis import (
    AnalysisSessionRepository,
    PerformanceMetricsRepository,
)
from breakout_screener.repositories.breakout_data import BreakoutDataRepository
from breakout_screener.repositories.master_data import MasterBreakoutDataRepository
from breakout_screener.repositories.stock import StockRepository


# Test database URL - using in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with AsyncSession(test_engine) as session:
        yield session


@pytest_asyncio.fixture
async def stock_repository(test_session) -> StockRepository:
    """Create stock repository for testing"""
    return StockRepository(test_session)


@pytest_asyncio.fixture
async def breakout_data_repository(test_session) -> BreakoutDataRepository:
    """Create breakout data repository for testing"""
    return BreakoutDataRepository(test_session)


@pytest_asyncio.fixture
async def master_data_repository(test_session) -> MasterBreakoutDataRepository:
    """Create master data repository for testing"""
    return MasterBreakoutDataRepository(test_session)


@pytest_asyncio.fixture
async def analysis_session_repository(test_session) -> AnalysisSessionRepository:
    """Create analysis session repository for testing"""
    return AnalysisSessionRepository(test_session)


@pytest_asyncio.fixture
async def performance_metrics_repository(test_session) -> PerformanceMetricsRepository:
    """Create performance metrics repository for testing"""
    return PerformanceMetricsRepository(test_session)


# Test data fixtures
@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    return {
        "symbol": "TESTSTOCK",
        "company_name": "Test Stock Company",
        "industry": "Technology",
        "sector": "IT Services",
        "market_cap": 10000000000,
        "is_active": True,
        "listing_date": date(2020, 1, 1),
        "stock_group": "A",
        "face_value": 10.0,
        "isin": "INE123456789",
    }


@pytest.fixture
def sample_breakout_data():
    """Sample breakout data for testing"""
    return {
        "trade_date": date(2023, 12, 1),
        "open_price": 100.0,
        "high_price": 110.0,
        "low_price": 95.0,
        "close_price": 105.0,
        "volume": 1000000,
        "tc": 107.5,
        "bc": 97.5,
        "pivot": 102.5,
        "r1": 112.5,
        "r2": 122.5,
        "r3": 132.5,
        "s1": 92.5,
        "s2": 82.5,
        "s3": 72.5,
        "breakout_status": BreakoutStatusEnum.UPSIDE_BREAKOUT,
        "pivot_type": PivotTypeEnum.BULLISH,
        "is_analyzed": True,
        "analysis_status": AnalysisStatusEnum.COMPLETED,
        "notes": "Test breakout data",
    }


@pytest.fixture
def sample_master_data():
    """Sample master breakout data for testing"""
    return {
        "snapshot_date": date(2023, 12, 1),
        "data_source": "NSE",
        "is_active": True,
        "metadata": {"source": "test", "version": "1.0"},
    }


@pytest.fixture
def sample_analysis_session():
    """Sample analysis session data for testing"""
    return {
        "session_name": "test_session_001",
        "analysis_date": date(2023, 12, 1),
        "start_time": datetime(2023, 12, 1, 9, 0, 0),
        "end_time": datetime(2023, 12, 1, 18, 0, 0),
        "status": AnalysisStatusEnum.COMPLETED,
        "created_by": "test_user",
        "parameters": {"param1": "value1", "param2": "value2"},
        "results": {"accuracy": 0.85, "processed_count": 100},
    }


@pytest.fixture
def sample_performance_metrics():
    """Sample performance metrics data for testing"""
    return {
        "metric_type": PerformanceMetricTypeEnum.ACCURACY,
        "metric_name": "Model Accuracy",
        "metric_value": 0.85,
        "metric_date": date(2023, 12, 1),
        "metadata": {"model_version": "1.0", "dataset_size": 1000},
    }


@pytest_asyncio.fixture
async def sample_stock(stock_repository: StockRepository, sample_stock_data):
    """Create a sample stock for testing"""
    stock = await stock_repository.create(sample_stock_data)
    return stock


@pytest_asyncio.fixture
async def sample_breakout(
    breakout_data_repository: BreakoutDataRepository,
    sample_stock: Stock,
    sample_breakout_data,
):
    """Create a sample breakout data for testing"""
    breakout_data = sample_breakout_data.copy()
    breakout_data["stock_id"] = sample_stock.id
    breakout = await breakout_data_repository.create(breakout_data)
    return breakout


@pytest_asyncio.fixture
async def sample_master(
    master_data_repository: MasterBreakoutDataRepository,
    sample_stock: Stock,
    sample_breakout: BreakoutData,
    sample_master_data,
):
    """Create a sample master breakout data for testing"""
    master_data = sample_master_data.copy()
    master_data["stock_id"] = sample_stock.id
    master_data["breakout_data_id"] = sample_breakout.id
    master = await master_data_repository.create(master_data)
    return master


@pytest_asyncio.fixture
async def sample_session(
    analysis_session_repository: AnalysisSessionRepository,
    sample_analysis_session,
):
    """Create a sample analysis session for testing"""
    session = await analysis_session_repository.create(sample_analysis_session)
    return session


@pytest_asyncio.fixture
async def sample_metrics(
    performance_metrics_repository: PerformanceMetricsRepository,
    sample_session: AnalysisSession,
    sample_performance_metrics,
):
    """Create a sample performance metrics for testing"""
    metrics_data = sample_performance_metrics.copy()
    metrics_data["session_id"] = sample_session.id
    metrics = await performance_metrics_repository.create(metrics_data)
    return metrics


# Utility fixtures
@pytest.fixture
def uuid_generator():
    """Generate random UUIDs for testing"""
    return lambda: uuid4()


@pytest.fixture
def date_generator():
    """Generate test dates"""
    return lambda year=2023, month=12, day=1: date(year, month, day)


@pytest.fixture
def datetime_generator():
    """Generate test datetimes"""
    return lambda year=2023, month=12, day=1, hour=12: datetime(year, month, day, hour)