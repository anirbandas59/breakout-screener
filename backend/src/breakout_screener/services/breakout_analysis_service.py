"""
Breakout Analysis Service
Core business logic for breakout pattern detection and CPR calculations
V2 implementation preserving exact V1 formulas and algorithms
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..models.enums import (
    BreakoutIndicatorEnum,
    CandleIndicatorEnum,
    VolumeIndicatorEnum,
)
from ..repositories.breakout_data import BreakoutDataRepository
from ..repositories.stock import StockRepository
from ..schemas.breakout_data import BreakoutDataCreate, BreakoutDataUpdate
from .yahoo_finance_service import YahooFinanceService

logger = get_logger(__name__)


@dataclass
class CPRAnalysis:
    """Central Pivot Range analysis results"""

    pivot: Decimal
    resistance_1: Decimal
    resistance_2: Decimal
    support_1: Decimal
    support_2: Decimal
    gap_percentage: Decimal
    is_narrow_gap: bool


@dataclass
class VolumeAnalysis:
    """Volume analysis results"""

    current_volume: int
    average_volume: Decimal
    volume_ratio: Decimal
    volume_indicator: VolumeIndicatorEnum


@dataclass
class CandleAnalysis:
    """Candle pattern analysis results"""

    candle_type: CandleIndicatorEnum
    body_percentage: Decimal
    upper_wick_percentage: Decimal
    lower_wick_percentage: Decimal


@dataclass
class BreakoutResult:
    """Complete breakout analysis result"""

    symbol: str
    analysis_date: datetime
    ohlcv_data: dict[str, Any]
    cpr_analysis: CPRAnalysis
    volume_analysis: VolumeAnalysis
    candle_analysis: CandleAnalysis
    previous_high: Decimal | None
    breakout_indicator: BreakoutIndicatorEnum
    analysis_summary: str


class BreakoutAnalysisService:
    """Service for breakout pattern analysis and CPR calculations"""

    def __init__(self):
        self.yahoo_service = YahooFinanceService()

    def calculate_cpr(
        self, high: Decimal, low: Decimal, close: Decimal, pivot_threshold: float = 0.5
    ) -> CPRAnalysis:
        """
        Calculate Central Pivot Range (CPR) - V1 exact formula preservation

        Args:
            high: High price
            low: Low price
            close: Close price
            pivot_threshold: Percentage threshold for narrow gap detection

        Returns:
            CPRAnalysis object with all calculated values
        """

        # Core CPR Formula: Pivot = (H + L + C) / 3
        pivot = (high + low + close) / Decimal("3")

        # Support and Resistance Levels (V1 formulas)
        resistance_1 = (Decimal("2") * pivot) - low  # R1 = (2 * Pivot) - Low
        resistance_2 = pivot + (high - low)  # R2 = Pivot + (High - Low)
        support_1 = (Decimal("2") * pivot) - high  # S1 = (2 * Pivot) - High
        support_2 = pivot - (high - low)  # S2 = Pivot - (High - Low)

        # Gap percentage calculation for narrow range detection
        gap_range = resistance_1 - support_1
        gap_percentage = (gap_range / pivot) * Decimal("100")

        # Narrow gap detection (V1 logic)
        is_narrow_gap = gap_percentage <= Decimal(str(pivot_threshold))

        return CPRAnalysis(
            pivot=pivot.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            resistance_1=resistance_1.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            resistance_2=resistance_2.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            support_1=support_1.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            support_2=support_2.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            gap_percentage=gap_percentage.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            is_narrow_gap=is_narrow_gap,
        )

    def analyze_volume(
        self, current_volume: int, average_volume: Decimal
    ) -> VolumeAnalysis:
        """
        Analyze volume patterns - V1 logic preservation

        Args:
            current_volume: Current day volume
            average_volume: 10-day average volume

        Returns:
            VolumeAnalysis object
        """

        if average_volume == 0:
            volume_ratio = Decimal("1")
        else:
            volume_ratio = Decimal(current_volume) / average_volume

        # V1 Volume Classification Logic
        if volume_ratio >= Decimal("2.0"):
            volume_indicator = VolumeIndicatorEnum.HIGH_VOLUME
        elif volume_ratio >= Decimal("1.0"):
            volume_indicator = VolumeIndicatorEnum.NORMAL_VOLUME
        else:
            volume_indicator = VolumeIndicatorEnum.LOW_VOLUME

        return VolumeAnalysis(
            current_volume=current_volume,
            average_volume=average_volume,
            volume_ratio=volume_ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            volume_indicator=volume_indicator,
        )

    def analyze_candle(
        self, open_price: Decimal, high: Decimal, low: Decimal, close: Decimal
    ) -> CandleAnalysis:
        """
        Analyze candle patterns - V1 logic preservation

        Args:
            open_price: Opening price
            high: High price
            low: Low price
            close: Close price

        Returns:
            CandleAnalysis object
        """

        # Calculate candle components
        total_range = high - low
        body_range = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low

        # Calculate percentages
        if total_range > 0:
            body_percentage = (body_range / total_range) * Decimal("100")
            upper_wick_percentage = (upper_wick / total_range) * Decimal("100")
            lower_wick_percentage = (lower_wick / total_range) * Decimal("100")
        else:
            body_percentage = upper_wick_percentage = lower_wick_percentage = Decimal(
                "0"
            )

        # V1 Candle Classification Logic
        if close > open_price:
            if body_percentage >= Decimal("70"):
                candle_type = CandleIndicatorEnum.BULLISH
            elif body_percentage <= Decimal("10"):
                candle_type = CandleIndicatorEnum.DOJI
            else:
                candle_type = CandleIndicatorEnum.NEUTRAL
        elif close < open_price:
            if body_percentage >= Decimal("70"):
                candle_type = CandleIndicatorEnum.BEARISH
            elif upper_wick_percentage >= Decimal("60"):
                candle_type = CandleIndicatorEnum.SHOOTING_STAR
            else:
                candle_type = CandleIndicatorEnum.BEARISH
        else:
            candle_type = CandleIndicatorEnum.DOJI

        # Check for hammer pattern (V1 logic)
        if (
            lower_wick_percentage >= Decimal("60")
            and body_percentage <= Decimal("30")
            and upper_wick_percentage <= Decimal("20")
        ):
            candle_type = CandleIndicatorEnum.HAMMER

        return CandleAnalysis(
            candle_type=candle_type,
            body_percentage=body_percentage.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            upper_wick_percentage=upper_wick_percentage.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            lower_wick_percentage=lower_wick_percentage.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        )

    def determine_breakout(
        self,
        current_close: Decimal,
        previous_high: Decimal | None,
        cpr_analysis: CPRAnalysis,
        volume_analysis: VolumeAnalysis,
        candle_analysis: CandleAnalysis,
    ) -> BreakoutIndicatorEnum:
        """
        Determine breakout status - V1 multi-criteria logic preservation

        Args:
            current_close: Current close price
            previous_high: Previous period high
            cpr_analysis: CPR analysis results
            volume_analysis: Volume analysis results
            candle_analysis: Candle analysis results

        Returns:
            BreakoutIndicatorEnum
        """

        breakout_criteria = 0

        # Criteria 1: Close above previous high (if available)
        if previous_high and current_close > previous_high:
            breakout_criteria += 1

        # Criteria 2: Close above resistance level
        if current_close > cpr_analysis.resistance_1:
            breakout_criteria += 1

        # Criteria 3: Volume above average
        if volume_analysis.volume_indicator in [
            VolumeIndicatorEnum.HIGH_VOLUME,
            VolumeIndicatorEnum.NORMAL_VOLUME,
        ]:
            breakout_criteria += 1

        # Criteria 4: Bullish candle pattern
        if candle_analysis.candle_type in [
            CandleIndicatorEnum.BULLISH,
            CandleIndicatorEnum.HAMMER,
        ]:
            breakout_criteria += 1

        # Criteria 5: Narrow gap (higher probability)
        if cpr_analysis.is_narrow_gap:
            breakout_criteria += 1

        # V1 Breakout Decision Logic
        if breakout_criteria >= 3:
            return BreakoutIndicatorEnum.BREAKOUT
        elif breakout_criteria >= 2:
            return BreakoutIndicatorEnum.POTENTIAL_BREAKOUT
        else:
            return BreakoutIndicatorEnum.NO_BREAKOUT

    async def analyze_symbol(
        self,
        symbol: str,
        analysis_date: datetime,
        pivot_threshold: float = 0.5,
        historical_days: int = 20,
    ) -> BreakoutResult | None:
        """
        Complete breakout analysis for a single symbol

        Args:
            symbol: Stock symbol
            analysis_date: Date for analysis
            pivot_threshold: Pivot gap threshold percentage
            historical_days: Days of historical data to fetch

        Returns:
            BreakoutResult or None if analysis failed
        """

        logger.debug(
            f"Starting breakout analysis for {symbol} on {analysis_date.date()}"
        )

        try:
            # Fetch historical data
            start_date = analysis_date - timedelta(
                days=historical_days + 10
            )  # Buffer for weekends
            historical_data = await self.yahoo_service.fetch_historical_data(
                symbol=symbol, start_date=start_date, end_date=analysis_date
            )

            if not historical_data or not historical_data.data_points:
                logger.warning(f"No historical data available for {symbol}")
                return None

            # Find the data point for analysis date
            analysis_point = None
            for point in historical_data.data_points:
                if point.date.date() == analysis_date.date():
                    analysis_point = point
                    break

            if not analysis_point:
                logger.warning(
                    f"No data available for {symbol} on {analysis_date.date()}"
                )
                return None

            # Calculate previous high (10-day lookback)
            previous_high = self.yahoo_service.calculate_previous_high(
                historical_data, analysis_date, lookback_days=10
            )

            # Calculate average volume (10-day)
            avg_volume = historical_data.average_volume(days=10)

            # Perform analyses
            cpr_analysis = self.calculate_cpr(
                high=analysis_point.high,
                low=analysis_point.low,
                close=analysis_point.close,
                pivot_threshold=pivot_threshold,
            )

            volume_analysis = self.analyze_volume(
                current_volume=analysis_point.volume, average_volume=avg_volume
            )

            candle_analysis = self.analyze_candle(
                open_price=analysis_point.open,
                high=analysis_point.high,
                low=analysis_point.low,
                close=analysis_point.close,
            )

            # Determine breakout status
            breakout_indicator = self.determine_breakout(
                current_close=analysis_point.close,
                previous_high=previous_high,
                cpr_analysis=cpr_analysis,
                volume_analysis=volume_analysis,
                candle_analysis=candle_analysis,
            )

            # Generate analysis summary
            summary = f"CPR: {cpr_analysis.pivot} | Gap: {cpr_analysis.gap_percentage}% | Vol: {volume_analysis.volume_ratio}x | Pattern: {candle_analysis.candle_type.value}"

            # Create result
            result = BreakoutResult(
                symbol=symbol,
                analysis_date=analysis_date,
                ohlcv_data={
                    "open": analysis_point.open,
                    "high": analysis_point.high,
                    "low": analysis_point.low,
                    "close": analysis_point.close,
                    "volume": analysis_point.volume,
                },
                cpr_analysis=cpr_analysis,
                volume_analysis=volume_analysis,
                candle_analysis=candle_analysis,
                previous_high=previous_high,
                breakout_indicator=breakout_indicator,
                analysis_summary=summary,
            )

            logger.debug(f"Analysis completed for {symbol}: {breakout_indicator.value}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze {symbol}: {str(e)}")
            return None

    async def save_analysis_to_db(
        self, db: AsyncSession, analysis_result: BreakoutResult
    ) -> bool:
        """
        Save analysis results to database

        Args:
            db: Database session
            analysis_result: Analysis results

        Returns:
            True if saved successfully, False otherwise
        """

        try:
            # Get stock from database
            stock_repo = StockRepository(db)
            stock = await stock_repo.get_by_symbol(analysis_result.symbol)

            if not stock:
                logger.warning(f"Stock {analysis_result.symbol} not found in database")
                return False

            # Create breakout data record
            breakout_repo = BreakoutDataRepository(db)

            # Check if record already exists
            existing_record = await breakout_repo.get_by_stock_and_date(
                stock.id, analysis_result.analysis_date.date()
            )

            ohlcv = analysis_result.ohlcv_data
            cpr = analysis_result.cpr_analysis
            vol = analysis_result.volume_analysis

            breakout_data = {
                "stock_id": stock.id,
                "trade_date": analysis_result.analysis_date.date(),
                "open_price": ohlcv["open"],
                "high_price": ohlcv["high"],
                "low_price": ohlcv["low"],
                "close_price": ohlcv["close"],
                "volume": ohlcv["volume"],
                "previous_high": analysis_result.previous_high,
                "cpr": cpr.pivot,
                "resistance_1": cpr.resistance_1,
                "resistance_2": cpr.resistance_2,
                "support_1": cpr.support_1,
                "support_2": cpr.support_2,
                "gap_percentage": cpr.gap_percentage,
                "breakout_indicator": analysis_result.breakout_indicator,
                "candle_indicator": analysis_result.candle_analysis.candle_type,
                "volume_indicator": vol.volume_indicator,
                "analysis_summary": analysis_result.analysis_summary,
            }

            if existing_record:
                # Update existing record
                update_data = BreakoutDataUpdate(**breakout_data)
                await breakout_repo.update(existing_record.id, update_data)
            else:
                # Create new record
                create_data = BreakoutDataCreate(**breakout_data)
                await breakout_repo.create(create_data)

            logger.debug(f"Saved analysis for {analysis_result.symbol} to database")
            return True

        except Exception as e:
            logger.error(
                f"Failed to save analysis for {analysis_result.symbol}: {str(e)}"
            )
            return False

    async def analyze_multiple_symbols(
        self,
        db: AsyncSession,
        symbols: list[str],
        analysis_date: datetime,
        pivot_threshold: float = 0.5,
        max_concurrent: int = 5,
    ) -> dict[str, Any]:
        """
        Analyze multiple symbols concurrently

        Args:
            db: Database session
            symbols: List of symbols to analyze
            analysis_date: Analysis date
            pivot_threshold: Pivot threshold
            max_concurrent: Maximum concurrent analyses

        Returns:
            Analysis summary
        """

        logger.info(
            f"Starting analysis for {len(symbols)} symbols on {analysis_date.date()}"
        )
        start_time = datetime.now()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_and_save(symbol: str) -> tuple[str, bool]:
            async with semaphore:
                try:
                    result = await self.analyze_symbol(
                        symbol, analysis_date, pivot_threshold
                    )
                    if result:
                        success = await self.save_analysis_to_db(db, result)
                        return symbol, success
                    return symbol, False
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {str(e)}")
                    return symbol, False

        # Execute all analyses
        tasks = [analyze_and_save(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = 0
        failed = 0
        errors = []

        for result in results:
            if isinstance(result, Exception):
                failed += 1
                errors.append(str(result))
            else:
                symbol, success = result
                if success:
                    successful += 1
                else:
                    failed += 1

        # Commit database changes
        await db.commit()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "status": "SUCCESS" if successful > 0 else "FAILED",
            "total_symbols": len(symbols),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(symbols)) * 100 if symbols else 0,
            "duration_seconds": duration,
            "start_time": start_time,
            "end_time": end_time,
            "analysis_date": analysis_date.date(),
            "pivot_threshold": pivot_threshold,
            "errors": errors[:10],  # Limit error list
        }

        logger.info(
            f"Analysis completed: {successful}/{len(symbols)} successful in {duration:.1f}s"
        )
        return summary
