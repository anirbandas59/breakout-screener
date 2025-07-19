-- Breakout Screener V2 Database Schema
-- This script creates the improved V2 database schema with proper constraints,
-- foreign keys, audit fields, and indexing strategy.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create audit trigger function for tracking changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create enum types for better data integrity
CREATE TYPE breakout_indicator_enum AS ENUM (
    'BREAKOUT', 
    'POTENTIAL_BREAKOUT', 
    'NO_BREAKOUT'
);

CREATE TYPE candle_indicator_enum AS ENUM (
    'BULLISH', 
    'BEARISH', 
    'NEUTRAL', 
    'DOJI', 
    'HAMMER', 
    'SHOOTING_STAR'
);

CREATE TYPE volume_indicator_enum AS ENUM (
    'HIGH_VOLUME', 
    'NORMAL_VOLUME', 
    'LOW_VOLUME'
);

CREATE TYPE stock_group_enum AS ENUM (
    'NIFTY_50',
    'NIFTY_200', 
    'NIFTY_MIDCAP_150',
    'NIFTY_MIDSMALLCAP_400',
    'NIFTY_SMALLCAP_250'
);

-- Create stocks master table for normalized stock information
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    isin_code VARCHAR(12),
    stock_group stock_group_enum NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT true,
    listing_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_by VARCHAR(100) DEFAULT 'system'
);

-- Create improved breakout_data table with foreign key references
CREATE TABLE IF NOT EXISTS breakout_data_v2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    open_price DECIMAL(12,2) NOT NULL CHECK (open_price > 0),
    high_price DECIMAL(12,2) NOT NULL CHECK (high_price > 0),
    low_price DECIMAL(12,2) NOT NULL CHECK (low_price > 0),
    close_price DECIMAL(12,2) NOT NULL CHECK (close_price > 0),
    previous_high DECIMAL(12,2),
    volume BIGINT NOT NULL CHECK (volume >= 0),
    
    -- CPR (Central Pivot Range) calculations
    cpr DECIMAL(12,2),
    resistance_1 DECIMAL(12,2),
    resistance_2 DECIMAL(12,2),
    support_1 DECIMAL(12,2),
    support_2 DECIMAL(12,2),
    
    -- Indicators
    narrow_gap BOOLEAN DEFAULT false,
    breakout_indicator breakout_indicator_enum DEFAULT 'NO_BREAKOUT',
    candle_indicator candle_indicator_enum DEFAULT 'NEUTRAL',
    volume_indicator volume_indicator_enum DEFAULT 'NORMAL_VOLUME',
    
    -- Analysis metadata
    chart_link TEXT,
    analysis_notes TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_by VARCHAR(100) DEFAULT 'system',
    
    -- Constraints
    CONSTRAINT valid_ohlc CHECK (
        high_price >= open_price AND 
        high_price >= close_price AND 
        low_price <= open_price AND 
        low_price <= close_price
    ),
    CONSTRAINT unique_stock_date UNIQUE (stock_id, trade_date)
);

-- Create master breakout data table for historical snapshots
CREATE TABLE IF NOT EXISTS master_breakout_data_v2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    open_price DECIMAL(12,2) NOT NULL,
    high_price DECIMAL(12,2) NOT NULL,
    low_price DECIMAL(12,2) NOT NULL,
    close_price DECIMAL(12,2) NOT NULL,
    previous_high DECIMAL(12,2),
    volume BIGINT NOT NULL,
    
    -- CPR calculations
    cpr DECIMAL(12,2),
    resistance_1 DECIMAL(12,2),
    resistance_2 DECIMAL(12,2),
    support_1 DECIMAL(12,2),
    support_2 DECIMAL(12,2),
    
    -- Indicators
    narrow_gap BOOLEAN DEFAULT false,
    breakout_indicator breakout_indicator_enum DEFAULT 'NO_BREAKOUT',
    candle_indicator candle_indicator_enum DEFAULT 'NEUTRAL',
    volume_indicator volume_indicator_enum DEFAULT 'NORMAL_VOLUME',
    
    -- Analysis metadata
    chart_link TEXT,
    analysis_notes TEXT,
    confidence_score DECIMAL(3,2),
    
    -- Snapshot metadata
    snapshot_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_table VARCHAR(50) DEFAULT 'breakout_data_v2',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- Create analysis sessions table for tracking analysis runs
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    total_stocks_processed INTEGER DEFAULT 0,
    successful_analyses INTEGER DEFAULT 0,
    failed_analyses INTEGER DEFAULT 0,
    error_details JSONB,
    configuration JSONB,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- Create performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    measurement_date DATE NOT NULL,
    stock_id UUID REFERENCES stocks(id),
    session_id UUID REFERENCES analysis_sessions(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add triggers for updated_at columns
CREATE TRIGGER update_stocks_updated_at 
    BEFORE UPDATE ON stocks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_breakout_data_v2_updated_at 
    BEFORE UPDATE ON breakout_data_v2 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create comprehensive indexes for performance
-- Stocks table indexes
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_group ON stocks(stock_group);
CREATE INDEX IF NOT EXISTS idx_stocks_active ON stocks(is_active);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);

-- Breakout data indexes
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_stock_id ON breakout_data_v2(stock_id);
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_trade_date ON breakout_data_v2(trade_date);
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_stock_date ON breakout_data_v2(stock_id, trade_date);
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_breakout_indicator ON breakout_data_v2(breakout_indicator);
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_volume ON breakout_data_v2(volume);
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_created_at ON breakout_data_v2(created_at);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_breakout_data_v2_composite_analysis 
    ON breakout_data_v2(trade_date, breakout_indicator, volume_indicator);

-- Master breakout data indexes
CREATE INDEX IF NOT EXISTS idx_master_breakout_data_v2_stock_id ON master_breakout_data_v2(stock_id);
CREATE INDEX IF NOT EXISTS idx_master_breakout_data_v2_trade_date ON master_breakout_data_v2(trade_date);
CREATE INDEX IF NOT EXISTS idx_master_breakout_data_v2_snapshot_date ON master_breakout_data_v2(snapshot_date);

-- Analysis sessions indexes
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_start_time ON analysis_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_status ON analysis_sessions(status);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_date ON performance_metrics(metric_name, measurement_date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_stock_id ON performance_metrics(stock_id);

-- Text search indexes for flexible searching
CREATE INDEX IF NOT EXISTS idx_stocks_company_name_gin ON stocks USING gin(company_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_breakout_data_analysis_notes_gin ON breakout_data_v2 USING gin(analysis_notes gin_trgm_ops);

COMMENT ON TABLE stocks IS 'Master table containing stock information with proper normalization';
COMMENT ON TABLE breakout_data_v2 IS 'Main table for storing daily breakout analysis data with improved constraints';
COMMENT ON TABLE master_breakout_data_v2 IS 'Historical snapshots of breakout data for auditing and comparison';
COMMENT ON TABLE analysis_sessions IS 'Tracking table for analysis runs and batch processing';
COMMENT ON TABLE performance_metrics IS 'Table for storing various performance and analytical metrics';

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trading_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO trading_user;