import logging

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.breakout_data import BreakoutData
from app.services.fetch_scripts import fetch_script_historical_data
from app.utils.suspension_flag import SUSPEND_ANALYSIS

# logging.basicConfig(level=logging.INFO)


def generate_BOData(db: Session, analysis_date: str, pivot_val: float) -> dict:
    """
    Generate breakout data for all scripts in the breakout_data table.

    Args:
        db (Session): SQLAlchemy session.
        analysis_date (str): Date for which the analysis needs to run (format: YYYY-MM-DD).
        pivot_val (float): Percentage of the gap to be considered narrow.

    Returns:
        dict: Status of the analysis.
    """
    # global SUSPEND_ANALYSIS

    # SUSPEND_ANALYSIS = False

    # pivot_val = 0.5
    pivot_percentage = pivot_val / 100

    # Validate the date format
    try:
        analysis_date_val = datetime.strptime(analysis_date, "%Y-%m-%d")
    except ValueError:
        return {
            "error": "Invalid date format. Use YYYY-MM-DD"
        }

    # Fetch all scripts
    scripts = db.query(BreakoutData).all()

    if not scripts:
        logging.warning("No scripts available for analysis")
        return {
            "error": "No scripts available for analysis."
        }

    logging.info("Starting analysis in generate_BOData")
    for script in scripts[:5]:
        if SUSPEND_ANALYSIS.is_set():
            logging.warning(
                "Analysis suspended. Halting analysis at script: %s", script.script_name)
            return {
                "status": "Analysis suspended by user."
            }

        script_name: str = script.script_name
        logging.info("Processing stock: %s", script_name)

        # Replace special characters
        script_name.replace("&", '%26')
        df = fetch_script_historical_data(script_name)

        if df.empty:
            logging.warning("No data found for %s. Skipping ...", script_name)
            continue

        logging.info("Data fetched for script %s ==> %d rows",
                     script_name, df.size)

        if str(analysis_date_val) not in df.index:
            logging.warning(
                "No data available for %s on %s. Skipping...", script_name, analysis_date_val)
            continue

        today_data = df.loc[str(analysis_date_val)]
        today_open, today_high, today_low, today_close, today_volume = today_data[
            "Open"], today_data["High"], today_data["Low"], today_data["Close"], today_data["Volume"]
        logging.info("Open: %.2f", today_open)
        logging.info("High: %.2f", today_high)
        logging.info("Low: %.2f", today_low)
        logging.info("Close: %.2f", today_close)
        logging.info("Volume: %.2f", today_volume)

        # Calculate Previous Highs and Average Volume
        prev_highs = df[df.index < analysis_date_val]["High"].iloc[:10]
        prev_high = prev_highs.max() if not prev_highs.empty else 0
        avg_volume = df[df.index <
                        analysis_date_val]["Volume"].iloc[:10].mean()

        logging.info("Previous High: %.2f", prev_high)
        logging.info("Avg Volume: %d", avg_volume)

        # Calculate Pivot Points
        pivot = (today_high + today_low + today_close) / 3
        bcp = (today_high + today_low) / 2
        tcp = (pivot - bcp) + pivot
        res1 = (2 * pivot) - today_low
        sup1 = (2 * pivot) - today_high
        res2 = pivot + (res1 - sup1)
        sup2 = pivot - (res1 - sup1)
        gap = abs(tcp - bcp)

        logging.info("Pivot: %.2f", pivot)
        logging.info("Resistance Level 1: %.2f", res1)
        logging.info("Support Level 1: %.2f", sup1)
        logging.info("Resistance Level 2: %.2f", res2)
        logging.info("Support Level 2: %.2f", sup2)
        logging.info("Band Gap: %.2f", gap)

        # Determine Candle Indicator
        if today_close < today_open:
            candle_indicator = "Red candle"
        elif today_close > today_open:
            candle_indicator = "Green candle"
        else:
            candle_indicator = "Doji"

        logging.info("Candle Indicator: %s", candle_indicator)

        # Determine Breakout Indicator
        if today_close <= today_open:
            breakout_indicator = "Red candle"
        elif today_close <= prev_high:
            breakout_indicator = "no breakout"
        elif (today_high - today_open) >= (5 * (today_high - today_close)):
            breakout_indicator = "Breakout"
        elif (today_high - today_open) < (5 * (today_high - today_close)):
            breakout_indicator = "Big Sell Wick"
        else:
            breakout_indicator = "No Entry"

        logging.info("Breakout Indicator: %s", breakout_indicator)

        # Determine Volume Indicator
        if today_volume > (avg_volume * 2):
            volume_indicator = "Good"
        elif today_volume > avg_volume:
            volume_indicator = "Average"
        else:
            volume_indicator = "Low"

        logging.info("Volume Indicator: %s", volume_indicator)

        if gap <= (pivot_percentage * today_close):
            is_narrow_gap = "Yes"
        else:
            is_narrow_gap = "No"

        logging.info("Narrow Gap: %s", is_narrow_gap)

        # Check suspension before database updates
        if SUSPEND_ANALYSIS.is_set():
            logging.warning("Suspension detected before database update")
            return {
                "status": "Analysis suspended by user."
            }

        # Update db record
        try:
            db_record = (
                db.query(BreakoutData).filter_by(
                    script_name=script_name).first()
            )

            logging.info("Record found: %s", script_name)

            if db_record:
                db_record.open = round(float(today_open), 2)
                db_record.high = round(float(today_high), 2)
                db_record.low = round(float(today_low), 2)
                db_record.close = round(float(today_close), 2)
                db_record.previous_high = round(float(prev_high), 2)
                db_record.volume = round(float(today_volume), 0)
                db_record.cpr = round(float(pivot), 2)
                db_record.res1 = round(float(res1), 2)
                db_record.res2 = round(float(res2), 2)
                db_record.supp1 = round(float(sup1), 2)
                db_record.supp2 = round(float(sup2), 2)
                db_record.narrow_gap = is_narrow_gap
                db_record.candle_indicator = candle_indicator
                db_record.breakout_indicator = breakout_indicator
                db_record.volume_indicator = volume_indicator
                db_record.date = analysis_date_val

                db.commit()
                logging.info("Data updated for script %s", script_name)
            else:
                logging.info("Update skipped for script %s", script_name)
        except Exception as e:
            logging.error("Error updating database for %s: %s",
                          script_name, e)

    logging.info("BO Analysis completed successfully")
    return {
        "status": "BO Analysis completed successfully"
    }
