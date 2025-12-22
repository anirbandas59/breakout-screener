# Breakout Screener - Claude Development Guide

## Project Overview

The Breakout Screener is a full-stack financial application designed to analyze and screen stocks for breakout patterns. It provides real-time data processing, technical analysis, and a user-friendly interface for traders and investors.

### Architecture
- **Backend**: FastAPI with Python
- **Frontend**: Next.js with TypeScript and React
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Deployment**: WSL-based development environment

## Project Structure

```
breakout-screener/
├── app/                          # FastAPI backend application
│   ├── celery/                   # Celery configuration and worker setup
│   ├── config.py                 # Application settings and environment variables
│   ├── db/                       # Database configuration and session management
│   ├── main.py                   # FastAPI application entry point
│   ├── models/                   # SQLAlchemy models and Pydantic schemas
│   ├── routers/                  # API route definitions
│   ├── services/                 # Business logic and data processing
│   ├── tasks/                    # Celery task definitions
│   ├── tests/                    # Backend test files
│   └── utils/                    # Helper functions and utilities
├── frontend/                     # Next.js frontend application
│   ├── src/
│   │   ├── app/                  # Next.js app router pages
│   │   ├── components/           # React components
│   │   ├── services/             # API service layer
│   │   ├── types/                # TypeScript type definitions
│   │   └── utils/                # Frontend utilities
│   └── package.json
├── backend/                      # Backend-specific files
├── docs/                         # Documentation and wireframes
├── shared/                       # Shared resources
└── README.md                     # Main setup and installation guide
```

## Key Components

### Backend Components

#### 1. API Routes (`app/routers/routes.py`)
Main API endpoints include:
- `GET /` - Health check endpoint
- `GET /get_data` - Fetch paginated breakout data
- `POST /fetch_script_symbols` - Fetch stock symbols from NSE
- `POST /generate_bodata` - Generate breakout analysis data
- `POST /clear_chart` - Clear chart data for specific date
- `POST /clear_complete_data` - Clear all data

#### 2. Configuration (`app/config.py`)
Settings management using Pydantic with support for:
- Database connection strings
- NSE URLs for different indices (Nifty 50, 200, Midcap, etc.)
- Celery/Redis configuration
- Application ports and hostnames

#### 3. Database Models (`app/models/`)
- `breakout_data` - Main table for breakout analysis results
- `master_table` - Master data storage
- Support for technical indicators, CPR levels, and volume analysis

#### 4. Services (`app/services/`)
Business logic modules:
- `fetch_data.py` - Data fetching operations
- `fetch_scripts.py` - Stock symbol retrieval
- `generate_bo_data.py` - Breakout analysis generation
- `nse_data.py` - NSE data processing
- `clear_chart.py` - Data cleanup operations

#### 5. Celery Tasks (`app/tasks/`)
Asynchronous task processing:
- `fetch_script_symbols_task()` - Background symbol fetching
- `generate_bo_data_task()` - Background breakout analysis
- `clear_chart_data_task()` - Background data cleanup

### Frontend Components

#### 1. Core Components (`frontend/src/components/`)
- `Header/` - Application header
- `Navbar/` - Navigation component
- `InputForm/` - Data input forms
- `DataTable/` - Data display table
- `Loader/` - Loading indicators
- `Pagination/` - Data pagination
- `ButtonGroups/` - Action buttons
- `DisplayFields/` - Data display fields

#### 2. Services (`frontend/src/services/`)
- `api.ts` - API service layer for backend communication

#### 3. Types (`frontend/src/types/`)
- `AppInterfaces.ts` - TypeScript interface definitions

#### 4. Utilities (`frontend/src/utils/`)
- `axiosInstance.ts` - Configured Axios instance
- `helperFn.ts` - Helper functions

## Development Commands

### Backend Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run database migrations
alembic upgrade head

# Start Celery worker
celery -A app.celery_app.celery worker --loglevel=info
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Testing Commands
```bash
# Backend tests
pytest app/tests/

# Check backend dependencies
pip install -r test-requirements.txt
```

## Database Schema

### breakout_data Table
Key fields for technical analysis:
- `script_name`, `group_name`, `date`
- OHLCV data (`open`, `high`, `low`, `close`, `volume`)
- Technical indicators (`breakout_indicator`, `candle_indicator`, `volume_indicator`)
- CPR levels (`cpr`, `res1`, `res2`, `supp1`, `supp2`)
- `narrow_gap` flag and chart `link`

### master_table
Similar structure to `breakout_data` for master data storage.

## Environment Configuration

### Backend Environment (`.env`)
```env
DATABASE_URL=postgresql://trading_user:secure_password@localhost:5432/breakout_screener
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
NSE_URL_NIFTY_50=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050
# Additional NSE URLs for other indices
```

### Frontend Environment (`.env.local`)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Celery**: Distributed task queue
- **Redis**: In-memory data store for Celery broker
- **PostgreSQL**: Primary database
- **Pandas**: Data manipulation and analysis
- **Selenium**: Web scraping for NSE data

### Frontend
- **Next.js 15**: React framework with App Router
- **React 19**: UI library
- **TypeScript**: Static type checking
- **Material-UI**: Component library
- **Axios**: HTTP client
- **Jotai**: State management
- **Tailwind CSS**: Utility-first CSS framework

## Development Workflow

1. **Data Flow**: NSE data → Backend processing → Database storage → Frontend display
2. **Async Processing**: Heavy computations handled by Celery workers
3. **Real-time Updates**: Task status polling for long-running operations
4. **Pagination**: Efficient data loading with paginated APIs

## Common Development Tasks

### Adding New API Endpoints
1. Define route in `app/routers/routes.py`
2. Implement business logic in appropriate service module
3. Add corresponding frontend API call in `frontend/src/services/api.ts`
4. Update TypeScript interfaces if needed

### Database Changes
1. Update SQLAlchemy models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

### Adding New Components
1. Create component in `frontend/src/components/`
2. Follow existing patterns for styling and props
3. Update imports in parent components

## Testing Strategy

- Backend tests using pytest framework
- Test files located in `app/tests/`
- Separate test requirements in `test-requirements.txt`

## Performance Considerations

- Use Celery for CPU-intensive operations
- Implement pagination for large datasets
- Redis caching for frequently accessed data
- Database indexing on commonly queried fields

## Security Notes

- Environment variables for sensitive configuration
- CORS middleware configured for frontend origin
- Database user with minimal required permissions
- Input validation using Pydantic models

## Deployment Notes

- WSL-based development environment
- PostgreSQL database setup with specific user permissions
- Redis server for Celery task queue
- Multi-process setup using tmux for development

This guide provides the essential information needed for understanding and contributing to the Breakout Screener project.