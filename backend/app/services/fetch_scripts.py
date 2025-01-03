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
    # Get NSE URL from environment variables
    logging.basicConfig(level=logging.INFO)
    nse_urls = settings.nse_urls
    # nse_url = os.getenv(settings.nse_url)
    # print(NSE_URL)
    # driver.get(NSE_URL)

    driver = get_chrome_driver()

    try:
        for url in nse_urls:
            logging.info("Fetching data from URL: %s", url)
            driver.get(url)

            # Wait for page to load
            driver.implicitly_wait(10)

            try:  # Locate the data
                table = driver.find_element(By.ID, "equityStockTable")
                table_header = driver.find_element(
                    By.ID, "equityStockTablecol0")
                for _ in range(3):
                    table_header.click()
                    time.sleep(3)
                    # driver.implicitly_wait(5)

                rows = table.find_elements(By.TAG_NAME, "tr")

                data = []
                # index = 5

                if len(rows) > 10:
                    # cells = rows[1].find_elements(By.TAG_NAME, "td")
                    group_name = rows[1].find_elements(
                        By.TAG_NAME, "td")[0].text.strip()

                    for index in range(5, (len(rows) // 4) + 4):
                        cells = rows[5 + (index - 5) *
                                     4].find_elements(By.TAG_NAME, "td")
                        # driver.implicitly_wait(3)
                        if len(cells) > 10:
                            script_name = cells[0].text.strip()
                            data.append({
                                "group_name": group_name,
                                "script_name": script_name
                            })
                            # print(script_name)

                # print(data)
                logging.info(
                    "Data captured from %s: [Count: %d] => %s", url, len(data), data[:10])

                # Save the data into the database
                for item in data:
                    chart_link = f"https://gocharting.com/terminal?ticker=NSE:{
                        item['script_name']}&layout=1"
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
                        db_record.link = chart_link

                db.commit()

            except Exception as e:
                logging.error("Error fetching data from %s: %s", url, e)
                # print("------------------------------------------------------>")
                # print(f"Error fetching script symbols: {e}")

    finally:
        driver.quit()


def fetch_script_historical_data(script_name: str):

    logging.basicConfig(level=logging.INFO)

    yfin_hist_url = settings.yfin_hist_url.replace("SCRIPT", script_name)
    print("Fetching data from %s", yfin_hist_url)

    driver = get_chrome_driver()
    driver.implicitly_wait(10)

    try:
        driver.get(yfin_hist_url)
        table = driver.find_element(By.TAG_NAME, "table")

        # Extract table headers
        table_head = table.find_element(By.TAG_NAME, "thead")
        headers = [th.text.strip()
                   for th in table_head.find_elements(By.TAG_NAME, "th")]
        # print(headers)

        # Extract table rows
        table_body = table.find_element(By.TAG_NAME, "tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")

        # Parse table data
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == len(headers):  # Ensure the row has all columns
                row_data = [cell.text.strip() for cell in cells]
                data.append(row_data)

        # Create a DataFrame
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

        return df
    finally:
        driver.quit()
