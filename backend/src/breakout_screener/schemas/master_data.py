"""
Pydantic schemas for MasterBreakoutData model
"""

from datetime import date
from uuid import UUID

from pydantic import Field, field_validator

from .base import BaseSchema, FilterParams, ListResponse, TimestampMixin, UUIDMixin


class MasterBreakoutDataBase(BaseSchema):
    """Base schema for MasterBreakoutData model"""

    # Stock relationship
    stock_id: UUID = Field(..., description="Foreign key to Stock")

    # Snapshot information
    snapshot_date: date = Field(..., description="Date of the data snapshot")
    data_source: str = Field(..., min_length=1, max_length=50, description="Source of the data")
    is_active: bool = Field(True, description="Whether this snapshot is active")

    # Optional relationship to breakout data
    breakout_data_id: UUID | None = Field(None, description="Foreign key to BreakoutData if applicable")

    # Metadata
    data_version: str | None = Field(None, max_length=20, description="Version of the data format")
    processing_notes: str | None = Field(None, max_length=500, description="Processing notes or comments")
    data_quality_score: int | None = Field(None, ge=0, le=100, description="Data quality score (0-100)")

    @field_validator('data_source')
    @classmethod
    def validate_data_source(cls, v: str) -> str:
        """Validate and normalize data source"""
        source = v.strip().lower()
        if not source:
            raise ValueError('Data source cannot be empty')
        return source

    @field_validator('data_quality_score')
    @classmethod
    def validate_data_quality_score(cls, v: int | None) -> int | None:
        """Validate data quality score"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Data quality score must be between 0 and 100')
        return v


class MasterBreakoutDataCreate(MasterBreakoutDataBase):
    """Schema for creating new master breakout data"""

    # All fields from base are required for creation
    pass


class MasterBreakoutDataUpdate(BaseSchema):
    """Schema for updating existing master breakout data"""

    # Allow partial updates
    snapshot_date: date | None = Field(None, description="Date of the data snapshot")
    data_source: str | None = Field(None, min_length=1, max_length=50, description="Source of the data")
    is_active: bool | None = Field(None, description="Whether this snapshot is active")
    breakout_data_id: UUID | None = Field(None, description="Foreign key to BreakoutData")
    data_version: str | None = Field(None, max_length=20, description="Version of the data format")
    processing_notes: str | None = Field(None, max_length=500, description="Processing notes")
    data_quality_score: int | None = Field(None, ge=0, le=100, description="Data quality score")

    @field_validator('data_source')
    @classmethod
    def validate_data_source(cls, v: str | None) -> str | None:
        """Validate and normalize data source"""
        if v is not None:
            source = v.strip().lower()
            if not source:
                raise ValueError('Data source cannot be empty')
            return source
        return v


class MasterBreakoutDataResponse(MasterBreakoutDataBase, UUIDMixin, TimestampMixin):
    """Schema for master breakout data API responses"""

    # Include related stock information
    stock_symbol: str | None = Field(None, description="Stock symbol")
    stock_company_name: str | None = Field(None, description="Company name")

    # Include breakout data information if linked
    has_breakout_data: bool = Field(False, description="Whether linked to breakout data")
    breakout_trade_date: date | None = Field(None, description="Trade date of linked breakout data")
    breakout_status: str | None = Field(None, description="Status of linked breakout data")

    # Snapshot statistics
    records_in_snapshot: int | None = Field(None, ge=0, description="Number of records in this snapshot")
    snapshot_completeness: float | None = Field(None, ge=0, le=100, description="Snapshot completeness percentage")


class MasterBreakoutDataList(ListResponse):
    """Schema for paginated master breakout data list responses"""

    items: list[MasterBreakoutDataResponse] = Field(..., description="List of master breakout data")


class MasterBreakoutDataFilter(FilterParams):
    """Schema for master breakout data filtering parameters"""

    # Stock filters
    stock_id: UUID | None = Field(None, description="Filter by stock ID")
    symbol: str | None = Field(None, description="Filter by stock symbol")

    # Snapshot filters
    snapshot_date_from: date | None = Field(None, description="Snapshot date from (inclusive)")
    snapshot_date_to: date | None = Field(None, description="Snapshot date to (inclusive)")
    data_source: str | None = Field(None, description="Filter by data source")
    is_active: bool | None = Field(None, description="Filter by active status")

    # Data quality filters
    min_data_quality_score: int | None = Field(None, ge=0, le=100, description="Minimum data quality score")
    max_data_quality_score: int | None = Field(None, ge=0, le=100, description="Maximum data quality score")

    # Relationship filters
    has_breakout_data: bool | None = Field(None, description="Filter by breakout data existence")
    breakout_data_id: UUID | None = Field(None, description="Filter by specific breakout data ID")

    # Data version filter
    data_version: str | None = Field(None, description="Filter by data version")

    @field_validator('data_source')
    @classmethod
    def validate_data_source(cls, v: str | None) -> str | None:
        """Validate data source filter"""
        if v is not None:
            return v.strip().lower()
        return v


class MasterBreakoutDataSummary(BaseSchema):
    """Schema for master breakout data summary statistics"""

    total_snapshots: int = Field(..., ge=0, description="Total number of snapshots")
    active_snapshots: int = Field(..., ge=0, description="Number of active snapshots")
    inactive_snapshots: int = Field(..., ge=0, description="Number of inactive snapshots")

    # Date range
    earliest_snapshot: date | None = Field(None, description="Earliest snapshot date")
    latest_snapshot: date | None = Field(None, description="Latest snapshot date")

    # Data sources breakdown
    data_sources: dict[str, int] = Field(..., description="Breakdown by data sources")
    data_versions: dict[str, int] = Field(..., description="Breakdown by data versions")

    # Quality statistics
    avg_data_quality_score: float | None = Field(None, ge=0, le=100, description="Average data quality score")
    min_data_quality_score: int | None = Field(None, ge=0, le=100, description="Minimum data quality score")
    max_data_quality_score: int | None = Field(None, ge=0, le=100, description="Maximum data quality score")

    # Relationship statistics
    with_breakout_data: int = Field(..., ge=0, description="Snapshots linked to breakout data")
    without_breakout_data: int = Field(..., ge=0, description="Snapshots not linked to breakout data")

    @field_validator('data_sources', 'data_versions')
    @classmethod
    def validate_breakdown(cls, v: dict) -> dict:
        """Validate breakdown dictionaries"""
        if not isinstance(v, dict):
            raise ValueError('Breakdown must be a dictionary')
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError('Breakdown keys must be strings')
            if not isinstance(value, int) or value < 0:
                raise ValueError('Breakdown values must be non-negative integers')
        return v


class SnapshotSummary(BaseSchema):
    """Schema for individual snapshot summary"""

    snapshot_date: date = Field(..., description="Snapshot date")
    total_records: int = Field(..., ge=0, description="Total records in snapshot")
    active_records: int = Field(..., ge=0, description="Active records in snapshot")
    unique_sources: int = Field(..., ge=0, description="Number of unique data sources")
    unique_stocks: int = Field(..., ge=0, description="Number of unique stocks")

    # Quality metrics
    avg_quality_score: float | None = Field(None, ge=0, le=100, description="Average quality score")
    completeness_percentage: float = Field(..., ge=0, le=100, description="Snapshot completeness")

    # Breakout data links
    linked_to_breakout_data: int = Field(..., ge=0, description="Records linked to breakout data")

    # Data sources in this snapshot
    data_sources: list[str] = Field(..., description="Data sources in this snapshot")


class MasterBreakoutDataBulkCreate(BaseSchema):
    """Schema for bulk master data creation"""

    snapshots: list[MasterBreakoutDataCreate] = Field(
        ..., min_items=1, max_items=10000, description="List of snapshots to create"
    )
    skip_duplicates: bool = Field(True, description="Skip duplicate snapshots")
    default_data_source: str | None = Field(None, description="Default data source if not specified")

    @field_validator('snapshots')
    @classmethod
    def validate_snapshots(cls, v: list[MasterBreakoutDataCreate]) -> list[MasterBreakoutDataCreate]:
        """Validate snapshots list"""
        if not v:
            raise ValueError('At least one snapshot is required')
        if len(v) > 10000:
            raise ValueError('Cannot create more than 10000 snapshots at once')
        return v


class MasterBreakoutDataBulkUpdate(BaseSchema):
    """Schema for bulk master data updates"""

    updates: list[dict] = Field(..., min_items=1, max_items=10000, description="List of snapshot updates")

    @field_validator('updates')
    @classmethod
    def validate_updates(cls, v: list[dict]) -> list[dict]:
        """Validate updates list"""
        if not v:
            raise ValueError('At least one update is required')
        if len(v) > 10000:
            raise ValueError('Cannot update more than 10000 snapshots at once')

        for update in v:
            if 'id' not in update:
                raise ValueError('Each update must contain an id field')

        return v


class MasterBreakoutDataImport(BaseSchema):
    """Schema for importing master data from external sources"""

    source: str = Field(..., description="Import source")
    snapshot_date: date = Field(..., description="Target snapshot date")
    data: list[dict] = Field(..., description="Raw import data")
    data_version: str | None = Field(None, description="Data version")
    overwrite_existing: bool = Field(False, description="Overwrite existing snapshots")
    validate_only: bool = Field(False, description="Only validate, don't import")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate import source"""
        allowed_sources = ['v1', 'csv', 'excel', 'api', 'manual']
        if v.lower() not in allowed_sources:
            raise ValueError(f'Source must be one of: {", ".join(allowed_sources)}')
        return v.lower()


class MasterBreakoutDataImportResult(BaseSchema):
    """Schema for master data import results"""

    total_processed: int = Field(..., ge=0, description="Total records processed")
    successful_imports: int = Field(..., ge=0, description="Successfully imported")
    failed_imports: int = Field(..., ge=0, description="Failed imports")
    skipped_existing: int = Field(..., ge=0, description="Skipped existing records")
    duplicates_found: int = Field(..., ge=0, description="Duplicate records found")

    import_errors: list[dict] = Field(default_factory=list, description="Import errors")
    imported_snapshots: list[MasterBreakoutDataResponse] = Field(
        default_factory=list, description="Successfully imported snapshots"
    )

    processing_time_seconds: float = Field(..., ge=0, description="Total processing time")

    @property
    def success_rate(self) -> float:
        """Calculate import success rate"""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_imports / self.total_processed) * 100


class MasterBreakoutDataCleanup(BaseSchema):
    """Schema for data cleanup operations"""

    operation: str = Field(..., description="Cleanup operation type")
    snapshot_date_from: date | None = Field(None, description="Start date for cleanup")
    snapshot_date_to: date | None = Field(None, description="End date for cleanup")
    data_sources: list[str] | None = Field(None, description="Specific data sources to clean")
    dry_run: bool = Field(True, description="Perform dry run without actual deletion")

    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate cleanup operation"""
        allowed_operations = [
            'remove_duplicates', 'remove_inactive', 'remove_old_snapshots',
            'remove_low_quality', 'remove_orphaned', 'archive_old'
        ]
        if v.lower() not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v.lower()


class MasterBreakoutDataCleanupResult(BaseSchema):
    """Schema for cleanup operation results"""

    operation: str = Field(..., description="Cleanup operation performed")
    total_evaluated: int = Field(..., ge=0, description="Total records evaluated")
    records_affected: int = Field(..., ge=0, description="Records affected by operation")
    records_removed: int = Field(..., ge=0, description="Records removed")
    records_archived: int = Field(..., ge=0, description="Records archived")

    was_dry_run: bool = Field(..., description="Whether this was a dry run")
    processing_time_seconds: float = Field(..., ge=0, description="Processing time")

    operation_details: dict = Field(default_factory=dict, description="Detailed operation results")
    warnings: list[str] = Field(default_factory=list, description="Operation warnings")
