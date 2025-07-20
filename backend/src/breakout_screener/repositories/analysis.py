"""
Analysis repositories for sessions and performance metrics
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, desc, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.analysis import AnalysisSession, PerformanceMetrics
from ..models.enums import AnalysisStatusEnum, PerformanceMetricTypeEnum
from .base import (
    BaseRepository,
    FilterParams,
    NotFoundError,
    PaginationParams,
    SortParams,
)

logger = get_logger(__name__)


class AnalysisSessionFilterParams(FilterParams):
    """AnalysisSession-specific filter parameters"""

    def __init__(
        self,
        session_name: str | None = None,
        analysis_date_from: date | None = None,
        analysis_date_to: date | None = None,
        status: AnalysisStatusEnum | None = None,
        created_by: str | None = None,
        has_metrics: bool | None = None,
        **kwargs
    ):
        self.session_name = session_name
        self.analysis_date_from = analysis_date_from
        self.analysis_date_to = analysis_date_to
        self.status = status
        self.created_by = created_by
        self.has_metrics = has_metrics

        # Call parent with remaining filters
        super().__init__(**kwargs)


class PerformanceMetricsFilterParams(FilterParams):
    """PerformanceMetrics-specific filter parameters"""

    def __init__(
        self,
        metric_type: PerformanceMetricTypeEnum | None = None,
        metric_date_from: date | None = None,
        metric_date_to: date | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        session_id: UUID | None = None,
        **kwargs
    ):
        self.metric_type = metric_type
        self.metric_date_from = metric_date_from
        self.metric_date_to = metric_date_to
        self.min_value = min_value
        self.max_value = max_value
        self.session_id = session_id

        # Call parent with remaining filters
        super().__init__(**kwargs)


class AnalysisSessionRepository(BaseRepository[AnalysisSession]):
    """
    Repository for AnalysisSession model with business-specific operations.
    Provides queries for analysis session management and tracking.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, AnalysisSession)

    # Unique field implementations

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> AnalysisSession | None:
        """Get analysis session by unique field (session_name)"""
        if field_name == "session_name":
            return await self.get_by_session_name(field_value)
        else:
            raise ValueError(f"Field '{field_name}' is not a unique field for AnalysisSession")

    async def get_by_session_name(
        self,
        session_name: str,
        load_relationships: list[str] | None = None
    ) -> AnalysisSession | None:
        """
        Get analysis session by session name
        
        Args:
            session_name: Session name
            load_relationships: List of relationships to eager load
            
        Returns:
            AnalysisSession if found, None otherwise
        """
        try:
            query = select(AnalysisSession).where(
                AnalysisSession.session_name == session_name
            )

            # Add eager loading if specified
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(AnalysisSession, relationship):
                        query = query.options(selectinload(getattr(AnalysisSession, relationship)))

            result = await self.session.execute(query)
            analysis_session = result.scalar_one_or_none()

            if analysis_session:
                self.logger.debug("AnalysisSession retrieved", session_name=session_name)
            else:
                self.logger.debug("AnalysisSession not found", session_name=session_name)

            return analysis_session

        except Exception as e:
            self.logger.error(
                "Failed to get analysis session by name",
                session_name=session_name,
                error=str(e)
            )
            raise

    async def get_by_session_name_or_raise(self, session_name: str) -> AnalysisSession:
        """
        Get analysis session by name or raise NotFoundError
        
        Args:
            session_name: Session name
            
        Returns:
            AnalysisSession
            
        Raises:
            NotFoundError: If session not found
        """
        session = await self.get_by_session_name(session_name)
        if not session:
            raise NotFoundError(f"AnalysisSession with name '{session_name}' not found")
        return session

    # Date range queries

    async def get_by_date_range(
        self,
        from_date: date,
        to_date: date,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[AnalysisSession]:
        """
        Get analysis sessions within date range
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of analysis sessions within date range
        """
        try:
            query = select(AnalysisSession).where(
                and_(
                    AnalysisSession.analysis_date >= from_date,
                    AnalysisSession.analysis_date <= to_date
                )
            )

            # Add sorting
            if sort:
                if hasattr(AnalysisSession, sort.sort_by):
                    sort_column = getattr(AnalysisSession, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by analysis_date descending
                query = query.order_by(desc(AnalysisSession.analysis_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(AnalysisSession, relationship):
                        query = query.options(selectinload(getattr(AnalysisSession, relationship)))

            result = await self.session.execute(query)
            sessions = result.scalars().all()

            self.logger.debug(
                "AnalysisSessions retrieved by date range",
                from_date=from_date,
                to_date=to_date,
                count=len(sessions)
            )
            return list(sessions)

        except Exception as e:
            self.logger.error(
                "Failed to get analysis sessions by date range",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # Business logic queries

    async def get_by_status(
        self,
        status: AnalysisStatusEnum,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[AnalysisSession]:
        """
        Get analysis sessions by status
        
        Args:
            status: Analysis status to filter by
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of analysis sessions with specified status
        """
        try:
            query = select(AnalysisSession).where(
                AnalysisSession.status == status
            )

            # Add sorting
            if sort:
                if hasattr(AnalysisSession, sort.sort_by):
                    sort_column = getattr(AnalysisSession, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(AnalysisSession.analysis_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            sessions = result.scalars().all()

            self.logger.debug(
                "AnalysisSessions retrieved by status",
                status=status.value,
                count=len(sessions)
            )
            return list(sessions)

        except Exception as e:
            self.logger.error(
                "Failed to get analysis sessions by status",
                status=status.value,
                error=str(e)
            )
            raise

    async def get_active_sessions(
        self,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[AnalysisSession]:
        """
        Get active analysis sessions (in progress or completed recently)
        
        Args:
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of active analysis sessions
        """
        try:
            query = select(AnalysisSession).where(
                or_(
                    AnalysisSession.status == AnalysisStatusEnum.IN_PROGRESS,
                    and_(
                        AnalysisSession.status == AnalysisStatusEnum.COMPLETED,
                        AnalysisSession.end_time.isnot(None),
                        AnalysisSession.end_time >= datetime.utcnow() - func.interval('7 days')
                    )
                )
            )

            # Add sorting
            if sort:
                if hasattr(AnalysisSession, sort.sort_by):
                    sort_column = getattr(AnalysisSession, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(AnalysisSession.start_time))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            sessions = result.scalars().all()

            self.logger.debug("Active analysis sessions retrieved", count=len(sessions))
            return list(sessions)

        except Exception as e:
            self.logger.error("Failed to get active analysis sessions", error=str(e))
            raise

    async def get_recent_sessions(
        self,
        days: int = 30,
        limit: int = 50,
        load_relationships: list[str] | None = None
    ) -> list[AnalysisSession]:
        """
        Get recent analysis sessions
        
        Args:
            days: Number of days to look back
            limit: Maximum number of sessions to return
            load_relationships: List of relationships to eager load
            
        Returns:
            List of recent analysis sessions
        """
        try:
            cutoff_date = datetime.utcnow() - func.interval(f'{days} days')

            query = select(AnalysisSession).where(
                AnalysisSession.created_at >= cutoff_date
            ).order_by(desc(AnalysisSession.created_at)).limit(limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(AnalysisSession, relationship):
                        query = query.options(selectinload(getattr(AnalysisSession, relationship)))

            result = await self.session.execute(query)
            sessions = result.scalars().all()

            self.logger.debug(
                "Recent analysis sessions retrieved",
                days=days,
                limit=limit,
                count=len(sessions)
            )
            return list(sessions)

        except Exception as e:
            self.logger.error(
                "Failed to get recent analysis sessions",
                days=days,
                limit=limit,
                error=str(e)
            )
            raise

    # Advanced filtering

    async def get_by_advanced_filter(
        self,
        filters: AnalysisSessionFilterParams,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[AnalysisSession]:
        """
        Get analysis sessions using advanced filter parameters
        
        Args:
            filters: Advanced filter parameters
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of filtered analysis sessions
        """
        try:
            query = select(AnalysisSession)
            conditions = []

            # Session name filter (partial match)
            if filters.session_name:
                conditions.append(AnalysisSession.session_name.ilike(f"%{filters.session_name}%"))

            # Date range filters
            if filters.analysis_date_from:
                conditions.append(AnalysisSession.analysis_date >= filters.analysis_date_from)
            if filters.analysis_date_to:
                conditions.append(AnalysisSession.analysis_date <= filters.analysis_date_to)

            # Status filter
            if filters.status:
                conditions.append(AnalysisSession.status == filters.status)

            # Created by filter
            if filters.created_by:
                conditions.append(AnalysisSession.created_by.ilike(f"%{filters.created_by}%"))

            # Has metrics filter
            if filters.has_metrics is not None:
                if filters.has_metrics:
                    conditions.append(AnalysisSession.performance_metrics.any())
                else:
                    conditions.append(~AnalysisSession.performance_metrics.any())

            # Apply additional filters from base class
            for key, value in filters.filters.items():
                if hasattr(AnalysisSession, key):
                    conditions.append(getattr(AnalysisSession, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(AnalysisSession, sort.sort_by):
                    sort_column = getattr(AnalysisSession, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by analysis_date descending
                query = query.order_by(desc(AnalysisSession.analysis_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(AnalysisSession, relationship):
                        query = query.options(selectinload(getattr(AnalysisSession, relationship)))

            result = await self.session.execute(query)
            sessions = result.scalars().all()

            self.logger.debug(
                "AnalysisSessions retrieved by advanced filter",
                count=len(sessions)
            )
            return list(sessions)

        except Exception as e:
            self.logger.error("Failed to get analysis sessions by advanced filter", error=str(e))
            raise

    # Aggregation queries

    async def get_session_summary(
        self,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> dict[str, Any]:
        """
        Get analysis session summary statistics
        
        Args:
            from_date: Optional start date
            to_date: Optional end date
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            query = select(
                func.count(AnalysisSession.id).label('total_sessions'),
                func.count(AnalysisSession.id).filter(
                    AnalysisSession.status == AnalysisStatusEnum.COMPLETED
                ).label('completed_sessions'),
                func.count(AnalysisSession.id).filter(
                    AnalysisSession.status == AnalysisStatusEnum.IN_PROGRESS
                ).label('in_progress_sessions'),
                func.count(AnalysisSession.id).filter(
                    AnalysisSession.status == AnalysisStatusEnum.FAILED
                ).label('failed_sessions'),
                func.avg(
                    extract('epoch', AnalysisSession.end_time - AnalysisSession.start_time)
                ).filter(
                    AnalysisSession.end_time.isnot(None)
                ).label('avg_duration_seconds')
            )

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(AnalysisSession.analysis_date >= from_date)
            if to_date:
                conditions.append(AnalysisSession.analysis_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            row = result.first()

            summary = {
                'from_date': from_date,
                'to_date': to_date,
                'total_sessions': row.total_sessions if row else 0,
                'completed_sessions': row.completed_sessions if row else 0,
                'in_progress_sessions': row.in_progress_sessions if row else 0,
                'failed_sessions': row.failed_sessions if row else 0,
                'avg_duration_minutes': (
                    round(row.avg_duration_seconds / 60, 2)
                    if row and row.avg_duration_seconds else 0.0
                ),
                'success_rate': (
                    (row.completed_sessions / row.total_sessions * 100)
                    if row and row.total_sessions > 0 else 0.0
                )
            }

            self.logger.debug(
                "Analysis session summary retrieved",
                from_date=from_date,
                to_date=to_date,
                summary=summary
            )
            return summary

        except Exception as e:
            self.logger.error(
                "Failed to get analysis session summary",
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise


class PerformanceMetricsRepository(BaseRepository[PerformanceMetrics]):
    """
    Repository for PerformanceMetrics model with business-specific operations.
    Provides queries for performance metrics analysis and tracking.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PerformanceMetrics)

    # Unique field implementations

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> PerformanceMetrics | None:
        """Get performance metrics by unique field (session + metric_type + metric_date combination)"""
        if field_name == "session_metric_date":
            # Expecting field_value to be a tuple (session_id, metric_type, metric_date)
            if isinstance(field_value, tuple) and len(field_value) == 3:
                return await self.get_by_session_metric_and_date(
                    field_value[0], field_value[1], field_value[2]
                )
            else:
                raise ValueError(
                    "Field value for 'session_metric_date' must be a tuple "
                    "(session_id, metric_type, metric_date)"
                )
        else:
            raise ValueError(f"Field '{field_name}' is not a unique field for PerformanceMetrics")

    async def get_by_session_metric_and_date(
        self,
        session_id: UUID,
        metric_type: PerformanceMetricTypeEnum,
        metric_date: date
    ) -> PerformanceMetrics | None:
        """
        Get performance metrics by session, metric type, and date
        
        Args:
            session_id: Analysis session UUID
            metric_type: Performance metric type
            metric_date: Metric date
            
        Returns:
            PerformanceMetrics if found, None otherwise
        """
        try:
            query = select(PerformanceMetrics).where(
                and_(
                    PerformanceMetrics.session_id == session_id,
                    PerformanceMetrics.metric_type == metric_type,
                    PerformanceMetrics.metric_date == metric_date
                )
            )

            result = await self.session.execute(query)
            metrics = result.scalar_one_or_none()

            if metrics:
                self.logger.debug(
                    "PerformanceMetrics retrieved",
                    session_id=session_id,
                    metric_type=metric_type.value,
                    metric_date=metric_date
                )
            else:
                self.logger.debug(
                    "PerformanceMetrics not found",
                    session_id=session_id,
                    metric_type=metric_type.value,
                    metric_date=metric_date
                )

            return metrics

        except Exception as e:
            self.logger.error(
                "Failed to get performance metrics by session, type and date",
                session_id=session_id,
                metric_type=metric_type.value,
                metric_date=metric_date,
                error=str(e)
            )
            raise

    # Business logic queries

    async def get_by_session(
        self,
        session_id: UUID,
        metric_type: PerformanceMetricTypeEnum | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[PerformanceMetrics]:
        """
        Get performance metrics by session
        
        Args:
            session_id: Analysis session UUID
            metric_type: Optional metric type filter
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of performance metrics for session
        """
        try:
            query = select(PerformanceMetrics).where(
                PerformanceMetrics.session_id == session_id
            )

            if metric_type:
                query = query.where(PerformanceMetrics.metric_type == metric_type)

            # Add sorting
            if sort:
                if hasattr(PerformanceMetrics, sort.sort_by):
                    sort_column = getattr(PerformanceMetrics, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(PerformanceMetrics.metric_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            metrics_list = result.scalars().all()

            self.logger.debug(
                "PerformanceMetrics retrieved by session",
                session_id=session_id,
                metric_type=metric_type.value if metric_type else None,
                count=len(metrics_list)
            )
            return list(metrics_list)

        except Exception as e:
            self.logger.error(
                "Failed to get performance metrics by session",
                session_id=session_id,
                metric_type=metric_type.value if metric_type else None,
                error=str(e)
            )
            raise

    async def get_by_metric_type(
        self,
        metric_type: PerformanceMetricTypeEnum,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None
    ) -> list[PerformanceMetrics]:
        """
        Get performance metrics by metric type
        
        Args:
            metric_type: Performance metric type
            from_date: Optional start date
            to_date: Optional end date
            pagination: Pagination parameters
            sort: Sort parameters
            
        Returns:
            List of performance metrics of specified type
        """
        try:
            query = select(PerformanceMetrics).where(
                PerformanceMetrics.metric_type == metric_type
            )

            # Add date filters if provided
            conditions = []
            if from_date:
                conditions.append(PerformanceMetrics.metric_date >= from_date)
            if to_date:
                conditions.append(PerformanceMetrics.metric_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(PerformanceMetrics, sort.sort_by):
                    sort_column = getattr(PerformanceMetrics, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(PerformanceMetrics.metric_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(query)
            metrics_list = result.scalars().all()

            self.logger.debug(
                "PerformanceMetrics retrieved by type",
                metric_type=metric_type.value,
                from_date=from_date,
                to_date=to_date,
                count=len(metrics_list)
            )
            return list(metrics_list)

        except Exception as e:
            self.logger.error(
                "Failed to get performance metrics by type",
                metric_type=metric_type.value,
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise

    # Advanced filtering

    async def get_by_advanced_filter(
        self,
        filters: PerformanceMetricsFilterParams,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[PerformanceMetrics]:
        """
        Get performance metrics using advanced filter parameters
        
        Args:
            filters: Advanced filter parameters
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of filtered performance metrics
        """
        try:
            query = select(PerformanceMetrics)
            conditions = []

            # Metric type filter
            if filters.metric_type:
                conditions.append(PerformanceMetrics.metric_type == filters.metric_type)

            # Date range filters
            if filters.metric_date_from:
                conditions.append(PerformanceMetrics.metric_date >= filters.metric_date_from)
            if filters.metric_date_to:
                conditions.append(PerformanceMetrics.metric_date <= filters.metric_date_to)

            # Value range filters
            if filters.min_value is not None:
                conditions.append(PerformanceMetrics.metric_value >= filters.min_value)
            if filters.max_value is not None:
                conditions.append(PerformanceMetrics.metric_value <= filters.max_value)

            # Session filter
            if filters.session_id:
                conditions.append(PerformanceMetrics.session_id == filters.session_id)

            # Apply additional filters from base class
            for key, value in filters.filters.items():
                if hasattr(PerformanceMetrics, key):
                    conditions.append(getattr(PerformanceMetrics, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(PerformanceMetrics, sort.sort_by):
                    sort_column = getattr(PerformanceMetrics, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
            else:
                # Default sort by metric_date descending
                query = query.order_by(desc(PerformanceMetrics.metric_date))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(PerformanceMetrics, relationship):
                        query = query.options(selectinload(getattr(PerformanceMetrics, relationship)))

            result = await self.session.execute(query)
            metrics_list = result.scalars().all()

            self.logger.debug(
                "PerformanceMetrics retrieved by advanced filter",
                count=len(metrics_list)
            )
            return list(metrics_list)

        except Exception as e:
            self.logger.error("Failed to get performance metrics by advanced filter", error=str(e))
            raise

    # Aggregation queries

    async def get_metrics_summary(
        self,
        session_id: UUID | None = None,
        metric_type: PerformanceMetricTypeEnum | None = None,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> dict[str, Any]:
        """
        Get performance metrics summary statistics
        
        Args:
            session_id: Optional session filter
            metric_type: Optional metric type filter
            from_date: Optional start date
            to_date: Optional end date
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            query = select(
                func.count(PerformanceMetrics.id).label('total_metrics'),
                func.avg(PerformanceMetrics.metric_value).label('avg_value'),
                func.min(PerformanceMetrics.metric_value).label('min_value'),
                func.max(PerformanceMetrics.metric_value).label('max_value'),
                func.stddev(PerformanceMetrics.metric_value).label('stddev_value')
            )

            # Apply filters
            conditions = []
            if session_id:
                conditions.append(PerformanceMetrics.session_id == session_id)
            if metric_type:
                conditions.append(PerformanceMetrics.metric_type == metric_type)
            if from_date:
                conditions.append(PerformanceMetrics.metric_date >= from_date)
            if to_date:
                conditions.append(PerformanceMetrics.metric_date <= to_date)

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            row = result.first()

            summary = {
                'session_id': session_id,
                'metric_type': metric_type.value if metric_type else None,
                'from_date': from_date,
                'to_date': to_date,
                'total_metrics': row.total_metrics if row else 0,
                'avg_value': float(row.avg_value) if row and row.avg_value else 0.0,
                'min_value': float(row.min_value) if row and row.min_value else 0.0,
                'max_value': float(row.max_value) if row and row.max_value else 0.0,
                'stddev_value': float(row.stddev_value) if row and row.stddev_value else 0.0
            }

            self.logger.debug(
                "Performance metrics summary retrieved",
                session_id=session_id,
                metric_type=metric_type.value if metric_type else None,
                from_date=from_date,
                to_date=to_date,
                summary=summary
            )
            return summary

        except Exception as e:
            self.logger.error(
                "Failed to get performance metrics summary",
                session_id=session_id,
                metric_type=metric_type.value if metric_type else None,
                from_date=from_date,
                to_date=to_date,
                error=str(e)
            )
            raise
