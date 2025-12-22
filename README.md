# Breakout Screener

A web application to shortlist positional breakout stocks using the Breakout System. Analyzes NSE stocks for breakout patterns using technical indicators like CPR (Central Pivot Range), support/resistance levels, and volume analysis.

## Features

- Fetch stock symbols from NSE indices (Nifty 50, 200, Midcap 150, etc.)
- Analyze breakout patterns with technical indicators
- Calculate CPR, resistance, and support levels
- Volume and candle pattern analysis
- Narrow gap detection for pivot-based entries
- Paginated data display with chart links

## Tech Stack

**Backend**: FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL
**Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
**Data**: Selenium (NSE scraping), Pandas

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/anirbandas59/breakout-screener.git
cd breakout-screener
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

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
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery Worker
source venv/bin/activate
celery -A app.celery.celery_app worker --loglevel=info

# Terminal 4: Frontend
cd frontend
npm run dev
```

### Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Fetch List**: Click to fetch stock symbols from NSE indices
2. **Select Date**: Choose the analysis date
3. **Set Pivot %**: Configure narrow gap threshold (default: 0.5%)
4. **Start**: Begin breakout analysis
5. **View Results**: See analyzed stocks with indicators in the table
6. **Chart Link**: Click to view detailed chart on GoCharting

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | Health check |
| `/api/get_data` | GET | Fetch paginated breakout data |
| `/api/fetch_script_symbols` | POST | Fetch symbols from NSE |
| `/api/generate_bodata` | POST | Generate breakout analysis |
| `/api/clear_chart` | POST | Clear data for specific date |
| `/api/clear_complete_data` | POST | Archive and clear all data |
| `/api/task_status/{id}` | GET | Get Celery task status |
| `/api/suspend_action` | POST | Stop ongoing analysis |

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guide.

### Running Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run tests
pytest app/tests/
```

## Project Structure

```
breakout-screener/
├── app/                  # FastAPI backend
│   ├── celery/           # Celery configuration
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── routers/          # API routes
│   ├── services/         # Business logic
│   ├── tasks/            # Celery tasks
│   └── utils/            # Utilities
├── frontend/             # Next.js frontend
│   └── src/
│       ├── app/          # Pages
│       ├── components/   # React components
│       ├── services/     # API services
│       └── types/        # TypeScript types
├── docs/                 # Documentation
└── alembic/              # Database migrations
```

## Known Issues

See [docs/project-analysis.md](docs/project-analysis.md) for known issues and planned improvements.

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.
