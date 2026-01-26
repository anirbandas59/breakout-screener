import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData


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

        # First, try to get data from breakout_data table
        result = _query_table(
            db, BreakoutData, page, limit, search, breakout_filters, date
        )

        if result["total"] > 0:
            return {
                **result,
                "data_source": "breakout_data"
            }

        # If no data found and date is specified, try master_breakout_data
        if date:
            logging.info("No data in breakout_data for date %s, checking master_breakout_data", date)
            result = _query_table(
                db, MasterBOData, page, limit, search, breakout_filters, date
            )

            if result["total"] > 0:
                return {
                    **result,
                    "data_source": "master_breakout_data"
                }

        # No data found anywhere
        logging.info("No data found for the specified criteria")
        return {
            "total": 0,
            "data": [],
            "data_date": None,
            "data_source": None
        }

    except Exception as e:
        logging.error("Error fetching BO Data from database: %s", str(e))
        return {"error": str(e)}


def _query_table(
    db: Session,
    model,
    page: int,
    limit: int,
    search: Optional[str] = None,
    breakout_filters: Optional[List[str]] = None,
    date: Optional[str] = None
):
    """
    Query a specific table with filters.

    Args:
        db: Database session
        model: SQLAlchemy model (BreakoutData or MasterBOData)
        page: Page number
        limit: Records per page
        search: Search term
        breakout_filters: Breakout indicator filters
        date: Date filter

    Returns:
        dict with total, data, and data_date
    """
    query = db.query(model)

    # Apply date filter if provided
    if date:
        query = query.filter(model.date == date)
        logging.info("Applied date filter: %s", date)

    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(model.script_name.ilike(search_pattern))
        logging.info("Applied search filter: %s", search)

    # Apply breakout indicator filter if provided
    if breakout_filters and len(breakout_filters) > 0:
        query = query.filter(model.breakout_indicator.in_(breakout_filters))
        logging.info("Applied breakout filters: %s", breakout_filters)

    # Order by id
    query = query.order_by(model.id.asc())

    # Get total count after applying filters
    total: int = query.count()

    logging.info("Found %d records in %s", total, model.__tablename__)

    if total == 0:
        return {
            "total": 0,
            "data": [],
            "data_date": None
        }

    # Get the date from the data (use the first record's date or query distinct)
    # If no date filter was applied, get the most common date in the result set
    if date:
        data_date = date
    else:
        # Get the date from the first record that has a date
        first_record = query.filter(model.date.isnot(None)).first()
        data_date = str(first_record.date) if first_record and first_record.date else None

    # Apply pagination
    data = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "data": data,
        "data_date": data_date
    }
