"""
Repository for master_breakout_data table operations.

Isolates all SQLAlchemy queries for the MasterBOData model.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.master_data import MasterBOData
from app.repositories.query_helpers import query_table


class MasterRepository:
    """Encapsulates all database operations for the master_breakout_data table."""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Read operations
    # -------------------------

    def get_all_ordered(self) -> List[MasterBOData]:
        """Fetch all records ordered by id ascending."""
        return self.db.query(MasterBOData).order_by(MasterBOData.id.asc()).all()



    def query_with_filters(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        breakout_filters: Optional[List[str]] = None,
        date: Optional[str] = None,
    ) -> dict:
        """
        Query master_breakout_data with optional filters and pagination.

        Returns:
            dict with keys: total, data, data_date
        """
        return query_table(self.db, MasterBOData, page, limit, search, breakout_filters, date)

    # -------------------------
    # Write operations
    # -------------------------

    def bulk_upsert(self, records_data: List[dict]) -> None:
        """
        Bulk upsert records into master_breakout_data using PostgreSQL
        INSERT ... ON CONFLICT DO UPDATE.

        Falls back to a loop-based upsert for non-PostgreSQL dialects (e.g. SQLite in tests).
        """
        if not records_data:
            return

        dialect = self.db.bind.dialect.name if self.db.bind else "postgresql"

        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            stmt = pg_insert(MasterBOData).values(records_data)
            upsert_stmt = stmt.on_conflict_do_update(
                constraint='uq_master_script_date',
                set_={
                    'group_name': stmt.excluded.group_name,
                    'open': stmt.excluded.open,
                    'high': stmt.excluded.high,
                    'low': stmt.excluded.low,
                    'close': stmt.excluded.close,
                    'previous_high': stmt.excluded.previous_high,
                    'volume': stmt.excluded.volume,
                    'cpr': stmt.excluded.cpr,
                    'res1': stmt.excluded.res1,
                    'res2': stmt.excluded.res2,
                    'supp1': stmt.excluded.supp1,
                    'supp2': stmt.excluded.supp2,
                    'narrow_gap': stmt.excluded.narrow_gap,
                    'breakout_indicator': stmt.excluded.breakout_indicator,
                    'candle_indicator': stmt.excluded.candle_indicator,
                    'volume_indicator': stmt.excluded.volume_indicator,
                    'link': stmt.excluded.link,
                }
            )
            self.db.execute(upsert_stmt)
        else:
            # Fallback for SQLite (test environment)
            for row in records_data:
                existing = (
                    self.db.query(MasterBOData)
                    .filter_by(script_name=row['script_name'], date=row['date'])
                    .first()
                )
                if existing:
                    for key, value in row.items():
                        if key not in ('script_name', 'date'):
                            setattr(existing, key, value)
                else:
                    self.db.add(MasterBOData(**row))

    # -------------------------
    # Transaction helpers
    # -------------------------

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
