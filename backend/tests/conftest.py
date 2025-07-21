"""
Test configuration and fixtures for Breakout Screener V2
"""

import asyncio
import sys
from collections.abc import AsyncGenerator, Generator
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from breakout_screener.models.analysis import AnalysisSession
from breakout_screener.models.breakout_data import BreakoutDataV2
from breakout_screener.models.enums import (
    AnalysisStatusEnum,
    BreakoutIndicatorEnum,
    CandleIndicatorEnum,
    PerformanceMetricTypeEnum,
    VolumeIndicatorEnum,
)

# from breakout_screener.models.master_data import MasterBreakoutDataV2
from breakout_screener.models.stock import Stock
from breakout_screener.repositories.analysis import (
    AnalysisSessionRepository,
    PerformanceMetricsRepository,
)
from breakout_screener.repositories.breakout_data import BreakoutDataRepository
from breakout_screener.repositories.master_data import MasterBreakoutDataRepository
from breakout_screener.repositories.stock import StockRepository

# Test database URL - using PostgreSQL test database
TEST_DATABASE_URL = (
    "postgresql+asyncpg://trading_user:tpassword@localhost:5432/trading_db_test"
)


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
    )

    # Tables already exist in test database, just clean data
    async with engine.begin() as conn:
        # Clean up existing data before each test
        await conn.execute(text("TRUNCATE TABLE performance_metrics CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE analysis_sessions CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE master_breakout_data_v2 CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE breakout_data_v2 CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE master_breakout_data CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE breakout_data CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE stocks CASCADE;"))

    yield engine

    # Clean up after test
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE performance_metrics CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE analysis_sessions CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE master_breakout_data_v2 CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE breakout_data_v2 CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE master_breakout_data CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE breakout_data CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE stocks CASCADE;"))

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
    from breakout_screener.models.enums import StockGroupEnum

    return {
        "symbol": "TESTSTOCK",
        "company_name": "Test Stock Company",
        "industry": "Technology",
        "sector": "IT Services",
        "market_cap": 10000000000,
        "is_active": True,
        "listing_date": date(2020, 1, 1),
        "stock_group": StockGroupEnum.NIFTY_50,
        "isin_code": "INE123456789",
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
        "previous_high": 108.0,
        "volume": 1000000,
        "cpr": 102.5,
        "resistance_1": 107.5,
        "resistance_2": 112.5,
        "support_1": 97.5,
        "support_2": 92.5,
        "narrow_gap": False,
        "breakout_indicator": BreakoutIndicatorEnum.BREAKOUT,
        "candle_indicator": CandleIndicatorEnum.BULLISH,
        "volume_indicator": VolumeIndicatorEnum.HIGH_VOLUME,
        "chart_link": "https://example.com/chart",
        "analysis_notes": "Test breakout data",
        "confidence_score": 0.85,
    }


@pytest.fixture
def sample_master_data():
    """Sample master breakout data for testing"""
    return {
        "trade_date": date(2023, 12, 1),
        "open_price": 100.0,
        "high_price": 110.0,
        "low_price": 95.0,
        "close_price": 105.0,
        "volume": 1000000,
        "cpr": 102.5,
        "resistance_1": 107.5,
        "support_1": 97.5,
        "narrow_gap": False,
        "source_table": "test_source",
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
        "metric_metadata": {"model_version": "1.0", "dataset_size": 1000},
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
    sample_breakout: BreakoutDataV2,
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
