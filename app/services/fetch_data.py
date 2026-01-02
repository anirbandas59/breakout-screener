import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.breakout_data import BreakoutData


def get_breakout_data(
    db: Session,
    page: int,
    limit: int,
    search: Optional[str] = None,
    breakout_filters: Optional[List[str]] = None
):
    try:
        logging.info("Fetching BO Data from database.")
        query = db.query(BreakoutData)

        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(BreakoutData.script_name.ilike(search_pattern))
            logging.info("Applied search filter: %s", search)

        # Apply breakout indicator filter if provided
        if breakout_filters and len(breakout_filters) > 0:
            query = query.filter(BreakoutData.breakout_indicator.in_(breakout_filters))
            logging.info("Applied breakout filters: %s", breakout_filters)

        # Order by id
        query = query.order_by(BreakoutData.id.asc())

        # Get total count after applying filters
        total: int = query.count()

        logging.info(
            "Fetched %d records from database successfully.", total)

        # Apply pagination
        data = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "total": total,
            "data": data
        }
    except Exception as e:
        logging.error("Error fetching BO Data from database: %s", str(e))
        return {"error": str(e)}
