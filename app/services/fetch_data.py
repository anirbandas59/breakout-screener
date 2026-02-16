import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories import BreakoutRepository, MasterRepository
from app.utils.error_handlers import DatabaseError


def get_breakout_data(
    db: Session,
    page: int,
    limit: int,
    search: Optional[str] = None,
    breakout_filters: Optional[List[str]] = None,
    date: Optional[str] = None
):
    """
    Fetch breakout data with optional search, filters, and date.

    Data fetching priority:
    1. If date specified: Try breakout_data for that date, fallback to master_breakout_data
    2. If no date: Fetch from breakout_data, get the latest date from data

    Args:
        db: Database session
        page: Page number for pagination
        limit: Records per page
        search: Search term for script name
        breakout_filters: List of breakout indicator values to filter
        date: Optional date filter in YYYY-MM-DD format

    Returns:
        dict with total, data, data_date, and data_source
    """
    try:
        logging.info("Fetching BO Data from database.")
        breakout_repo = BreakoutRepository(db)
        master_repo = MasterRepository(db)

        # First, try to get data from breakout_data table
        result = breakout_repo.query_with_filters(page, limit, search, breakout_filters, date)

        if result["total"] > 0:
            return {**result, "data_source": "breakout_data"}

        # If no data found and date is specified, try master_breakout_data
        if date:
            logging.info("No data in breakout_data for date %s, checking master_breakout_data", date)
            result = master_repo.query_with_filters(page, limit, search, breakout_filters, date)

            if result["total"] > 0:
                return {**result, "data_source": "master_breakout_data"}

        # No data found anywhere
        logging.info("No data found for the specified criteria")
        return {"total": 0, "data": [], "data_date": None, "data_source": None}

    except Exception as e:
        raise DatabaseError(str(e), operation="fetch_breakout_data") from e
