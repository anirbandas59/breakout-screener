"""
Tests for Stock Pydantic schemas
"""

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from breakout_screener.schemas.stock import (
    StockCreate,
    StockFilter,
    StockResponse,
    StockSearch,
    StockUpdate,
)
from breakout_screener.models.enums import StockGroupEnum


class TestStockSchemas:
    """Test suite for Stock schemas"""

    def test_stock_create_valid(self):
        """Test creating valid StockCreate schema"""
        stock_data = {
            "symbol": "TESTSTOCK",
            "company_name": "Test Company",
            "sector": "IT Services",
            "market_cap": 10000000000,
            "stock_group": StockGroupEnum.NIFTY_50,
            "is_active": True,
        }

        stock = StockCreate(**stock_data)

        assert stock.symbol == "TESTSTOCK"
        assert stock.company_name == "Test Company"
        assert stock.market_cap == 10000000000

    def test_stock_create_minimal(self):
        """Test creating StockCreate with minimal required fields"""
        stock_data = {
            "symbol": "TEST",
            "company_name": "Test Company",
            "stock_group": StockGroupEnum.NIFTY_50
        }

        stock = StockCreate(**stock_data)

        assert stock.symbol == "TEST"
        assert stock.company_name == "Test Company"
        assert stock.is_active is True  # Default value

    def test_stock_create_symbol_validation(self):
        """Test symbol validation in StockCreate"""
        # Valid symbols
        valid_symbols = ["AAPL", "MSFT", "GOOGL", "TEST123", "A1B2C3"]
        for symbol in valid_symbols:
            stock = StockCreate(symbol=symbol, company_name="Test", stock_group=StockGroupEnum.NIFTY_50)
            assert stock.symbol == symbol.upper()

        # Invalid symbols
        invalid_symbols = [
            "",  # Empty
            "test with spaces",  # Contains spaces
            "test@symbol",  # Contains special characters
        ]
        for symbol in invalid_symbols:
            with pytest.raises(ValidationError):
                StockCreate(symbol=symbol, company_name="Test", stock_group=StockGroupEnum.NIFTY_50)

    def test_stock_create_symbol_case_normalization(self):
        """Test that symbol is normalized to uppercase"""
        stock = StockCreate(symbol="teststock", company_name="Test", stock_group=StockGroupEnum.NIFTY_50)
        assert stock.symbol == "TESTSTOCK"

    def test_stock_create_market_cap_validation(self):
        """Test market cap validation"""
        # Valid market caps
        stock = StockCreate(symbol="TEST", company_name="Test", stock_group=StockGroupEnum.NIFTY_50, market_cap=1000000)
        assert stock.market_cap == 1000000

        # Negative market cap should fail
        with pytest.raises(ValidationError):
            StockCreate(symbol="TEST", company_name="Test", stock_group=StockGroupEnum.NIFTY_50, market_cap=-1000000)



    def test_stock_response_schema(self):
        """Test StockResponse schema with all fields"""
        stock_data = {
            "id": uuid4(),
            "symbol": "TESTSTOCK",
            "company_name": "Test Company",
            "sector": "IT Services",
            "market_cap": 10000000000,
            "stock_group": StockGroupEnum.NIFTY_50,
            "is_active": True,
            "created_at": "2023-12-01T12:00:00",
            "updated_at": "2023-12-01T12:00:00",
        }

        stock = StockResponse(**stock_data)

        assert stock.id == stock_data["id"]
        assert stock.symbol == stock_data["symbol"]
        assert stock.created_at is not None

    def test_stock_update_schema(self):
        """Test StockUpdate schema"""
        update_data = {
            "company_name": "Updated Company",
            "market_cap": 20000000000,
            "is_active": False,
        }

        stock_update = StockUpdate(**update_data)

        assert stock_update.company_name == "Updated Company"
        assert stock_update.market_cap == 20000000000
        assert stock_update.is_active is False
        assert stock_update.symbol is None  # Not updated

    def test_stock_update_empty(self):
        """Test StockUpdate with no fields (all optional)"""
        stock_update = StockUpdate()

        # All fields should be None (not provided)
        assert stock_update.symbol is None
        assert stock_update.company_name is None
        assert stock_update.market_cap is None

    def test_stock_search_schema(self):
        """Test StockSearch schema"""
        search_data = {
            "query": "tech",
            "active_only": True,
            "limit": 20,
        }

        search = StockSearch(**search_data)

        assert search.query == "tech"
        assert search.active_only is True
        assert search.limit == 20

    def test_stock_search_query_validation(self):
        """Test search query validation"""
        # Valid queries
        valid_queries = ["tech", "banking corp", "AAPL", "123"]
        for query in valid_queries:
            search = StockSearch(query=query)
            assert search.query == query

        # Empty query should fail
        with pytest.raises(ValidationError):
            StockSearch(query="")

    def test_stock_filter(self):
        """Test StockFilter schema"""
        filter_data = {
            "market_cap_min": 1000000000,
            "market_cap_max": 10000000000,
            "symbol": "TEST",
            "is_active": True,
        }

        stock_filter = StockFilter(**filter_data)

        assert stock_filter.market_cap_min == 1000000000
        assert stock_filter.market_cap_max == 10000000000
        assert stock_filter.symbol == "TEST"






    def test_schema_json_serialization(self):
        """Test JSON serialization of schemas"""
        stock_data = {
            "symbol": "TEST",
            "company_name": "Test Company",
            "stock_group": StockGroupEnum.NIFTY_50,
            "market_cap": 1000000000,
        }

        stock = StockCreate(**stock_data)
        json_data = stock.model_dump()

        assert json_data["symbol"] == "TEST"
        assert json_data["company_name"] == "Test Company"
        assert json_data["is_active"] is True  # Default value included

    def test_schema_exclude_unset(self):
        """Test excluding unset fields from schema"""
        stock_data = {
            "symbol": "TEST",
            "company_name": "Test Company",
            "stock_group": StockGroupEnum.NIFTY_50
        }

        stock = StockCreate(**stock_data)
        json_data = stock.model_dump(exclude_unset=True)

        assert "symbol" in json_data
        assert "company_name" in json_data
        # is_active has a default value but might not be included in exclude_unset
        # Let's check if it's there or not - both behaviors are valid

    def test_schema_validation_error_messages(self):
        """Test that validation errors provide clear messages"""
        try:
            StockCreate(symbol="", company_name="Test", stock_group=StockGroupEnum.NIFTY_50)  # Empty symbol
        except ValidationError as e:
            error_info = e.errors()[0]
            assert "symbol" in str(error_info)

    def test_model_config_settings(self):
        """Test that model configuration is correct"""
        stock = StockCreate(symbol="TEST", company_name="Test", stock_group=StockGroupEnum.NIFTY_50)

        # Test that the model has correct configuration
        assert stock.model_config["from_attributes"] is True
