"""
Pydantic schemas for Analysis models (AnalysisSession and PerformanceMetrics)
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import Field, computed_field, field_validator

from ..models.enums import AnalysisStatusEnum, PerformanceMetricTypeEnum
from .base import BaseSchema, FilterParams, ListResponse, TimestampMixin, UUIDMixin


class AnalysisSessionBase(BaseSchema):
    """Base schema for AnalysisSession model"""

    session_name: str = Field(..., min_length=1, max_length=100, description="Unique session name")
    analysis_date: date = Field(..., description="Date of the analysis")
    status: AnalysisStatusEnum = Field(..., description="Current status of the analysis")

    # Timing information
    start_time: datetime | None = Field(None, description="Analysis start time")
    end_time: datetime | None = Field(None, description="Analysis end time")

    # Configuration and parameters
    analysis_parameters: dict | None = Field(None, description="Analysis configuration parameters")
    data_source: str | None = Field(None, max_length=50, description="Source of the data being analyzed")

    # Progress tracking
    total_items: int | None = Field(None, ge=0, description="Total items to analyze")
    processed_items: int | None = Field(None, ge=0, description="Items processed so far")

    # Results summary
    success_count: int | None = Field(None, ge=0, description="Number of successful analyses")
    error_count: int | None = Field(None, ge=0, description="Number of failed analyses")
    warning_count: int | None = Field(None, ge=0, description="Number of warnings generated")

    # Notes and metadata
    description: str | None = Field(None, max_length=500, description="Session description")
    tags: list[str] | None = Field(None, description="Session tags for categorization")

    @field_validator('session_name')
    @classmethod
    def validate_session_name(cls, v: str) -> str:
        """Validate and normalize session name"""
        name = v.strip()
        if not name:
            raise ValueError('Session name cannot be empty')
        # Replace spaces with underscores and ensure valid characters
        name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in name)
        return name

    @field_validator('processed_items')
    @classmethod
    def validate_processed_items(cls, v: int | None, info) -> int | None:
        """Validate processed items doesn't exceed total"""
        if v is not None and 'total_items' in info.data:
            total = info.data['total_items']
            if total is not None and v > total:
                raise ValueError('Processed items cannot exceed total items')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate and normalize tags"""
        if v is not None:
            # Remove empty tags and normalize
            tags = [tag.strip().lower() for tag in v if tag.strip()]
            return tags if tags else None
        return v

    @computed_field
    @property
    def progress_percentage(self) -> float | None:
        """Calculate progress percentage"""
        if self.total_items and self.processed_items is not None:
            if self.total_items > 0:
                return (self.processed_items / self.total_items) * 100
        return None

    @computed_field
    @property
    def duration_seconds(self) -> float | None:
        """Calculate duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class AnalysisSessionCreate(AnalysisSessionBase):
    """Schema for creating new analysis session"""

    # Override defaults for creation
    status: AnalysisStatusEnum = Field(AnalysisStatusEnum.PENDING, description="Initial status")
    start_time: datetime | None = Field(None, description="Analysis start time")


class AnalysisSessionUpdate(BaseSchema):
    """Schema for updating existing analysis session"""

    # Allow partial updates
    session_name: str | None = Field(None, min_length=1, max_length=100, description="Session name")
    analysis_date: date | None = Field(None, description="Analysis date")
    status: AnalysisStatusEnum | None = Field(None, description="Session status")

    start_time: datetime | None = Field(None, description="Analysis start time")
    end_time: datetime | None = Field(None, description="Analysis end time")

    analysis_parameters: dict | None = Field(None, description="Analysis parameters")
    data_source: str | None = Field(None, max_length=50, description="Data source")

    total_items: int | None = Field(None, ge=0, description="Total items to analyze")
    processed_items: int | None = Field(None, ge=0, description="Items processed")

    success_count: int | None = Field(None, ge=0, description="Successful analyses")
    error_count: int | None = Field(None, ge=0, description="Failed analyses")
    warning_count: int | None = Field(None, ge=0, description="Warnings generated")

    description: str | None = Field(None, max_length=500, description="Session description")
    tags: list[str] | None = Field(None, description="Session tags")


class AnalysisSessionResponse(AnalysisSessionBase, UUIDMixin, TimestampMixin):
    """Schema for analysis session API responses"""

    # Additional computed fields
    is_running: bool = Field(False, description="Whether the session is currently running")
    is_completed: bool = Field(False, description="Whether the session has completed")
    has_errors: bool = Field(False, description="Whether the session has errors")

    # Performance metrics count
    metrics_count: int | None = Field(None, ge=0, description="Number of associated performance metrics")

    # Success rate
    success_rate: float | None = Field(None, ge=0, le=100, description="Success rate percentage")

    @computed_field
    @property
    def estimated_completion_time(self) -> datetime | None:
        """Estimate completion time based on progress"""
        if (self.start_time and self.progress_percentage and
            self.progress_percentage > 0 and self.status == AnalysisStatusEnum.IN_PROGRESS):

            elapsed = datetime.utcnow() - self.start_time
            total_estimated = elapsed / (self.progress_percentage / 100)
            return self.start_time + total_estimated
        return None


class AnalysisSessionList(ListResponse):
    """Schema for paginated analysis session list responses"""

    items: list[AnalysisSessionResponse] = Field(..., description="List of analysis sessions")


class AnalysisSessionFilter(FilterParams):
    """Schema for analysis session filtering parameters"""

    # Session filters
    session_name: str | None = Field(None, description="Filter by session name (partial match)")
    status: AnalysisStatusEnum | None = Field(None, description="Filter by status")

    # Date filters
    analysis_date_from: date | None = Field(None, description="Analysis date from (inclusive)")
    analysis_date_to: date | None = Field(None, description="Analysis date to (inclusive)")

    # Data source filter
    data_source: str | None = Field(None, description="Filter by data source")

    # Progress filters
    min_progress: float | None = Field(None, ge=0, le=100, description="Minimum progress percentage")
    max_progress: float | None = Field(None, ge=0, le=100, description="Maximum progress percentage")

    # Performance filters
    min_success_rate: float | None = Field(None, ge=0, le=100, description="Minimum success rate")
    has_errors: bool | None = Field(None, description="Filter by error presence")
    has_metrics: bool | None = Field(None, description="Filter by metrics presence")

    # Tags filter
    tags: list[str] | None = Field(None, description="Filter by tags (any match)")

    # User filter
    created_by: str | None = Field(None, description="Filter by creator")


class AnalysisSessionSummary(BaseSchema):
    """Schema for analysis session summary statistics"""

    total_sessions: int = Field(..., ge=0, description="Total number of sessions")

    # Status breakdown
    status_breakdown: dict[str, int] = Field(..., description="Sessions by status")

    # Timing statistics
    avg_duration_minutes: float | None = Field(None, ge=0, description="Average session duration")
    total_processing_time_hours: float | None = Field(None, ge=0, description="Total processing time")

    # Performance statistics
    total_items_processed: int | None = Field(None, ge=0, description="Total items processed across all sessions")
    overall_success_rate: float | None = Field(None, ge=0, le=100, description="Overall success rate")

    # Date range
    earliest_session: date | None = Field(None, description="Earliest session date")
    latest_session: date | None = Field(None, description="Latest session date")

    # Active sessions
    currently_running: int = Field(..., ge=0, description="Currently running sessions")
    pending_sessions: int = Field(..., ge=0, description="Pending sessions")


# Performance Metrics Schemas

class PerformanceMetricsBase(BaseSchema):
    """Base schema for PerformanceMetrics model"""

    # Session relationship
    session_id: UUID = Field(..., description="Foreign key to AnalysisSession")

    # Metric information
    metric_type: PerformanceMetricTypeEnum = Field(..., description="Type of performance metric")
    metric_date: date = Field(..., description="Date of the metric")
    metric_value: float = Field(..., description="Numeric value of the metric")

    # Optional metadata
    metric_unit: str | None = Field(None, max_length=20, description="Unit of measurement")
    metric_description: str | None = Field(None, max_length=200, description="Metric description")

    # Context information
    context_data: dict | None = Field(None, description="Additional context for the metric")
    tags: list[str] | None = Field(None, description="Metric tags for categorization")

    @field_validator('metric_value')
    @classmethod
    def validate_metric_value(cls, v: float) -> float:
        """Validate metric value"""
        if not isinstance(v, (int, float)):
            raise ValueError('Metric value must be a number')
        # Allow negative values for some metrics (e.g., performance changes)
        return float(v)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate and normalize tags"""
        if v is not None:
            tags = [tag.strip().lower() for tag in v if tag.strip()]
            return tags if tags else None
        return v


class PerformanceMetricsCreate(PerformanceMetricsBase):
    """Schema for creating new performance metrics"""

    # All fields from base are required for creation
    pass


class PerformanceMetricsUpdate(BaseSchema):
    """Schema for updating existing performance metrics"""

    # Allow partial updates
    metric_type: PerformanceMetricTypeEnum | None = Field(None, description="Metric type")
    metric_date: date | None = Field(None, description="Metric date")
    metric_value: float | None = Field(None, description="Metric value")

    metric_unit: str | None = Field(None, max_length=20, description="Unit of measurement")
    metric_description: str | None = Field(None, max_length=200, description="Metric description")

    context_data: dict | None = Field(None, description="Additional context")
    tags: list[str] | None = Field(None, description="Metric tags")


class PerformanceMetricsResponse(PerformanceMetricsBase, UUIDMixin, TimestampMixin):
    """Schema for performance metrics API responses"""

    # Include session information
    session_name: str | None = Field(None, description="Associated session name")
    session_status: str | None = Field(None, description="Associated session status")

    # Computed fields
    is_latest: bool = Field(False, description="Whether this is the latest metric of its type")
    days_ago: int | None = Field(None, description="Days since metric date")


class PerformanceMetricsList(ListResponse):
    """Schema for paginated performance metrics list responses"""

    items: list[PerformanceMetricsResponse] = Field(..., description="List of performance metrics")


class PerformanceMetricsFilter(FilterParams):
    """Schema for performance metrics filtering parameters"""

    # Session filters
    session_id: UUID | None = Field(None, description="Filter by session ID")
    session_name: str | None = Field(None, description="Filter by session name")

    # Metric filters
    metric_type: PerformanceMetricTypeEnum | None = Field(None, description="Filter by metric type")
    metric_date_from: date | None = Field(None, description="Metric date from (inclusive)")
    metric_date_to: date | None = Field(None, description="Metric date to (inclusive)")

    # Value filters
    min_value: float | None = Field(None, description="Minimum metric value")
    max_value: float | None = Field(None, description="Maximum metric value")

    # Metadata filters
    metric_unit: str | None = Field(None, description="Filter by metric unit")
    tags: list[str] | None = Field(None, description="Filter by tags (any match)")

    # Computed filters
    is_latest: bool | None = Field(None, description="Filter for latest metrics only")


class PerformanceMetricsSummary(BaseSchema):
    """Schema for performance metrics summary statistics"""

    total_metrics: int = Field(..., ge=0, description="Total number of metrics")
    unique_metric_types: int = Field(..., ge=0, description="Number of unique metric types")
    unique_sessions: int = Field(..., ge=0, description="Number of unique sessions")

    # Value statistics
    avg_value: float | None = Field(None, description="Average metric value")
    min_value: float | None = Field(None, description="Minimum metric value")
    max_value: float | None = Field(None, description="Maximum metric value")
    stddev_value: float | None = Field(None, description="Standard deviation of values")

    # Date range
    earliest_metric: date | None = Field(None, description="Earliest metric date")
    latest_metric: date | None = Field(None, description="Latest metric date")

    # Type breakdown
    metric_type_breakdown: dict[str, int] = Field(..., description="Metrics by type")

    # Time series data (last 30 days)
    recent_trend: list[dict] | None = Field(None, description="Recent metric trend data")


class PerformanceMetricsBulkCreate(BaseSchema):
    """Schema for bulk performance metrics creation"""

    metrics: list[PerformanceMetricsCreate] = Field(
        ..., min_items=1, max_items=10000, description="List of metrics to create"
    )
    skip_duplicates: bool = Field(True, description="Skip duplicate metrics")

    @field_validator('metrics')
    @classmethod
    def validate_metrics(cls, v: list[PerformanceMetricsCreate]) -> list[PerformanceMetricsCreate]:
        """Validate metrics list"""
        if not v:
            raise ValueError('At least one metric is required')
        if len(v) > 10000:
            raise ValueError('Cannot create more than 10000 metrics at once')
        return v


class PerformanceMetricsExport(BaseSchema):
    """Schema for metrics export requests"""

    format: str = Field(..., description="Export format (csv, excel, json)")
    filters: PerformanceMetricsFilter | None = Field(None, description="Export filters")
    include_session_info: bool = Field(True, description="Include session information")
    include_context_data: bool = Field(False, description="Include context data")
    group_by_metric_type: bool = Field(False, description="Group by metric type")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format"""
        allowed_formats = ['csv', 'excel', 'json', 'xlsx']
        if v.lower() not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v.lower()


class MetricTrendAnalysis(BaseSchema):
    """Schema for metric trend analysis"""

    metric_type: PerformanceMetricTypeEnum = Field(..., description="Metric type to analyze")
    date_from: date = Field(..., description="Analysis start date")
    date_to: date = Field(..., description="Analysis end date")

    # Trend analysis results
    trend_direction: str | None = Field(None, description="Overall trend direction")
    trend_strength: float | None = Field(None, ge=0, le=1, description="Trend strength (0-1)")

    # Statistical data
    linear_regression: dict | None = Field(None, description="Linear regression analysis")
    moving_averages: dict | None = Field(None, description="Moving average calculations")
    volatility: float | None = Field(None, ge=0, description="Metric volatility")

    # Data points
    data_points: list[dict] = Field(..., description="Actual data points used in analysis")
    predictions: list[dict] | None = Field(None, description="Future value predictions")
