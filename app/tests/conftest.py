"""
Pytest configuration and fixtures for testing.

This module provides comprehensive test fixtures for:
- Database setup with SQLite in-memory
- Test client with dependency overrides
- Sample test data factories
- Mock external dependencies (yfinance, Celery)
"""

import pytest
from datetime import date, datetime
from typing import Generator, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd

from app.db.session import Base, get_db
from app.main import app
from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData


# ===========================
# Database Fixtures
# ===========================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create an in-memory SQLite database engine for testing.

    Uses StaticPool to maintain single connection across threads.
    Database is created fresh for each test function.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create a database session with automatic rollback.

    Each test gets a clean session that is rolled back after the test.
    This ensures test isolation without affecting other tests.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with database dependency override.

    The test client uses the test database session instead of the real one.
    This allows testing API endpoints in isolation.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ===========================
# Test Data Factories
# ===========================

@pytest.fixture
def sample_breakout_data(db_session: Session) -> List[BreakoutData]:
    """
    Create sample breakout data records for testing.

    Returns a list of 5 diverse records covering different scenarios:
    - BREAKOUT with good volume
    - NO_BREAKOUT with average volume
    - BIG_SELL_WICK with low volume
    - RED_CANDLE
    - NO_ENTRY
    """
    test_date = date(2024, 1, 15)

    records = [
        BreakoutData(
            script_name="RELIANCE",
            group_name="NIFTY_50",
            date=test_date,
            open=2400.0,
            high=2450.0,
            low=2390.0,
            close=2445.0,
            previous_high=2420.0,
            volume=5000000,
            cpr=2415.0,
            res1=2440.0,
            res2=2465.0,
            supp1=2390.0,
            supp2=2365.0,
            narrow_gap="Yes",
            breakout_indicator="Breakout",
            candle_indicator="Green candle",
            volume_indicator="Good",
            link="https://example.com/RELIANCE"
        ),
        BreakoutData(
            script_name="TCS",
            group_name="NIFTY_50",
            date=test_date,
            open=3500.0,
            high=3520.0,
            low=3480.0,
            close=3510.0,
            previous_high=3550.0,
            volume=2000000,
            cpr=3500.0,
            res1=3520.0,
            res2=3540.0,
            supp1=3480.0,
            supp2=3460.0,
            narrow_gap="No",
            breakout_indicator="no breakout",
            candle_indicator="Green candle",
            volume_indicator="Average",
            link="https://example.com/TCS"
        ),
        BreakoutData(
            script_name="INFY",
            group_name="NIFTY_50",
            date=test_date,
            open=1500.0,
            high=1550.0,
            low=1490.0,
            close=1505.0,
            previous_high=1520.0,
            volume=500000,
            cpr=1513.0,
            res1=1539.0,
            res2=1565.0,
            supp1=1487.0,
            supp2=1461.0,
            narrow_gap="Yes",
            breakout_indicator="Big Sell Wick",
            candle_indicator="Green candle",
            volume_indicator="Low",
            link="https://example.com/INFY"
        ),
        BreakoutData(
            script_name="HDFC",
            group_name="NIFTY_50",
            date=test_date,
            open=1600.0,
            high=1610.0,
            low=1570.0,
            close=1580.0,
            previous_high=1620.0,
            volume=3000000,
            cpr=1587.0,
            res1=1600.0,
            res2=1613.0,
            supp1=1574.0,
            supp2=1561.0,
            narrow_gap="No",
            breakout_indicator="Red candle",
            candle_indicator="Red candle",
            volume_indicator="Average",
            link="https://example.com/HDFC"
        ),
        BreakoutData(
            script_name="ICICI",
            group_name="NIFTY_50",
            date=test_date,
            open=900.0,
            high=920.0,
            low=895.0,
            close=910.0,
            previous_high=910.0,
            volume=4000000,
            cpr=908.0,
            res1=921.0,
            res2=934.0,
            supp1=895.0,
            supp2=882.0,
            narrow_gap="Yes",
            breakout_indicator="No Entry",
            candle_indicator="Green candle",
            volume_indicator="Good",
            link="https://example.com/ICICI"
        ),
    ]

    for record in records:
        db_session.add(record)
    db_session.commit()

    return records


@pytest.fixture
def large_dataset(db_session: Session) -> List[BreakoutData]:
    """
    Create a large dataset of 500 records for performance testing.

    This fixture is used to test bulk operations and pagination.
    Records have sequential script names (STOCK_001 to STOCK_500).
    """
    test_date = date(2024, 1, 15)
    records = []

    for i in range(1, 501):
        record = BreakoutData(
            script_name=f"STOCK_{i:03d}",
            group_name="NIFTY_500",
            date=test_date,
            open=1000.0 + i,
            high=1050.0 + i,
            low=990.0 + i,
            close=1040.0 + i,
            previous_high=1020.0 + i,
            volume=1000000 + i * 1000,
            cpr=1020.0 + i,
            res1=1035.0 + i,
            res2=1050.0 + i,
            supp1=1005.0 + i,
            supp2=990.0 + i,
            narrow_gap="Yes" if i % 2 == 0 else "No",
            breakout_indicator=["Breakout", "no breakout", "Big Sell Wick", "Red candle", "No Entry"][i % 5],
            candle_indicator=["Green candle", "Red candle", "Doji"][i % 3],
            volume_indicator=["Good", "Average", "Low"][i % 3],
            link=f"https://example.com/STOCK_{i:03d}"
        )
        records.append(record)

    db_session.bulk_save_objects(records)
    db_session.commit()

    return records


@pytest.fixture
def sample_master_data(db_session: Session) -> List[MasterBOData]:
    """
    Create sample master breakout data for archive testing.

    Returns 3 records in master table for testing archive operations.
    """
    test_date = date(2024, 1, 10)

    records = [
        MasterBOData(
            script_name="RELIANCE",
            group_name="NIFTY_50",
            date=test_date,
            open=2350.0,
            high=2380.0,
            low=2340.0,
            close=2375.0,
            previous_high=2370.0,
            volume=4500000,
            cpr=2357.0,
            res1=2374.0,
            res2=2391.0,
            supp1=2340.0,
            supp2=2323.0,
            narrow_gap="Yes",
            breakout_indicator="Breakout",
            candle_indicator="Green candle",
            volume_indicator="Good",
            link="https://example.com/RELIANCE"
        ),
        MasterBOData(
            script_name="TCS",
            group_name="NIFTY_50",
            date=test_date,
            open=3450.0,
            high=3470.0,
            low=3440.0,
            close=3465.0,
            previous_high=3480.0,
            volume=1800000,
            cpr=3453.0,
            res1=3466.0,
            res2=3479.0,
            supp1=3440.0,
            supp2=3427.0,
            narrow_gap="No",
            breakout_indicator="no breakout",
            candle_indicator="Green candle",
            volume_indicator="Average",
            link="https://example.com/TCS"
        ),
        MasterBOData(
            script_name="INFY",
            group_name="NIFTY_50",
            date=test_date,
            open=1480.0,
            high=1495.0,
            low=1475.0,
            close=1490.0,
            previous_high=1500.0,
            volume=600000,
            cpr=1487.0,
            res1=1494.0,
            res2=1501.0,
            supp1=1480.0,
            supp2=1473.0,
            narrow_gap="Yes",
            breakout_indicator="no breakout",
            candle_indicator="Green candle",
            volume_indicator="Low",
            link="https://example.com/INFY"
        ),
    ]

    for record in records:
        db_session.add(record)
    db_session.commit()

    return records


# ===========================
# Mock External Dependencies
# ===========================

@pytest.fixture
def mock_yfinance():
    """
    Mock yfinance data fetching to avoid external API calls.

    Returns a sample DataFrame with OHLCV data for testing.
    """
    sample_data = pd.DataFrame({
        'Open': [2400.0, 2410.0, 2405.0, 2420.0, 2430.0, 2425.0, 2435.0, 2440.0, 2445.0, 2450.0, 2445.0],
        'High': [2420.0, 2425.0, 2415.0, 2435.0, 2445.0, 2440.0, 2450.0, 2455.0, 2460.0, 2465.0, 2450.0],
        'Low': [2390.0, 2395.0, 2400.0, 2410.0, 2420.0, 2415.0, 2425.0, 2430.0, 2435.0, 2440.0, 2435.0],
        'Close': [2410.0, 2415.0, 2405.0, 2430.0, 2440.0, 2435.0, 2445.0, 2450.0, 2455.0, 2445.0, 2445.0],
        'Volume': [4000000, 4200000, 3800000, 4500000, 5000000, 4800000, 5200000, 5500000, 5800000, 6000000, 5000000]
    }, index=pd.date_range('2024-01-01', periods=11, freq='D').strftime('%Y-%m-%d'))

    with patch('app.services.fetch_scripts.fetch_script_historical_data', return_value=sample_data):
        yield sample_data


@pytest.fixture
def mock_celery_task():
    """
    Mock Celery task for synchronous testing.

    This fixture allows testing task logic without running Celery workers.
    Tasks execute synchronously and return immediately.
    """
    mock_task = MagicMock()
    mock_task.id = "test-task-id-12345"
    mock_task.status = "SUCCESS"
    mock_task.result = {"status": "SUCCESS", "message": "Test completed"}

    with patch('celery.result.AsyncResult', return_value=mock_task):
        yield mock_task


# ===========================
# Test Configuration
# ===========================

@pytest.fixture(autouse=True)
def reset_suspension_flag():
    """
    Reset suspension flag before each test.

    This ensures tests don't interfere with each other via shared state.
    """
    from app.utils.suspension_flag import SUSPEND_ANALYSIS
    SUSPEND_ANALYSIS.clear()
    yield
    SUSPEND_ANALYSIS.clear()


@pytest.fixture
def test_date():
    """Provide a consistent test date for all tests."""
    return date(2024, 1, 15)


@pytest.fixture
def test_date_str():
    """Provide test date as string in YYYY-MM-DD format."""
    return "2024-01-15"
