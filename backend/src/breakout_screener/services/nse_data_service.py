"""
NSE Data Extraction Service
Handles web scraping of NSE indices data using Selenium for dynamic content
V2 implementation preserving V1 business logic
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import config
from ..core.logging import get_logger
from ..models.enums import StockGroupEnum
from ..repositories.stock import StockRepository
from ..schemas.stock import StockCreate, StockUpdate

logger = get_logger(__name__)


@dataclass
class StockSymbolData:
    """Data structure for extracted stock symbols"""

    symbol: str
    company_name: str
    group: str
    chart_link: str
    last_price: float | None = None
    change: float | None = None
    pct_change: float | None = None


class NSEDataService:
    """Service for extracting stock data from NSE indices"""

    def __init__(self):
        self.base_url = config.NSE_BASE_URL
        self.timeout = config.NSE_TIMEOUT
        self.max_retries = config.MAX_RETRIES
        self.chart_base_url = config.CHART_BASE_URL

    def _get_chrome_driver(self) -> webdriver.Chrome:
        """Configure and return Chrome WebDriver instance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values": {"notifications": 2},
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    def _generate_chart_link(self, symbol: str) -> str:
        """Generate GoCharting.com link for stock symbol"""
        return f"{self.chart_base_url}{symbol}.NS"

    def _extract_table_data(
        self, driver: webdriver.Chrome, group_name: str
    ) -> list[StockSymbolData]:
        """Extract stock data from NSE equity table"""
        stocks = []

        try:
            # Wait for table to load
            WebDriverWait(driver, self.timeout).until(
                ec.presence_of_element_located((By.ID, "equityStockTable"))
            )

            # Find and sort the table
            table = driver.find_element(By.ID, "equityStockTable")

            # Try to sort by symbol (first column)
            try:
                table_header = driver.find_element(By.ID, "equityStockTablecol0")
                # Click header 3 times for consistent sorting (V1 behavior)
                for _ in range(3):
                    table_header.click()
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not sort table for {group_name}: {str(e)}")

            # Extract table rows
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:  # Ensure minimum required columns
                        symbol = cells[0].text.strip()
                        company_name = cells[1].text.strip()

                        # Extract price data if available
                        last_price = None
                        change = None
                        pct_change = None

                        if len(cells) >= 5:
                            try:
                                last_price = float(
                                    cells[2].text.strip().replace(",", "")
                                )
                                change = float(cells[3].text.strip().replace(",", ""))
                                pct_change = float(
                                    cells[4].text.strip().replace("%", "")
                                )
                            except (ValueError, AttributeError):
                                pass  # Price data extraction failed, continue with symbol only

                        if symbol and company_name:
                            stock_data = StockSymbolData(
                                symbol=symbol,
                                company_name=company_name,
                                group=group_name,
                                chart_link=self._generate_chart_link(symbol),
                                last_price=last_price,
                                change=change,
                                pct_change=pct_change,
                            )
                            stocks.append(stock_data)

                except Exception as e:
                    logger.warning(
                        f"Failed to extract row data for {group_name}: {str(e)}"
                    )
                    continue

        except TimeoutException:
            logger.error(f"Timeout waiting for table to load for {group_name}")
        except Exception as e:
            logger.error(f"Failed to extract table data for {group_name}: {str(e)}")

        return stocks

    async def fetch_nse_symbols(
        self, group_filter: list[str] | None = None
    ) -> dict[str, list[StockSymbolData]]:
        """
        Fetch stock symbols from NSE indices

        Args:
            group_filter: Optional list of group names to fetch. If None, fetch all groups.

        Returns:
            Dictionary mapping group names to lists of stock symbols
        """
        logger.info("Starting NSE symbols extraction")

        nse_urls = config.NSE_URLS
        if group_filter:
            nse_urls = {k: v for k, v in nse_urls.items() if k in group_filter}

        all_symbols = {}
        driver = None

        try:
            driver = self._get_chrome_driver()

            for group_name, url in nse_urls.items():
                logger.info(f"Fetching data from {group_name}: {url}")

                retry_count = 0
                while retry_count < self.max_retries:
                    try:
                        driver.get(url)
                        time.sleep(5)  # Wait for page to load

                        symbols = self._extract_table_data(driver, group_name)

                        if symbols:
                            all_symbols[group_name] = symbols
                            logger.info(
                                f"Extracted {len(symbols)} symbols from {group_name}"
                            )
                            break
                        else:
                            retry_count += 1
                            logger.warning(
                                f"No symbols extracted from {group_name}, retry {retry_count}"
                            )

                    except Exception as e:
                        retry_count += 1
                        logger.error(
                            f"Error extracting from {group_name} (retry {retry_count}): {str(e)}"
                        )

                        if retry_count >= self.max_retries:
                            logger.error(f"Max retries exceeded for {group_name}")
                            all_symbols[group_name] = []
                        else:
                            time.sleep(10)  # Wait before retry

        except Exception as e:
            logger.error(f"Fatal error in NSE symbols extraction: {str(e)}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error occurred: {str(e)}")

        total_symbols = sum(len(symbols) for symbols in all_symbols.values())
        logger.info(f"NSE symbols extraction completed. Total symbols: {total_symbols}")

        return all_symbols

    async def save_symbols_to_db(
        self, db: AsyncSession, symbols_data: dict[str, list[StockSymbolData]]
    ) -> dict[str, int]:
        """
        Save extracted symbols to database

        Args:
            db: Database session
            symbols_data: Dictionary of extracted symbols data

        Returns:
            Dictionary with counts of created/updated records per group
        """
        logger.info("Saving symbols to database")

        stock_repo = StockRepository(db)
        result_counts = {}

        for group_name, symbols in symbols_data.items():
            created_count = 0
            updated_count = 0

            for symbol_data in symbols:
                try:
                    # Convert group name to enum
                    try:
                        stock_group = StockGroupEnum[group_name]
                    except KeyError:
                        logger.warning(f"Unknown group: {group_name}, using OTHER")
                        stock_group = StockGroupEnum.OTHER

                    # Check if stock exists
                    existing_stock = await stock_repo.get_by_symbol(symbol_data.symbol)

                    if existing_stock:
                        # Update existing stock
                        update_data = StockUpdate(
                            company_name=symbol_data.company_name,
                            stock_group=stock_group,
                            chart_link=symbol_data.chart_link,
                            last_price=symbol_data.last_price,
                            change=symbol_data.change,
                            pct_change=symbol_data.pct_change,
                            is_active=True,
                            updated_at=datetime.utcnow(),
                        )
                        await stock_repo.update(existing_stock.id, update_data)
                        updated_count += 1
                    else:
                        # Create new stock
                        create_data = StockCreate(
                            symbol=symbol_data.symbol,
                            company_name=symbol_data.company_name,
                            stock_group=stock_group,
                            chart_link=symbol_data.chart_link,
                            last_price=symbol_data.last_price,
                            change=symbol_data.change,
                            pct_change=symbol_data.pct_change,
                            is_active=True,
                        )
                        await stock_repo.create(create_data)
                        created_count += 1

                except Exception as e:
                    logger.error(
                        f"Failed to save symbol {symbol_data.symbol}: {str(e)}"
                    )
                    continue

            result_counts[group_name] = {
                "created": created_count,
                "updated": updated_count,
                "total": len(symbols),
            }

            logger.info(
                f"Group {group_name}: {created_count} created, {updated_count} updated"
            )

        await db.commit()
        logger.info("Symbols saved to database successfully")

        return result_counts

    async def fetch_and_save_symbols(
        self, db: AsyncSession, group_filter: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Complete workflow: fetch NSE symbols and save to database

        Args:
            db: Database session
            group_filter: Optional list of group names to process

        Returns:
            Summary of the operation
        """
        start_time = datetime.utcnow()

        try:
            # Extract symbols from NSE
            symbols_data = await self.fetch_nse_symbols(group_filter)

            # Save to database
            save_results = await self.save_symbols_to_db(db, symbols_data)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            return {
                "status": "SUCCESS",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "groups_processed": list(symbols_data.keys()),
                "save_results": save_results,
                "total_symbols": sum(
                    result["total"] for result in save_results.values()
                ),
                "total_created": sum(
                    result["created"] for result in save_results.values()
                ),
                "total_updated": sum(
                    result["updated"] for result in save_results.values()
                ),
            }

        except Exception as e:
            logger.error(f"NSE symbols fetch and save failed: {str(e)}")
            return {
                "status": "FAILED",
                "error": str(e),
                "start_time": start_time,
                "end_time": datetime.utcnow(),
            }
