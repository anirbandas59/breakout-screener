from typing import Optional, List
import logging
from sqlalchemy.orm import Session

def query_table(
    db: Session,
    model,
    page: int,
    limit: int,
    search: Optional[str] = None,
    breakout_filters: Optional[List[str]] = None,
    date: Optional[str] = None,
) -> dict:
    """
    Shared query logic for both BreakoutData and MasterBOData tables.

    Returns:
        dict with keys: total, data, data_date
    """
    query = db.query(model)

    if date:
        query = query.filter(model.date == date)
        logging.info("Applied date filter: %s", date)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(model.script_name.ilike(search_pattern))
        logging.info("Applied search filter: %s", search)

    if breakout_filters and len(breakout_filters) > 0:
        query = query.filter(model.breakout_indicator.in_(breakout_filters))
        logging.info("Applied breakout filters: %s", breakout_filters)

    query = query.order_by(model.id.asc())
    total: int = query.count()

    logging.info("Found %d records in %s", total, model.__tablename__)

    if total == 0:
        return {"total": 0, "data": [], "data_date": None}

    if date:
        data_date = date
    else:
        first_record = query.filter(model.date.isnot(None)).first()
        data_date = str(first_record.date) if first_record and first_record.date else None

    data = query.offset((page - 1) * limit).limit(limit).all()

    return {"total": total, "data": data, "data_date": data_date}
