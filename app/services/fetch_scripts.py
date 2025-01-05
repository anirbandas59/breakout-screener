import time
import os
import logging
import pandas as pd

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
                # Find the table
                table = driver.find_element(By.ID, "equityStockTable")
                # Find the table header
                table_header = driver.find_element(
                    By.ID, "equityStockTablecol0")

                # Click on the header 3 times to sort the data
                for _ in range(3):
                    table_header.click()
                    time.sleep(3)
                    # driver.implicitly_wait(5)

                # Get the rows
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Create a list of dictionaries
                data = []
                # index = 5

                # Loop through the rows
                if len(rows) > 10:
                    # Get the group name
                    # cells = rows[1].find_elements(By.TAG_NAME, "td")
                    group_name = rows[1].find_elements(
                        By.TAG_NAME, "td")[0].text.strip()

                    # Loop through the rows
                    for index in range(5, (len(rows) // 4) + 4):
                        # Get the cells
                        cells = rows[5 + (index - 5) *
                                     4].find_elements(By.TAG_NAME, "td")
                        # driver.implicitly_wait(3)
                        if len(cells) > 10:
                            # Get the script name
                            script_name = cells[0].text.strip()
                            # Add the data to the list
                            data.append({
                                "group_name": group_name,
                                "script_name": script_name
                            })
                            # print(script_name)

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


def fetch_script_historical_data(script_name: str) -> pd.DataFrame:
    """
    Fetches the historical data for a script from Yahoo Finance and returns it as a pandas DataFrame.

    Args:
        script_name (str): The script name to fetch data for.

    Returns:
        pd.DataFrame: A DataFrame containing the historical data for the script.
    """
    # logging.basicConfig(level=logging.INFO)

    # Replace the script name in the URL
    yfin_hist_url = settings.yfin_hist_url.replace("SCRIPT", script_name)
    logging.info("Fetching data from %s", yfin_hist_url)
    print("Fetching data from %s", yfin_hist_url)

    # Create a Chrome driver with an implicit wait of 10 seconds
    driver = get_chrome_driver()
    driver.implicitly_wait(10)

    try:
        # Navigate to the Yahoo Finance page
        driver.get(yfin_hist_url)
        # Find the table element
        table = driver.find_element(By.TAG_NAME, "table")

        # Extract the table headers
        table_head = table.find_element(By.TAG_NAME, "thead")
        headers = [th.text.strip()
                   for th in table_head.find_elements(By.TAG_NAME, "th")]
        # print(headers)

        # Extract the table rows
        table_body = table.find_element(By.TAG_NAME, "tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")

        # Parse the table data
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == len(headers):  # Ensure the row has all columns
                row_data = [cell.text.strip() for cell in cells]
                data.append(row_data)

        # Create a DataFrame from the parsed data
        df = pd.DataFrame(data, columns=headers)
        # print(df)

        # Parse and set the Date column as index
        df["Date"] = pd.to_datetime(
            df["Date"], errors="coerce")  # Handle invalid dates
        df = df.dropna(subset=["Date"]).set_index("Date")

        # Convert numeric columns
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            df[col] = pd.to_numeric(
                df[col].str.replace(",", ""), errors="coerce")

    finally:
        # Quit the driver
        driver.quit()

    return df
