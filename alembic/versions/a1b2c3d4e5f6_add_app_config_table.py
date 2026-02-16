"""add app_config table

Revision ID: a1b2c3d4e5f6
Revises: 133307eeaf5e
Create Date: 2026-02-16 00:00:00.000000

"""
import os
from datetime import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '133307eeaf5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'app_config',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Seed initial NSE URL values from environment variables
    # Falls back to empty string if not set (admin can update via /api/config)
    nse_urls = [
        {
            'key': 'nse_url_nifty_50',
            'value': os.getenv('NSE_URL_NIFTY_50', ''),
            'description': 'NSE live equity market URL for Nifty 50 index',
        },
        {
            'key': 'nse_url_nifty_200',
            'value': os.getenv('NSE_URL_NIFTY_200', ''),
            'description': 'NSE live equity market URL for Nifty 200 index',
        },
        {
            'key': 'nse_url_nifty_midcap_150',
            'value': os.getenv('NSE_URL_NIFTY_MIDCAP_150', ''),
            'description': 'NSE live equity market URL for Nifty Midcap 150 index',
        },
        {
            'key': 'nse_url_nifty_midsmallcap_400',
            'value': os.getenv('NSE_URL_NIFTY_MIDSMALLCAP_400', ''),
            'description': 'NSE live equity market URL for Nifty MidSmallcap 400 index',
        },
        {
            'key': 'nse_url_nifty_smallcap_250',
            'value': os.getenv('NSE_URL_NIFTY_SMALLCAP_250', ''),
            'description': 'NSE live equity market URL for Nifty Smallcap 250 index',
        },
    ]

    # Only seed rows that have a non-empty value
    rows_to_insert = [row for row in nse_urls if row['value']]
    if rows_to_insert:
        op.bulk_insert(
            sa.table(
                'app_config',
                sa.column('key', sa.String),
                sa.column('value', sa.Text),
                sa.column('description', sa.String),
            ),
            rows_to_insert,
        )


def downgrade() -> None:
    op.drop_table('app_config')
