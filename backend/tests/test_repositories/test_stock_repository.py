"""
Tests for StockRepository
"""

import pytest
from sqlalchemy.exc import IntegrityError

from breakout_screener.models.stock import Stock
from breakout_screener.repositories.base import NotFoundError, PaginationParams, SortParams
from breakout_screener.repositories.stock import StockRepository


class TestStockRepository:
    """Test suite for StockRepository"""

    @pytest.mark.asyncio
    async def test_create_stock(self, stock_repository: StockRepository, sample_stock_data):
        """Test creating a new stock"""
        stock = await stock_repository.create(sample_stock_data)
        
        assert stock.id is not None
        assert stock.symbol == sample_stock_data["symbol"]
        assert stock.company_name == sample_stock_data["company_name"]
        assert stock.is_active == sample_stock_data["is_active"]
        assert stock.created_at is not None

    @pytest.mark.asyncio
    async def test_create_duplicate_symbol_fails(
        self, stock_repository: StockRepository, sample_stock_data
    ):
        """Test that creating a stock with duplicate symbol fails"""
        await stock_repository.create(sample_stock_data)
        
        # Try to create another stock with same symbol
        with pytest.raises(IntegrityError):
            await stock_repository.create(sample_stock_data)

    @pytest.mark.asyncio
    async def test_get_by_id(self, stock_repository: StockRepository, sample_stock: Stock):
        """Test getting stock by ID"""
        retrieved_stock = await stock_repository.get_by_id(sample_stock.id)
        
        assert retrieved_stock is not None
        assert retrieved_stock.id == sample_stock.id
        assert retrieved_stock.symbol == sample_stock.symbol

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, stock_repository: StockRepository, uuid_generator):
        """Test getting non-existent stock by ID"""
        non_existent_id = uuid_generator()
        stock = await stock_repository.get_by_id(non_existent_id)
        
        assert stock is None

    @pytest.mark.asyncio
    async def test_get_by_symbol(self, stock_repository: StockRepository, sample_stock: Stock):
        """Test getting stock by symbol"""
        stock = await stock_repository.get_by_symbol(sample_stock.symbol)
        
        assert stock is not None
        assert stock.id == sample_stock.id
        assert stock.symbol == sample_stock.symbol

    @pytest.mark.asyncio
    async def test_get_by_symbol_case_insensitive(
        self, stock_repository: StockRepository, sample_stock: Stock
    ):
        """Test that symbol lookup is case insensitive"""
        stock = await stock_repository.get_by_symbol(sample_stock.symbol.lower())
        
        assert stock is not None
        assert stock.id == sample_stock.id

    @pytest.mark.asyncio
    async def test_get_by_symbol_not_found(self, stock_repository: StockRepository):
        """Test getting non-existent stock by symbol"""
        stock = await stock_repository.get_by_symbol("NONEXISTENT")
        
        assert stock is None

    @pytest.mark.asyncio
    async def test_get_by_symbol_or_raise(
        self, stock_repository: StockRepository, sample_stock: Stock
    ):
        """Test get_by_symbol_or_raise with existing stock"""
        stock = await stock_repository.get_by_symbol_or_raise(sample_stock.symbol)
        
        assert stock.id == sample_stock.id

    @pytest.mark.asyncio
    async def test_get_by_symbol_or_raise_not_found(self, stock_repository: StockRepository):
        """Test get_by_symbol_or_raise with non-existent stock"""
        with pytest.raises(NotFoundError):
            await stock_repository.get_by_symbol_or_raise("NONEXISTENT")

    @pytest.mark.asyncio
    async def test_update_stock(self, stock_repository: StockRepository, sample_stock: Stock):
        """Test updating a stock"""
        update_data = {
            "company_name": "Updated Company Name",
            "market_cap": 20000000000,
        }
        
        updated_stock = await stock_repository.update(sample_stock.id, update_data)
        
        assert updated_stock.company_name == update_data["company_name"]
        assert updated_stock.market_cap == update_data["market_cap"]
        assert updated_stock.symbol == sample_stock.symbol  # Unchanged
        assert updated_stock.updated_at is not None

    @pytest.mark.asyncio
    async def test_delete_stock(self, stock_repository: StockRepository, sample_stock: Stock):
        """Test deleting a stock"""
        result = await stock_repository.delete(sample_stock.id)
        
        assert result is True
        
        # Verify stock is deleted
        deleted_stock = await stock_repository.get_by_id(sample_stock.id)
        assert deleted_stock is None

    @pytest.mark.asyncio
    async def test_delete_non_existent_stock(
        self, stock_repository: StockRepository, uuid_generator
    ):
        """Test deleting non-existent stock"""
        result = await stock_repository.delete(uuid_generator())
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_stocks(self, stock_repository: StockRepository, sample_stock_data):
        """Test getting all stocks"""
        # Create multiple stocks
        stocks_data = [
            {**sample_stock_data, "symbol": f"TEST{i}", "isin": f"INE12345678{i}"}
            for i in range(3)
        ]
        
        for stock_data in stocks_data:
            await stock_repository.create(stock_data)
        
        stocks = await stock_repository.get_all()
        
        assert len(stocks) == 3
        assert all(isinstance(stock, Stock) for stock in stocks)

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(
        self, stock_repository: StockRepository, sample_stock_data
    ):
        """Test getting stocks with pagination"""
        # Create 5 stocks
        for i in range(5):
            stock_data = {
                **sample_stock_data,
                "symbol": f"TEST{i}",
                "isin": f"INE12345678{i}",
            }
            await stock_repository.create(stock_data)
        
        # Get first page
        pagination = PaginationParams(page=1, limit=2)
        stocks_page1 = await stock_repository.get_all(pagination=pagination)
        
        assert len(stocks_page1) == 2
        
        # Get second page
        pagination = PaginationParams(page=2, limit=2)
        stocks_page2 = await stock_repository.get_all(pagination=pagination)
        
        assert len(stocks_page2) == 2
        
        # Verify different stocks
        page1_ids = {stock.id for stock in stocks_page1}
        page2_ids = {stock.id for stock in stocks_page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_get_all_with_sorting(
        self, stock_repository: StockRepository, sample_stock_data
    ):
        """Test getting stocks with sorting"""
        # Create stocks with different symbols
        symbols = ["ZTEST", "ATEST", "MTEST"]
        for symbol in symbols:
            stock_data = {
                **sample_stock_data,
                "symbol": symbol,
                "isin": f"INE{symbol}123",
            }
            await stock_repository.create(stock_data)
        
        # Sort by symbol ascending
        sort_params = SortParams(sort_by="symbol", sort_order="asc")
        sorted_stocks = await stock_repository.get_all(sort=sort_params)
        
        symbols_retrieved = [stock.symbol for stock in sorted_stocks]
        assert symbols_retrieved == sorted(symbols)

    @pytest.mark.asyncio
    async def test_get_active_stocks(
        self, stock_repository: StockRepository, sample_stock_data
    ):
        """Test getting only active stocks"""
        # Create active and inactive stocks
        active_stock_data = {**sample_stock_data, "symbol": "ACTIVE", "is_active": True}
        inactive_stock_data = {
            **sample_stock_data,
            "symbol": "INACTIVE",
            "isin": "INE987654321",
            "is_active": False,
        }
        
        await stock_repository.create(active_stock_data)
        await stock_repository.create(inactive_stock_data)
        
        active_stocks = await stock_repository.get_active_stocks()
        
        assert len(active_stocks) == 1
        assert active_stocks[0].symbol == "ACTIVE"
        assert active_stocks[0].is_active is True

    @pytest.mark.asyncio
    async def test_search_stocks(self, stock_repository: StockRepository, sample_stock_data):
        """Test searching stocks by name or symbol"""
        # Create stocks with searchable names
        stocks_data = [
            {
                **sample_stock_data,
                "symbol": "TECH1",
                "company_name": "Technology Company One",
                "isin": "INE123456781",
            },
            {
                **sample_stock_data,
                "symbol": "TECH2", 
                "company_name": "Technology Company Two",
                "isin": "INE123456782",
            },
            {
                **sample_stock_data,
                "symbol": "BANK1",
                "company_name": "Banking Corporation",
                "isin": "INE123456783",
            },
        ]
        
        for stock_data in stocks_data:
            await stock_repository.create(stock_data)
        
        # Search by partial company name
        tech_stocks = await stock_repository.search_stocks("Technology")
        assert len(tech_stocks) == 2
        
        # Search by symbol
        bank_stocks = await stock_repository.search_stocks("BANK")
        assert len(bank_stocks) == 1
        assert bank_stocks[0].symbol == "BANK1"

    @pytest.mark.asyncio
    async def test_get_by_market_cap_range(
        self, stock_repository: StockRepository, sample_stock_data
    ):
        """Test filtering stocks by market cap range"""
        # Create stocks with different market caps
        stocks_data = [
            {**sample_stock_data, "symbol": "SMALL", "market_cap": 1000000000},
            {**sample_stock_data, "symbol": "MEDIUM", "market_cap": 5000000000, "isin": "INE123456782"},
            {**sample_stock_data, "symbol": "LARGE", "market_cap": 10000000000, "isin": "INE123456783"},
        ]
        
        for stock_data in stocks_data:
            await stock_repository.create(stock_data)
        
        # Get stocks with market cap between 2B and 8B
        filtered_stocks = await stock_repository.get_by_market_cap_range(
            min_market_cap=2000000000, max_market_cap=8000000000
        )
        
        assert len(filtered_stocks) == 1
        assert filtered_stocks[0].symbol == "MEDIUM"

    @pytest.mark.asyncio
    async def test_get_by_sector(self, stock_repository: StockRepository, sample_stock_data):
        """Test getting stocks by sector"""
        # Create stocks in different sectors
        stocks_data = [
            {**sample_stock_data, "symbol": "TECH1", "sector": "Technology"},
            {**sample_stock_data, "symbol": "BANK1", "sector": "Banking", "isin": "INE123456782"},
            {**sample_stock_data, "symbol": "TECH2", "sector": "Technology", "isin": "INE123456783"},
        ]
        
        for stock_data in stocks_data:
            await stock_repository.create(stock_data)
        
        tech_stocks = await stock_repository.get_by_sector("Technology")
        
        assert len(tech_stocks) == 2
        assert all(stock.sector == "Technology" for stock in tech_stocks)

    @pytest.mark.asyncio
    async def test_count_stocks(self, stock_repository: StockRepository, sample_stock_data):
        """Test counting stocks"""
        # Create multiple stocks
        for i in range(3):
            stock_data = {
                **sample_stock_data,
                "symbol": f"TEST{i}",
                "isin": f"INE12345678{i}",
            }
            await stock_repository.create(stock_data)
        
        count = await stock_repository.count()
        assert count == 3
        
        # Count with filter
        count_active = await stock_repository.count({"is_active": True})
        assert count_active == 3

    @pytest.mark.asyncio
    async def test_exists_stock(self, stock_repository: StockRepository, sample_stock: Stock):
        """Test checking if stock exists"""
        exists = await stock_repository.exists(sample_stock.id)
        assert exists is True
        
        # Check non-existent stock
        from uuid import uuid4
        exists_false = await stock_repository.exists(uuid4())
        assert exists_false is False

    @pytest.mark.asyncio
    async def test_bulk_create_stocks(self, stock_repository: StockRepository, sample_stock_data):
        """Test bulk creating stocks"""
        stocks_data = [
            {**sample_stock_data, "symbol": f"BULK{i}", "isin": f"INE12345678{i}"}
            for i in range(3)
        ]
        
        created_stocks = await stock_repository.bulk_create(stocks_data)
        
        assert len(created_stocks) == 3
        assert all(stock.id is not None for stock in created_stocks)
        assert all(stock.created_at is not None for stock in created_stocks)

    @pytest.mark.asyncio
    async def test_get_by_unique_field(
        self, stock_repository: StockRepository, sample_stock: Stock
    ):
        """Test getting stock by unique field (symbol)"""
        stock = await stock_repository.get_by_unique_field("symbol", sample_stock.symbol)
        
        assert stock is not None
        assert stock.id == sample_stock.id

    @pytest.mark.asyncio
    async def test_get_by_unique_field_invalid_field(
        self, stock_repository: StockRepository
    ):
        """Test getting stock by invalid unique field"""
        with pytest.raises(ValueError):
            await stock_repository.get_by_unique_field("invalid_field", "value")