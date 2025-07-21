"""Initial V2 models migration

Revision ID: 001
Revises: 
Create Date: 2025-01-20 12:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE breakoutstatus AS ENUM ('NO_BREAKOUT', 'UPSIDE_BREAKOUT', 'DOWNSIDE_BREAKOUT', 'BOTH_BREAKOUT')")
    op.execute("CREATE TYPE pivottype AS ENUM ('BULLISH', 'BEARISH', 'NEUTRAL')")
    op.execute("CREATE TYPE analysisstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')")
    op.execute("CREATE TYPE performancemetrictype AS ENUM ('ACCURACY', 'PRECISION', 'RECALL', 'F1_SCORE', 'RETURN_RATE', 'SHARPE_RATIO', 'MAX_DRAWDOWN', 'WIN_RATE', 'PROFIT_FACTOR', 'CUSTOM')")

    # Create stocks table
    op.create_table('stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('market_cap', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('listing_date', sa.Date(), nullable=True),
        sa.Column('stock_group', sa.String(10), nullable=True),
        sa.Column('face_value', postgresql.NUMERIC(10, 2), nullable=True),
        sa.Column('isin', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol'),
        sa.UniqueConstraint('isin')
    )
    op.create_index('ix_stocks_symbol', 'stocks', ['symbol'])
    op.create_index('ix_stocks_is_active', 'stocks', ['is_active'])
    op.create_index('ix_stocks_market_cap', 'stocks', ['market_cap'])

    # Create breakout_data table
    op.create_table('breakout_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('open_price', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('high_price', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('low_price', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('close_price', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('tc', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('bc', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('pivot', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('r1', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('r2', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('r3', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('s1', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('s2', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('s3', postgresql.NUMERIC(15, 4), nullable=True),
        sa.Column('breakout_status', sa.Enum('NO_BREAKOUT', 'UPSIDE_BREAKOUT', 'DOWNSIDE_BREAKOUT', 'BOTH_BREAKOUT', name='breakoutstatus'), nullable=False),
        sa.Column('pivot_type', sa.Enum('BULLISH', 'BEARISH', 'NEUTRAL', name='pivottype'), nullable=False),
        sa.Column('is_analyzed', sa.Boolean(), nullable=False, default=False),
        sa.Column('analysis_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', name='analysisstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id', 'trade_date', name='uq_breakout_data_stock_date')
    )
    op.create_index('ix_breakout_data_trade_date', 'breakout_data', ['trade_date'])
    op.create_index('ix_breakout_data_breakout_status', 'breakout_data', ['breakout_status'])
    op.create_index('ix_breakout_data_is_analyzed', 'breakout_data', ['is_analyzed'])

    # Create master_breakout_data table
    op.create_table('master_breakout_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('breakout_data_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('data_source', sa.String(50), nullable=False, default='NSE'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['breakout_data_id'], ['breakout_data.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id', 'snapshot_date', name='uq_master_breakout_data_stock_snapshot')
    )
    op.create_index('ix_master_breakout_data_snapshot_date', 'master_breakout_data', ['snapshot_date'])
    op.create_index('ix_master_breakout_data_is_active', 'master_breakout_data', ['is_active'])

    # Create analysis_sessions table
    op.create_table('analysis_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_name', sa.String(100), nullable=False),
        sa.Column('analysis_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', name='analysisstatus'), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_name')
    )
    op.create_index('ix_analysis_sessions_analysis_date', 'analysis_sessions', ['analysis_date'])
    op.create_index('ix_analysis_sessions_status', 'analysis_sessions', ['status'])

    # Create performance_metrics table
    op.create_table('performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_type', sa.Enum('ACCURACY', 'PRECISION', 'RECALL', 'F1_SCORE', 'RETURN_RATE', 'SHARPE_RATIO', 'MAX_DRAWDOWN', 'WIN_RATE', 'PROFIT_FACTOR', 'CUSTOM', name='performancemetrictype'), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', postgresql.NUMERIC(15, 4), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['analysis_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id', 'metric_type', 'metric_date', name='uq_performance_metrics_session_type_date')
    )
    op.create_index('ix_performance_metrics_metric_date', 'performance_metrics', ['metric_date'])
    op.create_index('ix_performance_metrics_metric_type', 'performance_metrics', ['metric_type'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('performance_metrics')
    op.drop_table('analysis_sessions')
    op.drop_table('master_breakout_data')
    op.drop_table('breakout_data')
    op.drop_table('stocks')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS performancemetrictype")
    op.execute("DROP TYPE IF EXISTS analysisstatus")
    op.execute("DROP TYPE IF EXISTS pivottype")
    op.execute("DROP TYPE IF EXISTS breakoutstatus")
