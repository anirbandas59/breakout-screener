"""
Health check endpoints for API v1
"""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import config
from ....core.database import (
    check_table_exists,
    db_manager,
    get_db,
    get_table_row_count,
)
from ....core.logging import get_logger
from ....core.redis import get_redis, redis_manager

router = APIRouter()
logger = get_logger(__name__)


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/database")
async def database_health(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Check database connectivity and basic operations"""
    try:
        # Check basic connectivity
        is_healthy = await db_manager.health_check()

        if not is_healthy:
            raise HTTPException(status_code=503, detail="Database connection failed")

        # Check if V2 tables exist
        tables_to_check = [
            "stocks",
            "breakout_data_v2",
            "master_breakout_data_v2",
            "analysis_sessions",
            "performance_metrics",
        ]

        table_status = {}
        for table in tables_to_check:
            exists = await check_table_exists(table)
            if exists:
                count = await get_table_row_count(table)
                table_status[table] = {"exists": True, "row_count": count}
            else:
                table_status[table] = {"exists": False, "row_count": 0}

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "connection": "ok",
            "tables": table_status,
        }

    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        raise HTTPException(
            status_code=503, detail=f"Database health check failed: {str(e)}"
        ) from e


@router.get("/redis")
async def redis_health() -> dict[str, Any]:
    """Check Redis connectivity and basic operations"""
    try:
        # Check basic connectivity
        is_healthy = await redis_manager.health_check()

        if not is_healthy:
            raise HTTPException(status_code=503, detail="Redis connection failed")

        # Test basic operations
        redis_client = await get_redis()

        # Test set/get operation
        test_key = "health_check_test"
        test_value = f"test_{int(time.time())}"

        await redis_client.set(test_key, test_value, ex=10)  # 10 second TTL
        retrieved_value = await redis_client.get(test_key)

        if retrieved_value != test_value:
            raise HTTPException(
                status_code=503, detail="Redis set/get operation failed"
            )

        # Clean up test key
        await redis_client.delete(test_key)

        # Get Redis info
        info = await redis_client.info()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "connection": "ok",
            "operations": "ok",
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
        }

    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        raise HTTPException(
            status_code=503, detail=f"Redis health check failed: {str(e)}"
        ) from e


@router.get("/services")
async def services_health(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Comprehensive health check for all services"""
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "services": {},
    }

    # Check database
    try:
        db_result = await database_health(db)
        health_data["services"]["database"] = {
            "status": "healthy",
            "details": db_result,
        }
    except HTTPException as e:
        health_data["services"]["database"] = {"status": "unhealthy", "error": e.detail}
        health_data["status"] = "degraded"

    # Check Redis
    try:
        redis_result = await redis_health()
        health_data["services"]["redis"] = {
            "status": "healthy",
            "details": redis_result,
        }
    except HTTPException as e:
        health_data["services"]["redis"] = {"status": "unhealthy", "error": e.detail}
        health_data["status"] = "degraded"

    # Add configuration status
    health_data["services"]["configuration"] = {
        "status": "healthy",
        "details": {
            "debug_mode": config.DEBUG,
            "log_level": config.LOG_LEVEL,
            "database_host": config.DATABASE_HOST,
            "redis_host": config.REDIS_HOST,
        },
    }

    return health_data
