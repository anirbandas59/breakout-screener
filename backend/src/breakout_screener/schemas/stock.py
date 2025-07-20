"""
Pydantic schemas for Stock model
"""

from decimal import Decimal

from pydantic import Field, field_validator

from ..models.enums import StockGroupEnum
from .base import BaseSchema, FilterParams, ListResponse, TimestampMixin, UUIDMixin


class StockBase(BaseSchema):
    """Base schema for Stock model"""

    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol (e.g., RELIANCE)")
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")
    stock_group: StockGroupEnum = Field(..., description="NSE stock group/index")
    sector: str | None = Field(None, max_length=100, description="Industry sector")
    market_cap: Decimal | None = Field(None, ge=0, description="Market capitalization in rupees")
    is_active: bool = Field(True, description="Whether the stock is actively traded")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and normalize stock symbol"""
        symbol = v.strip().upper()
        if not symbol:
            raise ValueError('Symbol cannot be empty')
        if not symbol.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return symbol

    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        """Validate company name"""
        name = v.strip()
        if not name:
            raise ValueError('Company name cannot be empty')
        return name

    @field_validator('market_cap')
    @classmethod
    def validate_market_cap(cls, v: Decimal | None) -> Decimal | None:
        """Validate market cap"""
        if v is not None and v < 0:
            raise ValueError('Market cap must be non-negative')
        return v


class StockCreate(StockBase):
    """Schema for creating a new stock"""

    # All fields from StockBase are required for creation
    pass


class StockUpdate(BaseSchema):
    """Schema for updating an existing stock"""

    symbol: str | None = Field(None, min_length=1, max_length=20, description="Stock symbol")
    company_name: str | None = Field(None, min_length=1, max_length=200, description="Company name")
    stock_group: StockGroupEnum | None = Field(None, description="NSE stock group/index")
    sector: str | None = Field(None, max_length=100, description="Industry sector")
    market_cap: Decimal | None = Field(None, ge=0, description="Market capitalization")
    is_active: bool | None = Field(None, description="Whether the stock is actively traded")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str | None) -> str | None:
        """Validate and normalize stock symbol"""
        if v is not None:
            symbol = v.strip().upper()
            if not symbol:
                raise ValueError('Symbol cannot be empty')
            if not symbol.isalnum():
                raise ValueError('Symbol must contain only alphanumeric characters')
            return symbol
        return v

    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v: str | None) -> str | None:
        """Validate company name"""
        if v is not None:
            name = v.strip()
            if not name:
                raise ValueError('Company name cannot be empty')
            return name
        return v


class StockResponse(StockBase, UUIDMixin, TimestampMixin):
    """Schema for stock API responses"""

    # Additional computed fields can be added here
    breakout_data_count: int | None = Field(None, description="Number of breakout data records")
    latest_breakout_date: str | None = Field(None, description="Latest breakout analysis date")


class StockList(ListResponse):
    """Schema for paginated stock list responses"""

    items: list[StockResponse] = Field(..., description="List of stocks")


class StockSearch(BaseSchema):
    """Schema for stock search parameters"""

    query: str = Field(..., min_length=1, description="Search query (symbol or company name)")
    active_only: bool = Field(True, description="Search only active stocks")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate search query"""
        query = v.strip()
        if not query:
            raise ValueError('Search query cannot be empty')
        return query


class StockFilter(FilterParams):
    """Schema for stock filtering parameters"""

    symbol: str | None = Field(None, description="Filter by symbol (partial match)")
    company_name: str | None = Field(None, description="Filter by company name (partial match)")
    stock_group: StockGroupEnum | None = Field(None, description="Filter by stock group")
    sector: str | None = Field(None, description="Filter by sector (partial match)")
    is_active: bool | None = Field(None, description="Filter by active status")
    market_cap_min: Decimal | None = Field(None, ge=0, description="Minimum market cap")
    market_cap_max: Decimal | None = Field(None, ge=0, description="Maximum market cap")

    @field_validator('market_cap_min', 'market_cap_max')
    @classmethod
    def validate_market_cap_range(cls, v: Decimal | None) -> Decimal | None:
        """Validate market cap range"""
        if v is not None and v < 0:
            raise ValueError('Market cap must be non-negative')
        return v


class StockSummary(BaseSchema):
    """Schema for stock summary statistics"""

    total_stocks: int = Field(..., ge=0, description="Total number of stocks")
    active_stocks: int = Field(..., ge=0, description="Number of active stocks")
    inactive_stocks: int = Field(..., ge=0, description="Number of inactive stocks")
    groups_breakdown: dict[str, int] = Field(..., description="Breakdown by stock groups")
    sectors_breakdown: dict[str, int] = Field(..., description="Breakdown by sectors")
    market_cap_stats: dict[str, float | None] = Field(..., description="Market cap statistics")

    @field_validator('groups_breakdown', 'sectors_breakdown')
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


class StockBulkCreate(BaseSchema):
    """Schema for bulk stock creation"""

    stocks: list[StockCreate] = Field(..., min_items=1, max_items=1000, description="List of stocks to create")

    @field_validator('stocks')
    @classmethod
    def validate_stocks(cls, v: list[StockCreate]) -> list[StockCreate]:
        """Validate stocks list"""
        if not v:
            raise ValueError('At least one stock is required')
        if len(v) > 1000:
            raise ValueError('Cannot create more than 1000 stocks at once')

        # Check for duplicate symbols
        symbols = [stock.symbol for stock in v]
        if len(symbols) != len(set(symbols)):
            raise ValueError('Duplicate symbols found in the list')

        return v


class StockBulkUpdate(BaseSchema):
    """Schema for bulk stock updates"""

    updates: list[dict] = Field(..., min_items=1, max_items=1000, description="List of stock updates")

    @field_validator('updates')
    @classmethod
    def validate_updates(cls, v: list[dict]) -> list[dict]:
        """Validate updates list"""
        if not v:
            raise ValueError('At least one update is required')
        if len(v) > 1000:
            raise ValueError('Cannot update more than 1000 stocks at once')

        for update in v:
            if 'id' not in update:
                raise ValueError('Each update must contain an id field')

        return v


class StockImport(BaseSchema):
    """Schema for importing stocks from external sources"""

    source: str = Field(..., description="Import source (e.g., 'nse', 'csv', 'v1')")
    data: list[dict] = Field(..., description="Raw import data")
    validate_only: bool = Field(False, description="Only validate, don't import")
    overwrite_existing: bool = Field(False, description="Overwrite existing stocks")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate import source"""
        allowed_sources = ['nse', 'csv', 'v1', 'manual']
        if v.lower() not in allowed_sources:
            raise ValueError(f'Source must be one of: {", ".join(allowed_sources)}')
        return v.lower()


class StockImportResult(BaseSchema):
    """Schema for stock import results"""

    total_processed: int = Field(..., ge=0, description="Total records processed")
    successful_imports: int = Field(..., ge=0, description="Successfully imported")
    failed_imports: int = Field(..., ge=0, description="Failed imports")
    skipped_existing: int = Field(..., ge=0, description="Skipped existing records")
    errors: list[dict] = Field(default_factory=list, description="Import errors")
    imported_stocks: list[StockResponse] = Field(default_factory=list, description="Successfully imported stocks")

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_imports / self.total_processed) * 100
