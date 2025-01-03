import logging
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData


def clear_complete_data(db: Session):
    """
    Clears out all data from breakout_data table
    """
    # Fetch all rows from breakout_data
    breakout_records = db.query(BreakoutData).all()

    for record in breakout_records:
        # Check if the record exists in master_table
        existing_record = db.query(MasterBOData).filter(
            MasterBOData.script_name == record.script_name,
            MasterBOData.date == record.date
        ).first()

        if not existing_record:
            master_record = MasterBOData(
                script_name=record.script_name,
                group_name=record.group_name,
                date=record.date,
                open=record.open,
                high=record.high,
                low=record.low,
                close=record.close,
                previous_high=record.previous_high,
                volume=record.volume,
                cpr=record.cpr,
                res1=record.res1,
                res2=record.res2,
                supp1=record.supp1,
                supp2=record.supp1,
                narrow_gap=record.narrow_gap,
                breakout_indicator=record.breakout_indicator,
                candle_indicator=record.candle_indicator,
                volume_indicator=record.volume_indicator,
                link=record.link,
            )

            db.add(master_record)

        else:
            existing_record.open = record.open
            existing_record.high = record.high
            existing_record.low = record.low
            existing_record.close = record.close
            existing_record.previous_high = record.previous_high
            existing_record.volume = record.volume
            existing_record.cpr = record.cpr
            existing_record.res1 = record.res1
            existing_record.res2 = record.res2
            existing_record.supp1 = record.supp1
            existing_record.supp2 = record.supp1
            existing_record.narrow_gap = record.narrow_gap
            existing_record.breakout_indicator = record.breakout_indicator
            existing_record.candle_indicator = record.candle_indicator
            existing_record.volume_indicator = record.volume_indicator

        db.commit()

    # Clear all data from breakout_data
    db.query(BreakoutData).delete()
    db.commit()
