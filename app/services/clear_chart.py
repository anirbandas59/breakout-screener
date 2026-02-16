import logging
from sqlalchemy.orm import Session

from app.repositories import BreakoutRepository
from app.utils.error_handlers import DatabaseError


def clear_chart_data(db: Session, date: str) -> bool:
    """
    Clear specific columns for a given date - Open, High, Low, Close, Volume, Prev High, CPR, RES-1, RES-2, SUPP-1, SUPP-2, NARROW_GAP.

    Args:
        db (Session): SQLAlchemy database session
        date(str): Date for which data should be cleared
    """
    repo = BreakoutRepository(db)
    try:
        count = repo.clear_chart_data_fields(date)

        if count == 0:
            return False

        repo.commit()
        logging.info("%d records cleared", count)
        return True

    except Exception as e:
        repo.rollback()
        raise DatabaseError(str(e), operation="clear_chart_data", table="breakout_data") from e
