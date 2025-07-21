"""
API v1 router for Breakout Screener V2
"""

from fastapi import APIRouter

from .endpoints import analysis, breakout_data, health, stocks, tasks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(breakout_data.router, prefix="/breakout-data", tags=["breakout-data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
