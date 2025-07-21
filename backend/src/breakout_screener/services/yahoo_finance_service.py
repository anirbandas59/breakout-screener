"""
Yahoo Finance Historical Data Service
Fetches historical OHLCV data for stocks using httpx (replacing Selenium from V1)
Modern async implementation with V1 business logic preservation
"""

import asyncio
import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import httpx
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import config
from ..core.logging import get_logger
from ..repositories.stock import StockRepository

logger = get_logger(__name__)


@dataclass
class HistoricalDataPoint:
    """Single day historical data point"""

    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adj_close: Decimal | None = None


@dataclass
class HistoricalData:
    """Complete historical data for a symbol"""

    symbol: str
    data_points: list[HistoricalDataPoint]
    start_date: datetime
    end_date: datetime
    total_days: int

    @property
    def latest(self) -> HistoricalDataPoint | None:
        """Get the latest data point"""
        return self.data_points[-1] if self.data_points else None

    @property
    def previous_highs(self, days: int = 10) -> list[Decimal]:
        """Get previous highs for breakout analysis (V1 logic preservation)"""
        if len(self.data_points) < days:
            return [point.high for point in self.data_points]
        return [point.high for point in self.data_points[-days:]]

    @property
    def average_volume(self, days: int = 10) -> Decimal:
        """Calculate average volume for last N days (V1 logic preservation)"""
        if not self.data_points:
            return Decimal("0")

        recent_points = (
            self.data_points[-days:]
            if len(self.data_points) >= days
            else self.data_points
        )
        total_volume = sum(point.volume for point in recent_points)
        return Decimal(total_volume) / len(recent_points)


class YahooFinanceService:
    """Service for fetching historical stock data from Yahoo Finance"""

    def __init__(self):
        self.base_url = config.YFIN_HIST_URL
        self.timeout = config.NSE_TIMEOUT
        self.max_retries = config.MAX_RETRIES

    async def _fetch_csv_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> str | None:
        """Fetch CSV data from Yahoo Finance using httpx"""

        # Convert symbol to Yahoo Finance format (add .NS for NSE stocks)
        yf_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol

        # Convert dates to timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        url = f"{self.base_url}/{yf_symbol}"
        params = {
            "period1": start_timestamp,
            "period2": end_timestamp,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Fetching {symbol} data (attempt {attempt + 1})")
                    response = await client.get(url, params=params, headers=headers)

                    if response.status_code == 200:
                        return response.text
                    elif response.status_code == 404:
                        logger.warning(f"Symbol {symbol} not found on Yahoo Finance")
                        return None
                    else:
                        logger.warning(
                            f"HTTP {response.status_code} for {symbol} (attempt {attempt + 1})"
                        )

                except Exception as e:
                    logger.warning(
                        f"Error fetching {symbol} (attempt {attempt + 1}): {str(e)}"
                    )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

        logger.error(
            f"Failed to fetch data for {symbol} after {self.max_retries} attempts"
        )
        return None

    def _parse_csv_data(self, csv_data: str, symbol: str) -> HistoricalData | None:
        """Parse CSV data into HistoricalData structure"""
        try:
            # Read CSV data into pandas DataFrame
            df = pd.read_csv(io.StringIO(csv_data))

            # Check if DataFrame is empty or has required columns
            required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
            if df.empty or not all(col in df.columns for col in required_columns):
                logger.warning(
                    f"Invalid CSV data for {symbol}: missing required columns"
                )
                return None

            # Convert Date column to datetime
            df["Date"] = pd.to_datetime(df["Date"])

            # Sort by date to ensure chronological order
            df = df.sort_values("Date")

            # Filter out invalid rows
            df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
            df = df[df["Volume"] > 0]  # Remove zero volume days

            if df.empty:
                logger.warning(f"No valid data points for {symbol}")
                return None

            # Create HistoricalDataPoint objects
            data_points = []
            for _, row in df.iterrows():
                try:
                    data_point = HistoricalDataPoint(
                        date=row["Date"].to_pydatetime(),
                        open=Decimal(str(row["Open"])),
                        high=Decimal(str(row["High"])),
                        low=Decimal(str(row["Low"])),
                        close=Decimal(str(row["Close"])),
                        volume=int(row["Volume"]),
                        adj_close=Decimal(str(row.get("Adj Close", row["Close"]))),
                    )
                    data_points.append(data_point)
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Invalid data point for {symbol} on {row['Date']}: {str(e)}"
                    )
                    continue

            if not data_points:
                logger.warning(f"No valid data points created for {symbol}")
                return None

            return HistoricalData(
                symbol=symbol,
                data_points=data_points,
                start_date=data_points[0].date,
                end_date=data_points[-1].date,
                total_days=len(data_points),
            )

        except Exception as e:
            logger.error(f"Failed to parse CSV data for {symbol}: {str(e)}")
            return None

    async def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime | None = None,
        days_back: int | None = None,
    ) -> HistoricalData | None:
        """
        Fetch historical data for a single symbol

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            start_date: Start date for data
            end_date: End date for data (if None, use today)
            days_back: Alternative to end_date, fetch N days from start_date

        Returns:
            HistoricalData object or None if failed
        """

        # Calculate end date if not provided
        if end_date is None:
            if days_back:
                end_date = start_date + timedelta(days=days_back)
            else:
                end_date = datetime.now()

        logger.info(
            f"Fetching historical data for {symbol} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Fetch CSV data
            csv_data = await self._fetch_csv_data(symbol, start_date, end_date)

            if not csv_data:
                return None

            # Parse CSV data
            historical_data = self._parse_csv_data(csv_data, symbol)

            if historical_data:
                logger.info(
                    f"Successfully fetched {historical_data.total_days} days of data for {symbol}"
                )

            return historical_data

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {str(e)}")
            return None

    async def fetch_multiple_symbols(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime | None = None,
        days_back: int | None = None,
        max_concurrent: int = 5,
    ) -> dict[str, HistoricalData | None]:
        """
        Fetch historical data for multiple symbols concurrently

        Args:
            symbols: List of stock symbols
            start_date: Start date for data
            end_date: End date for data
            days_back: Alternative to end_date
            max_concurrent: Maximum concurrent requests

        Returns:
            Dictionary mapping symbols to HistoricalData objects
        """

        logger.info(f"Fetching historical data for {len(symbols)} symbols")

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(
            symbol: str,
        ) -> tuple[str, HistoricalData | None]:
            async with semaphore:
                data = await self.fetch_historical_data(
                    symbol, start_date, end_date, days_back
                )
                return symbol, data

        # Execute all requests concurrently
        tasks = [fetch_with_semaphore(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        historical_data_map = {}
        successful_count = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {str(result)}")
                continue

            symbol, data = result
            historical_data_map[symbol] = data

            if data:
                successful_count += 1

        logger.info(
            f"Successfully fetched data for {successful_count}/{len(symbols)} symbols"
        )

        return historical_data_map

    async def fetch_symbols_from_db(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime | None = None,
        days_back: int | None = None,
        group_filter: list[str] | None = None,
        active_only: bool = True,
    ) -> dict[str, HistoricalData | None]:
        """
        Fetch historical data for all symbols in database

        Args:
            db: Database session
            start_date: Start date for historical data
            end_date: End date for data
            days_back: Alternative to end_date
            group_filter: Optional list of group names to filter
            active_only: Only fetch data for active stocks

        Returns:
            Dictionary mapping symbols to HistoricalData objects
        """

        # Get stocks from database
        stock_repo = StockRepository(db)

        if group_filter:
            stocks = []
            for group in group_filter:
                group_stocks = await stock_repo.get_by_group(group)
                stocks.extend(group_stocks)
        else:
            stocks = (
                await stock_repo.get_active_stocks()
                if active_only
                else await stock_repo.get_all()
            )

        if not stocks:
            logger.warning("No stocks found in database")
            return {}

        symbols = [stock.symbol for stock in stocks]
        logger.info(
            f"Fetching historical data for {len(symbols)} symbols from database"
        )

        return await self.fetch_multiple_symbols(
            symbols, start_date, end_date, days_back
        )

    def calculate_previous_high(
        self,
        historical_data: HistoricalData,
        analysis_date: datetime,
        lookback_days: int = 10,
    ) -> Decimal | None:
        """
        Calculate previous high for breakout analysis (V1 logic preservation)

        Args:
            historical_data: Historical data for the symbol
            analysis_date: Date for which analysis is being done
            lookback_days: Number of days to look back for high calculation

        Returns:
            Previous high value or None if insufficient data
        """

        # Filter data points up to analysis date
        relevant_points = [
            point
            for point in historical_data.data_points
            if point.date.date() < analysis_date.date()
        ]

        if not relevant_points:
            return None

        # Get last N days or all available points if less than N
        recent_points = (
            relevant_points[-lookback_days:]
            if len(relevant_points) >= lookback_days
            else relevant_points
        )

        if not recent_points:
            return None

        # Return maximum high from the period
        return max(point.high for point in recent_points)
