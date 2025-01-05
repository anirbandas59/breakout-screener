import logging
from sqlalchemy.orm import Session

from app.models.breakout_data import BreakoutData


def get_breakout_data(db: Session, page: int, limit: int):
    try:
        logging.info("Fetching BO Data from database.")
        result = db.query(BreakoutData).order_by(
            BreakoutData.id.asc())

        total = result.count()

        logging.info(
            "Fetched %d records from database successfully.", total)

        data = result.offset((page - 1) * limit).limit(limit).all()

        return {
            "total": total,
            "data": data
        }
    except Exception as e:
        logging.error("Error fetching BO Data from database: %s", str(e))
        return {"error": str(e)}
