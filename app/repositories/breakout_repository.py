"""
Repository for breakout_data table operations.

Isolates all SQLAlchemy queries for the BreakoutData model,
keeping service layer free of direct database concerns.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import update, text

from app.models.breakout_data import BreakoutData
from app.repositories.query_helpers import query_table


class BreakoutRepository:
    """Encapsulates all database operations for the breakout_data table."""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Read operations
    # -------------------------

    def get_all(self) -> List[BreakoutData]:
        """Fetch all records ordered by id."""
        return self.db.query(BreakoutData).all()

    def get_all_ordered(self) -> List[BreakoutData]:
        """Fetch all records ordered by id ascending."""
        return self.db.query(BreakoutData).order_by(BreakoutData.id.asc()).all()

    def get_by_script_name(self, script_name: str) -> Optional[BreakoutData]:
        """Fetch a single record by script_name."""
        return self.db.query(BreakoutData).filter_by(script_name=script_name).first()

    def get_by_date(self, date: str) -> List[BreakoutData]:
        """Fetch all records for a given date."""
        return self.db.query(BreakoutData).filter(BreakoutData.date == date).all()

    def count_by_date(self, date: str) -> int:
        """Count records for a given date."""
        return self.db.query(BreakoutData).filter(BreakoutData.date == date).count()



    def query_with_filters(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        breakout_filters: Optional[List[str]] = None,
        date: Optional[str] = None,
    ) -> dict:
        """
        Query breakout_data with optional filters and pagination.

        Returns:
            dict with keys: total, data, data_date
        """
        return query_table(self.db, BreakoutData, page, limit, search, breakout_filters, date)

    # -------------------------
    # Write operations
    # -------------------------

    def add(self, record: BreakoutData) -> None:
        """Add a new record to the session (does not commit)."""
        self.db.add(record)

    def clear_chart_data_fields(self, date: str) -> int:
        """
        Null out all analysis fields for records on the given date.

        Returns:
            Number of records affected (0 if none found).
        """
        count = self.count_by_date(date)
        if count == 0:
            logging.info("0 records found for date %s. Skipping ...", date)
            return 0

        logging.info("%d records found for date %s", count, date)
        self.db.execute(
            update(BreakoutData).where(BreakoutData.date == date).values(
                open=None, high=None, low=None, close=None,
                previous_high=None, volume=None,
                cpr=None, res1=None, res2=None, supp1=None, supp2=None,
                candle_indicator="", volume_indicator="",
                narrow_gap="", breakout_indicator=""
            )
        )
        return count

    def bulk_delete(self) -> None:
        """Delete all records from breakout_data."""
        self.db.query(BreakoutData).delete()

    def reset_sequence(self) -> None:
        """Reset the auto-increment sequence for breakout_data."""
        self.db.execute(text("ALTER SEQUENCE breakout_data_id_seq RESTART"))
        self.db.execute(text("UPDATE breakout_data SET id=DEFAULT"))

    # -------------------------
    # Transaction helpers
    # -------------------------

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
