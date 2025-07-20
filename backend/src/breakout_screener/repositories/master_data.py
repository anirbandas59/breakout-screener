"""
MasterBreakoutData repository for historical snapshots and analysis
"""

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.master_data import MasterBreakoutData
from ..models.stock import Stock
from .base import (
    BaseRepository,
    FilterParams,
    PaginationParams,
    SortParams,
)

logger = get_logger(__name__)


class MasterBreakoutDataFilterParams(FilterParams):
    """MasterBreakoutData-specific filter parameters"""

    def __init__(
        self,
        symbol: str | None = None,
        snapshot_date_from: date | None = None,
        snapshot_date_to: date | None = None,
        data_source: str | None = None,
        is_active: bool | None = None,
        has_breakout_data: bool | None = None,
        **kwargs
    ):
        self.symbol = symbol
        self.snapshot_date_from = snapshot_date_from
        self.snapshot_date_to = snapshot_date_to
        self.data_source = data_source
        self.is_active = is_active
        self.has_breakout_data = has_breakout_data

        # Call parent with remaining filters
        super().__init__(**kwargs)


class MasterBreakoutDataRepository(BaseRepository[MasterBreakoutData]):
    """
    Repository for MasterBreakoutData model with business-specific operations.
    Provides queries for historical data snapshots and analysis tracking.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, MasterBreakoutData)

    # Unique field implementations

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> MasterBreakoutData | None:
        """Get master breakout data by unique field (symbol + snapshot_date combination)"""
        if field_name == "symbol_snapshot":
            # Expecting field_value to be a tuple (symbol, snapshot_date)
            if isinstance(field_value, tuple) and len(field_value) == 2:
                return await self.get_by_symbol_and_snapshot_date(field_value[0], field_value[1])
            else:
                raise ValueError("Field value for 'symbol_snapshot' must be a tuple (symbol, snapshot_date)")
        else:
            raise ValueError(f"Field '{field_name}' is not a unique field for MasterBreakoutData")

    async def get_by_symbol_and_snapshot_date(
        self,
        symbol: str,
        snapshot_date: date,
        load_relationships: list[str] | None = None
    ) -> MasterBreakoutData | None:
        """
        Get master breakout data by symbol and snapshot date
        
        Args:
            symbol: Stock symbol
            snapshot_date: Snapshot date
            load_relationships: List of relationships to eager load
            
        Returns:
            MasterBreakoutData if found, None otherwise
        """
        try:
            query = select(MasterBreakoutData).join(MasterBreakoutData.stock).where(
                and_(
                    MasterBreakoutData.stock.has(symbol=symbol.upper()),
                    MasterBreakoutData.snapshot_date == snapshot_date
                )
            )

            # Add eager loading if specified
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(MasterBreakoutData, relationship):
                        query = query.options(selectinload(getattr(MasterBreakoutData, relationship)))

            result = await self.session.execute(query)
            master_data = result.scalar_one_or_none()

            if master_data:
                self.logger.debug("MasterBreakoutData retrieved", symbol=symbol, snapshot_date=snapshot_date)
            else:
                self.logger.debug("MasterBreakoutData not found", symbol=symbol, snapshot_date=snapshot_date)

            return master_data

        except Exception as e:
            self.logger.error(
                "Failed to get master breakout data by symbol and snapshot date",
                symbol=symbol,
                snapshot_date=snapshot_date,
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
    ) -> list[MasterBreakoutData]:
        """
        Get master breakout data within date range
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            symbols: Optional list of symbols to filter by
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of master breakout data within date range
        """
        try:
            query = select(MasterBreakoutData).where(
                and_(
                    MasterBreakoutData.snapshot_date >= from_date,
                    MasterBreakoutData.snapshot_date <= to_date
                )
            )

            # Filter by symbols if provided
            if symbols:
                symbol_list = [s.upper() for s in symbols]
                query = query.join(MasterBreakoutData.stock).where(
                    MasterBreakoutData.stock.has(Stock.symbol.in_(symbol_list))
                )

            # Add sorting
            if sort:
                if hasattr(MasterBreakoutData, sort.sort_by):
                    sort_column = getattr(MasterBreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by snapshot_date descending
                query = query.order_by(desc(MasterBreakoutData.snapshot_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(MasterBreakoutData, relationship):
                        query = query.options(selectinload(getattr(MasterBreakoutData, relationship)))

            result = await self.session.execute(query)
            master_data_list = result.scalars().all()

            self.logger.debug(
                "MasterBreakoutData retrieved by date range",
                from_date=from_date,
                to_date=to_date,
                symbols=symbols,
                count=len(master_data_list)
            )
            return list(master_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get master breakout data by date range",
                from_date=from_date,
                to_date=to_date,
                symbols=symbols,
                error=str(e)
            )
            raise

    async def get_latest_snapshot(
        self,
        symbol: str | None = None,
        limit: int = 100,
        load_relationships: list[str] | None = None
    ) -> list[MasterBreakoutData]:
        """
        Get latest snapshot data
        
        Args:
            symbol: Optional symbol to filter by
            limit: Number of latest records to return
            load_relationships: List of relationships to eager load
            
        Returns:
            List of latest master breakout data
        """
        try:
            query = select(MasterBreakoutData)

            if symbol:
                query = query.join(MasterBreakoutData.stock).where(
                    MasterBreakoutData.stock.has(symbol=symbol.upper())
                )

            query = query.order_by(desc(MasterBreakoutData.snapshot_date)).limit(limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(MasterBreakoutData, relationship):
                        query = query.options(selectinload(getattr(MasterBreakoutData, relationship)))

            result = await self.session.execute(query)
            master_data_list = result.scalars().all()

            self.logger.debug(
                "Latest master breakout data retrieved",
                symbol=symbol,
                limit=limit,
                count=len(master_data_list)
            )
            return list(master_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get latest master breakout data",
                symbol=symbol,
                limit=limit,
                error=str(e)
            )
            raise

    # Business logic queries

    async def get_active_snapshots(
        self,
        snapshot_date: date | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[MasterBreakoutData]:
        """
        Get active snapshots for a specific date or latest
        
        Args:
            snapshot_date: Optional snapshot date (defaults to latest)
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of active master breakout data
        """
        try:
            query = select(MasterBreakoutData).where(MasterBreakoutData.is_active == True)

            if snapshot_date:
                query = query.where(MasterBreakoutData.snapshot_date == snapshot_date)
            else:
                # Get latest snapshot date
                latest_date_query = select(func.max(MasterBreakoutData.snapshot_date))
                latest_date_result = await self.session.execute(latest_date_query)
                latest_date = latest_date_result.scalar()

                if latest_date:
                    query = query.where(MasterBreakoutData.snapshot_date == latest_date)

            # Add sorting
            if sort:
                if hasattr(MasterBreakoutData, sort.sort_by):
                    sort_column = getattr(MasterBreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by updated_at descending
                query = query.order_by(desc(MasterBreakoutData.updated_at))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            master_data_list = result.scalars().all()

            self.logger.debug(
                "Active master breakout data retrieved",
                snapshot_date=snapshot_date,
                count=len(master_data_list)
            )
            return list(master_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get active master breakout data",
                snapshot_date=snapshot_date,
                error=str(e)
            )
            raise

    async def get_by_data_source(
        self,
        data_source: str,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[MasterBreakoutData]:
        """
        Get master breakout data by data source
        
        Args:
            data_source: Data source identifier
            from_date: Optional start date
            to_date: Optional end date
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of master breakout data from specified source
        """
        try:
            query = select(MasterBreakoutData).where(
                MasterBreakoutData.data_source == data_source
            )

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(MasterBreakoutData.snapshot_date >= from_date)
            if to_date:
                conditions.append(MasterBreakoutData.snapshot_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(MasterBreakoutData, sort.sort_by):
                    sort_column = getattr(MasterBreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(MasterBreakoutData.snapshot_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            master_data_list = result.scalars().all()

            self.logger.debug(
                "MasterBreakoutData retrieved by data source",
                data_source=data_source,
                from_date=from_date,
                to_date=to_date,
                count=len(master_data_list)
            )
            return list(master_data_list)

        except Exception as e:
            self.logger.error(
                "Failed to get master breakout data by data source",
                data_source=data_source,
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # Advanced filtering

    async def get_by_advanced_filter(
        self,
        filters: MasterBreakoutDataFilterParams,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[MasterBreakoutData]:
        """
        Get master breakout data using advanced filter parameters
        
        Args:
            filters: Advanced filter parameters
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of filtered master breakout data
        """
        try:
            query = select(MasterBreakoutData)
            conditions = []

            # Symbol filter (requires join with stock)
            if filters.symbol:
                query = query.join(MasterBreakoutData.stock)
                conditions.append(MasterBreakoutData.stock.has(symbol=filters.symbol.upper()))

            # Date range filters
            if filters.snapshot_date_from:
                conditions.append(MasterBreakoutData.snapshot_date >= filters.snapshot_date_from)
            if filters.snapshot_date_to:
                conditions.append(MasterBreakoutData.snapshot_date <= filters.snapshot_date_to)

            # Data source filter
            if filters.data_source:
                conditions.append(MasterBreakoutData.data_source == filters.data_source)

            # Active status filter
            if filters.is_active is not None:
                conditions.append(MasterBreakoutData.is_active == filters.is_active)

            # Breakout data existence filter
            if filters.has_breakout_data is not None:
                if filters.has_breakout_data:
                    conditions.append(MasterBreakoutData.breakout_data_id.isnot(None))
                else:
                    conditions.append(MasterBreakoutData.breakout_data_id.is_(None))

            # Apply additional filters from base class
            for key, value in filters.filters.items():
                if hasattr(MasterBreakoutData, key):
                    conditions.append(getattr(MasterBreakoutData, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(MasterBreakoutData, sort.sort_by):
                    sort_column = getattr(MasterBreakoutData, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by snapshot_date descending
                query = query.order_by(desc(MasterBreakoutData.snapshot_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(MasterBreakoutData, relationship):
                        query = query.options(selectinload(getattr(MasterBreakoutData, relationship)))

            result = await self.session.execute(query)
            master_data_list = result.scalars().all()

            self.logger.debug(
                "MasterBreakoutData retrieved by advanced filter",
                count=len(master_data_list)
            )
            return list(master_data_list)

        except Exception as e:
            self.logger.error("Failed to get master breakout data by advanced filter", error=str(e))
            raise

    # Aggregation queries

    async def get_snapshot_summary(
        self,
        snapshot_date: date
    ) -> dict[str, Any]:
        """
        Get summary statistics for a snapshot date
        
        Args:
            snapshot_date: Snapshot date
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            query = select(
                func.count(MasterBreakoutData.id).label('total_records'),
                func.count(MasterBreakoutData.id).filter(
                    MasterBreakoutData.is_active == True
                ).label('active_records'),
                func.count(MasterBreakoutData.id).filter(
                    MasterBreakoutData.breakout_data_id.isnot(None)
                ).label('with_breakout_data'),
                func.count(func.distinct(MasterBreakoutData.data_source)).label('unique_sources')
            ).where(MasterBreakoutData.snapshot_date == snapshot_date)

            result = await self.session.execute(query)
            row = result.first()

            summary = {
                'snapshot_date': snapshot_date,
                'total_records': row.total_records if row else 0,
                'active_records': row.active_records if row else 0,
                'with_breakout_data': row.with_breakout_data if row else 0,
                'unique_sources': row.unique_sources if row else 0,
                'active_percentage': (
                    (row.active_records / row.total_records * 100)
                    if row and row.total_records > 0 else 0.0
                ),
                'breakout_data_percentage': (
                    (row.with_breakout_data / row.total_records * 100)
                    if row and row.total_records > 0 else 0.0
                )
            }

            self.logger.debug(
                "Snapshot summary retrieved",
                snapshot_date=snapshot_date,
                summary=summary
            )
            return summary

        except Exception as e:
            self.logger.error(
                "Failed to get snapshot summary",
                snapshot_date=snapshot_date,
                error=str(e)
            )
            raise

    async def get_data_source_summary(
        self,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> list[dict[str, Any]]:
        """
        Get summary by data source
        
        Args:
            from_date: Optional start date
            to_date: Optional end date
            
        Returns:
            List of data source summaries
        """
        try:
            query = select(
                MasterBreakoutData.data_source,
                func.count(MasterBreakoutData.id).label('total_records'),
                func.count(MasterBreakoutData.id).filter(
                    MasterBreakoutData.is_active == True
                ).label('active_records'),
                func.min(MasterBreakoutData.snapshot_date).label('earliest_date'),
                func.max(MasterBreakoutData.snapshot_date).label('latest_date')
            ).group_by(MasterBreakoutData.data_source)

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(MasterBreakoutData.snapshot_date >= from_date)
            if to_date:
                conditions.append(MasterBreakoutData.snapshot_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(desc(func.count(MasterBreakoutData.id)))

            result = await self.session.execute(query)
            summaries = []

            for row in result:
                summary = {
                    'data_source': row.data_source,
                    'total_records': row.total_records,
                    'active_records': row.active_records,
                    'earliest_date': row.earliest_date,
                    'latest_date': row.latest_date,
                    'active_percentage': (
                        (row.active_records / row.total_records * 100)
                        if row.total_records > 0 else 0.0
                    )
                }
                summaries.append(summary)

            self.logger.debug(
                "Data source summary retrieved",
                from_date=from_date,
                to_date=to_date,
                sources_count=len(summaries)
            )
            return summaries

        except Exception as e:
            self.logger.error(
                "Failed to get data source summary",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # V1 compatibility methods

    async def get_or_create_from_v1_data(
        self,
        v1_data: dict[str, Any],
        stock_id: UUID,
        snapshot_date: date | None = None
    ) -> tuple[MasterBreakoutData, bool]:
        """
        Get existing master data or create from V1 data format
        
        Args:
            v1_data: V1 master data dictionary
            stock_id: UUID of the related stock
            snapshot_date: Optional snapshot date (defaults to current date)
            
        Returns:
            Tuple of (MasterBreakoutData, created) where created is True if data was created
        """
        try:
            symbol = v1_data.get('script_name', '').strip().upper()
            snapshot_date = snapshot_date or date.today()

            if not symbol:
                raise ValueError("V1 data must contain script_name")

            # Try to get existing data
            existing_data = await self.get_by_symbol_and_snapshot_date(symbol, snapshot_date)
            if existing_data:
                self.logger.debug(
                    "Existing master data found for V1 data",
                    symbol=symbol,
                    snapshot_date=snapshot_date
                )
                return existing_data, False

            # Create new master data from V1 data
            master_data = MasterBreakoutData.from_v1_data(v1_data, stock_id, snapshot_date)
            created_data = await self.create(master_data.to_dict())

            self.logger.info(
                "MasterBreakoutData created from V1 data",
                symbol=symbol,
                snapshot_date=snapshot_date
            )
            return created_data, True

        except Exception as e:
            self.logger.error(
                "Failed to get or create master data from V1 data",
                error=str(e)
            )
            raise

    async def bulk_create_from_v1_data(
        self,
        v1_data_list: list[dict[str, Any]],
        stock_mapping: dict[str, UUID],
        snapshot_date: date | None = None
    ) -> list[MasterBreakoutData]:
        """
        Bulk create master data from V1 data format
        
        Args:
            v1_data_list: List of V1 master data dictionaries
            stock_mapping: Mapping of symbol to stock UUID
            snapshot_date: Optional snapshot date (defaults to current date)
            
        Returns:
            List of created master data
        """
        try:
            snapshot_date = snapshot_date or date.today()
            data_to_create = []

            for v1_data in v1_data_list:
                symbol = v1_data.get('script_name', '').strip().upper()

                if not symbol or symbol not in stock_mapping:
                    continue

                # Check if data already exists
                existing = await self.get_by_symbol_and_snapshot_date(symbol, snapshot_date)
                if existing:
                    continue

                # Create master data
                stock_id = stock_mapping[symbol]
                master_data = MasterBreakoutData.from_v1_data(v1_data, stock_id, snapshot_date)
                data_to_create.append(master_data.to_dict())

            if not data_to_create:
                self.logger.info("No new master data to create from V1 data")
                return []

            # Bulk create
            created_data = await self.bulk_create(data_to_create)

            self.logger.info(
                "Bulk created master data from V1 data",
                count=len(created_data),
                snapshot_date=snapshot_date
            )
            return created_data

        except Exception as e:
            self.logger.error("Failed to bulk create master data from V1 data", error=str(e))
            raise
