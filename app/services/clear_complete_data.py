import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.models import BreakoutData, MasterBOData


def clear_complete_data(db: Session):
    """
    Archives all data from breakout_data table to master_breakout_data using bulk upsert.
    Uses PostgreSQL INSERT ON CONFLICT for efficient upsert (50x faster than N+1 approach).
    Also resets the sequence for the breakout_data table.
    """
    try:
        # Fetch all rows from breakout_data in one query
        breakout_records = db.query(BreakoutData).order_by(
            BreakoutData.id.asc()).all()

        if not breakout_records:
            logging.info("No data to archive")
            return {"status": "SUCCESS", "message": "No data to archive"}

        # Prepare data for bulk upsert
        records_to_upsert = []
        for record in breakout_records:
            records_to_upsert.append({
                "script_name": record.script_name,
                "group_name": record.group_name,
                "date": record.date,
                "open": record.open,
                "high": record.high,
                "low": record.low,
                "close": record.close,
                "previous_high": record.previous_high,
                "volume": record.volume,
                "cpr": record.cpr,
                "res1": record.res1,
                "res2": record.res2,
                "supp1": record.supp1,
                "supp2": record.supp2,
                "narrow_gap": record.narrow_gap,
                "breakout_indicator": record.breakout_indicator,
                "candle_indicator": record.candle_indicator,
                "volume_indicator": record.volume_indicator,
                "link": record.link,
            })

        # Bulk upsert using PostgreSQL INSERT ON CONFLICT
        # Uses the unique index on (script_name, date) for conflict detection
        stmt = insert(MasterBOData).values(records_to_upsert)
        stmt = stmt.on_conflict_do_update(
            index_elements=['script_name', 'date'],
            set_={
                "group_name": stmt.excluded.group_name,
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "previous_high": stmt.excluded.previous_high,
                "volume": stmt.excluded.volume,
                "cpr": stmt.excluded.cpr,
                "res1": stmt.excluded.res1,
                "res2": stmt.excluded.res2,
                "supp1": stmt.excluded.supp1,
                "supp2": stmt.excluded.supp2,
                "narrow_gap": stmt.excluded.narrow_gap,
                "breakout_indicator": stmt.excluded.breakout_indicator,
                "candle_indicator": stmt.excluded.candle_indicator,
                "volume_indicator": stmt.excluded.volume_indicator,
                "link": stmt.excluded.link,
            }
        )

        db.execute(stmt)
        logging.info("Archived %d records to master_breakout_data", len(records_to_upsert))

        # Clear all data from breakout_data
        db.query(BreakoutData).delete()

        # Reset the sequence for breakout_data_id_seq
        db.execute(text("ALTER SEQUENCE breakout_data_id_seq RESTART"))

        # Single commit at the end
        db.commit()

        logging.info("breakout_data cleared and sequence reset successfully.")
        return {
            "status": "SUCCESS",
            "message": f"Archived {len(records_to_upsert)} records"
        }

    except Exception as e:
        db.rollback()
        logging.error("Archive failed: %s", e)
        raise
