"""Main File for FastAPI Application."""
import logging
# import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.utils import (
    general_exception_handler,
    validation_exception_handler
)

from app.config import settings
from app.routers import routes
from app.db.session import Base, engine
from app.tasks import example_task

# Initialize DB
Base.metadata.create_all(bind=engine)


app = FastAPI()

# Include API Routers
app.include_router(routes.router, prefix="/api")
logging.info("Routers are set up.")

print(f"{settings.app_hostname}:{settings.react_port}")

# Setup Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.app_hostname}:{settings.react_port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# celery_app = celery_init_app(app)


@app.post("/trigger_task")
async def trigger_task(name: str):
    """
    Trigger a Celery task and return its task ID.
    """
    task = example_task.delay(name)
    return {"task_id": task.id}


# logging.info("Celery app is set up.")


# def create_app() -> FastAPI:
#     """ Create FastAPI app"""

#     return app
