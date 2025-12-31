# NSE Table Scraping Fix

## Problem
The `fetch_script_symbols` function was only capturing 12 stocks from NSE indices instead of the full count (e.g., 50 stocks for Nifty 50, 200 for Nifty 200).

## Root Cause Analysis

### Investigation Process
Created a diagnostic script ([diagnose_nse_table.py](../app/utils/diagnose_nse_table.py)) to analyze the NSE table structure in detail.

### Findings

1. **Dynamic Table Loading**
   - NSE website loads table content asynchronously via JavaScript
   - Initial page load shows only 2 rows (header + index name)
   - Full table populates after ~5 seconds
   - Old code didn't wait for table to fully load

2. **Incorrect Table Structure Assumption**
   ```python
   # OLD (WRONG): Assumed 4 rows per stock
   for index in range(5, (len(rows) // 4) + 4):
       cells = rows[5 + (index - 5) * 4].find_elements(By.TAG_NAME, "td")
   ```

   **Actual structure:**
   - Row 0: Header row (15 `<th>` elements with column names)
   - Row 1: Index name row (e.g., "NIFTY 50") - contains the index name, not a stock
   - Rows 2+: Stock data rows (each has 15 `<td>` elements)

   Total: 52 rows for Nifty 50 (1 header + 1 index + 50 stocks)

3. **Math Error**
   - With 52 total rows: `(52 // 4) + 4 = 13 + 4 = 17`
   - Loop: `range(5, 17)` = 12 iterations
   - Result: Only 12 stocks captured

## Solution

### Changes to `fetch_scripts.py`

**File:** `app/services/fetch_scripts.py`

#### 1. Added Wait Logic (lines 42-58)
```python
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
```

**Purpose:** Ensures all table rows are loaded before attempting to extract data.

#### 2. Fixed Extraction Logic (lines 67-93)
```python
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
```

**Key improvements:**
- Iterates through ALL rows (starting from row 2)
- No hardcoded "4 rows per stock" assumption
- Validates each row has 15 cells before extracting
- Skips row 1 (index name) for stock extraction
- Uses row 1 only for group_name

#### 3. Enhanced Logging
Added detailed logging to track:
- Wait attempts and row counts
- Group name identification
- Each stock added (debug level)

## Testing

### Diagnostic Script
Created `app/utils/diagnose_nse_table.py` to analyze table structure:
- Shows detailed row-by-row analysis
- Identifies stock rows vs header/index rows
- Saves screenshot for manual verification
- Reports total stocks found

### Database Verification
```bash
uv run python -c "
from app.db.session import SessionLocal
from app.models.breakout_data import BreakoutData

db = SessionLocal()
total = db.query(BreakoutData).count()
nifty50_count = db.query(BreakoutData).filter(
    BreakoutData.group_name == 'NIFTY 50'
).count()
print(f'Total: {total}, NIFTY 50: {nifty50_count}')
db.close()
"
```

**Results:**
- Total unique scripts: 499 ✓
- NIFTY 50: 50 scripts ✓
- No duplicate symbols ✓

### Expected Behavior
For Nifty 50 URL, logs should show:
```
INFO: Fetching data from URL: https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050
INFO: Table found
INFO: Waiting for table data to load...
INFO: Wait attempt 1: 52 rows
INFO: Total rows found: 52
INFO: Group name: NIFTY 50
INFO: Data captured from ...: [Count: 50] => [...]
```

## Files Modified

1. **`app/services/fetch_scripts.py`** - Main fix
   - Added wait logic for dynamic table loading
   - Fixed row iteration to start from row 2
   - Removed incorrect 4-row-per-stock assumption

2. **`app/utils/diagnose_nse_table.py`** - Diagnostic tool (NEW)
   - Analyzes NSE table structure
   - Helps debug scraping issues
   - Saves screenshots for manual verification

## Notes

- **Index Overlap:** Stocks can appear in multiple indices (e.g., NIFTY 50 stocks are also in NIFTY 200)
- **Database Design:** Each script is stored once with one group_name (first occurrence)
- **No Duplicates:** Database constraint prevents duplicate script_name entries
- **Total Scripts:** 499 unique scripts across all indices is expected due to overlap

## Future Improvements

1. Consider storing multiple group associations per script
2. Add retry logic for network failures
3. Implement incremental updates instead of full re-fetch
4. Add unit tests for table parsing logic
5. Consider switching from Selenium to API-based fetching if NSE provides one
