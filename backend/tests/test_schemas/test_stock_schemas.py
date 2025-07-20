"""
Tests for Stock Pydantic schemas
"""

from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from breakout_screener.schemas.stock import (
    StockCreate,
    StockRead,
    StockSearch,
    StockUpdate,
    StockMarketCapFilter,
    StockSectorFilter,
)


class TestStockSchemas:
    """Test suite for Stock schemas"""

    def test_stock_create_valid(self):
        """Test creating valid StockCreate schema"""
        stock_data = {
            "symbol": "TESTSTOCK",
            "company_name": "Test Company",
            "industry": "Technology",
            "sector": "IT Services",
            "market_cap": 10000000000,
            "is_active": True,
            "listing_date": date(2020, 1, 1),
            "stock_group": "A",
            "face_value": 10.0,
            "isin": "INE123456789",
        }
        
        stock = StockCreate(**stock_data)
        
        assert stock.symbol == "TESTSTOCK"
        assert stock.company_name == "Test Company"
        assert stock.market_cap == 10000000000

    def test_stock_create_minimal(self):
        """Test creating StockCreate with minimal required fields"""
        stock_data = {"symbol": "TEST"}
        
        stock = StockCreate(**stock_data)
        
        assert stock.symbol == "TEST"
        assert stock.company_name is None
        assert stock.is_active is True  # Default value

    def test_stock_create_symbol_validation(self):
        """Test symbol validation in StockCreate"""
        # Valid symbols
        valid_symbols = ["AAPL", "MSFT", "GOOGL", "TEST123", "A1B2C3"]
        for symbol in valid_symbols:
            stock = StockCreate(symbol=symbol)
            assert stock.symbol == symbol.upper()
        
        # Invalid symbols
        invalid_symbols = ["", "A", "TOOLONGSYMBOL123", "test with spaces", "test@symbol"]
        for symbol in invalid_symbols:
            with pytest.raises(ValidationError):
                StockCreate(symbol=symbol)

    def test_stock_create_symbol_case_normalization(self):
        """Test that symbol is normalized to uppercase"""
        stock = StockCreate(symbol="teststock")
        assert stock.symbol == "TESTSTOCK"

    def test_stock_create_market_cap_validation(self):
        """Test market cap validation"""
        # Valid market caps
        stock = StockCreate(symbol="TEST", market_cap=1000000)
        assert stock.market_cap == 1000000
        
        # Negative market cap should fail
        with pytest.raises(ValidationError):
            StockCreate(symbol="TEST", market_cap=-1000000)

    def test_stock_create_face_value_validation(self):
        """Test face value validation"""
        # Valid face values
        stock = StockCreate(symbol="TEST", face_value=10.0)
        assert stock.face_value == 10.0
        
        # Negative face value should fail
        with pytest.raises(ValidationError):
            StockCreate(symbol="TEST", face_value=-10.0)

    def test_stock_create_isin_validation(self):
        """Test ISIN validation"""
        # Valid ISIN format
        stock = StockCreate(symbol="TEST", isin="INE123456789")
        assert stock.isin == "INE123456789"
        
        # Invalid ISIN formats
        invalid_isins = ["", "TOOLONG123456789", "SHORT", "123456789012"]
        for isin in invalid_isins:
            with pytest.raises(ValidationError):
                StockCreate(symbol="TEST", isin=isin)

    def test_stock_read_schema(self):
        """Test StockRead schema with all fields"""
        stock_data = {
            "id": uuid4(),
            "symbol": "TESTSTOCK",
            "company_name": "Test Company",
            "industry": "Technology",
            "sector": "IT Services",
            "market_cap": 10000000000,
            "is_active": True,
            "listing_date": date(2020, 1, 1),
            "stock_group": "A",
            "face_value": 10.0,
            "isin": "INE123456789",
            "created_at": "2023-12-01T12:00:00",
            "updated_at": "2023-12-01T12:00:00",
        }
        
        stock = StockRead(**stock_data)
        
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
            "is_active": True,
            "sector": "Technology",
            "min_market_cap": 1000000000,
            "max_market_cap": 50000000000,
        }
        
        search = StockSearch(**search_data)
        
        assert search.query == "tech"
        assert search.is_active is True
        assert search.sector == "Technology"
        assert search.min_market_cap == 1000000000

    def test_stock_search_query_validation(self):
        """Test search query validation"""
        # Valid queries
        valid_queries = ["tech", "banking corp", "AAPL", "123"]
        for query in valid_queries:
            search = StockSearch(query=query)
            assert search.query == query
        
        # Too short query should fail
        with pytest.raises(ValidationError):
            StockSearch(query="a")

    def test_stock_market_cap_filter(self):
        """Test StockMarketCapFilter schema"""
        filter_data = {
            "min_market_cap": 1000000000,
            "max_market_cap": 10000000000,
        }
        
        market_cap_filter = StockMarketCapFilter(**filter_data)
        
        assert market_cap_filter.min_market_cap == 1000000000
        assert market_cap_filter.max_market_cap == 10000000000

    def test_stock_market_cap_filter_validation(self):
        """Test market cap filter validation"""
        # min_market_cap greater than max_market_cap should fail
        with pytest.raises(ValidationError):
            StockMarketCapFilter(min_market_cap=10000000000, max_market_cap=1000000000)

    def test_stock_sector_filter(self):
        """Test StockSectorFilter schema"""
        filter_data = {
            "sectors": ["Technology", "Banking", "Healthcare"],
            "industries": ["Software", "Banking Services"],
        }
        
        sector_filter = StockSectorFilter(**filter_data)
        
        assert len(sector_filter.sectors) == 3
        assert "Technology" in sector_filter.sectors
        assert len(sector_filter.industries) == 2

    def test_stock_sector_filter_empty_lists(self):
        """Test StockSectorFilter with empty lists"""
        filter_data = {"sectors": [], "industries": []}
        
        sector_filter = StockSectorFilter(**filter_data)
        
        assert sector_filter.sectors == []
        assert sector_filter.industries == []

    def test_computed_fields_market_cap_category(self):
        """Test computed market cap category field"""
        # Large cap stock
        large_cap_stock = StockRead(
            id=uuid4(),
            symbol="LARGE",
            market_cap=50000000000,  # 50B
            created_at="2023-12-01T12:00:00",
        )
        assert large_cap_stock.market_cap_category == "Large Cap"
        
        # Mid cap stock
        mid_cap_stock = StockRead(
            id=uuid4(),
            symbol="MID",
            market_cap=5000000000,  # 5B
            created_at="2023-12-01T12:00:00",
        )
        assert mid_cap_stock.market_cap_category == "Mid Cap"
        
        # Small cap stock
        small_cap_stock = StockRead(
            id=uuid4(),
            symbol="SMALL",
            market_cap=500000000,  # 500M
            created_at="2023-12-01T12:00:00",
        )
        assert small_cap_stock.market_cap_category == "Small Cap"
        
        # Micro cap stock
        micro_cap_stock = StockRead(
            id=uuid4(),
            symbol="MICRO",
            market_cap=50000000,  # 50M
            created_at="2023-12-01T12:00:00",
        )
        assert micro_cap_stock.market_cap_category == "Micro Cap"

    def test_computed_fields_no_market_cap(self):
        """Test computed fields when market cap is None"""
        stock = StockRead(
            id=uuid4(),
            symbol="TEST",
            market_cap=None,
            created_at="2023-12-01T12:00:00",
        )
        assert stock.market_cap_category == "Unknown"

    def test_schema_json_serialization(self):
        """Test JSON serialization of schemas"""
        stock_data = {
            "symbol": "TEST",
            "company_name": "Test Company",
            "market_cap": 1000000000,
        }
        
        stock = StockCreate(**stock_data)
        json_data = stock.model_dump()
        
        assert json_data["symbol"] == "TEST"
        assert json_data["company_name"] == "Test Company"
        assert json_data["is_active"] is True  # Default value included

    def test_schema_exclude_unset(self):
        """Test excluding unset fields from schema"""
        stock_data = {"symbol": "TEST"}
        
        stock = StockCreate(**stock_data)
        json_data = stock.model_dump(exclude_unset=True)
        
        assert "symbol" in json_data
        assert "company_name" not in json_data  # Not set, should be excluded
        assert "is_active" in json_data  # Has default, should be included

    def test_schema_validation_error_messages(self):
        """Test that validation errors provide clear messages"""
        try:
            StockCreate(symbol="")  # Empty symbol
        except ValidationError as e:
            error_info = e.errors()[0]
            assert "symbol" in str(error_info)
            assert "length" in str(error_info).lower()

    def test_model_config_settings(self):
        """Test that model configuration is correct"""
        stock = StockCreate(symbol="TEST")
        
        # Test that the model has correct configuration
        assert hasattr(stock.model_config, 'from_attributes')
        assert stock.model_config.from_attributes is True