# Breakout Screener - Claude Development Guide

## Project Overview

The Breakout Screener is a full-stack financial application designed to analyze and screen stocks for breakout patterns. It provides real-time data processing, technical analysis, and a user-friendly interface for traders and investors.

### Architecture
- **Backend**: FastAPI with Python 3.13+
- **Frontend**: Next.js 15 with TypeScript and React 19
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Deployment**: WSL-based development environment

## Project Structure

```
breakout-screener/
├── app/                          # FastAPI backend application
│   ├── celery/                   # Celery configuration and worker setup
│   │   └── __init__.py          # Celery app initialization
│   ├── config.py                 # Application settings (Pydantic)
│   ├── db/                       # Database configuration
│   │   └── session.py           # SQLAlchemy session setup
│   ├── main.py                   # FastAPI application entry point
│   ├── models/                   # SQLAlchemy models and Pydantic schemas
│   │   ├── breakout_data.py     # Breakout data ORM model
│   │   ├── master_data.py       # Master archive table model
│   │   ├── enums.py             # Indicator enums (type-safe)
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── routers/                  # API route definitions
│   │   └── routes.py            # Main API routes
│   ├── services/                 # Business logic and data processing
│   ├── tasks/                    # Celery task definitions
│   │   └── __init__.py          # All task definitions
│   ├── tests/                    # Backend test files
│   └── utils/                    # Helper functions and utilities
├── frontend/                     # Next.js frontend application
│   └── src/
│       ├── app/                  # Next.js App Router pages
│       │   └── (dashboard)/     # Dashboard route group
│       │       ├── page.tsx     # Scanner (home page)
│       │       ├── reports/     # Historical reports
│       │       ├── settings/    # App settings
│       │       └── about/       # About page
│       ├── components/           # React components
│       │   ├── ui/              # shadcn/ui components
│       │   ├── layouts/         # Sidebar, ThemeToggle
│       │   └── ...              # Feature components
│       ├── services/             # API service layer
│       ├── store/                # Jotai state management
│       ├── types/                # TypeScript type definitions
│       └── utils/                # Frontend utilities
├── alembic/                      # Database migrations
├── docs/                         # Documentation
└── README.md                     # Setup and installation guide
```

## Key Components

### Backend Components

#### 1. API Routes (`app/routers/routes.py`)
Main API endpoints:
- `GET /api/` - Health check endpoint
- `GET /api/get_data` - Fetch paginated breakout data with search/filters
- `POST /api/fetch_script_symbols` - Fetch stock symbols from NSE (async task)
- `POST /api/generate_bodata` - Generate breakout analysis (async task)
- `POST /api/clear_chart` - Clear chart data for specific date
- `POST /api/clear_complete_data` - Archive and clear all data
- `GET /api/task_status/{task_id}` - Get Celery task status
- `GET /api/current_task` - Get currently running task (for page refresh resilience)
- `POST /api/suspend_action` - Suspend ongoing analysis

#### 2. Configuration (`app/config.py`)
Settings management using Pydantic with support for:
- Database connection strings (`database_url`)
- NSE URLs for different indices (Nifty 50, 200, Midcap, etc.)
- Celery/Redis configuration
- Application ports and hostnames
- Timezone settings (Asia/Kolkata)

#### 3. Database Models (`app/models/`)
- `breakout_data.py` - Main table for breakout analysis results
- `master_data.py` - Archive table (`master_breakout_data`)
- `schemas.py` - Pydantic validation schemas
- `enums.py` - Type-safe indicator enums (BreakoutIndicator, CandleIndicator, VolumeIndicator)

#### 4. Services (`app/services/`)
Business logic modules:
- `fetch_data.py` - Database retrieval with pagination, search, filters
- `fetch_scripts.py` - NSE scraping (Selenium) and historical data (yfinance)
- `generate_bo_data.py` - Core breakout analysis engine with suspension support
- `cpr_calculator.py` - CPR and pivot level calculations
- `clear_chart.py` - Date-specific data cleanup
- `clear_complete_data.py` - Archive to master table and reset

#### 5. Celery Tasks (`app/tasks/__init__.py`)
Asynchronous task processing:
- `fetch_script_symbols_task()` - Background symbol fetching
- `generate_bo_data_task()` - Background breakout analysis with progress tracking
- `clear_chart_data_task()` - Background data cleanup
- `clear_complete_data_task()` - Background archive and reset

#### 6. Utilities (`app/utils/`)
- `helpers.py` - Date/timezone utilities, suspension control
- `suspension_flag.py` - Threading Event for graceful task interruption
- `error_handlers.py` - Custom exceptions (DataFetchError, CPRCalculationError, etc.)
- `exception_handlers.py` - FastAPI exception handlers
- `selenium_driver.py` - Headless Chrome with bot-detection evasion

### Frontend Components

#### 1. Core Components (`frontend/src/components/`)
- `HomePage/` - Main orchestrator with task monitoring (2s polling)
- `DataTable/` - TanStack Table with sorting, filtering, search, CSV export
- `InputForm/` - Date picker, pivot gap, start-from configuration
- `ButtonGroups/` - Start/Stop/Clear action buttons
- `DisplayFields/` - Metrics display (scripts analyzed, duration)
- `Pagination/` - Table pagination controls
- `Loader/` - Skeleton loading component
- `Header/` - Application header with branding

#### 2. Layout Components (`frontend/src/components/layouts/`)
- `Sidebar.tsx` - Navigation sidebar (Scanner, Reports, Settings, About)
- `ThemeToggle.tsx` - Light/Dark mode toggle

#### 3. UI Components (`frontend/src/components/ui/`)
shadcn/ui components (15 total): badge, button, calendar, card, checkbox, dialog, input, label, popover, select, separator, skeleton, sonner, switch, table

#### 4. State Management (`frontend/src/store/`)
- `atoms.ts` - Jotai atoms for global state (14 atoms for scanner, table, UI state)

#### 5. Services (`frontend/src/services/`)
- `api.ts` - API client with functions: fetchScripts, generateBOData, clearChartData, clearCompleteData, getTaskStatus, getData, suspendAction, getCurrentTask

#### 6. Types (`frontend/src/types/`)
- `AppInterfaces.ts` - TypeScript interfaces (DataRow, DataResponse, TaskProgress, etc.)

#### 7. Utilities (`frontend/src/utils/`)
- `axiosInstance.ts` - Configured Axios instance (10s timeout)
- `helperFn.ts` - Date formatting, duration calculation
- `csvExport.ts` - CSV export using PapaParse

## Development Commands

### Backend Commands
```bash
# Create virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
# OR
uv pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run database migrations
alembic upgrade head

# Start Celery worker
celery -A app.celery.celery_app worker --loglevel=info
```

### Frontend Commands
```bash
cd frontend

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

# Install dev dependencies
uv pip install -e ".[dev]"
```

## Database Schema

### breakout_data Table
Primary table for analysis results:
- `id` (PK), `script_name`, `group_name`, `date`
- OHLCV: `open`, `high`, `low`, `close`, `volume`, `previous_high`
- CPR levels: `cpr`, `res1`, `res2`, `supp1`, `supp2`
- Indicators: `breakout_indicator`, `candle_indicator`, `volume_indicator`
- `narrow_gap` flag, `link` (chart URL)

### master_breakout_data Table
Archive table with identical schema to `breakout_data`.

## Environment Configuration

### Backend Environment (`.env`)
```env
DATABASE_URL=postgresql://trading_user:password@localhost:5432/trading_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
APP_HOSTNAME=localhost
APP_PORT=8000
REACT_PORT=3000
APP_TIMEZONE=Asia/Kolkata
NSE_URL_NIFTY_50=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050
# Additional NSE URLs for other indices
```

### Frontend Environment (`.env.local`)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migrations
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **PostgreSQL**: Primary database
- **Pandas**: Data manipulation
- **Selenium**: NSE index constituent scraping
- **yfinance**: Historical price data (60x faster than Selenium)
- **Tenacity**: Retry logic for API calls

### Frontend
- **Next.js 15**: React framework with App Router
- **React 19**: UI library
- **TypeScript**: Static type checking
- **Tailwind CSS v4**: Utility-first CSS
- **shadcn/ui**: Component library (Radix UI based)
- **Jotai**: State management (14 atoms)
- **TanStack Table**: Advanced table functionality
- **Axios**: HTTP client
- **next-themes**: Dark mode support
- **Sonner**: Toast notifications
- **PapaParse**: CSV export
- **date-fns**: Date utilities

## Development Workflow

1. **Data Flow**: NSE data → Backend processing → PostgreSQL → API → Frontend display
2. **Async Processing**: Celery workers handle heavy computations
3. **Real-time Updates**: 2-second polling for task status
4. **Task Resumption**: `getCurrentTask()` API for page refresh resilience
5. **Suspension Control**: Graceful task interruption via threading Event

## Common Development Tasks

### Adding New API Endpoints
1. Define route in `app/routers/routes.py`
2. Add Pydantic schemas in `app/models/schemas.py`
3. Implement business logic in appropriate service module
4. Add corresponding frontend API call in `frontend/src/services/api.ts`
5. Update TypeScript interfaces in `frontend/src/types/AppInterfaces.ts`

### Database Changes
1. Update SQLAlchemy models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

### Adding New Components
1. Create component in `frontend/src/components/`
2. Add Jotai atoms if needed in `frontend/src/store/atoms.ts`
3. Follow existing patterns for styling and props

## Key Features

- **Multi-Index Support**: Nifty 50, 200, Midcap 150, Smallcap 250
- **Breakout Detection**: Red Candle, No Breakout, Breakout, Big Sell Wick, No Entry
- **Volume Analysis**: Good, Average, Low indicators
- **Narrow Gap Detection**: Pivot-based entry identification
- **Resume Capability**: Start analysis from any index position
- **Dark Mode**: Full theme support with persistence
- **CSV Export**: Export analysis results
- **Chart Integration**: Direct links to GoCharting

## Performance Considerations

- Celery for long-running operations (400-500 scripts in ~10-15 minutes)
- Pagination for large datasets
- Database indexing on script_name, group_name, date
- Debounced search (300ms) in DataTable
- Auto-refresh every 10 seconds during analysis

## Security Notes

- Environment variables for sensitive configuration
- CORS middleware configured for frontend origin
- Input validation using Pydantic models
- Bot detection evasion for NSE scraping

## Known Issues

> **Detailed Analysis**: See `Planning/ANALYSIS.md` for comprehensive findings with file references.

### Critical Issues (Must Fix)

| Issue | Location | Impact |
|-------|----------|--------|
| Credentials logged to stdout | `app/config.py:56-58` | DATABASE_URL with password exposed in logs |
| Hardcoded DB credentials | `alembic.ini:65` | Secrets committed to version control |
| N+1 query in archive | `app/services/clear_complete_data.py:18-79` | 501 queries instead of 1-2 (50x slower) |
| Data copy bug | `app/services/clear_complete_data.py:40` | `supp2=record.supp1` copies wrong field |

### High Priority Issues

| Issue | Location | Impact |
|-------|----------|--------|
| No connection pooling | `app/db/session.py:13` | Connection exhaustion under load |
| Overly permissive CORS | `app/main.py:30-36` | `allow_methods=["*"]` too broad |
| Individual commits in loop | `app/services/generate_bo_data.py:216` | 500 disk syncs instead of ~10 |
| Low test coverage | `app/tests/` | ~2.5% coverage |

### Medium Priority Issues

| Issue | Location |
|-------|----------|
| Debug endpoint exposed | `app/routers/routes.py:208-213` (`/simulate_error`) |
| Redundant toast libraries | `frontend/package.json` (sonner + react-hot-toast) |
| Column definitions not memoized | `frontend/src/components/DataTable/DataTable.tsx:152-283` |
| Print statements instead of logging | `app/config.py:58`, `app/db/test_connection.py` |

## Improvement Plan

> **Detailed Plan**: See `Planning/IMPROVEMENT_PLAN.md` for comprehensive implementation guide.

### Phase Priority Overview

| Phase | Focus | Priority | Status |
|-------|-------|----------|--------|
| Phase 6 | Performance & Database Optimization | Critical | Pending |
| Phase 7 | Security Hardening | Critical | Pending |
| Phase 8 | Testing Infrastructure | High | Pending |
| Phase 9 | Code Quality & Refactoring | Medium | Pending |
| Phase 10 | Monitoring & Observability | Medium | Pending |
| Phase 11 | Celery Configuration | Medium | Pending |
| Phase 12 | Documentation | Low | Pending |

### Quick Wins (Implement First)

1. Remove `print(settings.model_dump())` from `config.py:58`
2. Add connection pool config to `session.py`
3. Restrict CORS methods to `["GET", "POST", "OPTIONS"]`
4. Remove `react-hot-toast` from `package.json`
5. Fix `supp2` copy bug in `clear_complete_data.py:40`

### Expected Impact After Fixes

- **Performance**: Archive operation 50x faster, 500→10 commits
- **Security**: No credential exposure, restricted attack surface
- **Reliability**: 60%+ test coverage, connection stability
- **Maintainability**: Cleaner code, structured logging
