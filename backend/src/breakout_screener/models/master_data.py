"""
Master breakout data model for historical snapshots
Enhanced version of V1 master_bo_data for auditing and comparison
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .breakout_data import BreakoutDataV2

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, validates

from .base import BaseModel
from .enums import BreakoutIndicatorEnum, CandleIndicatorEnum, VolumeIndicatorEnum


class MasterBreakoutDataV2(BaseModel):
    """
    Historical snapshots of breakout data for auditing and comparison.
    Enhanced version of V1 master_bo_data with proper foreign key relationships.
    """

    __tablename__ = "master_breakout_data_v2"

    # Foreign key to stocks table
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
        comment="Date of the trading session"
    )

    # OHLCV data (identical structure to BreakoutDataV2)
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

    # CPR (Central Pivot Range) calculations
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

    # Analysis indicators
    narrow_gap = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether CPR shows narrow gap"
    )

    breakout_indicator = Column(
        ENUM(BreakoutIndicatorEnum, name="breakout_indicator_enum"),
        default=BreakoutIndicatorEnum.NO_BREAKOUT,
        nullable=False,
        comment="Breakout analysis result"
    )

    candle_indicator = Column(
        ENUM(CandleIndicatorEnum, name="candle_indicator_enum"),
        default=CandleIndicatorEnum.NEUTRAL,
        nullable=False,
        comment="Candle pattern analysis"
    )

    volume_indicator = Column(
        ENUM(VolumeIndicatorEnum, name="volume_indicator_enum"),
        default=VolumeIndicatorEnum.NORMAL_VOLUME,
        nullable=False,
        comment="Volume strength analysis"
    )

    # Analysis metadata
    chart_link = Column(
        Text,
        nullable=True,
        comment="URL link to chart analysis"
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

    # Snapshot metadata (unique to master table)
    snapshot_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When this snapshot was created"
    )

    source_table = Column(
        String(50),
        default="breakout_data_v2",
        nullable=False,
        comment="Source table name for this snapshot"
    )

    # Relationships
    stock = relationship(
        "Stock",
        back_populates="master_breakout_data",
        lazy="joined"
    )

    # Table indexes for performance
    __table_args__ = (
        Index("idx_master_breakout_data_v2_stock_trade_date", "stock_id", "trade_date"),
        Index("idx_master_breakout_data_v2_snapshot_date", "snapshot_date"),
        Index("idx_master_breakout_data_v2_source_table", "source_table"),
        Index("idx_master_breakout_data_v2_breakout_snapshot", "breakout_indicator", "snapshot_date"),

        {"comment": "Historical snapshots of breakout data for auditing and comparison"}
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

    def __repr__(self) -> str:
        return (f"<MasterBreakoutDataV2(stock_id={self.stock_id}, trade_date={self.trade_date}, "
                f"snapshot_date={self.snapshot_date})>")

    @classmethod
    def from_breakout_data(cls, breakout_data: 'BreakoutDataV2',
                          snapshot_date: datetime | None = None) -> 'MasterBreakoutDataV2':
        """
        Create master record from breakout data.
        
        Args:
            breakout_data: BreakoutDataV2 instance to archive
            snapshot_date: When the snapshot was created (defaults to now)
            
        Returns:
            MasterBreakoutDataV2 instance ready for database insertion
        """
        return cls(
            stock_id=breakout_data.stock_id,
            trade_date=breakout_data.trade_date,
            open_price=breakout_data.open_price,
            high_price=breakout_data.high_price,
            low_price=breakout_data.low_price,
            close_price=breakout_data.close_price,
            previous_high=breakout_data.previous_high,
            volume=breakout_data.volume,
            cpr=breakout_data.cpr,
            resistance_1=breakout_data.resistance_1,
            resistance_2=breakout_data.resistance_2,
            support_1=breakout_data.support_1,
            support_2=breakout_data.support_2,
            narrow_gap=breakout_data.narrow_gap,
            breakout_indicator=breakout_data.breakout_indicator,
            candle_indicator=breakout_data.candle_indicator,
            volume_indicator=breakout_data.volume_indicator,
            chart_link=breakout_data.chart_link,
            analysis_notes=breakout_data.analysis_notes,
            confidence_score=breakout_data.confidence_score,
            snapshot_date=snapshot_date or datetime.utcnow(),
            source_table="breakout_data_v2"
        )

    @classmethod
    def from_v1_master_data(cls, v1_record: dict, stock_id: str) -> 'MasterBreakoutDataV2':
        """
        Create MasterBreakoutDataV2 instance from V1 master_bo_data record.
        
        Args:
            v1_record: Dictionary containing V1 master_bo_data fields
            stock_id: UUID of the corresponding stock in stocks table
            
        Returns:
            MasterBreakoutDataV2 instance ready for database insertion
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
            chart_link=v1_record.get('link'),
            snapshot_date=datetime.utcnow(),
            source_table="v1_migration"
        )

    def calculate_price_change_percent(self) -> Decimal | None:
        """Calculate price change percentage from open to close"""
        if self.open_price and self.close_price:
            return ((self.close_price - self.open_price) / self.open_price) * 100
        return None

    def is_breakout_confirmed(self) -> bool:
        """Check if this is a confirmed breakout"""
        return self.breakout_indicator == BreakoutIndicatorEnum.BREAKOUT

    def get_cpr_width(self) -> Decimal | None:
        """Calculate CPR width"""
        if self.resistance_1 and self.support_1:
            return abs(self.resistance_1 - self.support_1)
        return None

    def compare_with_current(self, current_data: 'BreakoutDataV2') -> dict:
        """
        Compare this historical record with current data.
        
        Args:
            current_data: Current BreakoutDataV2 record for same stock/date
            
        Returns:
            Dictionary of differences
        """
        differences = {}

        # Compare key fields
        fields_to_compare = [
            'open_price', 'high_price', 'low_price', 'close_price',
            'volume', 'cpr', 'resistance_1', 'resistance_2',
            'support_1', 'support_2', 'narrow_gap',
            'breakout_indicator', 'candle_indicator', 'volume_indicator'
        ]

        for field in fields_to_compare:
            master_value = getattr(self, field)
            current_value = getattr(current_data, field)

            if master_value != current_value:
                differences[field] = {
                    'historical': master_value,
                    'current': current_value
                }

        return differences

    def to_dict(self, include_stock: bool = True, exclude_fields: list | None = None) -> dict:
        """
        Convert master breakout data to dictionary.
        
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
        result['cpr_width'] = float(self.get_cpr_width() or 0)
        result['is_breakout_confirmed'] = self.is_breakout_confirmed()

        # Add enum display values
        result['breakout_indicator_display'] = self.breakout_indicator.value
        result['candle_indicator_display'] = self.candle_indicator.value
        result['volume_indicator_display'] = self.volume_indicator.value

        # Add snapshot metadata
        result['snapshot_age_days'] = (datetime.utcnow() - self.snapshot_date).days

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
        Convert back to V1 master_bo_data format for backward compatibility.
        
        Returns:
            Dictionary in V1 master_bo_data format
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
MasterBreakoutData = MasterBreakoutDataV2
