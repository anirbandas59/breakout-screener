"""
Main breakout analysis data model
Enhanced version of V1 breakout_data with proper relationships and validation
"""

from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, validates

from .base import BaseModel
from .enums import BreakoutIndicatorEnum, CandleIndicatorEnum, VolumeIndicatorEnum


class BreakoutDataV2(BaseModel):
    """
    Main table for storing daily breakout analysis data with improved constraints.
    Enhanced version of V1 breakout_data with proper foreign key relationships.
    """

    __tablename__ = "breakout_data_v2"

    # Foreign key to stocks table (normalized from V1 script_name)
    stock_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to stock in stocks table"
    )

    # Analysis date
    trade_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Date of the trading session being analyzed"
    )

    # OHLCV data (V1 compatibility fields)
    open_price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Opening price for the trading session"
    )

    high_price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Highest price during the trading session"
    )

    low_price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Lowest price during the trading session"
    )

    close_price = Column(
        DECIMAL(12, 2),
        nullable=False,
        comment="Closing price for the trading session"
    )

    previous_high = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Previous period high for breakout analysis"
    )

    volume = Column(
        BigInteger,
        nullable=False,
        comment="Trading volume for the session"
    )

    # CPR (Central Pivot Range) calculations - Core V1 business logic preserved
    cpr = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Central Pivot Point: (H+L+C)/3"
    )

    resistance_1 = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="First resistance level: (2*Pivot) - Low"
    )

    resistance_2 = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Second resistance level: Pivot + (R1 - S1)"
    )

    support_1 = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="First support level: (2*Pivot) - High"
    )

    support_2 = Column(
        DECIMAL(12, 2),
        nullable=True,
        comment="Second support level: Pivot - (R1 - S1)"
    )

    # Analysis indicators (V1 business logic preserved with enum constraints)
    narrow_gap = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether CPR shows narrow gap (V1: Yes/No -> Boolean)"
    )

    breakout_indicator = Column(
        ENUM(BreakoutIndicatorEnum, name="breakout_indicator_enum"),
        default=BreakoutIndicatorEnum.NO_BREAKOUT,
        nullable=False,
        index=True,
        comment="Breakout analysis result (enhanced from V1 string values)"
    )

    candle_indicator = Column(
        ENUM(CandleIndicatorEnum, name="candle_indicator_enum"),
        default=CandleIndicatorEnum.NEUTRAL,
        nullable=False,
        comment="Candle pattern analysis (enhanced from V1 string values)"
    )

    volume_indicator = Column(
        ENUM(VolumeIndicatorEnum, name="volume_indicator_enum"),
        default=VolumeIndicatorEnum.NORMAL_VOLUME,
        nullable=False,
        comment="Volume strength analysis (enhanced from V1 Good/Average/Low)"
    )

    # Analysis metadata
    chart_link = Column(
        Text,
        nullable=True,
        comment="URL link to chart analysis (V1 'link' field)"
    )

    analysis_notes = Column(
        Text,
        nullable=True,
        comment="Additional analysis notes and observations"
    )

    confidence_score = Column(
        DECIMAL(3, 2),
        nullable=True,
        comment="Analysis confidence score (0.0 to 1.0)"
    )

    # Relationships
    stock = relationship(
        "Stock",
        back_populates="breakout_data",
        lazy="joined"  # Eager load stock data for most queries
    )

    # Table constraints preserving V1 business logic
    __table_args__ = (
        # OHLC validation (standard trading data constraints)
        CheckConstraint(
            "open_price > 0",
            name="ck_breakout_data_v2_open_price_positive"
        ),
        CheckConstraint(
            "high_price > 0",
            name="ck_breakout_data_v2_high_price_positive"
        ),
        CheckConstraint(
            "low_price > 0",
            name="ck_breakout_data_v2_low_price_positive"
        ),
        CheckConstraint(
            "close_price > 0",
            name="ck_breakout_data_v2_close_price_positive"
        ),
        CheckConstraint(
            "volume >= 0",
            name="ck_breakout_data_v2_volume_non_negative"
        ),

        # OHLC relationship validation
        CheckConstraint(
            "high_price >= open_price AND high_price >= close_price AND "
            "low_price <= open_price AND low_price <= close_price",
            name="ck_breakout_data_v2_valid_ohlc"
        ),

        # Confidence score validation
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_breakout_data_v2_confidence_score_range"
        ),

        # Unique constraint - one record per stock per date
        UniqueConstraint(
            "stock_id", "trade_date",
            name="uq_breakout_data_v2_stock_date"
        ),

        # Performance indexes
        Index("idx_breakout_data_v2_stock_date", "stock_id", "trade_date"),
        Index("idx_breakout_data_v2_trade_date_breakout", "trade_date", "breakout_indicator"),
        Index("idx_breakout_data_v2_volume_date", "volume", "trade_date"),
        Index("idx_breakout_data_v2_composite_analysis",
              "trade_date", "breakout_indicator", "volume_indicator"),

        {"comment": "Main table for storing daily breakout analysis data with improved constraints"}
    )

    @validates('open_price', 'high_price', 'low_price', 'close_price')
    def validate_prices(self, key, price):
        """Validate price values"""
        if price is not None and price <= 0:
            raise ValueError(f"{key} must be positive: {price}")
        return price

    @validates('volume')
    def validate_volume(self, key, volume):
        """Validate volume"""
        if volume is not None and volume < 0:
            raise ValueError(f"Volume cannot be negative: {volume}")
        return volume

    @validates('confidence_score')
    def validate_confidence_score(self, key, score):
        """Validate confidence score range"""
        if score is not None and (score < 0 or score > 1):
            raise ValueError(f"Confidence score must be between 0 and 1: {score}")
        return score

    @validates('trade_date')
    def validate_trade_date(self, key, trade_date):
        """Validate trade date"""
        if trade_date is not None:
            from datetime import date as date_class
            if trade_date > date_class.today():
                raise ValueError(f"Trade date cannot be in future: {trade_date}")
        return trade_date

    def __repr__(self) -> str:
        return (f"<BreakoutDataV2(stock_id={self.stock_id}, trade_date={self.trade_date}, "
                f"breakout={self.breakout_indicator.value})>")

    @classmethod
    def from_v1_data(cls, v1_record: dict, stock_id: str) -> 'BreakoutDataV2':
        """
        Create BreakoutDataV2 instance from V1 breakout_data record.
        Preserves all V1 business logic while applying V2 enhancements.

        Args:
            v1_record: Dictionary containing V1 breakout_data fields
            stock_id: UUID of the corresponding stock in stocks table

        Returns:
            BreakoutDataV2 instance ready for database insertion
        """
        return cls(
            stock_id=stock_id,
            trade_date=v1_record.get('date'),
            open_price=v1_record.get('open'),
            high_price=v1_record.get('high'),
            low_price=v1_record.get('low'),
            close_price=v1_record.get('close'),
            previous_high=v1_record.get('previous_high'),
            volume=v1_record.get('volume'),
            cpr=v1_record.get('cpr'),
            resistance_1=v1_record.get('res1'),
            resistance_2=v1_record.get('res2'),
            support_1=v1_record.get('supp1'),
            support_2=v1_record.get('supp2'),
            narrow_gap=v1_record.get('narrow_gap', '').lower() == 'yes',
            breakout_indicator=BreakoutIndicatorEnum.from_v1_value(
                v1_record.get('breakout_indicator', '')
            ),
            candle_indicator=CandleIndicatorEnum.from_v1_value(
                v1_record.get('candle_indicator', '')
            ),
            volume_indicator=VolumeIndicatorEnum.from_v1_value(
                v1_record.get('volume_indicator', '')
            ),
            chart_link=v1_record.get('link')
        )

    def calculate_price_change_percent(self) -> Decimal | None:
        """Calculate price change percentage from open to close"""
        if self.open_price and self.close_price:
            return ((self.close_price - self.open_price) / self.open_price) * 100
        return None

    def calculate_volume_ratio_vs_avg(self, avg_volume: int) -> Decimal | None:
        """Calculate volume ratio vs average (preserves V1 logic)"""
        if avg_volume and avg_volume > 0:
            return Decimal(self.volume) / Decimal(avg_volume)
        return None

    def is_breakout_confirmed(self) -> bool:
        """Check if this is a confirmed breakout (V1 logic preserved)"""
        return self.breakout_indicator == BreakoutIndicatorEnum.BREAKOUT

    def get_cpr_width(self) -> Decimal | None:
        """Calculate CPR width (for narrow gap analysis)"""
        if self.resistance_1 and self.support_1:
            return abs(self.resistance_1 - self.support_1)
        return None

    def get_body_size(self) -> Decimal | None:
        """Calculate candle body size"""
        if self.open_price and self.close_price:
            return abs(self.close_price - self.open_price)
        return None

    def get_upper_shadow(self) -> Decimal | None:
        """Calculate upper shadow length"""
        if self.high_price and self.open_price and self.close_price:
            body_top = max(self.open_price, self.close_price)
            return self.high_price - body_top
        return None

    def get_lower_shadow(self) -> Decimal | None:
        """Calculate lower shadow length"""
        if self.low_price and self.open_price and self.close_price:
            body_bottom = min(self.open_price, self.close_price)
            return body_bottom - self.low_price
        return None

    def to_dict(self, include_stock: bool = True, exclude_fields: list | None = None) -> dict:
        """
        Convert breakout data to dictionary with optional stock information.

        Args:
            include_stock: Whether to include stock information
            exclude_fields: List of fields to exclude

        Returns:
            Dictionary representation
        """
        exclude_fields = exclude_fields or []
        result = super().to_dict(exclude_fields)

        # Add calculated fields
        result['price_change_percent'] = float(self.calculate_price_change_percent() or 0)
        result['body_size'] = float(self.get_body_size() or 0)
        result['cpr_width'] = float(self.get_cpr_width() or 0)
        result['is_breakout_confirmed'] = self.is_breakout_confirmed()

        # Add enum display values
        result['breakout_indicator_display'] = self.breakout_indicator.value
        result['candle_indicator_display'] = self.candle_indicator.value
        result['volume_indicator_display'] = self.volume_indicator.value

        if include_stock and self.stock:
            result['stock'] = {
                'symbol': self.stock.symbol,
                'company_name': self.stock.company_name,
                'stock_group': self.stock.stock_group.value,
                'stock_group_display': self.stock.group_display_name
            }

        return result

    def to_v1_format(self) -> dict:
        """
        Convert back to V1 format for backward compatibility.

        Returns:
            Dictionary in V1 breakout_data format
        """
        return {
            'script_name': self.stock.symbol if self.stock else '',
            'group_name': self.stock.stock_group.value if self.stock else '',
            'date': self.trade_date,
            'open': float(self.open_price) if self.open_price else None,
            'high': float(self.high_price) if self.high_price else None,
            'low': float(self.low_price) if self.low_price else None,
            'close': float(self.close_price) if self.close_price else None,
            'previous_high': float(self.previous_high) if self.previous_high else None,
            'volume': self.volume,
            'cpr': float(self.cpr) if self.cpr else None,
            'res1': float(self.resistance_1) if self.resistance_1 else None,
            'res2': float(self.resistance_2) if self.resistance_2 else None,
            'supp1': float(self.support_1) if self.support_1 else None,
            'supp2': float(self.support_2) if self.support_2 else None,
            'narrow_gap': 'Yes' if self.narrow_gap else 'No',
            'breakout_indicator': self.breakout_indicator.value,
            'candle_indicator': self.candle_indicator.value,
            'volume_indicator': self.volume_indicator.value,
            'link': self.chart_link
        }


# Alias for backward compatibility
BreakoutData = BreakoutDataV2
