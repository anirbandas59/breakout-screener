import logging
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.breakout_data import BreakoutData


def clear_chart_data(db: Session, date: str) -> None:
    """
    Clear specific columns for a given date - Open, High, Low, Close, Volume, Prev High, CPR, RES-1, RES-2, SUPP-1, SUPP-2, NARROW_GAP.

    Args:
        db (Session): SQLAlchemy database session
        date(str): Date for which data should be cleared
    """
    # Check if the record exists
    record_count = (
        db.query(BreakoutData)
        .filter(BreakoutData.date == date)
        .count()
    )

    if record_count == 0:
        logging.info("%d records found for date %s. Skipping ...",
                     record_count, date)
        return False

    logging.info("%d records found for date %s", record_count, date)

    db.execute(
        update(BreakoutData).where(BreakoutData.date == date).values(
            open=None, high=None, low=None, close=None, previous_high=None, volume=None,
            cpr=None, res1=None, res2=None, supp1=None, supp2=None,
            candle_indicator="", volume_indicator="", narrow_gap="", breakout_indicator=""
        )
    )

    db.commit()
    logging.info("%d records cleared", record_count)

    return True
