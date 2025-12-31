"""
Diagnostic script to understand NSE table structure.
This script will load the NSE page and analyze the table structure in detail.
"""
import time
import logging
from selenium.webdriver.common.by import By
from app.utils.selenium_driver import get_chrome_driver

logging.basicConfig(level=logging.INFO)


def diagnose_nse_table(url: str = "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050"):
    """
    Diagnose the NSE table structure to understand how stocks are organized.

    Args:
        url: NSE URL to analyze
    """
    driver = get_chrome_driver()

    try:
        logging.info(f"Loading URL: {url}")
        driver.get(url)

        # Wait longer for initial page load
        time.sleep(5)
        logging.info("Initial page load complete, waiting for table...")

        # Find the table
        table = driver.find_element(By.ID, "equityStockTable")
        logging.info("Table element found!")

        # Wait for table to populate - check row count every second
        logging.info("Waiting for table to populate...")
        for attempt in range(15):  # Wait up to 15 seconds
            rows = table.find_elements(By.TAG_NAME, "tr")
            logging.info(f"Attempt {attempt + 1}: {len(rows)} rows found")

            if len(rows) > 10:  # Assuming we need more than 10 rows
                break

            time.sleep(1)

        # Re-fetch rows after waiting
        rows = table.find_elements(By.TAG_NAME, "tr")
        logging.info(f"Total rows in table after waiting: {len(rows)}")

        # Analyze each row in detail
        logging.info("\n" + "="*80)
        logging.info("DETAILED ROW ANALYSIS")
        logging.info("="*80)

        stock_count = 0

        for i, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, "td")
            th_cells = row.find_elements(By.TAG_NAME, "th")

            cell_count = len(cells)
            th_count = len(th_cells)

            # Get text from first few cells
            first_cell_text = ""
            if cells:
                first_cell_text = cells[0].text.strip()
            elif th_cells:
                first_cell_text = th_cells[0].text.strip()

            # Log row details
            row_info = f"Row {i:3d}: "

            if th_count > 0:
                row_info += f"HEADER ({th_count} th) - {first_cell_text[:50]}"
            elif cell_count > 0:
                row_info += f"DATA ({cell_count:2d} td) - '{first_cell_text[:50]}'"

                # Check if this looks like a stock row
                if cell_count >= 10 and first_cell_text and len(first_cell_text) > 0:
                    # Could be a stock symbol
                    if first_cell_text.isupper() or first_cell_text[0].isupper():
                        stock_count += 1
                        row_info += f" *** STOCK #{stock_count} ***"
            else:
                row_info += "EMPTY"

            logging.info(row_info)

            # For the first 10 rows, show all cell contents
            if i < 10:
                if cells:
                    for j, cell in enumerate(cells[:5]):  # Show first 5 cells
                        logging.info(f"    Cell {j}: '{cell.text.strip()[:40]}'")

        logging.info("\n" + "="*80)
        logging.info(f"SUMMARY: Found {stock_count} potential stock rows")
        logging.info("="*80)

        # Try to find pagination controls
        logging.info("\nLooking for pagination controls...")
        try:
            pagination_select = driver.find_element(By.CSS_SELECTOR, "select[name='equityStockTable_length']")
            logging.info("Found pagination select!")

            from selenium.webdriver.support.ui import Select
            select = Select(pagination_select)
            options = [opt.text for opt in select.options]
            current_option = select.first_selected_option.text

            logging.info(f"Pagination options: {options}")
            logging.info(f"Current selection: {current_option}")
        except Exception as e:
            logging.info(f"No pagination select found: {e}")

        # Try to find "Show entries" text
        try:
            show_text = driver.find_element(By.CSS_SELECTOR, ".dataTables_length")
            logging.info(f"Show entries text: {show_text.text}")
        except Exception as e:
            logging.info(f"No show entries text found: {e}")

        # Look for table info (showing X to Y of Z entries)
        try:
            info_text = driver.find_element(By.CSS_SELECTOR, ".dataTables_info")
            logging.info(f"Table info: {info_text.text}")
        except Exception as e:
            logging.info(f"No table info found: {e}")

        # Save screenshot for manual inspection
        screenshot_path = "/tmp/nse_table_screenshot.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"\nScreenshot saved to: {screenshot_path}")

    finally:
        driver.quit()
        logging.info("\nDiagnostic complete!")


if __name__ == "__main__":
    diagnose_nse_table()
