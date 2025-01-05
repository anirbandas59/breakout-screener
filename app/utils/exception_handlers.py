import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


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
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Validation error during request {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": exc.errors(),
        },
    )
