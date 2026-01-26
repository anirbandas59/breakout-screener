# Breakout Screener V2

A production-ready web application to screen and analyze positional breakout stocks from NSE indices. Built with modern technologies, it processes 400-500 stocks efficiently using technical indicators like CPR (Central Pivot Range), support/resistance levels, and volume analysis.

## ✨ Features

### Core Functionality

- **Multi-Index Support**: Fetch stock symbols from NSE indices (Nifty 50, 200, Midcap 150, Smallcap 250, etc.)
- **Breakout Analysis**: Automated detection of breakout patterns with configurable parameters
- **Technical Indicators**:
  - CPR (Central Pivot Range) calculation
  - Support and resistance levels (RES1, RES2, SUPP1, SUPP2)
  - Volume analysis (Good/Average/Low)
  - Candle pattern recognition (Green/Red/Doji)
  - Narrow gap detection for pivot-based entries
- **Real-time Progress Tracking**: Live updates during analysis with stock-by-stock progress
- **Resume Capability**: Start analysis from any index position
- **Data Management**: Archive historical data, clear specific dates, or reset completely

### User Experience

- **Modern UI**: Built with shadcn/ui components and Tailwind CSS v4
- **Dark Mode**: Full dark mode support with theme toggle
- **Multi-page Dashboard**: Scanner, Reports, Settings, and About pages
- **Advanced Table**: Sorting, filtering, search, and CSV export capabilities
- **Responsive Design**: Mobile-friendly interface
- **Toast Notifications**: User feedback for all operations
- **Chart Integration**: Direct links to GoCharting for detailed analysis

### Performance

- **High Throughput**: Process 400-500 stocks in ~10-15 minutes
- **Async Processing**: Background task execution with Celery
- **Optimized Data Fetching**: yfinance integration (60x faster than Selenium)
- **Pagination**: Efficient data loading with configurable page sizes
- **Suspension Control**: Stop and resume analysis at any point

## 🛠 Tech Stack

### Backend

- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- Celery - Distributed task queue
- Redis - Message broker and result backend
- PostgreSQL - Primary database
- Pydantic - Data validation and settings
- yfinance - Historical stock data
- Selenium - NSE index constituent scraping

### Frontend

- Next.js 15 - React framework with App Router
- React 19 - UI library
- TypeScript - Type-safe JavaScript
- Tailwind CSS v4 - Utility-first CSS
- shadcn/ui - Component library
- Jotai - State management
- TanStack Table - Advanced table functionality
- Axios - HTTP client

## Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- uv (Python package manager) - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/anirbandas59/breakout-screener.git
cd breakout-screener
```

### 2. Backend Setup

```bash
# Create virtual environment (using uv)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
# OR
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb breakout_screener

# Run migrations
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL
```

## Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/breakout_screener

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# App
APP_HOSTNAME=localhost
APP_PORT=8000
REACT_PORT=3000
APP_TIMEZONE=Asia/Kolkata

# NSE URLs
NSE_URL_NIFTY_50=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050
NSE_URL_NIFTY_200=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20200
# ... additional NSE URLs

# Yahoo Finance
YFIN_HIST_URL=https://finance.yahoo.com/quote/SCRIPT.NS/history/
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## Running the Application

### Start all services (recommended)

Use tmux or separate terminals:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery Worker
source .venv/bin/activate
celery -A app.celery.celery_app worker --loglevel=info

# Terminal 4: Frontend
cd frontend
npm run dev
```

### Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Basic Workflow

1. **Fetch Stock List**: Click "Fetch List" to retrieve symbols from NSE indices
2. **Select Analysis Date**: Choose the date for which you want to analyze breakouts
3. **Configure Settings**:
   - **Pivot Gap %**: Set narrow gap threshold (default: 0.5%)
   - **Start From**: Optional - Resume analysis from specific stock index
4. **Generate Analysis**: Click "Start" to begin breakout detection
5. **Monitor Progress**: Watch real-time progress with current stock and completion percentage
6. **View Results**:
   - Browse analyzed stocks in the interactive table
   - Use search, filters, and sorting to find specific patterns
   - Export results to CSV for further analysis
7. **Access Charts**: Click chart links to view detailed technical analysis on GoCharting

### Advanced Features

- **Suspend Analysis**: Stop ongoing analysis and resume later using "Start From" field
- **Filter by Breakout**: Use table filters to show only specific breakout types
- **Historical Reports**: View past analysis results in the Reports page
- **Data Management**: Clear specific dates or archive all data to master table
- **Theme Toggle**: Switch between light and dark modes for comfortable viewing

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | Health check |
| `/api/get_data` | GET | Fetch paginated breakout data with optional search and filters |
| `/api/fetch_script_symbols` | POST | Fetch stock symbols from NSE indices (async task) |
| `/api/generate_bodata` | POST | Generate breakout analysis for all stocks (async task) |
| `/api/clear_chart` | POST | Clear breakout data for specific date |
| `/api/clear_complete_data` | POST | Archive current data to master table and clear |
| `/api/task_status/{id}` | GET | Get status of Celery task by ID |
| `/api/current_task` | GET | Get currently running task information |
| `/api/suspend_action` | POST | Suspend ongoing analysis |

Interactive API documentation available at: `http://localhost:8000/docs`

## 🧪 Development

### Running Tests

```bash
# Install dev dependencies (includes test tools)
uv pip install -e ".[dev]"

# Run tests
pytest app/tests/
```

## 📂 Project Structure

```
breakout_screener_v2/
├── app/                          # FastAPI backend application
│   ├── celery/                   # Celery worker configuration
│   │   └── __init__.py          # Celery app initialization
│   ├── db/                       # Database configuration
│   │   └── session.py           # SQLAlchemy session setup
│   ├── models/                   # Data models
│   │   ├── breakout_data.py     # Breakout data ORM model
│   │   ├── master_data.py       # Master archive table model
│   │   ├── enums.py             # Indicator enums (type-safe)
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── routers/                  # API endpoints
│   │   └── routes.py            # Main API routes
│   ├── services/                 # Business logic layer
│   │   ├── fetch_data.py        # Data retrieval service
│   │   ├── fetch_scripts.py     # NSE scraping & yfinance integration
│   │   ├── generate_bo_data.py  # Core breakout analysis engine
│   │   ├── cpr_calculator.py    # CPR calculation module
│   │   ├── clear_chart.py       # Date-specific data cleanup
│   │   └── clear_complete_data.py # Archive & reset operations
│   ├── tasks/                    # Celery async tasks
│   │   └── __init__.py          # Task definitions
│   ├── utils/                    # Utility functions
│   │   ├── helpers.py           # Date & timezone utilities
│   │   ├── error_handlers.py    # Custom exception classes
│   │   ├── exception_handlers.py # FastAPI exception handlers
│   │   └── suspension_flag.py   # Analysis suspension control
│   ├── tests/                    # Test suite
│   ├── config.py                # Application settings (Pydantic)
│   └── main.py                  # FastAPI application entry point
│
├── frontend/                     # Next.js frontend application
│   └── src/
│       ├── app/                 # Next.js 15 App Router
│       │   ├── (dashboard)/     # Dashboard route group
│       │   │   ├── layout.tsx   # Sidebar + header layout
│       │   │   ├── page.tsx     # Scanner (home page)
│       │   │   ├── reports/     # Historical reports page
│       │   │   ├── settings/    # Settings page
│       │   │   └── about/       # About page
│       │   ├── globals.css      # Global styles + Tailwind
│       │   └── layout.tsx       # Root layout
│       ├── components/          # React components
│       │   ├── ui/              # shadcn/ui components
│       │   ├── layouts/         # Layout components (Sidebar, Header)
│       │   ├── DataTable/       # Advanced table with filters
│       │   ├── InputForm/       # Analysis configuration form
│       │   ├── ButtonGroups/    # Action buttons
│       │   ├── DisplayFields/   # Status display
│       │   ├── Pagination/      # Table pagination
│       │   └── Loader/          # Loading indicators
│       ├── services/            # API integration
│       │   └── api.ts          # Axios-based API client
│       ├── store/               # State management
│       │   └── atoms.ts        # Jotai atoms
│       ├── types/               # TypeScript definitions
│       │   └── AppInterfaces.ts
│       └── utils/               # Frontend utilities
│           ├── axiosInstance.ts
│           ├── helperFn.ts
│           └── csvExport.ts
│
├── alembic/                      # Database migrations
│   ├── versions/                # Migration scripts
│   └── env.py                   # Alembic environment config
│
├── .env                          # Environment variables (not in git)
├── requirements.txt              # Python dependencies
├── alembic.ini                  # Alembic configuration
└── README.md                    # This file
```

## 📚 Documentation

- **API Documentation**: Interactive Swagger UI at `/docs` endpoint

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. Code follows existing patterns and style
2. All tests pass before submitting PR
3. New features include appropriate tests
4. Documentation is updated as needed

## ⚠️ Disclaimer

This application is for educational and research purposes. Stock market investments carry risk. Always do your own research and consult with financial advisors before making investment decisions.

## 📄 License

MIT License - see [LICENSE.md](LICENSE.md) for details.

## 🙏 Acknowledgments

- **NSE India**: Stock data source
- **Yahoo Finance**: Historical price data API
- **GoCharting**: Chart visualization integration
