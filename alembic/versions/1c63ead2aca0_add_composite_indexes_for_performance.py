"""add_composite_indexes_for_performance

Revision ID: 1c63ead2aca0
Revises: b7c08e250c1a
Create Date: 2026-01-27 06:02:15.297230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c63ead2aca0'
down_revision: Union[str, None] = 'b7c08e250c1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add composite indexes for performance optimization.
    These indexes improve query performance for:
    - Archive operation lookups (script_name, date)
    - Filtered data fetching (date, breakout_indicator)
    """
    # Composite index for existence checks in archive operation
    # Used by app/services/clear_complete_data.py:20-23
    op.create_index(
        'idx_breakout_data_script_date',
        'breakout_data',
        ['script_name', 'date'],
        unique=False
    )

    op.create_index(
        'idx_master_breakout_script_date',
        'master_breakout_data',
        ['script_name', 'date'],
        unique=False
    )

    # Index for filtering by date + breakout_indicator
    # Used by app/services/fetch_data.py for filtered queries
    op.create_index(
        'idx_breakout_data_date_indicator',
        'breakout_data',
        ['date', 'breakout_indicator'],
        unique=False
    )

    op.create_index(
        'idx_master_date_indicator',
        'master_breakout_data',
        ['date', 'breakout_indicator'],
        unique=False
    )


def downgrade() -> None:
    """Remove composite indexes."""
    op.drop_index('idx_master_date_indicator', table_name='master_breakout_data')
    op.drop_index('idx_breakout_data_date_indicator', table_name='breakout_data')
    op.drop_index('idx_master_breakout_script_date', table_name='master_breakout_data')
    op.drop_index('idx_breakout_data_script_date', table_name='breakout_data')
