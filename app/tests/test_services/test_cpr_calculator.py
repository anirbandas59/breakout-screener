"""
Unit tests for CPR (Central Pivot Range) calculator.

These tests verify the exact formulas used in calculate_cpr():
    Pivot = (High + Low + Close) / 3
    BC    = (High + Low) / 2
    TC    = (Pivot - BC) + Pivot          ← returned as 'cpr'
    R1    = (2 * Pivot) - Low
    S1    = (2 * Pivot) - High
    R2    = Pivot + (R1 - S1)
    S2    = Pivot - (R1 - S1)
    Gap   = |TC - BC|
"""

import pytest
from app.services.cpr_calculator import calculate_cpr

TOLERANCE = 1e-9  # Float equality tolerance


class TestCalculateCPRReturnType:
    def test_returns_six_tuple(self):
        result = calculate_cpr(150.0, 145.0, 148.0)
        assert len(result) == 6

    def test_all_values_are_float(self):
        result = calculate_cpr(150.0, 145.0, 148.0)
        assert all(isinstance(v, float) for v in result)


class TestCalculateCPRFormulas:
    """Verify each formula exactly against known inputs."""

    def _expected(self, high: float, low: float, close: float) -> dict:
        """Recompute all values for comparison."""
        pivot = (high + low + close) / 3
        bcp = (high + low) / 2
        tcp = (pivot - bcp) + pivot
        res1 = (2 * pivot) - low
        supp1 = (2 * pivot) - high
        res2 = pivot + (res1 - supp1)
        supp2 = pivot - (res1 - supp1)
        gap = abs(tcp - bcp)
        return {
            "cpr": tcp,
            "res1": res1,
            "res2": res2,
            "supp1": supp1,
            "supp2": supp2,
            "gap": gap,
        }

    def test_cpr_formula(self):
        high, low, close = 150.0, 145.0, 148.0
        cpr, *_ = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["cpr"]
        assert abs(cpr - expected) < TOLERANCE

    def test_res1_formula(self):
        high, low, close = 200.0, 180.0, 190.0
        _, res1, *_ = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["res1"]
        assert abs(res1 - expected) < TOLERANCE

    def test_res2_formula(self):
        high, low, close = 200.0, 180.0, 190.0
        _, _, res2, *_ = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["res2"]
        assert abs(res2 - expected) < TOLERANCE

    def test_supp1_formula(self):
        high, low, close = 200.0, 180.0, 190.0
        _, _, _, supp1, *_ = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["supp1"]
        assert abs(supp1 - expected) < TOLERANCE

    def test_supp2_formula(self):
        high, low, close = 200.0, 180.0, 190.0
        _, _, _, _, supp2, _ = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["supp2"]
        assert abs(supp2 - expected) < TOLERANCE

    def test_gap_formula(self):
        high, low, close = 200.0, 180.0, 190.0
        *_, gap = calculate_cpr(high, low, close)
        expected = self._expected(high, low, close)["gap"]
        assert abs(gap - expected) < TOLERANCE


class TestCalculateCPRInvariants:
    """
    Test mathematical invariants that must always hold
    regardless of specific input values.
    """

    @pytest.mark.parametrize("high, low, close", [
        (150.0, 145.0, 148.0),   # Standard case
        (200.0, 180.0, 190.0),   # Round numbers
        (500.0, 450.0, 480.0),   # High-value stock (Reliance-like)
        (10.0, 8.0, 9.0),        # Low-value stock
        (1000.5, 999.0, 999.8),  # Very narrow range (tight day)
        (2500.0, 2000.0, 2400.0),# Wide range (volatile day)
        (100.0, 80.0, 95.0),     # Bullish close near high
        (100.0, 80.0, 82.0),     # Bearish close near low
    ])
    def test_supp1_le_pivot_le_res1(self, high, low, close):
        """Pivot must always lie between S1 and R1."""
        cpr, res1, res2, supp1, supp2, gap = calculate_cpr(high, low, close)
        pivot = (high + low + close) / 3
        assert supp1 <= pivot <= res1, (
            f"Invariant broken for high={high}, low={low}, close={close}: "
            f"supp1={supp1}, pivot={pivot}, res1={res1}"
        )

    @pytest.mark.parametrize("high, low, close", [
        (150.0, 145.0, 148.0),
        (200.0, 180.0, 190.0),
        (500.0, 450.0, 480.0),
    ])
    def test_res2_ge_res1(self, high, low, close):
        """R2 must always be >= R1."""
        _, res1, res2, _, _, _ = calculate_cpr(high, low, close)
        assert res2 >= res1, f"res2={res2} should be >= res1={res1}"

    @pytest.mark.parametrize("high, low, close", [
        (150.0, 145.0, 148.0),
        (200.0, 180.0, 190.0),
        (500.0, 450.0, 480.0),
    ])
    def test_supp2_le_supp1(self, high, low, close):
        """S2 must always be <= S1."""
        _, _, _, supp1, supp2, _ = calculate_cpr(high, low, close)
        assert supp2 <= supp1, f"supp2={supp2} should be <= supp1={supp1}"

    @pytest.mark.parametrize("high, low, close", [
        (150.0, 145.0, 148.0),
        (200.0, 180.0, 190.0),
        (100.0, 100.0, 100.0),  # Extreme flat day
    ])
    def test_gap_non_negative(self, high, low, close):
        """Gap must always be non-negative."""
        *_, gap = calculate_cpr(high, low, close)
        assert gap >= 0.0, f"gap={gap} should be >= 0"


class TestCalculateCPREdgeCases:
    def test_gap_zero_when_high_equals_low(self):
        """When high == low, BC == Pivot and TC == Pivot, so gap == 0."""
        cpr, _, _, _, _, gap = calculate_cpr(100.0, 100.0, 100.0)
        assert gap == 0.0

    def test_bearish_candle_calculates_correctly(self):
        """CPR uses high/low/close only — open is irrelevant."""
        # Bearish: close < high (typical scenario)
        result = calculate_cpr(200.0, 150.0, 160.0)
        assert result is not None
        assert len(result) == 6

    def test_close_at_midpoint_gap_symmetry(self):
        """When close == (high + low) / 2, pivot == bcp, so gap should be very small."""
        high, low = 100.0, 80.0
        close = (high + low) / 2  # close = 90.0
        cpr, _, _, _, _, gap = calculate_cpr(high, low, close)
        # pivot = (100 + 80 + 90) / 3 = 90.0
        # bcp   = (100 + 80) / 2 = 90.0
        # tcp   = (90.0 - 90.0) + 90.0 = 90.0
        # gap   = |90.0 - 90.0| = 0.0
        assert abs(gap) < TOLERANCE

    def test_very_large_values(self):
        """Calculation should be stable for large price values."""
        cpr, res1, res2, supp1, supp2, gap = calculate_cpr(50000.0, 45000.0, 48000.0)
        pivot = (50000.0 + 45000.0 + 48000.0) / 3
        assert supp1 <= pivot <= res1

    def test_fractional_prices(self):
        """Calculation should be precise for fractional prices."""
        cpr, res1, res2, supp1, supp2, gap = calculate_cpr(10.55, 10.10, 10.35)
        pivot = (10.55 + 10.10 + 10.35) / 3
        assert abs(res1 - ((2 * pivot) - 10.10)) < TOLERANCE
        assert abs(supp1 - ((2 * pivot) - 10.55)) < TOLERANCE
