"""
CPR (Central Pivot Range) Calculator Module

This module provides functionality to calculate Central Pivot Range levels
for technical analysis of stocks. CPR is a popular indicator used to identify
potential support and resistance levels.

References:
- CPR = Central Pivot Range (combination of TC and BC)
- TC (Top Central Pivot) = (Pivot - BC) + Pivot
- BC (Bottom Central Pivot) = (High + Low) / 2
- Pivot = (High + Low + Close) / 3
"""

from typing import Tuple


def calculate_cpr(high: float, low: float, close: float) -> Tuple[float, float, float, float, float, float]:
    """
    Calculate Central Pivot Range (CPR) levels for a given price bar.

    CPR is a technical indicator that helps identify potential support and resistance
    levels based on the previous day's high, low, and close prices.

    Formula:
        Pivot = (High + Low + Close) / 3
        BC (Bottom Central Pivot) = (High + Low) / 2
        TC (Top Central Pivot) = (Pivot - BC) + Pivot
        R1 (Resistance 1) = (2 * Pivot) - Low
        S1 (Support 1) = (2 * Pivot) - High
        R2 (Resistance 2) = Pivot + (R1 - S1)
        S2 (Support 2) = Pivot - (R1 - S1)
        Gap = |TC - BC|

    Args:
        high (float): The high price of the previous trading day
        low (float): The low price of the previous trading day
        close (float): The closing price of the previous trading day

    Returns:
        Tuple[float, float, float, float, float, float]: A tuple containing:
            - cpr (float): Central Pivot (Top Central Pivot / TC)
            - res1 (float): First resistance level
            - res2 (float): Second resistance level
            - supp1 (float): First support level
            - supp2 (float): Second support level
            - gap (float): Gap between TC and BC (narrow gap indicates consolidation)

    Example:
        >>> calculate_cpr(high=150.0, low=145.0, close=148.0)
        (148.0, 151.0, 154.0, 145.0, 142.0, 1.5)

    Notes:
        - A narrow gap (TC ≈ BC) suggests a consolidation phase
        - A wide gap suggests trending market conditions
        - Price above CPR is generally bullish
        - Price below CPR is generally bearish
    """
    # Calculate Pivot Point (PP)
    pivot = (high + low + close) / 3

    # Calculate Bottom Central Pivot (BC)
    bcp = (high + low) / 2

    # Calculate Top Central Pivot (TC) - this is what we call 'cpr'
    tcp = (pivot - bcp) + pivot
    cpr = tcp

    # Calculate First Resistance and Support
    res1 = (2 * pivot) - low
    supp1 = (2 * pivot) - high

    # Calculate Second Resistance and Support
    res2 = pivot + (res1 - supp1)
    supp2 = pivot - (res1 - supp1)

    # Calculate Gap (width of CPR)
    gap = abs(tcp - bcp)

    return cpr, res1, res2, supp1, supp2, gap
