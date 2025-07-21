# Breakout Screener API Analysis & Breakdown

## Application Overview

The Breakout Screener is a FastAPI-based web application designed to analyze stock market breakout patterns. It provides a comprehensive system for fetching stock data, analyzing breakout patterns, and managing processed data with asynchronous task processing using Celery.

## Core Architecture

### Main Application (`app/main.py`)
- **FastAPI Framework**: Modern web framework with automatic API documentation
- **CORS Middleware**: Configured for React frontend integration
- **Exception Handlers**: Global error handling with custom handlers
- **Celery Integration**: Asynchronous task processing setup
- **Database**: SQLAlchemy ORM with automatic table creation

### Configuration (`app/config.py`)
- **Environment Variables**: Managed through Pydantic BaseSettings
- **NSE URLs**: Multiple National Stock Exchange data sources
- **Database Configuration**: PostgreSQL/SQLite connection settings
- **Redis/Celery**: Message broker and result backend configuration
- **Logging**: Structured logging to file and console

## Database Models

### 1. BreakoutData (`app/models/breakout_data.py`)
Primary table for active breakout analysis:
- **Basic Info**: script_name, group_name, date
- **OHLC Data**: open, high, low, close, previous_high, volume
- **Technical Indicators**: CPR (Central Pivot Range), resistance/support levels
- **Analysis Results**: breakout_indicator, candle_indicator, volume_indicator
- **UI Integration**: chart links for visualization

### 2. MasterBOData (`app/models/master_data.py`)
Archive table with identical structure to BreakoutData for historical data storage.

### 3. GenerateBODataRequest (`app/models/generate_bo_request.py`)
Request model for breakout analysis:
- **pivot_val**: Percentage threshold for analysis
- **date**: Target analysis date

## API Endpoints Analysis

### Data Retrieval Endpoints

#### 1. `GET /api/get_data` (routes.py:27)
**Purpose**: Fetch processed breakout data with pagination
**Functionality**:
- Retrieves analyzed breakout data from database
- Implements pagination (page, limit parameters)
- Returns total count and paginated results
- Used by frontend to display analysis results

**Dependencies**: 
- Database session
- `get_breakout_data` service

#### 2. `GET /api/task_status/{task_id}` (routes.py:198)
**Purpose**: Monitor Celery task execution status
**Functionality**:
- Tracks asynchronous task progress
- Returns task status and results
- Essential for frontend task monitoring
- Handles task failure scenarios

**Dependencies**: 
- Celery AsyncResult
- Redis backend for task state

### Data Processing Endpoints

#### 3. `POST /api/fetch_script_symbols` (routes.py:60)
**Purpose**: Initiate stock symbol collection from NSE
**Functionality**:
- Triggers Celery task for web scraping NSE data
- Scrapes multiple NSE indices (Nifty 50, 200, MidCap, SmallCap)
- Uses Selenium WebDriver for dynamic content
- Stores symbols with group classification and chart links

**Dependencies**: 
- Selenium WebDriver
- NSE website scraping
- Database persistence

#### 4. `POST /api/generate_bodata` (routes.py:86)
**Purpose**: Execute breakout pattern analysis
**Functionality**:
- Processes historical data for breakout detection
- Calculates technical indicators (CPR, resistance/support)
- Analyzes volume patterns and candle formations
- Accepts pivot value and date parameters
- Returns task ID for monitoring

**Dependencies**: 
- Yahoo Finance data fetching
- Technical analysis calculations
- Historical price data processing

### Data Management Endpoints

#### 5. `POST /api/clear_chart` (routes.py:128)
**Purpose**: Clear analysis data for current date
**Functionality**:
- Removes processed data for today's date
- Allows re-running analysis with different parameters
- Maintains data integrity for historical records

#### 6. `POST /api/clear_complete_data` (routes.py:150)
**Purpose**: Archive and reset analysis data
**Functionality**:
- Moves data from active table to master archive
- Clears active analysis table for new cycle
- Preserves historical data for reporting

### Utility Endpoints

#### 7. `POST /api/suspend_action` (routes.py:178)
**Purpose**: Emergency stop for running analysis
**Functionality**:
- Interrupts ongoing analysis processes
- Prevents system overload
- Provides manual control over long-running tasks

#### 8. `GET /api/simulate_error` (routes.py:190)
**Purpose**: Testing endpoint for error handling
**Functionality**:
- Triggers controlled exceptions for testing
- Validates error handling mechanisms
- Development/debugging utility

### Legacy Endpoints

#### 9. `GET /api/fetch-scripts` (stocks.py:6)
**Purpose**: Placeholder for script fetching (simplified version)
**Status**: Basic implementation, likely superseded by `/fetch_script_symbols`

## Services Layer

### Core Services

#### 1. Data Fetching (`fetch_scripts.py`)
- **Symbol Collection**: Web scraping from NSE using Selenium
- **Historical Data**: Yahoo Finance integration for OHLC data
- **Data Processing**: Pandas-based data manipulation
- **Error Handling**: Robust exception management for external APIs

#### 2. Breakout Analysis (`generate_bo_data.py`)
- **Technical Indicators**: CPR calculation, support/resistance identification
- **Pattern Recognition**: Breakout detection algorithms
- **Volume Analysis**: Trading volume correlation with price movements
- **Suspension Support**: Interruptible analysis for user control

#### 3. Data Management (`fetch_data.py`, `clear_*.py`)
- **Database Operations**: CRUD operations with pagination
- **Data Migration**: Moving data between active and archive tables
- **Cleanup Operations**: Selective data removal by date/criteria

## Asynchronous Task Processing

### Celery Integration
- **Task Queue**: Redis-based message broker
- **Background Processing**: Non-blocking API responses
- **Task Monitoring**: Real-time status tracking
- **Error Recovery**: Failed task handling and retry mechanisms

### Task Types
1. **Data Collection Tasks**: Symbol fetching, historical data retrieval
2. **Analysis Tasks**: Breakout pattern detection and calculation
3. **Maintenance Tasks**: Data cleanup and archival operations

## Technical Stack Dependencies

### Core Framework
- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **Celery**: Distributed task processing

### Data Processing
- **Pandas**: Data manipulation and analysis
- **Selenium**: Web scraping for dynamic content
- **WebDriver**: Browser automation for NSE data

### Infrastructure
- **Redis**: Message broker and caching
- **PostgreSQL/SQLite**: Database storage
- **Environment Variables**: Configuration management

## Security and Reliability Features

### Error Handling
- Global exception handlers for API consistency
- Service-level error management
- Task failure recovery mechanisms

### Data Integrity
- Database transactions for atomic operations
- Validation at multiple layers (Pydantic, SQLAlchemy)
- Suspension flags for safe operation interruption

### Performance Optimization
- Pagination for large datasets
- Asynchronous processing for time-intensive operations
- Connection pooling and session management

## Use Case Flow

1. **Setup Phase**: Fetch stock symbols from NSE indices
2. **Analysis Phase**: Generate breakout data with specified parameters
3. **Monitoring Phase**: Track task progress and view results
4. **Management Phase**: Clear/archive data as needed
5. **Maintenance Phase**: Handle errors and system suspension

## Integration Points

### Frontend Integration
- CORS configured for React application
- RESTful API design with consistent responses
- Task-based processing with status monitoring

### External Services
- NSE website for stock symbol data
- Yahoo Finance for historical price data
- Chart visualization through GoCharting platform

This analysis reveals a well-structured application focused on financial data analysis with proper separation of concerns, robust error handling, and scalable asynchronous processing capabilities.