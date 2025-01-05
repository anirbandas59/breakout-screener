"""Main File for FastAPI Application."""
import logging
# import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.utils import (
    general_exception_handler,
    validation_exception_handler
)

from app.config import settings
from app.routers import routes
from app.db.session import Base, engine
from app.celery import celery_init_app

# Initialize DB
Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    """ Create FastAPI app"""
    app = FastAPI()

    # Include API Routers
    app.include_router(routes.router, prefix="/api")
    logging.info("Routers are set up.")

    # Include exception handlers
    app.add_exception_handler(Exception, general_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)

    logging.info("Exception handlers are set up.")

    # Add app config for Celery
    app.state.config = {
        "CELERY": {
            "broker_url": settings.celery_broker_url,
            "result_backend": settings.celery_result_backend,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": settings.app_timezone,
            "enable_utc": True,
        }
    }
    logging.info("App State configurations are set up.")

    celery_app = celery_init_app(app)

    logging.info("Celery app is set up.")

    return app


# Centralized error handler for unhandled exceptions
# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logging.error("Unhandled error during request %s ==>\n %s",
#                   request.url, str(exc))
#     return JSONResponse(
#         content={
#             "message": "Internal server error",
#             "error": str(exc)},
#         status_code=500
#     )


# # Centralized error handler for validation errors
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     logging.error(f"Validation error during request {request.url}: {exc}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "message": "Validation error",
#             "details": exc.errors(),
#         },
#     )


# if __name__ == "__main__":
#     uvicorn.run(app, host=settings.app_hostname, port=settings.app_port)
