""" Application Routes """

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from sqlalchemy.orm import Session

from app.db.session import get_db
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
    TaskStatusResponse,
    TaskResultResponse,
    FetchScriptSymbolsRequest,
    ClearChartRequest,
)

from app.celery import celery_app

# =============================

router = APIRouter()


@router.get("/get_data", status_code=200, response_model=GetDataResponse)
def get_data(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    breakout_filters: Optional[List[str]] = Query(None)
):
    """
    Fetch processed breakout data with optional search and filters.

    Args:
        page (int): Page number for pagination.
        limit (int): Number of records per page.
        search (str, optional): Search term for filtering by script name.
        breakout_filters (List[str], optional): List of breakout indicator values to filter by.
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response with breakout data.
    """
    try:
        logging.info("Fetching processed breakout data...")
        result = get_breakout_data(db, page, limit, search, breakout_filters)

        # total, data = result["total"], result["data"]

        response = {
            "total": result["total"],
            "data": result["data"],
            "page": page,
            "limit": limit,
        }

        logging.info("Fetched processed breakout data successfully.")
        return response
    except Exception as e:
        logging.error("Error fetching processed breakout data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        logging.error("Error fetching Celery task: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


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

    # Validate the date format
    analysis_date_val = (
        request.date if not validate_date(request.date) else get_current_date()
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
        logging.error("Error during BO Data generation: %s", str(e))
        # Raise an HTTPException if the analysis fails
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        logging.error(
            "Error initiating task to clear complete data: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"An error occurred while initiating the task: {str(e)}"
        ) from e


@router.post("/suspend_action")
def api_suspend_action():
    """API to suspend the ongoing analysis."""
    try:
        logging.info("Suspending analysis...")
        suspend_action()
        return {"status": "SUCCESS", "message": "Analysis suspension triggered successfully"}
    except RuntimeError as e:
        logging.error("Error suspending analysis: %s", str(e))
        return {"status": "FAIL", "message": "Failed to suspend analysis", "error": str(e)}


@router.get("/simulate_error")
def simulate_error():
    """
    Simulate an error
    """
    raise Exception("Simulated error")


@router.get("/task_status/{task_id}", response_model=TaskResultResponse)
async def task_status(task_id: str):
    """
    Monitor the status of a Celery task.
    """

    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result,  # Actual result from the task
        }

        return JSONResponse(response)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving task status {str(e)}"
        ) from e


@router.get("/current_task", response_model=TaskResultResponse)
async def get_current_task():
    """
    Get the currently running task (if any).

    This endpoint checks for active Celery tasks and returns the most recent
    one that is still in PENDING or PROGRESS state. This allows the frontend
    to resume monitoring after a page refresh.

    Returns:
        TaskResultResponse with task_id, status, and result (or None if no active task)
    """
    try:
        # Get all active tasks from Celery
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()

        if not active_tasks:
            return JSONResponse({
                "task_id": None,
                "status": "NO_ACTIVE_TASK",
                "result": None
            })

        # Get the first active task from any worker
        for worker, tasks in active_tasks.items():
            if tasks:
                task_info = tasks[0]  # Get the first active task
                task_id = task_info['id']

                # Get detailed task status
                task_result = AsyncResult(task_id, app=celery_app)

                response = {
                    "task_id": task_id,
                    "status": task_result.status,
                    "result": task_result.result,
                }

                logging.info(f"Found active task: {task_id} with status {task_result.status}")
                return JSONResponse(response)

        # No active tasks found
        return JSONResponse({
            "task_id": None,
            "status": "NO_ACTIVE_TASK",
            "result": None
        })

    except Exception as e:
        logging.error(f"Error retrieving current task: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving current task {str(e)}"
        ) from e
