"""Main File for FastAPI Application."""
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.routers import routes
from app.db.session import Base, engine

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include API Routers
app.include_router(routes.router, prefix="/api")


# Centralized error handler for unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled error during request %s ==>\n %s",
                  request.url, str(exc))
    return JSONResponse(
        content={
            "message": "Internal server error",
            "error": str(exc)},
        status_code=500
    )


# Centralized error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Validation error during request {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": exc.errors(),
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_hostname, port=settings.app_port)
