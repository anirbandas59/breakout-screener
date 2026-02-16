#!/bin/bash

# Breakout Screener V2 Project Structure Creation Script
# This script creates the complete directory structure and initial files for V2

set -e

echo "🚀 Creating Breakout Screener V2 Project Structure..."

# Define the V2 project path
V2_PATH="$HOME/workspace/projects/breakout_screener_v2"

# Create the main project directory
echo "📁 Creating main project directory..."
mkdir -p "$V2_PATH"
cd "$V2_PATH"

echo "📁 Creating directory structure..."

# Backend directory structure
mkdir -p backend/src/breakout_screener/api/v1/endpoints
mkdir -p backend/src/breakout_screener/core
mkdir -p backend/src/breakout_screener/services
mkdir -p backend/src/breakout_screener/repositories
mkdir -p backend/src/breakout_screener/models
mkdir -p backend/src/breakout_screener/schemas
mkdir -p backend/src/breakout_screener/workers
mkdir -p backend/src/breakout_screener/utils
mkdir -p backend/tests/unit
mkdir -p backend/tests/integration
mkdir -p backend/tests/fixtures
mkdir -p backend/requirements
mkdir -p backend/migrations

# Frontend directory structure
mkdir -p frontend/src/app
mkdir -p frontend/src/components/ui
mkdir -p frontend/src/components/forms
mkdir -p frontend/src/components/tables
mkdir -p frontend/src/components/charts
mkdir -p frontend/src/hooks
mkdir -p frontend/src/lib
mkdir -p frontend/src/stores
mkdir -p frontend/src/types
mkdir -p frontend/__tests__/components
mkdir -p frontend/__tests__/hooks
mkdir -p frontend/__tests__/utils
mkdir -p frontend/public

# Shared directory structure
mkdir -p shared/types
mkdir -p shared/constants

# Infrastructure directory structure
mkdir -p infrastructure/docker
mkdir -p infrastructure/kubernetes
mkdir -p infrastructure/terraform

# Scripts directory
mkdir -p scripts

# Documentation directory
mkdir -p docs

# Logs directory (gitignored)
mkdir -p logs/backend
mkdir -p logs/frontend

echo "📄 Creating initial configuration files..."

# Root level configuration files
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production
.env.staging

# Build outputs
dist/
build/
*.egg-info/

# Frontend specific
.next/
out/
.nuxt/
.output/
.vercel/

# Backend specific
alembic/versions/*.py
!alembic/versions/__init__.py
EOF

# Environment variables template
cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://trading_user:secure_password@localhost:5432/breakout_screener_v2

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Application Configuration
APP_HOSTNAME=http://localhost
APP_PORT=8000
REACT_PORT=3000
APP_TIMEZONE=UTC

# NSE URLs
NSE_URL_NIFTY_50=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050
NSE_URL_NIFTY_200=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20200
NSE_URL_NIFTY_MIDCAP_150=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20MIDCAP%20150
NSE_URL_NIFTY_MIDSMALLCAP_400=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20MIDSMALLCAP%20400
NSE_URL_NIFTY_SMALLCAP_250=https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%20SMALLCAP%20250

# YFinance URLs
YFIN_HIST_URL=https://query1.finance.yahoo.com/v7/finance/download

# Security
SECRET_KEY=your-secret-key-here
API_V1_STR=/api/v1

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO

# Development
DEBUG=True
ENVIRONMENT=development
EOF

echo "✅ V2 Project structure created successfully!"
echo ""
echo "📁 Project created at: $V2_PATH"
echo ""
echo "🎯 Next steps:"
echo "1. cd $V2_PATH"
echo "2. cp .env.example .env"
echo "3. Edit .env with your configuration"
echo ""
echo "📚 Documentation: See V2_MIGRATION_PLAN.md for detailed implementation plan"
echo "🏗️ Structure: Modern architecture with proper separation of concerns"
echo "🚀 Ready: Foundation setup complete - ready for Phase 1 implementation!"