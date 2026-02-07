"""add_performance_indexes_and_unique_constraint

Revision ID: 119f2f91fea5
Revises: b7c08e250c1a
Create Date: 2026-02-07 10:18:22.229250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '119f2f91fea5'
down_revision: Union[str, None] = 'b7c08e250c1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for breakout_data lookups
    op.create_index(
        'ix_breakout_data_script_date',
        'breakout_data',
        ['script_name', 'date'],
        unique=False
    )

    # Index for breakout indicator filtering
    op.create_index(
        'ix_breakout_data_breakout_indicator',
        'breakout_data',
        ['breakout_indicator'],
        unique=False
    )

    # Unique composite index for master_breakout_data (required for upsert)
    op.create_index(
        'ix_master_breakout_data_script_date',
        'master_breakout_data',
        ['script_name', 'date'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_breakout_data_script_date', table_name='breakout_data')
    op.drop_index('ix_breakout_data_breakout_indicator', table_name='breakout_data')
    op.drop_index('ix_master_breakout_data_script_date', table_name='master_breakout_data')
