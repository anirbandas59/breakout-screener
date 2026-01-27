"""add_unique_constraint_master_table

Revision ID: 133307eeaf5e
Revises: 1c63ead2aca0
Create Date: 2026-01-27 06:18:51.954811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '133307eeaf5e'
down_revision: Union[str, None] = '1c63ead2aca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add unique constraint to master_breakout_data for bulk upsert operations.
    This constraint ensures (script_name, date) combinations are unique,
    which is required for PostgreSQL INSERT...ON CONFLICT DO UPDATE.
    """
    # Add unique constraint for ON CONFLICT clause
    # This ensures script_name + date combination is unique
    op.create_unique_constraint(
        'uq_master_script_date',
        'master_breakout_data',
        ['script_name', 'date']
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_constraint('uq_master_script_date', 'master_breakout_data', type_='unique')
