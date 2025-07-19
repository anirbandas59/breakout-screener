"""
API v1 router for Breakout Screener V2
"""

from fastapi import APIRouter

from .endpoints import health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Placeholder for future endpoints
# api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
# api_router.include_router(data.router, prefix="/data", tags=["data"])