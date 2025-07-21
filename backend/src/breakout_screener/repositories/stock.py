"""
Stock repository with business-specific queries
"""

from datetime import date
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.enums import StockGroupEnum
from ..models.stock import Stock
from .base import (
    BaseRepository,
    FilterParams,
    NotFoundError,
    PaginationParams,
    SortParams,
)

logger = get_logger(__name__)


class StockFilterParams(FilterParams):
    """Stock-specific filter parameters"""

    def __init__(
        self,
        symbol: str | None = None,
        company_name: str | None = None,
        stock_group: StockGroupEnum | None = None,
        sector: str | None = None,
        is_active: bool | None = None,
        market_cap_min: int | None = None,
        market_cap_max: int | None = None,
        **kwargs,
    ):
        self.symbol = symbol
        self.company_name = company_name
        self.stock_group = stock_group
        self.sector = sector
        self.is_active = is_active
        self.market_cap_min = market_cap_min
        self.market_cap_max = market_cap_max

        # Call parent with remaining filters
        super().__init__(**kwargs)


class StockRepository(BaseRepository[Stock]):
    """
    Repository for Stock model with business-specific operations.
    Provides queries for stock management, search, and analysis.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Stock)

    # Unique field implementations

    async def get_by_unique_field(
        self, field_name: str, field_value: Any
    ) -> Stock | None:
        """Get stock by unique field (symbol)"""
        if field_name == "symbol":
            return await self.get_by_symbol(field_value)
        else:
            raise ValueError(f"Field '{field_name}' is not a unique field for Stock")

    async def get_by_symbol(self, symbol: str) -> Stock | None:
        """
        Get stock by symbol

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')

        Returns:
            Stock if found, None otherwise
        """
        try:
            query = select(Stock).where(Stock.symbol == symbol.upper())
            result = await self.session.execute(query)
            stock = result.scalar_one_or_none()

            if stock:
                self.logger.debug("Stock retrieved by symbol", symbol=symbol)
            else:
                self.logger.debug("Stock not found by symbol", symbol=symbol)

            return stock

        except Exception as e:
            self.logger.error(
                "Failed to get stock by symbol", symbol=symbol, error=str(e)
            )
            raise

    async def get_by_symbol_or_raise(self, symbol: str) -> Stock:
        """
        Get stock by symbol or raise NotFoundError

        Args:
            symbol: Stock symbol

        Returns:
            Stock

        Raises:
            NotFoundError: If stock not found
        """
        stock = await self.get_by_symbol(symbol)
        if not stock:
            raise NotFoundError(f"Stock with symbol '{symbol}' not found")
        return stock

    # Business-specific queries

    async def get_active_stocks(
        self, pagination: PaginationParams | None = None, sort: SortParams | None = None
    ) -> list[Stock]:
        """
        Get all active stocks

        Args:
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            List of active stocks
        """
        filters = {"is_active": True}
        return await self.get_by_filter(filters, pagination, sort)

    async def get_stocks_by_group(
        self,
        stock_group: StockGroupEnum,
        active_only: bool = True,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
    ) -> list[Stock]:
        """
        Get stocks by NSE group/index

        Args:
            stock_group: NSE stock group (NIFTY_50, etc.)
            active_only: Whether to include only active stocks
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            List of stocks in the group
        """
        filters = {"stock_group": stock_group}
        if active_only:
            filters["is_active"] = True

        return await self.get_by_filter(filters, pagination, sort)

    async def search_stocks(
        self,
        search_term: str,
        active_only: bool = True,
        pagination: PaginationParams | None = None,
    ) -> list[Stock]:
        """
        Search stocks by symbol or company name

        Args:
            search_term: Search term to match against symbol/company name
            active_only: Whether to include only active stocks
            pagination: Pagination parameters

        Returns:
            List of matching stocks
        """
        try:
            search_pattern = f"%{search_term.upper()}%"

            query = select(Stock).where(
                or_(
                    Stock.symbol.ilike(search_pattern),
                    Stock.company_name.ilike(search_pattern),
                )
            )

            if active_only:
                query = query.where(Stock.is_active)

            # Sort by relevance (exact symbol match first, then symbol prefix, then name)
            query = query.order_by(
                (Stock.symbol == search_term.upper()).desc(),
                Stock.symbol.startswith(search_term.upper()).desc(),
                Stock.symbol,
                Stock.company_name,
            )

            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            stocks = result.scalars().all()

            self.logger.debug(
                "Stocks search completed", search_term=search_term, count=len(stocks)
            )
            return list(stocks)

        except Exception as e:
            self.logger.error(
                "Failed to search stocks", search_term=search_term, error=str(e)
            )
            raise

    async def get_stocks_by_sector(
        self,
        sector: str,
        active_only: bool = True,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
    ) -> list[Stock]:
        """
        Get stocks by sector

        Args:
            sector: Sector name (e.g., 'Technology', 'Banking')
            active_only: Whether to include only active stocks
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            List of stocks in the sector
        """
        filters = {"sector": sector}
        if active_only:
            filters["is_active"] = True

        return await self.get_by_filter(filters, pagination, sort)

    async def get_stocks_by_market_cap_range(
        self,
        min_market_cap: int | None = None,
        max_market_cap: int | None = None,
        active_only: bool = True,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
    ) -> list[Stock]:
        """
        Get stocks by market cap range

        Args:
            min_market_cap: Minimum market cap in rupees
            max_market_cap: Maximum market cap in rupees
            active_only: Whether to include only active stocks
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            List of stocks in the market cap range
        """
        try:
            query = select(Stock)

            conditions = []

            if active_only:
                conditions.append(Stock.is_active)

            if min_market_cap is not None:
                conditions.append(Stock.market_cap >= min_market_cap)

            if max_market_cap is not None:
                conditions.append(Stock.market_cap <= max_market_cap)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(Stock, sort.sort_by):
                    sort_column = getattr(Stock, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(sort_column.desc())
                    else:
                        query = query.order_by(sort_column.asc())
            else:
                # Default sort by market cap descending
                query = query.order_by(Stock.market_cap.desc())

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            stocks = result.scalars().all()

            self.logger.debug(
                "Stocks retrieved by market cap range",
                min_cap=min_market_cap,
                max_cap=max_market_cap,
                count=len(stocks),
            )
            return list(stocks)

        except Exception as e:
            self.logger.error(
                "Failed to get stocks by market cap range",
                min_cap=min_market_cap,
                max_cap=max_market_cap,
                error=str(e),
            )
            raise

    async def get_stocks_with_breakout_data(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationParams | None = None,
    ) -> list[Stock]:
        """
        Get stocks that have breakout data in the specified date range

        Args:
            from_date: Start date for breakout data
            to_date: End date for breakout data
            pagination: Pagination parameters

        Returns:
            List of stocks with breakout data
        """
        try:
            query = select(Stock).join(Stock.breakout_data)

            conditions = [Stock.is_active]

            if from_date:
                conditions.append(
                    Stock.breakout_data.any(
                        Stock.breakout_data.property.mapper.class_.trade_date
                        >= from_date
                    )
                )

            if to_date:
                conditions.append(
                    Stock.breakout_data.any(
                        Stock.breakout_data.property.mapper.class_.trade_date <= to_date
                    )
                )

            if conditions:
                query = query.where(and_(*conditions))

            # Distinct stocks only
            query = query.distinct()

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            stocks = result.scalars().all()

            self.logger.debug(
                "Stocks with breakout data retrieved",
                from_date=from_date,
                to_date=to_date,
                count=len(stocks),
            )
            return list(stocks)

        except Exception as e:
            self.logger.error(
                "Failed to get stocks with breakout data",
                from_date=from_date,
                to_date=to_date,
                error=str(e),
            )
            raise

    # Statistics and aggregation

    async def get_stocks_count_by_group(
        self, active_only: bool = True
    ) -> dict[str, int]:
        """
        Get count of stocks by NSE group

        Args:
            active_only: Whether to count only active stocks

        Returns:
            Dictionary with group name as key and count as value
        """
        try:
            query = select(Stock.stock_group, func.count(Stock.id)).group_by(
                Stock.stock_group
            )

            if active_only:
                query = query.where(Stock.is_active)

            result = await self.session.execute(query)
            group_counts = {}

            for group, count in result:
                group_counts[group.value] = count

            self.logger.debug("Stock counts by group retrieved", counts=group_counts)
            return group_counts

        except Exception as e:
            self.logger.error("Failed to get stock counts by group", error=str(e))
            raise

    async def get_stocks_count_by_sector(
        self, active_only: bool = True
    ) -> dict[str, int]:
        """
        Get count of stocks by sector

        Args:
            active_only: Whether to count only active stocks

        Returns:
            Dictionary with sector name as key and count as value
        """
        try:
            query = select(Stock.sector, func.count(Stock.id)).group_by(Stock.sector)

            if active_only:
                query = query.where(Stock.is_active)

            result = await self.session.execute(query)
            sector_counts = {}

            for sector, count in result:
                if sector:  # Skip None sectors
                    sector_counts[sector] = count

            self.logger.debug("Stock counts by sector retrieved", counts=sector_counts)
            return sector_counts

        except Exception as e:
            self.logger.error("Failed to get stock counts by sector", error=str(e))
            raise

    # V1 compatibility methods

    async def get_or_create_from_v1_data(
        self, script_name: str, group_name: str, company_name: str | None = None
    ) -> tuple[Stock, bool]:
        """
        Get existing stock or create from V1 data format

        Args:
            script_name: V1 script_name (stock symbol)
            group_name: V1 group_name (NSE index)
            company_name: Optional company name

        Returns:
            Tuple of (Stock, created) where created is True if stock was created
        """
        try:
            symbol = script_name.strip().upper()

            # Try to get existing stock
            existing_stock = await self.get_by_symbol(symbol)
            if existing_stock:
                self.logger.debug("Existing stock found for V1 data", symbol=symbol)
                return existing_stock, False

            # Create new stock from V1 data
            stock = Stock.from_v1_data(script_name, group_name, company_name)
            created_stock = await self.create(stock.to_dict())

            self.logger.info(
                "Stock created from V1 data", symbol=symbol, group=group_name
            )
            return created_stock, True

        except Exception as e:
            self.logger.error(
                "Failed to get or create stock from V1 data",
                script_name=script_name,
                group_name=group_name,
                error=str(e),
            )
            raise

    async def bulk_create_from_v1_data(
        self, v1_stock_data: list[dict[str, str]]
    ) -> list[Stock]:
        """
        Bulk create stocks from V1 data format

        Args:
            v1_stock_data: List of V1 stock data dictionaries

        Returns:
            List of created stocks
        """
        try:
            stocks_to_create = []

            for v1_data in v1_stock_data:
                script_name = v1_data.get("script_name", "")
                group_name = v1_data.get("group_name", "")
                company_name = v1_data.get("company_name")

                if not script_name or not group_name:
                    continue

                symbol = script_name.strip().upper()

                # Check if stock already exists
                existing = await self.get_by_symbol(symbol)
                if existing:
                    continue

                # Create stock data
                stock_data = Stock.from_v1_data(
                    script_name, group_name, company_name
                ).to_dict()
                stocks_to_create.append(stock_data)

            if not stocks_to_create:
                self.logger.info("No new stocks to create from V1 data")
                return []

            # Bulk create
            created_stocks = await self.bulk_create(stocks_to_create)

            self.logger.info(
                "Bulk created stocks from V1 data", count=len(created_stocks)
            )
            return created_stocks

        except Exception as e:
            self.logger.error("Failed to bulk create stocks from V1 data", error=str(e))
            raise

    # Advanced filtering

    async def get_stocks_by_advanced_filter(
        self,
        filters: StockFilterParams,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None,
    ) -> list[Stock]:
        """
        Get stocks using advanced filter parameters

        Args:
            filters: Advanced filter parameters
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load

        Returns:
            List of filtered stocks
        """
        try:
            query = select(Stock)

            conditions = []

            # Apply filters
            if filters.symbol:
                conditions.append(Stock.symbol.ilike(f"%{filters.symbol.upper()}%"))

            if filters.company_name:
                conditions.append(Stock.company_name.ilike(f"%{filters.company_name}%"))

            if filters.stock_group:
                conditions.append(Stock.stock_group == filters.stock_group)

            if filters.sector:
                conditions.append(Stock.sector.ilike(f"%{filters.sector}%"))

            if filters.is_active is not None:
                conditions.append(Stock.is_active == filters.is_active)

            if filters.market_cap_min is not None:
                conditions.append(Stock.market_cap >= filters.market_cap_min)

            if filters.market_cap_max is not None:
                conditions.append(Stock.market_cap <= filters.market_cap_max)

            # Apply additional filters from base class
            for key, value in filters.filters.items():
                if hasattr(Stock, key):
                    conditions.append(getattr(Stock, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(Stock, sort.sort_by):
                    sort_column = getattr(Stock, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(sort_column.desc())
                    else:
                        query = query.order_by(sort_column.asc())

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(Stock, relationship):
                        query = query.options(
                            selectinload(getattr(Stock, relationship))
                        )

            result = await self.session.execute(query)
            stocks = result.scalars().all()

            self.logger.debug("Stocks retrieved by advanced filter", count=len(stocks))
            return list(stocks)

        except Exception as e:
            self.logger.error("Failed to get stocks by advanced filter", error=str(e))
            raise

    async def count_by_advanced_filter(
        self, filters: dict[str, Any] | None = None
    ) -> int:
        """
        Count stocks matching advanced filter parameters

        Args:
            filters: Advanced filter parameters

        Returns:
            Total count of matching stocks
        """
        try:
            query = select(func.count(Stock.id))
            conditions = []

            if filters:
                # Apply same filtering logic as get_by_advanced_filter
                for key, value in filters.items():
                    if value is not None and hasattr(Stock, key):
                        if key in ["symbol", "company_name", "sector"]:
                            conditions.append(getattr(Stock, key).ilike(f"%{value}%"))
                        else:
                            conditions.append(getattr(Stock, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            count = result.scalar() or 0

            self.logger.debug("Stock count by advanced filter", count=count)
            return count

        except Exception as e:
            self.logger.error("Failed to count stocks by advanced filter", error=str(e))
            raise

    async def get_by_symbols(
        self, symbols: list[str], load_relationships: list[str] | None = None
    ) -> list[Stock]:
        """
        Get stocks by list of symbols

        Args:
            symbols: List of stock symbols
            load_relationships: List of relationships to eager load

        Returns:
            List of stocks matching the symbols
        """
        try:
            if not symbols:
                return []

            symbol_list = [s.upper() for s in symbols]
            query = select(Stock).where(Stock.symbol.in_(symbol_list))

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(Stock, relationship):
                        query = query.options(
                            selectinload(getattr(Stock, relationship))
                        )

            result = await self.session.execute(query)
            stocks = result.scalars().all()

            self.logger.debug(
                "Stocks retrieved by symbols", symbols=symbols, count=len(stocks)
            )
            return list(stocks)

        except Exception as e:
            self.logger.error(
                "Failed to get stocks by symbols", symbols=symbols, error=str(e)
            )
            raise
