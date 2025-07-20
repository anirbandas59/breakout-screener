"""
BreakoutData repository with filtering, aggregation, and date range queries
"""

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.breakout_data import BreakoutData
from ..models.enums import AnalysisStatusEnum, BreakoutStatusEnum, PivotTypeEnum
from ..models.stock import Stock
from .base import (
    BaseRepository,
    FilterParams,
    PaginationParams,
    SortParams,
)

logger = get_logger(__name__)


class BreakoutDataFilterParams(FilterParams):
    """BreakoutData-specific filter parameters"""

    def __init__(
        self,
        symbol: str | None = None,
        trade_date_from: date | None = None,
        trade_date_to: date | None = None,
        breakout_status: BreakoutStatusEnum | None = None,
        pivot_type: PivotTypeEnum | None = None,
        analysis_status: AnalysisStatusEnum | None = None,
        is_analyzed: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_volume: int | None = None,
        max_volume: int | None = None,
        min_cpr_width: float | None = None,
        max_cpr_width: float | None = None,
        has_breakout: bool | None = None,
        **kwargs
    ):
        self.symbol = symbol
        self.trade_date_from = trade_date_from
        self.trade_date_to = trade_date_to
        self.breakout_status = breakout_status
        self.pivot_type = pivot_type
        self.analysis_status = analysis_status
        self.is_analyzed = is_analyzed
        self.min_price = min_price
        self.max_price = max_price
        self.min_volume = min_volume
        self.max_volume = max_volume
        self.min_cpr_width = min_cpr_width
        self.max_cpr_width = max_cpr_width
        self.has_breakout = has_breakout

        # Call parent with remaining filters
        super().__init__(**kwargs)


class BreakoutDataRepository(BaseRepository[BreakoutData]):
    """
    Repository for BreakoutData model with business-specific operations.
    Provides queries for breakout analysis, filtering, and aggregation.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, BreakoutData)

    # Unique field implementations

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> BreakoutData | None:
        """Get breakout data by unique field (symbol + trade_date combination)"""
        if field_name == "symbol_date":
            # Expecting field_value to be a tuple (symbol, trade_date)
            if isinstance(field_value, tuple) and len(field_value) == 2:
                return await self.get_by_symbol_and_date(field_value[0], field_value[1])
            else:
                raise ValueError("Field value for 'symbol_date' must be a tuple (symbol, trade_date)")
        else:
            raise ValueError(f"Field '{field_name}' is not a unique field for BreakoutData")

    async def get_by_symbol_and_date(
        self,
        symbol: str,
        trade_date: date,
        load_relationships: list[str] | None = None
    ) -> BreakoutData | None:
        """
        Get breakout data by symbol and trade date
        
        Args:
            symbol: Stock symbol
            trade_date: Trading date
            load_relationships: List of relationships to eager load
            
        Returns:
            BreakoutData if found, None otherwise
        """
        try:
            query = select(BreakoutData).join(BreakoutData.stock).where(
                and_(
                    BreakoutData.stock.has(symbol=symbol.upper()),
                    BreakoutData.trade_date == trade_date
                )
            )

            # Add eager loading if specified
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(BreakoutData, relationship):
                        query = query.options(selectinload(getattr(BreakoutData, relationship)))

            result = await self.session.execute(query)
            breakout_data = result.scalar_one_or_none()

            if breakout_data:
                self.logger.debug("BreakoutData retrieved", symbol=symbol, trade_date=trade_date)
            else:
                self.logger.debug("BreakoutData not found", symbol=symbol, trade_date=trade_date)

            return breakout_data

        except Exception as e:
            self.logger.error(
                "Failed to get breakout data by symbol and date",
                symbol=symbol,
                trade_date=trade_date,
                error=str(e)
            )
            raise

    # Date range queries

    async def get_by_date_range(
        self,
        from_date: date,
        to_date: date,
        symbols: list[str] | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[BreakoutData]:
        """
        Get breakout data within date range
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            symbols: Optional list of symbols to filter by
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of breakout data within date range
        """
        try:
            query = select(BreakoutData).where(
                and_(
                    BreakoutData.trade_date >= from_date,
                    BreakoutData.trade_date <= to_date
                )
            )

            # Filter by symbols if provided
            if symbols:
                symbol_list = [s.upper() for s in symbols]
                query = query.join(BreakoutData.stock).where(
                    BreakoutData.stock.has(Stock.symbol.in_(symbol_list))
                )

            # Add sorting
            if sort:
                if hasattr(BreakoutData, sort.sort_by):
                    sort_column = getattr(BreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by trade_date descending, then symbol
                query = query.join(BreakoutData.stock).order_by(
                    desc(BreakoutData.trade_date),
                    BreakoutData.stock.has(symbol=asc(BreakoutData.stock.property.mapper.class_.symbol))
                )

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(BreakoutData, relationship):
                        query = query.options(selectinload(getattr(BreakoutData, relationship)))

            result = await self.session.execute(query)
            breakout_data_list = result.scalars().all()

            self.logger.debug(
                "BreakoutData retrieved by date range",
                from_date=from_date,
                to_date=to_date,
                symbols=symbols,
                count=len(breakout_data_list)
            )
            return list(breakout_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get breakout data by date range",
                from_date=from_date,
                to_date=to_date,
                symbols=symbols,
                error=str(e)
            )
            raise

    async def get_latest_by_symbol(
        self,
        symbol: str,
        limit: int = 10,
        load_relationships: list[str] | None = None
    ) -> list[BreakoutData]:
        """
        Get latest breakout data for a symbol
        
        Args:
            symbol: Stock symbol
            limit: Number of latest records to return
            load_relationships: List of relationships to eager load
            
        Returns:
            List of latest breakout data for symbol
        """
        try:
            query = select(BreakoutData).join(BreakoutData.stock).where(
                BreakoutData.stock.has(symbol=symbol.upper())
            ).order_by(desc(BreakoutData.trade_date)).limit(limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(BreakoutData, relationship):
                        query = query.options(selectinload(getattr(BreakoutData, relationship)))

            result = await self.session.execute(query)
            breakout_data_list = result.scalars().all()

            self.logger.debug(
                "Latest breakout data retrieved",
                symbol=symbol,
                limit=limit,
                count=len(breakout_data_list)
            )
            return list(breakout_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get latest breakout data by symbol",
                symbol=symbol,
                limit=limit,
                error=str(e)
            )
            raise

    # Business logic queries

    async def get_breakouts_by_status(
        self,
        breakout_status: BreakoutStatusEnum,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[BreakoutData]:
        """
        Get breakout data by breakout status
        
        Args:
            breakout_status: Breakout status to filter by
            from_date: Optional start date
            to_date: Optional end date
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of breakout data with specified status
        """
        try:
            query = select(BreakoutData).where(
                BreakoutData.breakout_status == breakout_status
            )

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(BreakoutData.trade_date >= from_date)
            if to_date:
                conditions.append(BreakoutData.trade_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(BreakoutData, sort.sort_by):
                    sort_column = getattr(BreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(BreakoutData.trade_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            breakout_data_list = result.scalars().all()

            self.logger.debug(
                "BreakoutData retrieved by status",
                status=breakout_status.value,
                from_date=from_date,
                to_date=to_date,
                count=len(breakout_data_list)
            )
            return list(breakout_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get breakout data by status",
                status=breakout_status.value,
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    async def get_unanalyzed_data(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationParams | None = None
    ) -> list[BreakoutData]:
        """
        Get unanalyzed breakout data
        
        Args:
            from_date: Optional start date
            to_date: Optional end date
            pagination: Pagination parameters
            
        Returns:
            List of unanalyzed breakout data
        """
        try:
            query = select(BreakoutData).where(
                or_(
                    BreakoutData.is_analyzed == False,
                    BreakoutData.analysis_status == AnalysisStatusEnum.PENDING
                )
            )

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(BreakoutData.trade_date >= from_date)
            if to_date:
                conditions.append(BreakoutData.trade_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            # Order by trade_date ascending (oldest first)
            query = query.order_by(asc(BreakoutData.trade_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            breakout_data_list = result.scalars().all()

            self.logger.debug(
                "Unanalyzed breakout data retrieved",
                from_date=from_date,
                to_date=to_date,
                count=len(breakout_data_list)
            )
            return list(breakout_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get unanalyzed breakout data",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # Advanced filtering

    async def get_by_advanced_filter(
        self,
        filters: BreakoutDataFilterParams,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[BreakoutData]:
        """
        Get breakout data using advanced filter parameters
        
        Args:
            filters: Advanced filter parameters
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of filtered breakout data
        """
        try:
            query = select(BreakoutData)
            conditions = []

            # Symbol filter (requires join with stock)
            if filters.symbol:
                query = query.join(BreakoutData.stock)
                conditions.append(BreakoutData.stock.has(symbol=filters.symbol.upper()))

            # Date range filters
            if filters.trade_date_from:
                conditions.append(BreakoutData.trade_date >= filters.trade_date_from)
            if filters.trade_date_to:
                conditions.append(BreakoutData.trade_date <= filters.trade_date_to)

            # Status filters
            if filters.breakout_status:
                conditions.append(BreakoutData.breakout_status == filters.breakout_status)
            if filters.pivot_type:
                conditions.append(BreakoutData.pivot_type == filters.pivot_type)
            if filters.analysis_status:
                conditions.append(BreakoutData.analysis_status == filters.analysis_status)
            if filters.is_analyzed is not None:
                conditions.append(BreakoutData.is_analyzed == filters.is_analyzed)

            # Price range filters
            if filters.min_price is not None:
                conditions.append(BreakoutData.close_price >= filters.min_price)
            if filters.max_price is not None:
                conditions.append(BreakoutData.close_price <= filters.max_price)

            # Volume range filters
            if filters.min_volume is not None:
                conditions.append(BreakoutData.volume >= filters.min_volume)
            if filters.max_volume is not None:
                conditions.append(BreakoutData.volume <= filters.max_volume)

            # CPR width filters
            if filters.min_cpr_width is not None:
                cpr_width = BreakoutData.tc - BreakoutData.bc
                conditions.append(cpr_width >= filters.min_cpr_width)
            if filters.max_cpr_width is not None:
                cpr_width = BreakoutData.tc - BreakoutData.bc
                conditions.append(cpr_width <= filters.max_cpr_width)

            # Breakout existence filter
            if filters.has_breakout is not None:
                if filters.has_breakout:
                    conditions.append(BreakoutData.breakout_status != BreakoutStatusEnum.NO_BREAKOUT)
                else:
                    conditions.append(BreakoutData.breakout_status == BreakoutStatusEnum.NO_BREAKOUT)

            # Apply additional filters from base class
            for key, value in filters.filters.items():
                if hasattr(BreakoutData, key):
                    conditions.append(getattr(BreakoutData, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(BreakoutData, sort.sort_by):
                    sort_column = getattr(BreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by trade_date descending
                query = query.order_by(desc(BreakoutData.trade_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(BreakoutData, relationship):
                        query = query.options(selectinload(getattr(BreakoutData, relationship)))

            result = await self.session.execute(query)
            breakout_data_list = result.scalars().all()

            self.logger.debug(
                "BreakoutData retrieved by advanced filter",
                count=len(breakout_data_list)
            )
            return list(breakout_data_list)

        except Exception as e:
            self.logger.error("Failed to get breakout data by advanced filter", error=str(e))
            raise

    # Aggregation queries

    async def get_breakout_counts_by_status(
        self,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> dict[str, int]:
        """
        Get count of breakouts by status
        
        Args:
            from_date: Optional start date
            to_date: Optional end date
            
        Returns:
            Dictionary with status as key and count as value
        """
        try:
            query = select(
                BreakoutData.breakout_status,
                func.count(BreakoutData.id)
            ).group_by(BreakoutData.breakout_status)

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(BreakoutData.trade_date >= from_date)
            if to_date:
                conditions.append(BreakoutData.trade_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            status_counts = {}

            for status, count in result:
                status_counts[status.value] = count

            self.logger.debug(
                "Breakout counts by status retrieved",
                from_date=from_date,
                to_date=to_date,
                counts=status_counts
            )
            return status_counts

        except Exception as e:
            self.logger.error(
                "Failed to get breakout counts by status",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    async def get_daily_breakout_summary(
        self,
        from_date: date,
        to_date: date
    ) -> list[dict[str, Any]]:
        """
        Get daily breakout summary with counts and statistics
        
        Args:
            from_date: Start date
            to_date: End date
            
        Returns:
            List of daily summary dictionaries
        """
        try:
            query = select(
                BreakoutData.trade_date,
                func.count(BreakoutData.id).label('total_records'),
                func.count(BreakoutData.id).filter(
                    BreakoutData.breakout_status != BreakoutStatusEnum.NO_BREAKOUT
                ).label('breakout_count'),
                func.avg(BreakoutData.volume).label('avg_volume'),
                func.avg(BreakoutData.close_price).label('avg_price'),
                func.count(BreakoutData.id).filter(
                    BreakoutData.is_analyzed == True
                ).label('analyzed_count')
            ).where(
                and_(
                    BreakoutData.trade_date >= from_date,
                    BreakoutData.trade_date <= to_date
                )
            ).group_by(BreakoutData.trade_date).order_by(BreakoutData.trade_date)

            result = await self.session.execute(query)
            daily_summaries = []

            for row in result:
                summary = {
                    'trade_date': row.trade_date,
                    'total_records': row.total_records,
                    'breakout_count': row.breakout_count or 0,
                    'avg_volume': float(row.avg_volume) if row.avg_volume else 0.0,
                    'avg_price': float(row.avg_price) if row.avg_price else 0.0,
                    'analyzed_count': row.analyzed_count or 0,
                    'breakout_percentage': (
                        (row.breakout_count / row.total_records * 100)
                        if row.total_records > 0 and row.breakout_count else 0.0
                    ),
                    'analysis_percentage': (
                        (row.analyzed_count / row.total_records * 100)
                        if row.total_records > 0 and row.analyzed_count else 0.0
                    )
                }
                daily_summaries.append(summary)

            self.logger.debug(
                "Daily breakout summary retrieved",
                from_date=from_date,
                to_date=to_date,
                days_count=len(daily_summaries)
            )
            return daily_summaries

        except Exception as e:
            self.logger.error(
                "Failed to get daily breakout summary",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # V1 compatibility methods

    async def get_or_create_from_v1_data(
        self,
        v1_data: dict[str, Any],
        stock_id: UUID
    ) -> tuple[BreakoutData, bool]:
        """
        Get existing breakout data or create from V1 data format
        
        Args:
            v1_data: V1 breakout data dictionary
            stock_id: UUID of the related stock
            
        Returns:
            Tuple of (BreakoutData, created) where created is True if data was created
        """
        try:
            trade_date = v1_data.get('trade_date')
            symbol = v1_data.get('script_name', '').strip().upper()

            if not trade_date or not symbol:
                raise ValueError("V1 data must contain trade_date and script_name")

            # Try to get existing data
            existing_data = await self.get_by_symbol_and_date(symbol, trade_date)
            if existing_data:
                self.logger.debug(
                    "Existing breakout data found for V1 data",
                    symbol=symbol,
                    trade_date=trade_date
                )
                return existing_data, False

            # Create new breakout data from V1 data
            breakout_data = BreakoutData.from_v1_data(v1_data, stock_id)
            created_data = await self.create(breakout_data.to_dict())

            self.logger.info(
                "BreakoutData created from V1 data",
                symbol=symbol,
                trade_date=trade_date
            )
            return created_data, True

        except Exception as e:
            self.logger.error(
                "Failed to get or create breakout data from V1 data",
                error=str(e)
            )
            raise

    async def bulk_create_from_v1_data(
        self,
        v1_data_list: list[dict[str, Any]],
        stock_mapping: dict[str, UUID]
    ) -> list[BreakoutData]:
        """
        Bulk create breakout data from V1 data format
        
        Args:
            v1_data_list: List of V1 breakout data dictionaries
            stock_mapping: Mapping of symbol to stock UUID
            
        Returns:
            List of created breakout data
        """
        try:
            data_to_create = []

            for v1_data in v1_data_list:
                symbol = v1_data.get('script_name', '').strip().upper()
                trade_date = v1_data.get('trade_date')

                if not symbol or not trade_date or symbol not in stock_mapping:
                    continue

                # Check if data already exists
                existing = await self.get_by_symbol_and_date(symbol, trade_date)
                if existing:
                    continue

                # Create breakout data
                stock_id = stock_mapping[symbol]
                breakout_data = BreakoutData.from_v1_data(v1_data, stock_id)
                data_to_create.append(breakout_data.to_dict())

            if not data_to_create:
                self.logger.info("No new breakout data to create from V1 data")
                return []

            # Bulk create
            created_data = await self.bulk_create(data_to_create)

            self.logger.info(
                "Bulk created breakout data from V1 data",
                count=len(created_data)
            )
            return created_data

        except Exception as e:
            self.logger.error("Failed to bulk create breakout data from V1 data", error=str(e))
            raise
