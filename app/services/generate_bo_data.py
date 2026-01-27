import logging

from datetime import datetime
from sqlalchemy.orm import Session
from celery import current_task

from app.models.breakout_data import BreakoutData
from app.models.enums import BreakoutIndicator, CandleIndicator, VolumeIndicator
from app.services.cpr_calculator import calculate_cpr
from app.services.fetch_scripts import fetch_script_historical_data
from app.utils.suspension_flag import SUSPEND_ANALYSIS
from app.utils.error_handlers import log_error_with_context, DatabaseError, CPRCalculationError

# logging.basicConfig(level=logging.INFO)


def generate_BOData(db: Session, analysis_date: str, pivot_val: float, start_from: int = 1) -> dict:
    """
    Generate breakout data for all scripts in the breakout_data table.

    Args:
        db (Session): SQLAlchemy session.
        analysis_date (str): Date for which the analysis needs to run (format: YYYY-MM-DD).
        pivot_val (float): Percentage of the gap to be considered narrow.
        start_from (int): Index to start processing from (1-indexed). Default is 1.

    Returns:
        dict: Status of the analysis.
    """
    # Clear any previous suspension flag at the start of a new task
    SUSPEND_ANALYSIS.clear()
    logging.info("Suspension flag cleared at task start.")

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
            "status": "FAIL",
            "error": "No scripts available for analysis."
        }

    # Apply start_from index (convert from 1-indexed to 0-indexed)
    scripts_to_process = scripts[start_from - 1:]
    total_scripts = len(scripts_to_process)

    # PERFORMANCE FIX: Batch commits to reduce disk I/O
    # Commit every BATCH_SIZE records instead of after each record
    BATCH_SIZE = 50
    commit_counter = 0

    logging.info("Starting analysis from script %d (total: %d scripts)", start_from, total_scripts)
    for i, script in enumerate(scripts_to_process):
        # Update progress (show absolute position: start_from + current index)
        current_position = start_from + i
        if current_task:
            current_task.update_state(
                state='PROGRESS',
                meta={
                    'current': current_position,
                    'total': len(scripts),
                    'script': script.script_name
                }
            )
        # Check suspension
        if SUSPEND_ANALYSIS.is_set():
            # PERFORMANCE FIX: Commit pending changes before suspending
            if commit_counter > 0:
                db.commit()
                logging.info("Committed %d pending records before suspension", commit_counter)
            logging.warning(
                "Analysis suspended. Halting analysis at script: %s", script.script_name)
            return {
                "status": "SUSPENDED",
                "message": f"Suspended at script {current_position} of {len(scripts)}"
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

        if analysis_date not in df.index:
            logging.warning(
                "No data available for %s on %s. Skipping...", script_name, analysis_date)
            continue

        today_data = df.loc[analysis_date]
        today_open, today_high, today_low, today_close, today_volume = today_data[
            "Open"], today_data["High"], today_data["Low"], today_data["Close"], today_data["Volume"]
        logging.info("Open: %.2f", today_open)
        logging.info("High: %.2f", today_high)
        logging.info("Low: %.2f", today_low)
        logging.info("Close: %.2f", today_close)
        logging.info("Volume: %.2f", today_volume)

        # Calculate Previous Highs and Average Volume
        prev_highs = df[df.index < analysis_date]["High"].iloc[:10]
        prev_high = prev_highs.max() if not prev_highs.empty else 0
        avg_volume = df[df.index <
                        analysis_date]["Volume"].iloc[:10].mean()

        logging.info("Previous High: %.2f", prev_high)
        logging.info("Avg Volume: %d", avg_volume)

        # Calculate CPR levels using dedicated calculator
        try:
            pivot, res1, res2, sup1, sup2, gap = calculate_cpr(today_high, today_low, today_close)
        except Exception as e:
            log_error_with_context(
                error=e,
                script_name=script_name,
                date=analysis_date,
                operation="calculate_cpr",
                high=today_high,
                low=today_low,
                close=today_close
            )
            raise CPRCalculationError(f"CPR calculation failed for {script_name}: {e}") from e

        logging.info("Pivot: %.2f", pivot)
        logging.info("Resistance Level 1: %.2f", res1)
        logging.info("Support Level 1: %.2f", sup1)
        logging.info("Resistance Level 2: %.2f", res2)
        logging.info("Support Level 2: %.2f", sup2)
        logging.info("Band Gap: %.2f", gap)

        # Determine Candle Indicator
        if today_close < today_open:
            candle_indicator = CandleIndicator.RED_CANDLE
        elif today_close > today_open:
            candle_indicator = CandleIndicator.GREEN_CANDLE
        else:
            candle_indicator = CandleIndicator.DOJI

        logging.info("Candle Indicator: %s", candle_indicator.value)

        # Determine Breakout Indicator
        if today_close <= today_open:
            breakout_indicator = BreakoutIndicator.RED_CANDLE
        elif today_close <= prev_high:
            breakout_indicator = BreakoutIndicator.NO_BREAKOUT
        elif (today_high - today_open) >= (5 * (today_high - today_close)):
            breakout_indicator = BreakoutIndicator.BREAKOUT
        elif (today_high - today_open) < (5 * (today_high - today_close)):
            breakout_indicator = BreakoutIndicator.BIG_SELL_WICK
        else:
            breakout_indicator = BreakoutIndicator.NO_ENTRY

        logging.info("Breakout Indicator: %s", breakout_indicator.value)

        # Determine Volume Indicator
        if today_volume > (avg_volume * 2):
            volume_indicator = VolumeIndicator.GOOD
        elif today_volume > avg_volume:
            volume_indicator = VolumeIndicator.AVERAGE
        else:
            volume_indicator = VolumeIndicator.LOW

        logging.info("Volume Indicator: %s", volume_indicator.value)

        if gap <= (pivot_percentage * today_close):
            is_narrow_gap = "Yes"
        else:
            is_narrow_gap = "No"

        logging.info("Narrow Gap: %s", is_narrow_gap)

        # Check suspension before database updates
        if SUSPEND_ANALYSIS.is_set():
            logging.warning("Suspension detected before database update")
            return {
                "status": "FAIL",
                "error": "Analysis suspended by user."
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
                db_record.candle_indicator = candle_indicator.value
                db_record.breakout_indicator = breakout_indicator.value
                db_record.volume_indicator = volume_indicator.value
                db_record.date = analysis_date_val.date()

                # PERFORMANCE FIX: Batch commits every BATCH_SIZE records
                commit_counter += 1
                if commit_counter >= BATCH_SIZE:
                    db.commit()
                    logging.info("Batch committed %d records at position %d", commit_counter, current_position)
                    commit_counter = 0

                logging.info("Data updated for script %s", script_name)
            else:
                logging.info("Update skipped for script %s", script_name)
        except Exception as e:
            log_error_with_context(
                error=e,
                script_name=script_name,
                date=analysis_date,
                operation="database_update"
            )
            db.rollback()
            commit_counter = 0  # Reset counter after rollback
            # Continue processing other scripts instead of failing entirely

    # PERFORMANCE FIX: Final commit for remaining records
    if commit_counter > 0:
        db.commit()
        logging.info("Final batch committed %d records", commit_counter)

    logging.info("BO Analysis completed successfully")
    return {
        "status": "SUCCESS",
        "message": f"Completed {total_scripts} scripts"
    }
