"""Add link column to breakout_data

Revision ID: 4f1ba500363f
Revises: 
Create Date: 2025-01-02 22:20:56.740673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f1ba500363f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('ix_breakout_data_date', table_name='breakout_data')
    # op.drop_index('ix_breakout_data_group_name', table_name='breakout_data')
    # op.drop_index('ix_breakout_data_id', table_name='breakout_data')
    # op.drop_index('ix_breakout_data_script_name', table_name='breakout_data')
    # op.drop_table('breakout_data')
    op.add_column('breakout_data', sa.Column(
        'link', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('breakout_data',
    # sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    # sa.Column('script_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    # sa.Column('group_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    # sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
    # sa.PrimaryKeyConstraint('id', name='breakout_data_pkey')
    # )
    # op.create_index('ix_breakout_data_script_name', 'breakout_data', ['script_name'], unique=False)
    # op.create_index('ix_breakout_data_id', 'breakout_data', ['id'], unique=False)
    # op.create_index('ix_breakout_data_group_name', 'breakout_data', ['group_name'], unique=False)
    # op.create_index('ix_breakout_data_date', 'breakout_data', ['date'], unique=False)
    op.drop_column('breakout_data', 'link')
    # ### end Alembic commands ###
