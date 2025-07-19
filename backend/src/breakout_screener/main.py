"""
Main FastAPI application for Breakout Screener V2
"""

import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from .core.config import config
from .core.database import db_manager
from .core.redis import redis_manager
from .core.logging import get_logger, log_api_request, log_error
from .api.v1.api import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Breakout Screener V2", version=config.VERSION)
    
    try:
        # Initialize database
        await db_manager.initialize()
        logger.info("Database initialized")
        
        # Initialize Redis
        await redis_manager.initialize()
        logger.info("Redis initialized")
        
        # Initialize other services here
        
        logger.info("Application startup complete")
        yield
        
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down application")
        
        try:
            await db_manager.close()
            await redis_manager.close()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))


# Create FastAPI application
app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description="Advanced breakout stock screener with real-time data analysis",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    log_api_request(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration=duration,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    log_error(exc, {
        "method": request.method,
        "path": str(request.url.path),
        "client_ip": request.client.host if request.client else "unknown"
    })
    
    if config.DEBUG:
        # Return detailed error in development
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # Return generic error in production
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )


# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": config.VERSION,
        "environment": config.ENVIRONMENT
    }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "services": {}
    }
    
    # Check database
    try:
        db_healthy = await db_manager.health_check()
        health_status["services"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "checks": ["connection"]
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Redis
    try:
        redis_healthy = await redis_manager.health_check()
        health_status["services"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "checks": ["connection"]
        }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Determine overall status
    service_statuses = [service["status"] for service in health_status["services"].values()]
    if any(status == "unhealthy" for status in service_statuses):
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": f"Welcome to {config.PROJECT_NAME}",
        "version": config.VERSION,
        "docs_url": "/docs" if config.DEBUG else "Documentation not available",
        "health_check": "/health"
    }


# Include API router
app.include_router(api_router, prefix=config.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "breakout_screener.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower(),
        access_log=config.DEBUG
    )