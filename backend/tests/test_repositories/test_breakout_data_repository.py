"""
Tests for BreakoutDataRepository
"""

from datetime import date, timedelta

import pytest

from breakout_screener.models.breakout_data import BreakoutData
from breakout_screener.models.enums import (
    AnalysisStatusEnum,
    BreakoutStatusEnum,
    PivotTypeEnum,
)
from breakout_screener.models.stock import Stock
from breakout_screener.repositories.base import PaginationParams, SortParams
from breakout_screener.repositories.breakout_data import (
    BreakoutDataFilterParams,
    BreakoutDataRepository,
)


class TestBreakoutDataRepository:
    """Test suite for BreakoutDataRepository"""

    @pytest.mark.asyncio
    async def test_create_breakout_data(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test creating new breakout data"""
        breakout_data = sample_breakout_data.copy()
        breakout_data["stock_id"] = sample_stock.id

        created_breakout = await breakout_data_repository.create(breakout_data)

        assert created_breakout.id is not None
        assert created_breakout.stock_id == sample_stock.id
        assert created_breakout.trade_date == sample_breakout_data["trade_date"]
        assert created_breakout.close_price == sample_breakout_data["close_price"]
        assert (
            created_breakout.breakout_indicator
            == sample_breakout_data["breakout_indicator"]
        )

    @pytest.mark.asyncio
    async def test_get_by_symbol_and_date(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_breakout: BreakoutData,
        sample_stock: Stock,
    ):
        """Test getting breakout data by symbol and date"""
        breakout = await breakout_data_repository.get_by_symbol_and_date(
            sample_stock.symbol, sample_breakout.trade_date
        )

        assert breakout is not None
        assert breakout.id == sample_breakout.id
        assert breakout.trade_date == sample_breakout.trade_date

    @pytest.mark.asyncio
    async def test_get_by_symbol_and_date_not_found(
        self, breakout_data_repository: BreakoutDataRepository
    ):
        """Test getting non-existent breakout data"""
        breakout = await breakout_data_repository.get_by_symbol_and_date(
            "NONEXISTENT", date(2023, 1, 1)
        )

        assert breakout is None

    @pytest.mark.asyncio
    async def test_get_by_date_range(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting breakout data within date range"""
        # Create multiple breakout records across different dates
        base_date = date(2023, 12, 1)
        breakout_records = []

        for i in range(5):
            breakout_data = sample_breakout_data.copy()
            breakout_data["stock_id"] = sample_stock.id
            breakout_data["trade_date"] = base_date + timedelta(days=i)
            breakout_records.append(
                await breakout_data_repository.create(breakout_data)
            )

        # Get data for 3-day range
        from_date = base_date + timedelta(days=1)
        to_date = base_date + timedelta(days=3)

        breakouts = await breakout_data_repository.get_by_date_range(from_date, to_date)

        assert len(breakouts) == 3
        assert all(from_date <= b.trade_date <= to_date for b in breakouts)

    @pytest.mark.asyncio
    async def test_get_by_date_range_with_symbols(
        self,
        breakout_data_repository: BreakoutDataRepository,
        stock_repository,
        sample_stock_data,
        sample_breakout_data,
    ):
        """Test getting breakout data by date range filtered by symbols"""
        # Create two stocks
        stock1 = await stock_repository.create(
            {**sample_stock_data, "symbol": "STOCK1"}
        )
        stock2 = await stock_repository.create(
            {**sample_stock_data, "symbol": "STOCK2", "isin": "INE987654321"}
        )

        # Create breakout data for both stocks
        trade_date = date(2023, 12, 1)

        breakout1_data = {
            **sample_breakout_data,
            "stock_id": stock1.id,
            "trade_date": trade_date,
        }
        breakout2_data = {
            **sample_breakout_data,
            "stock_id": stock2.id,
            "trade_date": trade_date,
        }

        await breakout_data_repository.create(breakout1_data)
        await breakout_data_repository.create(breakout2_data)

        # Get data for only STOCK1
        breakouts = await breakout_data_repository.get_by_date_range(
            trade_date, trade_date, symbols=["STOCK1"]
        )

        assert len(breakouts) == 1
        assert breakouts[0].stock_id == stock1.id

    @pytest.mark.asyncio
    async def test_get_latest_by_symbol(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting latest breakout data for a symbol"""
        base_date = date(2023, 12, 1)

        # Create multiple records with different dates
        for i in range(3):
            breakout_data = sample_breakout_data.copy()
            breakout_data["stock_id"] = sample_stock.id
            breakout_data["trade_date"] = base_date + timedelta(days=i)
            await breakout_data_repository.create(breakout_data)

        # Get latest 2 records
        latest_breakouts = await breakout_data_repository.get_latest_by_symbol(
            sample_stock.symbol, limit=2
        )

        assert len(latest_breakouts) == 2
        # Should be ordered by trade_date descending
        assert latest_breakouts[0].trade_date > latest_breakouts[1].trade_date

    @pytest.mark.asyncio
    async def test_get_breakouts_by_status(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting breakouts by status"""
        # Create breakouts with different statuses
        statuses = [
            BreakoutStatusEnum.UPSIDE_BREAKOUT,
            BreakoutStatusEnum.DOWNSIDE_BREAKOUT,
            BreakoutStatusEnum.NO_BREAKOUT,
        ]

        for i, status in enumerate(statuses):
            breakout_data = sample_breakout_data.copy()
            breakout_data["stock_id"] = sample_stock.id
            breakout_data["trade_date"] = date(2023, 12, 1) + timedelta(days=i)
            breakout_data["breakout_status"] = status
            await breakout_data_repository.create(breakout_data)

        # Get only upside breakouts
        upside_breakouts = await breakout_data_repository.get_breakouts_by_status(
            BreakoutStatusEnum.UPSIDE_BREAKOUT
        )

        assert len(upside_breakouts) == 1
        assert upside_breakouts[0].breakout_status == BreakoutStatusEnum.UPSIDE_BREAKOUT

    @pytest.mark.asyncio
    async def test_get_unanalyzed_data(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting unanalyzed breakout data"""
        # Create analyzed and unanalyzed data
        analyzed_data = sample_breakout_data.copy()
        analyzed_data.update(
            {
                "stock_id": sample_stock.id,
                "trade_date": date(2023, 12, 1),
                "is_analyzed": True,
                "analysis_status": AnalysisStatusEnum.COMPLETED,
            }
        )

        unanalyzed_data = sample_breakout_data.copy()
        unanalyzed_data.update(
            {
                "stock_id": sample_stock.id,
                "trade_date": date(2023, 12, 2),
                "is_analyzed": False,
                "analysis_status": AnalysisStatusEnum.PENDING,
            }
        )

        await breakout_data_repository.create(analyzed_data)
        await breakout_data_repository.create(unanalyzed_data)

        # Get unanalyzed data
        unanalyzed = await breakout_data_repository.get_unanalyzed_data()

        assert len(unanalyzed) == 1
        assert unanalyzed[0].is_analyzed is False

    @pytest.mark.asyncio
    async def test_get_by_advanced_filter(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test advanced filtering of breakout data"""
        # Create multiple breakout records with different attributes
        base_date = date(2023, 12, 1)

        breakout_configs = [
            {
                "trade_date": base_date,
                "close_price": 100.0,
                "volume": 1000000,
                "breakout_status": BreakoutStatusEnum.UPSIDE_BREAKOUT,
                "pivot_type": PivotTypeEnum.BULLISH,
            },
            {
                "trade_date": base_date + timedelta(days=1),
                "close_price": 200.0,
                "volume": 2000000,
                "breakout_status": BreakoutStatusEnum.DOWNSIDE_BREAKOUT,
                "pivot_type": PivotTypeEnum.BEARISH,
            },
        ]

        for config in breakout_configs:
            breakout_data = sample_breakout_data.copy()
            breakout_data.update(config)
            breakout_data["stock_id"] = sample_stock.id
            await breakout_data_repository.create(breakout_data)

        # Filter by price range and breakout status
        filters = BreakoutDataFilterParams(
            symbol=sample_stock.symbol,
            min_price=150.0,
            max_price=250.0,
            breakout_status=BreakoutStatusEnum.DOWNSIDE_BREAKOUT,
        )

        filtered_breakouts = await breakout_data_repository.get_by_advanced_filter(
            filters
        )

        assert len(filtered_breakouts) == 1
        assert filtered_breakouts[0].close_price == 200.0
        assert (
            filtered_breakouts[0].breakout_status
            == BreakoutStatusEnum.DOWNSIDE_BREAKOUT
        )

    @pytest.mark.asyncio
    async def test_get_breakout_counts_by_status(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting breakout counts grouped by status"""
        # Create breakouts with different statuses
        statuses_counts = {
            BreakoutStatusEnum.UPSIDE_BREAKOUT: 3,
            BreakoutStatusEnum.DOWNSIDE_BREAKOUT: 2,
            BreakoutStatusEnum.NO_BREAKOUT: 1,
        }

        day_counter = 0
        for status, count in statuses_counts.items():
            for _ in range(count):
                breakout_data = sample_breakout_data.copy()
                breakout_data.update(
                    {
                        "stock_id": sample_stock.id,
                        "trade_date": date(2023, 12, 1) + timedelta(days=day_counter),
                        "breakout_status": status,
                    }
                )
                await breakout_data_repository.create(breakout_data)
                day_counter += 1

        # Get counts by status
        status_counts = await breakout_data_repository.get_breakout_counts_by_status()

        assert status_counts["UPSIDE_BREAKOUT"] == 3
        assert status_counts["DOWNSIDE_BREAKOUT"] == 2
        assert status_counts["NO_BREAKOUT"] == 1

    @pytest.mark.asyncio
    async def test_get_daily_breakout_summary(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test getting daily breakout summary"""
        base_date = date(2023, 12, 1)

        # Create multiple breakouts for one day
        for i in range(3):
            breakout_data = sample_breakout_data.copy()
            breakout_data.update(
                {
                    "stock_id": sample_stock.id,
                    "trade_date": base_date,
                    "close_price": 100.0 + i * 10,
                    "volume": 1000000 + i * 100000,
                    "breakout_status": BreakoutStatusEnum.UPSIDE_BREAKOUT
                    if i < 2
                    else BreakoutStatusEnum.NO_BREAKOUT,
                    "is_analyzed": True,
                }
            )
            await breakout_data_repository.create(breakout_data)

        # Get daily summary
        summary = await breakout_data_repository.get_daily_breakout_summary(
            base_date, base_date
        )

        assert len(summary) == 1
        day_summary = summary[0]

        assert day_summary["trade_date"] == base_date
        assert day_summary["total_records"] == 3
        assert day_summary["breakout_count"] == 2  # 2 actual breakouts
        assert day_summary["analyzed_count"] == 3
        assert day_summary["avg_price"] == 110.0  # (100 + 110 + 120) / 3

    @pytest.mark.asyncio
    async def test_get_by_unique_field(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_breakout: BreakoutData,
        sample_stock: Stock,
    ):
        """Test getting breakout data by unique field (symbol + date)"""
        breakout = await breakout_data_repository.get_by_unique_field(
            "symbol_date", (sample_stock.symbol, sample_breakout.trade_date)
        )

        assert breakout is not None
        assert breakout.id == sample_breakout.id

    @pytest.mark.asyncio
    async def test_get_by_unique_field_invalid_field(
        self, breakout_data_repository: BreakoutDataRepository
    ):
        """Test getting breakout data by invalid unique field"""
        with pytest.raises(ValueError):
            await breakout_data_repository.get_by_unique_field("invalid_field", "value")

    @pytest.mark.asyncio
    async def test_get_by_unique_field_invalid_value_format(
        self, breakout_data_repository: BreakoutDataRepository
    ):
        """Test getting breakout data with invalid value format"""
        with pytest.raises(ValueError):
            await breakout_data_repository.get_by_unique_field("symbol_date", "invalid")

    @pytest.mark.asyncio
    async def test_bulk_create_breakout_data(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test bulk creating breakout data"""
        base_date = date(2023, 12, 1)

        breakouts_data = []
        for i in range(3):
            breakout_data = sample_breakout_data.copy()
            breakout_data.update(
                {
                    "stock_id": sample_stock.id,
                    "trade_date": base_date + timedelta(days=i),
                }
            )
            breakouts_data.append(breakout_data)

        created_breakouts = await breakout_data_repository.bulk_create(breakouts_data)

        assert len(created_breakouts) == 3
        assert all(breakout.id is not None for breakout in created_breakouts)

    @pytest.mark.asyncio
    async def test_update_breakout_data(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_breakout: BreakoutData,
    ):
        """Test updating breakout data"""
        update_data = {
            "is_analyzed": True,
            "analysis_status": AnalysisStatusEnum.COMPLETED,
            "notes": "Updated notes",
        }

        updated_breakout = await breakout_data_repository.update(
            sample_breakout.id, update_data
        )

        assert updated_breakout.is_analyzed is True
        assert updated_breakout.analysis_status == AnalysisStatusEnum.COMPLETED
        assert updated_breakout.notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_pagination_and_sorting(
        self,
        breakout_data_repository: BreakoutDataRepository,
        sample_stock: Stock,
        sample_breakout_data,
    ):
        """Test pagination and sorting functionality"""
        base_date = date(2023, 12, 1)

        # Create multiple records
        for i in range(5):
            breakout_data = sample_breakout_data.copy()
            breakout_data.update(
                {
                    "stock_id": sample_stock.id,
                    "trade_date": base_date + timedelta(days=i),
                    "close_price": 100.0 + i * 10,
                }
            )
            await breakout_data_repository.create(breakout_data)

        # Test pagination
        pagination = PaginationParams(page=1, limit=2)
        breakouts_page1 = await breakout_data_repository.get_all(pagination=pagination)

        assert len(breakouts_page1) == 2

        # Test sorting by close_price ascending
        sort_params = SortParams(sort_by="close_price", sort_order="asc")
        sorted_breakouts = await breakout_data_repository.get_all(sort=sort_params)

        prices = [float(b.close_price) for b in sorted_breakouts]
        assert prices == sorted(prices)
