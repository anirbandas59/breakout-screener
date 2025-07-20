"""
Pydantic schemas for BreakoutData model
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field, computed_field, field_validator

from ..models.enums import (
    AnalysisStatusEnum,
    BreakoutStatusEnum,
    CandleIndicatorEnum,
    PivotTypeEnum,
    VolumeIndicatorEnum,
)
from .base import BaseSchema, FilterParams, ListResponse, TimestampMixin, UUIDMixin


class BreakoutDataBase(BaseSchema):
    """Base schema for BreakoutData model"""

    # Stock relationship
    stock_id: UUID = Field(..., description="Foreign key to Stock")

    # Trading data
    trade_date: date = Field(..., description="Trading date")
    open_price: Decimal = Field(..., gt=0, description="Opening price")
    high_price: Decimal = Field(..., gt=0, description="High price")
    low_price: Decimal = Field(..., gt=0, description="Low price")
    close_price: Decimal = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")

    # CPR (Central Pivot Range) calculations
    pivot: Decimal = Field(..., gt=0, description="Pivot point (H+L+C)/3")
    bc: Decimal = Field(..., gt=0, description="Bottom Central (support)")
    tc: Decimal = Field(..., gt=0, description="Top Central (resistance)")

    # Technical indicators
    candle_indicator: CandleIndicatorEnum = Field(..., description="Candle pattern indicator")
    volume_indicator: VolumeIndicatorEnum = Field(..., description="Volume analysis indicator")

    # Analysis results
    breakout_status: BreakoutStatusEnum = Field(..., description="Breakout analysis result")
    pivot_type: PivotTypeEnum = Field(..., description="Type of pivot analysis")
    analysis_status: AnalysisStatusEnum = Field(AnalysisStatusEnum.PENDING, description="Analysis processing status")
    is_analyzed: bool = Field(False, description="Whether the data has been analyzed")

    # Additional analysis data
    avg_volume_10d: Decimal | None = Field(None, ge=0, description="10-day average volume")
    volume_ratio: Decimal | None = Field(None, ge=0, description="Volume ratio vs average")
    price_change_pct: Decimal | None = Field(None, description="Price change percentage")
    breakout_strength: Decimal | None = Field(None, ge=0, le=100, description="Breakout strength score (0-100)")

    # Narrow gap analysis
    is_narrow_gap: bool | None = Field(None, description="Whether the gap is narrow")
    gap_percentage: Decimal | None = Field(None, ge=0, description="Gap percentage")

    @field_validator('open_price', 'high_price', 'low_price', 'close_price', 'pivot', 'bc', 'tc')
    @classmethod
    def validate_positive_prices(cls, v: Decimal) -> Decimal:
        """Validate that prices are positive"""
        if v <= 0:
            raise ValueError('Price values must be positive')
        return v

    @field_validator('volume')
    @classmethod
    def validate_volume(cls, v: int) -> int:
        """Validate volume"""
        if v < 0:
            raise ValueError('Volume must be non-negative')
        return v

    def validate_ohlc_constraints(self) -> None:
        """Validate OHLC price constraints"""
        if not (self.low_price <= self.open_price <= self.high_price):
            raise ValueError('Open price must be between low and high prices')
        if not (self.low_price <= self.close_price <= self.high_price):
            raise ValueError('Close price must be between low and high prices')
        if self.high_price < self.low_price:
            raise ValueError('High price must be greater than or equal to low price')

    @computed_field
    @property
    def cpr_width(self) -> Decimal:
        """Calculate CPR width"""
        return self.tc - self.bc

    @computed_field
    @property
    def cpr_width_percentage(self) -> Decimal:
        """Calculate CPR width as percentage of pivot"""
        if self.pivot > 0:
            return (self.cpr_width / self.pivot) * 100
        return Decimal('0')


class BreakoutDataCreate(BreakoutDataBase):
    """Schema for creating new breakout data"""

    # Override to make analysis fields optional for creation
    analysis_status: AnalysisStatusEnum = Field(AnalysisStatusEnum.PENDING, description="Analysis processing status")
    is_analyzed: bool = Field(False, description="Whether the data has been analyzed")


class BreakoutDataUpdate(BaseSchema):
    """Schema for updating existing breakout data"""

    # Allow partial updates of most fields
    open_price: Decimal | None = Field(None, gt=0, description="Opening price")
    high_price: Decimal | None = Field(None, gt=0, description="High price")
    low_price: Decimal | None = Field(None, gt=0, description="Low price")
    close_price: Decimal | None = Field(None, gt=0, description="Closing price")
    volume: int | None = Field(None, ge=0, description="Trading volume")

    candle_indicator: CandleIndicatorEnum | None = Field(None, description="Candle pattern indicator")
    volume_indicator: VolumeIndicatorEnum | None = Field(None, description="Volume analysis indicator")
    breakout_status: BreakoutStatusEnum | None = Field(None, description="Breakout analysis result")
    pivot_type: PivotTypeEnum | None = Field(None, description="Type of pivot analysis")
    analysis_status: AnalysisStatusEnum | None = Field(None, description="Analysis processing status")
    is_analyzed: bool | None = Field(None, description="Whether the data has been analyzed")

    avg_volume_10d: Decimal | None = Field(None, ge=0, description="10-day average volume")
    volume_ratio: Decimal | None = Field(None, ge=0, description="Volume ratio vs average")
    price_change_pct: Decimal | None = Field(None, description="Price change percentage")
    breakout_strength: Decimal | None = Field(None, ge=0, le=100, description="Breakout strength score")
    is_narrow_gap: bool | None = Field(None, description="Whether the gap is narrow")
    gap_percentage: Decimal | None = Field(None, ge=0, description="Gap percentage")


class BreakoutDataResponse(BreakoutDataBase, UUIDMixin, TimestampMixin):
    """Schema for breakout data API responses"""

    # Include stock information
    stock_symbol: str | None = Field(None, description="Stock symbol")
    stock_company_name: str | None = Field(None, description="Company name")

    # Additional computed fields
    trading_day_of_week: str | None = Field(None, description="Day of the week")
    is_weekend: bool | None = Field(None, description="Whether trade date is on weekend")

    @computed_field
    @property
    def price_range(self) -> Decimal:
        """Calculate price range for the day"""
        return self.high_price - self.low_price

    @computed_field
    @property
    def price_range_percentage(self) -> Decimal:
        """Calculate price range as percentage of opening price"""
        if self.open_price > 0:
            return (self.price_range / self.open_price) * 100
        return Decimal('0')


class BreakoutDataList(ListResponse):
    """Schema for paginated breakout data list responses"""

    items: list[BreakoutDataResponse] = Field(..., description="List of breakout data")


class BreakoutDataFilter(FilterParams):
    """Schema for breakout data filtering parameters"""

    # Stock filters
    stock_id: UUID | None = Field(None, description="Filter by stock ID")
    symbol: str | None = Field(None, description="Filter by stock symbol")

    # Date filters
    trade_date_from: date | None = Field(None, description="Trade date from (inclusive)")
    trade_date_to: date | None = Field(None, description="Trade date to (inclusive)")

    # Status filters
    breakout_status: BreakoutStatusEnum | None = Field(None, description="Filter by breakout status")
    pivot_type: PivotTypeEnum | None = Field(None, description="Filter by pivot type")
    analysis_status: AnalysisStatusEnum | None = Field(None, description="Filter by analysis status")
    is_analyzed: bool | None = Field(None, description="Filter by analysis completion")

    # Price filters
    min_price: Decimal | None = Field(None, ge=0, description="Minimum close price")
    max_price: Decimal | None = Field(None, ge=0, description="Maximum close price")

    # Volume filters
    min_volume: int | None = Field(None, ge=0, description="Minimum volume")
    max_volume: int | None = Field(None, ge=0, description="Maximum volume")

    # CPR filters
    min_cpr_width: Decimal | None = Field(None, ge=0, description="Minimum CPR width")
    max_cpr_width: Decimal | None = Field(None, ge=0, description="Maximum CPR width")

    # Technical filters
    candle_indicator: CandleIndicatorEnum | None = Field(None, description="Filter by candle indicator")
    volume_indicator: VolumeIndicatorEnum | None = Field(None, description="Filter by volume indicator")

    # Analysis filters
    has_breakout: bool | None = Field(None, description="Filter for breakout presence")
    is_narrow_gap: bool | None = Field(None, description="Filter by narrow gap analysis")
    min_breakout_strength: Decimal | None = Field(None, ge=0, le=100, description="Minimum breakout strength")

    @field_validator('trade_date_from', 'trade_date_to')
    @classmethod
    def validate_trade_dates(cls, v: date | None) -> date | None:
        """Validate trade dates"""
        if v is not None:
            # Allow future dates for trade data
            pass
        return v


class BreakoutDataSummary(BaseSchema):
    """Schema for breakout data summary statistics"""

    total_records: int = Field(..., ge=0, description="Total breakout data records")
    analyzed_records: int = Field(..., ge=0, description="Number of analyzed records")
    unanalyzed_records: int = Field(..., ge=0, description="Number of unanalyzed records")

    # Breakout statistics
    breakout_counts: dict[str, int] = Field(..., description="Counts by breakout status")
    breakout_percentage: float = Field(..., ge=0, le=100, description="Overall breakout percentage")

    # Date range
    earliest_date: date | None = Field(None, description="Earliest trade date")
    latest_date: date | None = Field(None, description="Latest trade date")

    # Price statistics
    avg_price: float | None = Field(None, description="Average close price")
    min_price: float | None = Field(None, description="Minimum close price")
    max_price: float | None = Field(None, description="Maximum close price")

    # Volume statistics
    avg_volume: float | None = Field(None, description="Average volume")
    total_volume: int | None = Field(None, description="Total volume")

    # Analysis performance
    analysis_success_rate: float = Field(..., ge=0, le=100, description="Analysis success rate")


class DailyBreakoutSummary(BaseSchema):
    """Schema for daily breakout summary"""

    trade_date: date = Field(..., description="Trading date")
    total_records: int = Field(..., ge=0, description="Total records for the day")
    breakout_count: int = Field(..., ge=0, description="Number of breakouts")
    analyzed_count: int = Field(..., ge=0, description="Number of analyzed records")

    # Percentages
    breakout_percentage: float = Field(..., ge=0, le=100, description="Breakout percentage")
    analysis_percentage: float = Field(..., ge=0, le=100, description="Analysis completion percentage")

    # Aggregated metrics
    avg_volume: float = Field(..., ge=0, description="Average volume")
    avg_price: float = Field(..., ge=0, description="Average close price")
    avg_breakout_strength: float | None = Field(None, ge=0, le=100, description="Average breakout strength")

    # Technical indicators breakdown
    candle_indicators: dict[str, int] = Field(default_factory=dict, description="Candle indicator counts")
    volume_indicators: dict[str, int] = Field(default_factory=dict, description="Volume indicator counts")


class BreakoutDataBulkAnalysis(BaseSchema):
    """Schema for bulk analysis requests"""

    trade_date_from: date = Field(..., description="Start date for analysis")
    trade_date_to: date = Field(..., description="End date for analysis")
    symbols: list[str] | None = Field(None, description="Specific symbols to analyze")
    force_reanalysis: bool = Field(False, description="Force re-analysis of already analyzed data")
    analysis_params: dict | None = Field(None, description="Custom analysis parameters")

    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v: list[str] | None) -> list[str] | None:
        """Validate symbols list"""
        if v is not None:
            if len(v) > 1000:
                raise ValueError('Cannot analyze more than 1000 symbols at once')
            # Normalize symbols
            return [symbol.strip().upper() for symbol in v if symbol.strip()]
        return v


class BreakoutDataBulkAnalysisResult(BaseSchema):
    """Schema for bulk analysis results"""

    total_requested: int = Field(..., ge=0, description="Total records requested for analysis")
    successfully_analyzed: int = Field(..., ge=0, description="Successfully analyzed records")
    failed_analysis: int = Field(..., ge=0, description="Failed analysis records")
    skipped_existing: int = Field(..., ge=0, description="Skipped already analyzed records")

    analysis_errors: list[dict] = Field(default_factory=list, description="Analysis errors")
    processing_time_seconds: float = Field(..., ge=0, description="Total processing time")

    @property
    def success_rate(self) -> float:
        """Calculate analysis success rate"""
        if self.total_requested == 0:
            return 0.0
        return (self.successfully_analyzed / self.total_requested) * 100


class BreakoutDataExport(BaseSchema):
    """Schema for data export requests"""

    format: str = Field(..., description="Export format (csv, excel, json)")
    filters: BreakoutDataFilter | None = Field(None, description="Export filters")
    include_stock_info: bool = Field(True, description="Include stock information")
    include_computed_fields: bool = Field(True, description="Include computed fields")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format"""
        allowed_formats = ['csv', 'excel', 'json', 'xlsx']
        if v.lower() not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v.lower()
