"""
Analysis API endpoints (AnalysisSession and PerformanceMetrics)
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.logging import get_logger
from ....repositories.analysis import AnalysisSessionRepository, PerformanceMetricsRepository
from ....schemas.base import ListResponse, PaginationParams, SortParams, SuccessResponse
from ....schemas.analysis import (
    AnalysisSessionCreate,
    AnalysisSessionFilter,
    AnalysisSessionList,
    AnalysisSessionResponse,
    AnalysisSessionSummary,
    AnalysisSessionUpdate,
    PerformanceMetricsCreate,
    PerformanceMetricsFilter,
    PerformanceMetricsList,
    PerformanceMetricsResponse,
    PerformanceMetricsSummary,
    PerformanceMetricsUpdate,
)

router = APIRouter()
logger = get_logger(__name__)


async def get_analysis_session_repository(
    db: AsyncSession = Depends(get_db)
) -> AnalysisSessionRepository:
    """Dependency to get AnalysisSession repository"""
    return AnalysisSessionRepository(db)


async def get_performance_metrics_repository(
    db: AsyncSession = Depends(get_db)
) -> PerformanceMetricsRepository:
    """Dependency to get PerformanceMetrics repository"""
    return PerformanceMetricsRepository(db)


# Analysis Session Endpoints

@router.get("/sessions/", response_model=AnalysisSessionList, summary="List analysis sessions")
async def list_analysis_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("analysis_date", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session_name: Optional[str] = Query(None, description="Filter by session name"),
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Retrieve a paginated list of analysis sessions.
    
    - **page**: Page number (1-based)
    - **limit**: Number of items per page (max 1000)
    - **sort_by**: Field to sort by
    - **sort_order**: Sort direction (asc or desc)
    - **status**: Filter by session status
    - **session_name**: Filter by session name (partial match)
    """
    try:
        pagination = PaginationParams(page=page, limit=limit)
        sort = SortParams(sort_by=sort_by, sort_order=sort_order)
        
        filters = AnalysisSessionFilter(
            status=status,
            session_name=session_name,
        )
        
        sessions = await repository.get_by_advanced_filter(
            filters=filters,
            pagination=pagination,
            sort=sort,
            load_relationships=["performance_metrics"],
        )
        
        # Create response with computed fields
        items = []
        for session in sessions:
            response_data = AnalysisSessionResponse.model_validate(session)
            response_data.is_running = session.status.value == "IN_PROGRESS"
            response_data.is_completed = session.status.value == "COMPLETED"
            response_data.has_errors = session.error_count > 0 if session.error_count else False
            response_data.metrics_count = len(session.performance_metrics) if session.performance_metrics else 0
            
            # Calculate success rate
            if session.total_items and session.total_items > 0:
                success_count = session.success_count or 0
                response_data.success_rate = (success_count / session.total_items) * 100
            
            items.append(response_data)
        
        return AnalysisSessionList.create(
            items=items,
            total=len(items),  # This would need a proper count method
            pagination=pagination,
        )
        
    except Exception as e:
        logger.error("Failed to list analysis sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=AnalysisSessionResponse, 
           summary="Get analysis session by ID")
async def get_analysis_session(
    session_id: UUID,
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Retrieve a specific analysis session by its ID.
    
    - **session_id**: UUID of the analysis session to retrieve
    """
    try:
        session = await repository.get_by_id(
            session_id,
            load_relationships=["performance_metrics"]
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis session with ID {session_id} not found"
            )
        
        response_data = AnalysisSessionResponse.model_validate(session)
        response_data.is_running = session.status.value == "IN_PROGRESS"
        response_data.is_completed = session.status.value == "COMPLETED"
        response_data.has_errors = session.error_count > 0 if session.error_count else False
        response_data.metrics_count = len(session.performance_metrics) if session.performance_metrics else 0
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get analysis session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis session: {str(e)}"
        )


@router.get("/sessions/name/{session_name}", response_model=AnalysisSessionResponse,
           summary="Get analysis session by name")
async def get_analysis_session_by_name(
    session_name: str,
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Retrieve an analysis session by its name.
    
    - **session_name**: Name of the analysis session
    """
    try:
        session = await repository.get_by_session_name(
            session_name,
            load_relationships=["performance_metrics"]
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis session with name '{session_name}' not found"
            )
        
        response_data = AnalysisSessionResponse.model_validate(session)
        response_data.is_running = session.status.value == "IN_PROGRESS"
        response_data.is_completed = session.status.value == "COMPLETED"
        response_data.has_errors = session.error_count > 0 if session.error_count else False
        response_data.metrics_count = len(session.performance_metrics) if session.performance_metrics else 0
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get analysis session by name", session_name=session_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis session: {str(e)}"
        )


@router.post("/sessions/", response_model=AnalysisSessionResponse, 
            status_code=status.HTTP_201_CREATED, summary="Create analysis session")
async def create_analysis_session(
    session_data: AnalysisSessionCreate,
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Create a new analysis session.
    
    - **session_name**: Unique session name
    - **analysis_date**: Date of the analysis
    - **status**: Initial status (defaults to PENDING)
    - **description**: Optional description
    - **analysis_parameters**: Optional configuration parameters
    """
    try:
        # Check if session with name already exists
        existing_session = await repository.get_by_session_name(session_data.session_name)
        if existing_session:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Analysis session with name '{session_data.session_name}' already exists"
            )
        
        created_session = await repository.create(session_data.model_dump())
        
        logger.info("Analysis session created", session_name=session_data.session_name)
        return AnalysisSessionResponse.model_validate(created_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create analysis session", session_name=session_data.session_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis session: {str(e)}"
        )


@router.put("/sessions/{session_id}", response_model=AnalysisSessionResponse, 
           summary="Update analysis session")
async def update_analysis_session(
    session_id: UUID,
    session_data: AnalysisSessionUpdate,
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Update an existing analysis session.
    
    - **session_id**: UUID of the session to update
    - Provide only the fields you want to update
    """
    try:
        existing_session = await repository.get_by_id(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis session with ID {session_id} not found"
            )
        
        update_data = session_data.model_dump(exclude_unset=True)
        updated_session = await repository.update(session_id, update_data)
        
        logger.info("Analysis session updated", session_id=session_id)
        return AnalysisSessionResponse.model_validate(updated_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update analysis session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update analysis session: {str(e)}"
        )


@router.delete("/sessions/{session_id}", response_model=SuccessResponse, 
              summary="Delete analysis session")
async def delete_analysis_session(
    session_id: UUID,
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Delete an analysis session.
    
    - **session_id**: UUID of the session to delete
    
    Note: This will also delete all related performance metrics.
    """
    try:
        existing_session = await repository.get_by_id(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis session with ID {session_id} not found"
            )
        
        await repository.delete(session_id)
        
        logger.info("Analysis session deleted", session_id=session_id, session_name=existing_session.session_name)
        return SuccessResponse(
            message=f"Analysis session '{existing_session.session_name}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete analysis session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis session: {str(e)}"
        )


# Performance Metrics Endpoints

@router.get("/metrics/", response_model=PerformanceMetricsList, summary="List performance metrics")
async def list_performance_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("metric_date", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    session_id: Optional[UUID] = Query(None, description="Filter by session ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    repository: PerformanceMetricsRepository = Depends(get_performance_metrics_repository),
):
    """
    Retrieve a paginated list of performance metrics.
    
    - **page**: Page number (1-based)
    - **limit**: Number of items per page (max 1000)
    - **session_id**: Filter by analysis session ID
    - **metric_type**: Filter by performance metric type
    """
    try:
        pagination = PaginationParams(page=page, limit=limit)
        sort = SortParams(sort_by=sort_by, sort_order=sort_order)
        
        filters = PerformanceMetricsFilter(
            session_id=session_id,
            metric_type=metric_type,
        )
        
        metrics = await repository.get_by_advanced_filter(
            filters=filters,
            pagination=pagination,
            sort=sort,
            load_relationships=["session"],
        )
        
        # Create response with session information
        items = []
        for metric in metrics:
            response_data = PerformanceMetricsResponse.model_validate(metric)
            if metric.session:
                response_data.session_name = metric.session.session_name
                response_data.session_status = metric.session.status.value
            items.append(response_data)
        
        return PerformanceMetricsList.create(
            items=items,
            total=len(items),  # This would need a proper count method
            pagination=pagination,
        )
        
    except Exception as e:
        logger.error("Failed to list performance metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@router.post("/metrics/", response_model=PerformanceMetricsResponse,
            status_code=status.HTTP_201_CREATED, summary="Create performance metric")
async def create_performance_metric(
    metric_data: PerformanceMetricsCreate,
    repository: PerformanceMetricsRepository = Depends(get_performance_metrics_repository),
):
    """
    Create a new performance metric.
    
    - **session_id**: UUID of the analysis session
    - **metric_type**: Type of performance metric
    - **metric_date**: Date of the metric
    - **metric_value**: Numeric value of the metric
    - **metric_unit**: Optional unit of measurement
    - **metric_description**: Optional description
    """
    try:
        created_metric = await repository.create(metric_data.model_dump())
        
        logger.info("Performance metric created", metric_type=metric_data.metric_type)
        return PerformanceMetricsResponse.model_validate(created_metric)
        
    except Exception as e:
        logger.error("Failed to create performance metric", metric_type=metric_data.metric_type, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create performance metric: {str(e)}"
        )


@router.get("/sessions/{session_id}/summary/", response_model=AnalysisSessionSummary,
           summary="Get analysis session summary")
async def get_analysis_session_summary(
    from_date: Optional[date] = Query(None, description="Summary from date"),
    to_date: Optional[date] = Query(None, description="Summary to date"),
    repository: AnalysisSessionRepository = Depends(get_analysis_session_repository),
):
    """
    Get summary statistics for analysis sessions.
    
    - **from_date**: Optional start date for summary
    - **to_date**: Optional end date for summary
    """
    try:
        summary = await repository.get_session_summary(from_date, to_date)
        return AnalysisSessionSummary(**summary)
        
    except Exception as e:
        logger.error("Failed to get analysis session summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis session summary: {str(e)}"
        )


@router.get("/metrics/summary/", response_model=PerformanceMetricsSummary,
           summary="Get performance metrics summary")
async def get_performance_metrics_summary(
    session_id: Optional[UUID] = Query(None, description="Filter by session ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    from_date: Optional[date] = Query(None, description="Summary from date"),
    to_date: Optional[date] = Query(None, description="Summary to date"),
    repository: PerformanceMetricsRepository = Depends(get_performance_metrics_repository),
):
    """
    Get summary statistics for performance metrics.
    
    - **session_id**: Optional session filter
    - **metric_type**: Optional metric type filter
    - **from_date**: Optional start date
    - **to_date**: Optional end date
    """
    try:
        summary = await repository.get_metrics_summary(
            session_id=session_id,
            metric_type=metric_type,
            from_date=from_date,
            to_date=to_date,
        )
        return PerformanceMetricsSummary(**summary)
        
    except Exception as e:
        logger.error("Failed to get performance metrics summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics summary: {str(e)}"
        )