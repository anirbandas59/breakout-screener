"""
Enum definitions for database models
These enums match the PostgreSQL enum types created in the database schema
"""

import enum


class BreakoutIndicatorEnum(str, enum.Enum):
    """
    Breakout analysis indicator values
    Maps to V1 breakout_indicator field values
    """
    BREAKOUT = "BREAKOUT"
    POTENTIAL_BREAKOUT = "POTENTIAL_BREAKOUT"
    NO_BREAKOUT = "NO_BREAKOUT"

    # V1 compatibility mappings
    @classmethod
    def from_v1_value(cls, v1_value: str) -> 'BreakoutIndicatorEnum':
        """Convert V1 breakout indicator values to V2 enum"""
        if not v1_value:
            return cls.NO_BREAKOUT

        v1_lower = v1_value.lower().strip()

        # Map V1 values to V2 enums
        if v1_lower in ["breakout", "breakout confirmed"]:
            return cls.BREAKOUT
        elif v1_lower in ["potential breakout", "possible breakout"]:
            return cls.POTENTIAL_BREAKOUT
        elif v1_lower in ["no breakout", "red candle", "big sell wick"]:
            return cls.NO_BREAKOUT
        else:
            # Default for unknown values
            return cls.NO_BREAKOUT


class CandleIndicatorEnum(str, enum.Enum):
    """
    Candle pattern analysis indicator values
    """
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    DOJI = "DOJI"
    HAMMER = "HAMMER"
    SHOOTING_STAR = "SHOOTING_STAR"

    @classmethod
    def from_v1_value(cls, v1_value: str) -> 'CandleIndicatorEnum':
        """Convert V1 candle indicator values to V2 enum"""
        if not v1_value:
            return cls.NEUTRAL

        v1_lower = v1_value.lower().strip()

        # Map V1 values to V2 enums
        if v1_lower in ["bullish", "green candle", "positive"]:
            return cls.BULLISH
        elif v1_lower in ["bearish", "red candle", "negative"]:
            return cls.BEARISH
        elif v1_lower in ["doji"]:
            return cls.DOJI
        elif v1_lower in ["hammer"]:
            return cls.HAMMER
        elif v1_lower in ["shooting star", "shooting_star"]:
            return cls.SHOOTING_STAR
        else:
            return cls.NEUTRAL


class VolumeIndicatorEnum(str, enum.Enum):
    """
    Volume strength analysis indicator values
    Maps to V1 volume_indicator field values
    """
    HIGH_VOLUME = "HIGH_VOLUME"
    NORMAL_VOLUME = "NORMAL_VOLUME"
    LOW_VOLUME = "LOW_VOLUME"

    @classmethod
    def from_v1_value(cls, v1_value: str) -> 'VolumeIndicatorEnum':
        """Convert V1 volume indicator values to V2 enum"""
        if not v1_value:
            return cls.NORMAL_VOLUME

        v1_lower = v1_value.lower().strip()

        # Map V1 values to V2 enums (preserve exact V1 logic)
        if v1_lower in ["good", "high", "strong"]:
            return cls.HIGH_VOLUME
        elif v1_lower in ["average", "normal", "medium"]:
            return cls.NORMAL_VOLUME
        elif v1_lower in ["low", "weak", "poor"]:
            return cls.LOW_VOLUME
        else:
            return cls.NORMAL_VOLUME


class StockGroupEnum(str, enum.Enum):
    """
    NSE stock group/index classifications
    Maps to V1 group_name field values
    """
    NIFTY_50 = "NIFTY_50"
    NIFTY_200 = "NIFTY_200"
    NIFTY_MIDCAP_150 = "NIFTY_MIDCAP_150"
    NIFTY_MIDSMALLCAP_400 = "NIFTY_MIDSMALLCAP_400"
    NIFTY_SMALLCAP_250 = "NIFTY_SMALLCAP_250"

    @classmethod
    def from_v1_value(cls, v1_value: str) -> 'StockGroupEnum':
        """Convert V1 group_name values to V2 enum"""
        if not v1_value:
            return cls.NIFTY_50  # Default fallback

        v1_clean = v1_value.upper().strip().replace(" ", "_")

        # Direct mapping for most cases
        if v1_clean in ["NIFTY_50", "NIFTY50"]:
            return cls.NIFTY_50
        elif v1_clean in ["NIFTY_200", "NIFTY200"]:
            return cls.NIFTY_200
        elif v1_clean in ["NIFTY_MIDCAP_150", "NIFTYMIDCAP150", "MIDCAP_150"]:
            return cls.NIFTY_MIDCAP_150
        elif v1_clean in ["NIFTY_MIDSMALLCAP_400", "NIFTYMIDSMALLCAP400", "MIDSMALLCAP_400"]:
            return cls.NIFTY_MIDSMALLCAP_400
        elif v1_clean in ["NIFTY_SMALLCAP_250", "NIFTYSMALLCAP250", "SMALLCAP_250"]:
            return cls.NIFTY_SMALLCAP_250
        else:
            # Default for unknown groups
            return cls.NIFTY_50

    @property
    def display_name(self) -> str:
        """Get human-readable display name"""
        return self.value.replace("_", " ").title()

    @property
    def nse_url_key(self) -> str:
        """Get corresponding NSE URL configuration key"""
        return f"NSE_URL_{self.value}"
