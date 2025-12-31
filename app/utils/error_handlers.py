"""
Centralized error handling utilities.

This module provides custom exception classes and error handling utilities
for consistent error reporting across the application.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


# ===========================
# Custom Exception Classes
# ===========================

class DataFetchError(Exception):
    """
    Raised when data fetching from external sources fails.

    This includes failures from:
    - yfinance API (network issues, invalid symbols)
    - NSE website scraping (timeouts, structure changes)
    - Any other external data source
    """

    def __init__(self, message: str, script_name: Optional[str] = None, source: Optional[str] = None):
        self.script_name = script_name
        self.source = source
        super().__init__(message)


class CPRCalculationError(Exception):
    """
    Raised when CPR calculation fails due to invalid data.

    This occurs when:
    - OHLC values are missing or invalid
    - Mathematical operations fail (division by zero, etc.)
    - Data types are incorrect
    """

    def __init__(self, message: str, script_name: Optional[str] = None, values: Optional[Dict[str, Any]] = None):
        self.script_name = script_name
        self.values = values
        super().__init__(message)


class DatabaseError(Exception):
    """
    Raised when database operations fail.

    This includes:
    - Connection failures
    - Query execution errors
    - Commit/rollback failures
    - Constraint violations
    """

    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        self.operation = operation
        self.table = table
        super().__init__(message)


class TaskExecutionError(Exception):
    """
    Raised when Celery task execution fails.

    This includes:
    - Task timeout errors
    - Worker crashes
    - Invalid task arguments
    - Task suspension/cancellation
    """

    def __init__(self, message: str, task_id: Optional[str] = None, task_name: Optional[str] = None):
        self.task_id = task_id
        self.task_name = task_name
        super().__init__(message)


# ===========================
# Error Handlers
# ===========================

def handle_service_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Convert service errors to HTTP exceptions with logging.

    Args:
        error: The caught exception
        context: Optional dict with request details (script_name, date, operation)

    Returns:
        HTTPException with appropriate status code and message

    Example:
        try:
            data = fetch_data(script_name)
        except Exception as e:
            raise handle_service_error(e, {"script_name": script_name, "operation": "fetch_data"})
    """
    context = context or {}
    logger.error(f"Service error: {error}", extra=context, exc_info=True)

    if isinstance(error, DataFetchError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch data: {str(error)}"
        )
    elif isinstance(error, CPRCalculationError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to calculate CPR: {str(error)}"
        )
    elif isinstance(error, DatabaseError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(error)}"
        )
    elif isinstance(error, TaskExecutionError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(error)}"
        )


def log_error_with_context(
    error: Exception,
    script_name: Optional[str] = None,
    date: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log error with contextual information for debugging.

    Args:
        error: The exception to log
        script_name: Stock script name being processed
        date: Date of analysis
        operation: Operation being performed
        **kwargs: Additional context fields

    Example:
        log_error_with_context(
            error=e,
            script_name="RELIANCE",
            date="2025-12-31",
            operation="calculate_indicators",
            pivot_val=0.5
        )
    """
    context = {
        "script_name": script_name,
        "date": date,
        "operation": operation,
        **kwargs
    }
    # Remove None values
    context = {k: v for k, v in context.items() if v is not None}

    logger.error(
        f"Error in {operation or 'unknown operation'}: {str(error)}",
        extra=context,
        exc_info=True
    )
