""" Application Routes """

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db, get_pool_stats
from app.services import get_breakout_data
from app.tasks import (
    fetch_script_symbols_task,
    generate_bo_data_task,
    clear_chart_data_task,
    clear_complete_data_task,
)
from app.utils import get_current_date, suspend_action, validate_date
from app.models import GenerateBODataRequest
from app.models.schemas import (
    GetDataResponse,
    GetDataQueryParams,
    TaskStatusResponse,
    TaskResultResponse,
    FetchScriptSymbolsRequest,
    ClearChartRequest,
    HealthResponse,
    SuspendResponse,
)
from app.utils.error_handlers import handle_service_error
from app.dependencies import get_celery_dispatcher, CeleryTaskDispatcher

# =============================

router = APIRouter()


@router.get("/health", status_code=200, response_model=HealthResponse)
def health_check():
    """
    Health check endpoint with database connection pool statistics.

    Returns:
        dict: Health status and connection pool metrics
    """
    try:
        pool_stats = get_pool_stats()

        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "pool_stats": pool_stats
            }
        }
    except Exception as e:
        logging.error("Health check failed: %s", str(e))
        return {
            "status": "unhealthy",
            "database": {
                "connected": False,
                "error": str(e)
            }
        }


@router.get("/get_data", status_code=200, response_model=GetDataResponse)
def get_data(
    page: int = Query(1, ge=1, description="Page number (minimum 1)"),
    limit: int = Query(10, ge=1, le=100, description="Records per page (max 100)"),
    search: Optional[str] = Query(None, max_length=100, description="Search term for script name"),
    breakout_filters: Optional[List[str]] = Query(None, description="Breakout indicator filter values"),
    date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date filter in YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Fetch processed breakout data with optional search, filters, and date.
    
    Returns:
        JSON response with breakout data, including data_date and data_source.
    """
    try:
        logging.info("Fetching processed breakout data...")
        logging.debug("Breakout filters received: %s", breakout_filters)
        
        result = get_breakout_data(
            db,
            page,
            limit,
            search,
            breakout_filters,
            date
        )

        response = {
            "total": result["total"],
            "data": result["data"],
            "page": page,
            "limit": limit,
            "data_date": result.get("data_date"),
            "data_source": result.get("data_source"),
        }

        logging.info("Fetched processed breakout data successfully. Date: %s, Source: %s",
                     result.get("data_date"), result.get("data_source"))
        return response
    except Exception as e:
        raise handle_service_error(e, {"operation": "get_data"}) from e


@router.post("/fetch_script_symbols", status_code=200, response_model=TaskStatusResponse)
def fetch_scripts():
    """
    Fetch script symbols from NSE and save to database.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response indicating success or failure.
    """
    try:
        logging.info("Triggering Celery task to fetch script symbols...")
        task = fetch_script_symbols_task.apply_async()

        logging.info("Celery task triggered. Task ID: %s", task.id)
        return {
            "task_id": task.id,
            "message": "Fetching Task triggered successfully",
        }

    except Exception as e:
        raise handle_service_error(e, {"operation": "fetch_script_symbols"}) from e


@router.post("/generate_bodata", status_code=200, response_model=TaskStatusResponse)
def generate_bodata(request: GenerateBODataRequest):
    """
    Generate breakout data for all scripts in the breakout_data table.

    Args:
        request (GenerateBODataRequest): Request object containing
            the date and pivot value for the analysis.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Status of the analysis.
    """
    # Fetch the pivot value from the request
    pivot_val = request.pivot_val
    start_from = request.start_from

    # Validate the date format - use request.date if valid, otherwise fallback to current date
    analysis_date_val = (
        request.date if validate_date(request.date) else get_current_date()
    )

    try:
        logging.info(
            "Starting BO Data generation for date: %s with pivot value: %s, start_from: %s",
            analysis_date_val,
            pivot_val,
            start_from,
        )
        # Call the function to generate the BO Data
        task = generate_bo_data_task.apply_async(
            args=[analysis_date_val, pivot_val, start_from])

        return {
            "task_id": task.id,
            "message": "BO Data generation task started"
        }

    except Exception as e:
        raise handle_service_error(e, {"operation": "generate_bodata"}) from e


@router.post("/clear_chart", status_code=202, response_model=TaskStatusResponse)
def clear_chart():
    """
    Clear chart data for a specific date

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response indicating success or failure.
    """
    today_date = get_current_date()

    logging.info("Clearing BO Data for date: %s", today_date)
    task = clear_chart_data_task.apply_async(args=[today_date])

    return {
        "task_id": task.id,
        "message": f"Chart data for '{today_date}' clear task initiated"
    }


@router.post("/clear_complete_data", status_code=202, response_model=TaskStatusResponse)
def clear_complete_data():
    """
    Initiates a task to clear all data from breakout_data and push to master_table.

    Returns:
        JSON response with the task ID and status.
    """
    try:
        logging.info(
            "Initiating task to clear complete data from breakout_data.")

        # Start the Celery task and pass the task ID back to the client
        task = clear_complete_data_task.apply_async()

        return {
            "task_id": task.id,
            "message": "Clear complete data task initiated."
        }

    except Exception as e:
        raise handle_service_error(e, {"operation": "clear_complete_data"}) from e


@router.post("/suspend_action", response_model=SuspendResponse)
def api_suspend_action():
    """API to suspend the ongoing analysis."""
    try:
        logging.info("Suspending analysis...")
        suspend_action()
        return {"status": "SUCCESS", "message": "Analysis suspension triggered successfully"}
    except RuntimeError as e:
        logging.error("Error suspending analysis: %s", str(e))
        return {"status": "FAIL", "message": "Failed to suspend analysis", "error": str(e)}


# SECURITY FIX: Debug endpoint removed
# This endpoint exposed error handling in production
# If debugging is needed, use proper logging and monitoring tools


@router.get("/task_status/{task_id}", response_model=TaskResultResponse)
async def task_status(
    task_id: str,
    dispatcher: CeleryTaskDispatcher = Depends(get_celery_dispatcher),
):
    """
    Monitor the status of a Celery task.
    """
    try:
        task_result = dispatcher.get_task_result(task_id)

        # Safely extract result — Celery may store exception objects that aren't JSON-serializable
        try:
            result_data = task_result.result
            if isinstance(result_data, Exception):
                result_data = str(result_data)
        except Exception:
            result_data = None

        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": result_data,
        }
    except Exception as e:
        raise handle_service_error(e, {"operation": "task_status", "task_id": task_id}) from e


@router.get("/current_task", response_model=TaskResultResponse)
async def get_current_task(
    dispatcher: CeleryTaskDispatcher = Depends(get_celery_dispatcher),
):
    """
    Get the currently running task (if any).

    This endpoint checks for active Celery tasks and returns the most recent
    one that is still in PENDING or PROGRESS state. This allows the frontend
    to resume monitoring after a page refresh.

    Returns:
        TaskResultResponse with task_id, status, and result (or None if no active task)
    """
    try:
        active_tasks = dispatcher.inspect_active()

        if not active_tasks:
            return {
                "task_id": None,
                "status": "NO_ACTIVE_TASK",
                "result": None,
            }

        # Get the first active task from any worker
        for worker, tasks in active_tasks.items():
            if tasks:
                task_info = tasks[0]  # Get the first active task
                task_id = task_info['id']

                task_result = dispatcher.get_task_result(task_id)

                # Safely extract result — may contain non-serializable exception objects
                try:
                    result_data = task_result.result
                    if isinstance(result_data, Exception):
                        result_data = str(result_data)
                except Exception:
                    result_data = None

                logging.info("Found active task: %s with status %s", task_id, task_result.status)
                return {
                    "task_id": task_id,
                    "status": task_result.status,
                    "result": result_data,
                }

        # No active tasks found
        return {
            "task_id": None,
            "status": "NO_ACTIVE_TASK",
            "result": None,
        }

    except Exception as e:
        raise handle_service_error(e, {"operation": "get_current_task"}) from e
