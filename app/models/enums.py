"""
Enum types for breakout analysis indicators.

This module defines type-safe enums to replace magic strings throughout the application.
"""

from enum import Enum


class BreakoutIndicator(str, Enum):
    """
    Breakout indicator values for stock analysis.

    Values:
        RED_CANDLE: Stock closed below opening price
        NO_BREAKOUT: Stock closed below previous high
        BREAKOUT: Stock broke out with strong momentum
        BIG_SELL_WICK: Stock broke out but has large upper wick (profit booking)
        NO_ENTRY: No clear entry signal
    """
    RED_CANDLE = "Red candle"
    NO_BREAKOUT = "no breakout"
    BREAKOUT = "Breakout"
    BIG_SELL_WICK = "Big Sell Wick"
    NO_ENTRY = "No Entry"


class CandleIndicator(str, Enum):
    """
    Candle color indicator based on open/close relationship.

    Values:
        RED_CANDLE: Bearish candle (close < open)
        GREEN_CANDLE: Bullish candle (close > open)
        DOJI: Neutral candle (close = open)
    """
    RED_CANDLE = "Red candle"
    GREEN_CANDLE = "Green candle"
    DOJI = "Doji"


class VolumeIndicator(str, Enum):
    """
    Volume indicator relative to average volume.

    Values:
        GOOD: Volume > 2x average (strong participation)
        AVERAGE: Volume > average but < 2x average
        LOW: Volume below average (weak participation)
    """
    GOOD = "Good"
    AVERAGE = "Average"
    LOW = "Low"
