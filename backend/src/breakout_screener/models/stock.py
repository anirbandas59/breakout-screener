"""
Stock master data model
Normalized stock information with proper validations
"""

from datetime import date

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Date, Index, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship, validates

from .base import BaseModel
from .enums import StockGroupEnum


class Stock(BaseModel):
    """
    Master table for stock information with proper normalization.
    Maps to V1 script_name and group_name fields in a normalized structure.
    """

    __tablename__ = "stocks"

    # Core stock identification
    symbol = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Stock symbol/ticker (e.g., RELIANCE, TCS)",
    )

    company_name = Column(String(255), nullable=False, comment="Full company name")

    isin_code = Column(
        String(12),
        nullable=True,
        comment="International Securities Identification Number",
    )

    # Stock classification
    stock_group = Column(
        ENUM(StockGroupEnum, name="stock_group_enum"),
        nullable=False,
        index=True,
        comment="NSE index group classification",
    )

    # Additional company information
    sector = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Business sector (e.g., Technology, Banking)",
    )

    industry = Column(
        String(100), nullable=True, comment="Specific industry within sector"
    )

    market_cap = Column(
        BigInteger, nullable=True, comment="Market capitalization in rupees"
    )

    # Status and dates
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether stock is actively traded",
    )

    listing_date = Column(
        Date, nullable=True, comment="Date when stock was first listed on exchange"
    )

    # Relationships
    breakout_data = relationship(
        "BreakoutDataV2",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    master_breakout_data = relationship(
        "MasterBreakoutDataV2",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    performance_metrics = relationship(
        "PerformanceMetrics",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "market_cap IS NULL OR market_cap > 0", name="ck_stock_market_cap_positive"
        ),
        CheckConstraint(
            "listing_date IS NULL OR listing_date <= CURRENT_DATE",
            name="ck_stock_listing_date_not_future",
        ),
        Index("idx_stocks_symbol_active", "symbol", "is_active"),
        Index("idx_stocks_group_active", "stock_group", "is_active"),
        Index("idx_stocks_sector_group", "sector", "stock_group"),
        {
            "comment": "Master table containing stock information with proper normalization"
        },
    )

    @validates("symbol")
    def validate_symbol(self, key, symbol):
        """Validate stock symbol format"""
        if not symbol:
            raise ValueError("Stock symbol cannot be empty")

        # Clean and validate symbol
        symbol = symbol.strip().upper()

        # Basic validation - alphanumeric with some special characters
        if not symbol.replace("&", "").replace("-", "").replace(".", "").isalnum():
            raise ValueError(f"Invalid stock symbol format: {symbol}")

        if len(symbol) > 20:
            raise ValueError(f"Stock symbol too long: {symbol}")

        return symbol

    @validates("company_name")
    def validate_company_name(self, key, company_name):
        """Validate company name"""
        if not company_name or not company_name.strip():
            raise ValueError("Company name cannot be empty")

        company_name = company_name.strip()

        if len(company_name) > 255:
            raise ValueError(f"Company name too long: {company_name[:50]}...")

        return company_name

    @validates("isin_code")
    def validate_isin_code(self, key, isin_code):
        """Validate ISIN code format"""
        if isin_code is None:
            return None

        isin_code = isin_code.strip().upper()

        # ISIN should be 12 characters: 2 country code + 9 identifier + 1 check digit
        if len(isin_code) != 12:
            raise ValueError(f"ISIN code must be 12 characters: {isin_code}")

        # Should start with country code (letters) followed by alphanumeric
        if not (isin_code[:2].isalpha() and isin_code[2:].isalnum()):
            raise ValueError(f"Invalid ISIN code format: {isin_code}")

        return isin_code

    @validates("market_cap")
    def validate_market_cap(self, key, market_cap):
        """Validate market cap value"""
        if market_cap is not None and market_cap <= 0:
            raise ValueError(f"Market cap must be positive: {market_cap}")
        return market_cap

    @validates("listing_date")
    def validate_listing_date(self, key, listing_date):
        """Validate listing date"""
        if listing_date is not None:
            from datetime import date as date_class

            if listing_date > date_class.today():
                raise ValueError(f"Listing date cannot be in future: {listing_date}")
        return listing_date

    def __repr__(self) -> str:
        return f"<Stock(symbol={self.symbol}, group={self.stock_group.value}, active={self.is_active})>"

    @classmethod
    def from_v1_data(
        cls, script_name: str, group_name: str, company_name: str | None = None
    ) -> "Stock":
        """
        Create Stock instance from V1 data format.

        Args:
            script_name: V1 script_name field (stock symbol)
            group_name: V1 group_name field (NSE index)
            company_name: Optional company name (will use symbol if not provided)

        Returns:
            Stock instance ready for database insertion
        """
        return cls(
            symbol=script_name.strip().upper(),
            company_name=company_name or script_name.strip().upper(),
            stock_group=StockGroupEnum.from_v1_value(group_name),
            is_active=True,
        )

    @property
    def display_name(self) -> str:
        """Get display-friendly stock name"""
        return f"{self.symbol} - {self.company_name}"

    @property
    def group_display_name(self) -> str:
        """Get display-friendly group name"""
        return self.stock_group.display_name

    def get_latest_breakout_data(self, limit: int = 1):
        """Get latest breakout analysis data for this stock"""
        return self.breakout_data.order_by(
            self.breakout_data.property.mapper.class_.trade_date.desc()
        ).limit(limit)

    def get_breakout_data_for_date_range(self, start_date: date, end_date: date):
        """Get breakout data for specific date range"""
        return self.breakout_data.filter(
            self.breakout_data.property.mapper.class_.trade_date.between(
                start_date, end_date
            )
        ).order_by(self.breakout_data.property.mapper.class_.trade_date.desc())

    def to_dict(
        self, include_relationships: bool = False, exclude_fields: list | None = None
    ) -> dict:
        """
        Convert stock to dictionary with optional relationship data.

        Args:
            include_relationships: Whether to include related data
            exclude_fields: List of fields to exclude

        Returns:
            Dictionary representation
        """
        exclude_fields = exclude_fields or []
        result = super().to_dict(exclude_fields)

        # Add enum display values
        result["stock_group_display"] = self.group_display_name
        result["display_name"] = self.display_name

        if include_relationships:
            # Add latest breakout data
            latest_data = self.get_latest_breakout_data().first()
            result["latest_breakout_data"] = (
                latest_data.to_dict() if latest_data else None
            )

            # Add breakout data count
            result["total_breakout_records"] = self.breakout_data.count()

        return result
