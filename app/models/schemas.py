"""
Pydantic schemas for request and response validation.

This module provides comprehensive input validation and response schemas
for all API endpoints, ensuring data integrity and auto-generated API documentation.
"""

import re
from datetime import date
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


# ===========================
# Request Schemas
# ===========================

class FetchScriptSymbolsRequest(BaseModel):
    """Request schema for fetching script symbols."""
    group_name: str = Field(..., min_length=1, max_length=100, description="Stock group name (e.g., NIFTY_50)")


class GenerateBODataRequest(BaseModel):
    """Request schema for generating breakout data."""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Analysis date in YYYY-MM-DD format")
    pivot_val: float = Field(default=0.5, ge=0, le=10, description="Pivot gap percentage threshold (0-10)")
    start_from: int = Field(default=1, ge=1, le=10000, description="Start processing from this script index (1-based, max 10000)")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date string is in correct format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format, use YYYY-MM-DD')
        return v


class ClearChartRequest(BaseModel):
    """Request schema for clearing chart data."""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date to clear in YYYY-MM-DD format")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date string is in correct format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format, use YYYY-MM-DD')
        return v


# ===========================
# Response Schemas
# ===========================

class TaskStatusResponse(BaseModel):
    """Response schema for task status endpoint."""
    task_id: str = Field(..., description="Celery task ID")
    message: str = Field(..., description="Status message")


class TaskResultResponse(BaseModel):
    """Response schema for task result polling."""
    status: str = Field(..., description="Task status: PENDING, PROGRESS, SUCCESS, FAILURE")
    result: Optional[Any] = Field(default=None, description="Task result data or progress metadata")


class BreakoutDataItem(BaseModel):
    """Schema for individual breakout data record."""
    id: int
    script_name: str
    group_name: Optional[str]
    date: Optional[date]
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    previous_high: Optional[float]
    volume: Optional[float]
    cpr: Optional[float]
    res1: Optional[float]
    res2: Optional[float]
    supp1: Optional[float]
    supp2: Optional[float]
    narrow_gap: Optional[str]
    breakout_indicator: Optional[str]
    candle_indicator: Optional[str]
    volume_indicator: Optional[str]
    link: Optional[str]

    class Config:
        from_attributes = True


class GetDataResponse(BaseModel):
    """Response schema for get_data endpoint."""
    total: int = Field(..., description="Total number of records")
    data: List[BreakoutDataItem] = Field(..., description="List of breakout data records")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Records per page")
    data_date: Optional[str] = Field(default=None, description="Date of the data in YYYY-MM-DD format")
    data_source: Optional[str] = Field(default=None, description="Source table: 'breakout_data' or 'master_breakout_data'")


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ===========================
# Validation Constants
# ===========================

# Valid breakout indicator values — must match BreakoutIndicator enum .value strings
VALID_BREAKOUT_INDICATORS = [
    "Red candle",
    "no breakout",
    "Breakout",
    "Big Sell Wick",
    "No Entry",
]

# Regex for safe search strings (alphanumeric + basic punctuation)
SAFE_SEARCH_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.&]+$')


# ===========================
# Query Params Schema
# ===========================

class GetDataQueryParams(BaseModel):
    """
    Query parameter validation for GET /get_data endpoint.

    Security features:
    - Pagination limit capped at 100 to prevent DoS
    - Search string sanitized to prevent SQL injection
    - Date format validated
    - Breakout filters validated against enum values
    """
    page: int = Field(default=1, ge=1, description="Page number (minimum 1)")
    limit: int = Field(default=10, ge=1, le=100, description="Records per page (max 100)")
    search: Optional[str] = Field(default=None, max_length=100, description="Search term for script name")
    breakout_filters: Optional[List[str]] = Field(default=None, description="Breakout indicator filter values")
    date: Optional[str] = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date filter in YYYY-MM-DD")

    @field_validator('search')
    @classmethod
    def sanitize_search(cls, v: Optional[str]) -> Optional[str]:
        """
        Sanitize search string to prevent SQL injection and XSS attacks.
        Only allows alphanumeric characters and basic punctuation.
        """
        if v is None:
            return v

        # Strip whitespace
        v = v.strip()

        if not v:
            return None

        # Check if string contains only safe characters
        if not SAFE_SEARCH_PATTERN.match(v):
            raise ValueError(
                'Search string contains invalid characters. '
                'Only alphanumeric, spaces, hyphens, underscores, periods, and ampersands are allowed.'
            )

        return v

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date string is in correct format."""
        if v is None:
            return v

        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format, use YYYY-MM-DD')
        return v

    @field_validator('breakout_filters')
    @classmethod
    def validate_breakout_filters(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate breakout filter values against enum."""
        if v is None:
            return v

        invalid_filters = [f for f in v if f not in VALID_BREAKOUT_INDICATORS]
        if invalid_filters:
            raise ValueError(
                f'Invalid breakout indicator values: {invalid_filters}. '
                f'Valid values are: {VALID_BREAKOUT_INDICATORS}'
            )

        return v


# ===========================
# Health Check Schemas
# ===========================

class DatabasePoolStats(BaseModel):
    """Database connection pool statistics."""
    pool_size: int = Field(..., description="Configured pool size")
    checked_in: int = Field(..., description="Connections available in pool")
    checked_out: int = Field(..., description="Connections currently in use")
    overflow: int = Field(..., description="Overflow connections in use")
    total_connections: int = Field(..., description="Total active connections")


class DatabaseHealthInfo(BaseModel):
    """Database health and pool info."""
    connected: bool = Field(..., description="Whether the DB is reachable")
    pool_stats: Optional[DatabasePoolStats] = Field(default=None, description="Connection pool metrics")
    error: Optional[str] = Field(default=None, description="Error message if connection failed")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str = Field(..., description="Overall health status: 'healthy' or 'unhealthy'")
    database: DatabaseHealthInfo


# ===========================
# Suspend Action Schema
# ===========================

class SuspendResponse(BaseModel):
    """Response schema for suspend_action endpoint."""
    status: str = Field(..., description="Result status: SUCCESS or FAIL")
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(default=None, description="Error detail if status is FAIL")


# ===========================
# Enums Schema
# ===========================

class EnumsResponse(BaseModel):
    """Response schema for /api/enums endpoint."""
    breakout_indicators: List[str] = Field(..., description="All breakout indicator values")
    candle_indicators: List[str] = Field(..., description="All candle indicator values")
    volume_indicators: List[str] = Field(..., description="All volume indicator values")


# ===========================
# App Config Schemas
# ===========================

class AppConfigItem(BaseModel):
    """Single app configuration entry."""
    id: int
    key: str
    value: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AppConfigListResponse(BaseModel):
    """Response schema for listing config entries."""
    items: List[AppConfigItem]


class UpsertConfigRequest(BaseModel):
    """Request schema for creating or updating a config entry."""
    key: str = Field(..., min_length=1, max_length=100, description="Config key (e.g. nse_url_nifty_50)")
    value: str = Field(..., min_length=1, description="Config value")
    description: Optional[str] = Field(default=None, max_length=255, description="Human-readable description")
