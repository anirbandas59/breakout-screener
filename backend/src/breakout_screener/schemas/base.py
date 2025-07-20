"""
Base Pydantic schemas with common patterns and mixins
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        validate_assignment=True,  # Validate on assignment
        str_strip_whitespace=True,  # Strip whitespace from strings
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
        # Use enum values in JSON serialization
        use_enum_values=True,
    )


class UUIDMixin(BaseSchema):
    """Mixin for models with UUID primary key"""

    id: UUID = Field(..., description="Unique identifier")


class TimestampMixin(BaseSchema):
    """Mixin for models with timestamp fields"""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str | None = Field(None, description="Created by user")
    updated_by: str | None = Field(None, description="Updated by user")


class PaginationParams(BaseSchema):
    """Pagination parameters for API requests"""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(50, ge=1, le=1000, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.limit

    @field_validator('page')
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Limit must be >= 1')
        if v > 1000:
            raise ValueError('Limit must be <= 1000')
        return v


class SortParams(BaseSchema):
    """Sorting parameters for API requests"""

    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order: asc or desc")

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        if v.lower() not in ['asc', 'desc', 'ascending', 'descending']:
            raise ValueError('Sort order must be asc, desc, ascending, or descending')
        return v.lower()

    @property
    def is_descending(self) -> bool:
        """Check if sort order is descending"""
        return self.sort_order in ['desc', 'descending']


class FilterParams(BaseSchema):
    """Base filter parameters"""

    # Common date filters
    created_from: datetime | None = Field(None, description="Created after this date")
    created_to: datetime | None = Field(None, description="Created before this date")
    updated_from: datetime | None = Field(None, description="Updated after this date")
    updated_to: datetime | None = Field(None, description="Updated before this date")

    @field_validator('created_from', 'created_to', 'updated_from', 'updated_to')
    @classmethod
    def validate_dates(cls, v: datetime | None) -> datetime | None:
        """Validate date fields"""
        if v is not None and v > datetime.utcnow():
            raise ValueError('Date cannot be in the future')
        return v


class ListResponse(BaseSchema):
    """Generic list response with pagination metadata"""

    items: list = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        pagination: PaginationParams
    ) -> "ListResponse":
        """Create a list response with pagination metadata"""
        pages = (total + pagination.limit - 1) // pagination.limit

        return cls(
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1
        )


class SuccessResponse(BaseSchema):
    """Generic success response"""

    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
    data: dict | None = Field(None, description="Optional response data")


class ErrorResponse(BaseSchema):
    """Generic error response"""

    success: bool = Field(False, description="Whether the operation was successful")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict | None = Field(None, description="Optional error details")


class HealthResponse(BaseSchema):
    """Health check response"""

    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    services: dict | None = Field(None, description="Individual service statuses")
    version: str | None = Field(None, description="Application version")
    uptime: str | None = Field(None, description="Application uptime")


class ValidationErrorDetail(BaseSchema):
    """Validation error detail"""

    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    invalid_value: str | None = Field(None, description="The invalid value")


class ValidationErrorResponse(BaseSchema):
    """Validation error response with field details"""

    success: bool = Field(False, description="Whether the operation was successful")
    error: str = Field("validation_error", description="Error type")
    message: str = Field(..., description="Overall validation error message")
    errors: list[ValidationErrorDetail] = Field(..., description="Field-specific validation errors")
