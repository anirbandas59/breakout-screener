"""
Task management API endpoints
Endpoints for triggering and monitoring Celery background tasks
V2 implementation preserving V1 task functionality
"""

from datetime import datetime

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ....celery_app import celery_app
from ....core.logging import get_logger
from ....tasks.analysis_tasks import (
    analyze_single_symbol_task,
    generate_breakout_analysis_task,
)
from ....tasks.data_extraction_tasks import fetch_nse_symbols_task
from ....tasks.data_management_tasks import (
    archive_analysis_data_task,
    clear_analysis_data_task,
    suspend_analysis_task,
)

router = APIRouter()
logger = get_logger(__name__)


# Request/Response schemas
class NSESymbolsRequest(BaseModel):
    """Request schema for NSE symbols extraction"""

    group_filter: list[str] | None = Field(
        None,
        description="Optional list of NSE groups to extract (e.g., ['NIFTY_50', 'NIFTY_200'])",
    )


class BreakoutAnalysisRequest(BaseModel):
    """Request schema for breakout analysis"""

    analysis_date: str = Field(
        ..., description="Date for analysis in YYYY-MM-DD format", example="2024-01-15"
    )
    pivot_threshold: float = Field(
        0.5,
        description="Pivot gap threshold percentage for narrow range detection",
        ge=0.1,
        le=5.0,
    )
    group_filter: list[str] | None = Field(
        None, description="Optional list of stock groups to analyze"
    )
    active_only: bool = Field(True, description="Only analyze active stocks")


class SingleSymbolAnalysisRequest(BaseModel):
    """Request schema for single symbol analysis"""

    symbol: str = Field(..., description="Stock symbol to analyze", example="RELIANCE")
    analysis_date: str = Field(
        ..., description="Date for analysis in YYYY-MM-DD format", example="2024-01-15"
    )
    pivot_threshold: float = Field(
        0.5, description="Pivot gap threshold percentage", ge=0.1, le=5.0
    )
    save_to_db: bool = Field(True, description="Save results to database")


class ClearDataRequest(BaseModel):
    """Request schema for clearing analysis data"""

    target_date: str = Field(
        ...,
        description="Date to clear data for in YYYY-MM-DD format",
        example="2024-01-15",
    )
    selective: bool = Field(
        True,
        description="If True, clear only calculated fields; if False, delete entire records",
    )


class ArchiveDataRequest(BaseModel):
    """Request schema for archiving analysis data"""

    archive_before_date: str | None = Field(
        None,
        description="Archive data before this date (YYYY-MM-DD). If None, uses keep_recent_days",
        example="2024-01-01",
    )
    keep_recent_days: int = Field(
        30, description="Number of recent days to keep in active table", ge=1, le=365
    )


class TaskResponse(BaseModel):
    """Response schema for task operations"""

    task_id: str
    task_name: str
    status: str
    message: str
    timestamp: datetime


# API Endpoints


@router.post("/fetch-symbols", response_model=TaskResponse)
async def fetch_nse_symbols(request: NSESymbolsRequest):
    """
    Trigger NSE stock symbols extraction task
    V2 implementation of V1's fetch_script_symbols endpoint

    This endpoint triggers a background task that:
    - Scrapes NSE indices for stock symbols
    - Extracts company names and generates chart links
    - Updates the stocks table with latest data
    """
    try:
        logger.info(
            f"Triggering NSE symbols extraction with filter: {request.group_filter}"
        )

        # Start the Celery task
        task = fetch_nse_symbols_task.delay(request.group_filter)

        response = TaskResponse(
            task_id=task.id,
            task_name="fetch_nse_symbols_task",
            status="PENDING",
            message="NSE symbols extraction task started successfully",
            timestamp=datetime.now(),
        )

        logger.info(f"NSE symbols task started: {task.id}")
        return response

    except Exception as e:
        logger.error(f"Failed to start NSE symbols task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start NSE symbols extraction: {str(e)}",
        ) from e


@router.post("/generate-analysis", response_model=TaskResponse)
async def generate_breakout_analysis(request: BreakoutAnalysisRequest):
    """
    Trigger breakout analysis for all symbols
    V2 implementation of V1's generate_bodata endpoint

    This endpoint triggers a background task that:
    - Fetches historical data for all symbols
    - Calculates CPR, support/resistance levels
    - Performs breakout detection analysis
    - Updates breakout_data_v2 table with results
    """
    try:
        # Validate date format
        try:
            datetime.strptime(request.analysis_date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            ) from e

        logger.info(f"Triggering breakout analysis for {request.analysis_date}")

        # Start the Celery task
        task = generate_breakout_analysis_task.delay(
            analysis_date=request.analysis_date,
            pivot_threshold=request.pivot_threshold,
            group_filter=request.group_filter,
            active_only=request.active_only,
        )

        response = TaskResponse(
            task_id=task.id,
            task_name="generate_breakout_analysis_task",
            status="PENDING",
            message=f"Breakout analysis task started for {request.analysis_date}",
            timestamp=datetime.now(),
        )

        logger.info(f"Breakout analysis task started: {task.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start breakout analysis task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start breakout analysis: {str(e)}",
        ) from e


@router.post("/analyze-symbol", response_model=TaskResponse)
async def analyze_single_symbol(request: SingleSymbolAnalysisRequest):
    """
    Trigger analysis for a single symbol

    This endpoint is useful for:
    - Testing analysis logic on specific symbols
    - Re-analyzing individual stocks
    - Debugging analysis issues
    """
    try:
        # Validate date format
        try:
            datetime.strptime(request.analysis_date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            ) from e

        logger.info(f"Triggering single symbol analysis: {request.symbol}")

        # Start the Celery task
        task = analyze_single_symbol_task.delay(
            symbol=request.symbol.upper(),
            analysis_date=request.analysis_date,
            pivot_threshold=request.pivot_threshold,
            save_to_db=request.save_to_db,
        )

        response = TaskResponse(
            task_id=task.id,
            task_name="analyze_single_symbol_task",
            status="PENDING",
            message=f"Single symbol analysis started for {request.symbol}",
            timestamp=datetime.now(),
        )

        logger.info(f"Single symbol analysis task started: {task.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start single symbol analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start single symbol analysis: {str(e)}",
        ) from e


@router.post("/clear-data", response_model=TaskResponse)
async def clear_analysis_data(request: ClearDataRequest):
    """
    Clear analysis data for a specific date
    V2 implementation of V1's clear_chart endpoint

    This endpoint triggers a task that:
    - Clears calculated analysis fields for the specified date
    - Allows re-running analysis with different parameters
    - Maintains stock symbols and basic data
    """
    try:
        # Validate date format
        try:
            datetime.strptime(request.target_date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            ) from e

        logger.info(f"Triggering data clearing for {request.target_date}")

        # Start the Celery task
        task = clear_analysis_data_task.delay(
            target_date=request.target_date, selective=request.selective
        )

        operation = "selective clearing" if request.selective else "complete deletion"
        response = TaskResponse(
            task_id=task.id,
            task_name="clear_analysis_data_task",
            status="PENDING",
            message=f"Data {operation} task started for {request.target_date}",
            timestamp=datetime.now(),
        )

        logger.info(f"Data clearing task started: {task.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start data clearing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start data clearing: {str(e)}",
        ) from e


@router.post("/archive-data", response_model=TaskResponse)
async def archive_analysis_data(request: ArchiveDataRequest):
    """
    Archive old analysis data to master table
    V2 implementation of V1's clear_complete_data endpoint

    This endpoint triggers a task that:
    - Moves old data from breakout_data_v2 to master_breakout_data_v2
    - Cleans up active table while preserving historical data
    - Maintains data integrity during the archival process
    """
    try:
        # Validate date format if provided
        if request.archive_before_date:
            try:
                datetime.strptime(request.archive_before_date, "%Y-%m-%d")
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD",
                ) from e

        logger.info("Triggering data archival")

        # Start the Celery task
        task = archive_analysis_data_task.delay(
            archive_before_date=request.archive_before_date,
            keep_recent_days=request.keep_recent_days,
        )

        response = TaskResponse(
            task_id=task.id,
            task_name="archive_analysis_data_task",
            status="PENDING",
            message="Data archival task started",
            timestamp=datetime.now(),
        )

        logger.info(f"Data archival task started: {task.id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start data archival task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start data archival: {str(e)}",
        ) from e


@router.post("/suspend", response_model=TaskResponse)
async def suspend_analysis():
    """
    Suspend ongoing analysis operations
    V2 implementation of V1's suspend_action endpoint

    This endpoint:
    - Sets suspension flags in Redis
    - Revokes running analysis tasks
    - Provides emergency stop functionality
    """
    try:
        logger.info("Triggering analysis suspension")

        # Start the suspension task
        task = suspend_analysis_task.delay()

        response = TaskResponse(
            task_id=task.id,
            task_name="suspend_analysis_task",
            status="PENDING",
            message="Analysis suspension task started",
            timestamp=datetime.now(),
        )

        logger.info(f"Analysis suspension task started: {task.id}")
        return response

    except Exception as e:
        logger.error(f"Failed to suspend analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suspend analysis: {str(e)}",
        ) from e


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status and results of a Celery task
    V2 implementation of V1's task_status endpoint

    Args:
        task_id: The Celery task ID

    Returns:
        Task status information and results
    """
    try:
        # Get task result
        task_result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": task_result.status,
            "timestamp": datetime.now(),
        }

        if task_result.state == "PENDING":
            response.update(
                {"message": "Task is waiting to be processed", "current": 0, "total": 1}
            )
        elif task_result.state == "PROGRESS":
            response.update(
                {
                    "message": task_result.info.get("message", "Task in progress"),
                    "current": task_result.info.get("current", 0),
                    "total": task_result.info.get("total", 1),
                }
            )
        elif task_result.state == "SUCCESS":
            # Task completed successfully
            result = task_result.result
            response.update(
                {
                    "message": "Task completed successfully",
                    "result": result,
                    "completed_at": result.get("end_time")
                    if isinstance(result, dict)
                    else None,
                }
            )
        elif task_result.state == "FAILURE":
            # Task failed
            response.update(
                {
                    "message": "Task failed",
                    "error": str(task_result.info),
                    "traceback": task_result.traceback,
                }
            )
        else:
            # Other states (RETRY, REVOKED, etc.)
            response.update(
                {
                    "message": f"Task is in {task_result.state} state",
                    "info": str(task_result.info) if task_result.info else None,
                }
            )

        logger.debug(f"Task status retrieved: {task_id} - {task_result.state}")
        return response

    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        ) from e
