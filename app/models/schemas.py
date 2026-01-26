"""
Pydantic schemas for request and response validation.

This module provides comprehensive input validation and response schemas
for all API endpoints, ensuring data integrity and auto-generated API documentation.
"""

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
    start_from: int = Field(default=1, ge=1, description="Start processing from this script index (1-based)")

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
