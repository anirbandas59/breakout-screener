import time
import os
import logging
import pandas as pd
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.utils.error_handlers import log_error_with_context, DataFetchError

from selenium.webdriver.common.by import By
from sqlalchemy.orm import Session

from app.models.breakout_data import BreakoutData
from app.utils.selenium_driver import get_chrome_driver
from app.config import settings
# from app.config import NSE_URL


def fetch_script_symbols(db: Session):
    """
    Fetches the script symbols from NSE and saves it into the database.
    """
    # Get NSE URL from environment variables
    # logging.basicConfig(level=logging.INFO)
    nse_urls = settings.nse_urls
    # nse_url = os.getenv(settings.nse_url)
    # print(NSE_URL)
    # driver.get(NSE_URL)

    # Get the chrome driver
    driver = get_chrome_driver()

    try:
        # Loop through the NSE URLs
        for url in nse_urls:
            logging.info("Fetching data from URL: %s", url)
            driver.get(url)

            # Wait for page to load
            driver.implicitly_wait(10)

            try:  # Locate the data
                # Wait for page content to load
                time.sleep(5)

                # Find the table
                table = driver.find_element(By.ID, "equityStockTable")
                logging.info("Table found")

                # Wait for table to populate with data
                logging.info("Waiting for table data to load...")
                for attempt in range(15):
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logging.info(f"Wait attempt {attempt + 1}: {len(rows)} rows")

                    if len(rows) > 10:  # Table has loaded with data
                        break

                    time.sleep(1)

                # Re-fetch rows after waiting
                rows = table.find_elements(By.TAG_NAME, "tr")
                logging.info(f"Total rows found: {len(rows)}")

                # Create a list of dictionaries
                data = []

                # Table structure discovered:
                # Row 0: Header row (th elements)
                # Row 1: Index name row (e.g., "NIFTY 50") - SKIP THIS!
                # Rows 2+: Actual stock data rows (each has 15 td elements)

                if len(rows) > 2:
                    # Get the group name from row 1 (index name)
                    group_name = rows[1].find_elements(
                        By.TAG_NAME, "td")[0].text.strip()
                    logging.info(f"Group name: {group_name}")

                    # Extract stocks from rows 2 onwards (skip header and index name row)
                    for row_index in range(2, len(rows)):
                        cells = rows[row_index].find_elements(By.TAG_NAME, "td")

                        # Each stock row has 15 cells
                        if len(cells) >= 15:
                            # First cell contains the script name
                            script_name = cells[0].text.strip()

                            # Skip empty names
                            if script_name:
                                data.append({
                                    "group_name": group_name,
                                    "script_name": script_name
                                })
                                logging.debug(f"Row {row_index}: Added {script_name}")

                # Log the data
                # print(data)
                logging.info(
                    "Data captured from %s: [Count: %d] => %s", url, len(data), data[:10])

                # Save the data into the database
                for item in data:
                    # Create the chart link
                    chart_link = f"https://gocharting.com/terminal?ticker=NSE:{
                        item['script_name']}&layout=1"
                    # Check if the record exists
                    db_record = db.query(BreakoutData).filter_by(
                        script_name=item["script_name"],
                        # group_name=item["group_name"]
                    ).first()

                    if not db_record:
                        # Insert new record
                        db_record = BreakoutData(
                            script_name=item["script_name"],
                            group_name=item["group_name"],
                            link=chart_link,
                            date=None  # Placeholder
                        )
                        db.add(db_record)
                    else:
                        # Update the record
                        db_record.link = chart_link

                # Commit the changes
                db.commit()

            except Exception as e:
                # Log the error
                logging.error("Error fetching data from %s: %s", url, e)
                # print("------------------------------------------------------>")
                # print(f"Error fetching script symbols: {e}")

    finally:
        # Quit the driver
        driver.quit()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logging.warning(
        f"Retrying {retry_state.fn.__name__}, attempt {retry_state.attempt_number}"
    )
)
def fetch_script_historical_data(script_name: str, period: str = "1mo") -> pd.DataFrame:
    """
    Fetch historical OHLCV data using yfinance.

    Args:
        script_name: NSE stock symbol (e.g., "RELIANCE")
        period: Data period (default "1mo" for 1 month)

    Returns:
        DataFrame with Date index and OHLCV columns
    """
    try:
        ticker = yf.Ticker(f"{script_name}.NS")
        df = ticker.history(period=period)

        if df.empty:
            logging.warning(f"No data returned for {script_name}")
            return pd.DataFrame()

        # Ensure column names match expected format
        df.index = df.index.strftime('%Y-%m-%d')
        return df

    except Exception as e:
        log_error_with_context(
            error=e,
            script_name=script_name,
            operation="fetch_historical_data",
            period=period
        )
        return pd.DataFrame()
