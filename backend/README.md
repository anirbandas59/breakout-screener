# Breakout Screener V2 Backend

Advanced breakout stock screener with real-time data analysis.

## Features

- FastAPI with async support
- SQLAlchemy 2.0 with PostgreSQL
- Redis caching and session management
- Structured logging with structlog
- Environment-based configuration
- Comprehensive health checks

## Installation

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

## Usage

```bash
# Run development server
uvicorn breakout_screener.main:app --reload

# Run with environment variables
python -m breakout_screener.main
```

## Health Checks

- Basic health: `GET /health`
- Detailed health: `GET /health/detailed`  
- API health: `GET /api/v1/health/services`

## Environment Variables

See `.env.example` for required environment variables.