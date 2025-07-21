"""
BreakoutData API endpoints
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.logging import get_logger
from ....repositories.breakout_data import BreakoutDataRepository
from ....schemas.base import PaginationParams, SortParams, SuccessResponse
from ....schemas.breakout_data import (
    BreakoutDataCreate,
    BreakoutDataFilter,
    BreakoutDataList,
    BreakoutDataResponse,
    BreakoutDataSummary,
    BreakoutDataUpdate,
    DailyBreakoutSummary,
)

router = APIRouter()
logger = get_logger(__name__)


async def get_breakout_data_repository(
    db: AsyncSession = Depends(get_db),
) -> BreakoutDataRepository:
    """Dependency to get BreakoutData repository"""
    return BreakoutDataRepository(db)


@router.get(
    "/", response_model=BreakoutDataList, summary="List breakout data with filtering"
)
async def list_breakout_data(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("trade_date", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    symbol: str | None = Query(None, description="Filter by stock symbol"),
    trade_date_from: date | None = Query(None, description="Trade date from"),
    trade_date_to: date | None = Query(None, description="Trade date to"),
    breakout_status: str | None = Query(None, description="Filter by breakout status"),
    is_analyzed: bool | None = Query(None, description="Filter by analysis status"),
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Retrieve a paginated list of breakout data with optional filtering.

    - **page**: Page number (1-based)
    - **limit**: Number of items per page (max 1000)
    - **sort_by**: Field to sort by (trade_date, symbol, breakout_status, etc.)
    - **sort_order**: Sort direction (asc or desc)
    - **symbol**: Filter by stock symbol
    - **trade_date_from**: Filter by trade date from (inclusive)
    - **trade_date_to**: Filter by trade date to (inclusive)
    - **breakout_status**: Filter by breakout status
    - **is_analyzed**: Filter by analysis completion status
    """
    try:
        # Create pagination and sorting parameters
        pagination = PaginationParams(page=page, limit=limit)
        sort = SortParams(sort_by=sort_by, sort_order=sort_order)

        # Create filter parameters
        filters = BreakoutDataFilter(
            symbol=symbol,
            trade_date_from=trade_date_from,
            trade_date_to=trade_date_to,
            breakout_status=breakout_status,
            is_analyzed=is_analyzed,
        )

        # Get filtered breakout data
        breakout_data = await repository.get_by_advanced_filter(
            filters=filters,
            pagination=pagination,
            sort=sort,
            load_relationships=["stock"],
        )

        # Get total count for pagination metadata
        total_count = len(breakout_data)  # This would need a proper count method

        # Create response with stock information
        items = []
        for data in breakout_data:
            response_data = BreakoutDataResponse.model_validate(data)
            if data.stock:
                response_data.stock_symbol = data.stock.symbol
                response_data.stock_company_name = data.stock.company_name
            items.append(response_data)

        return BreakoutDataList.create(
            items=items,
            total=total_count,
            pagination=pagination,
        )

    except Exception as e:
        logger.error("Failed to list breakout data", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve breakout data: {str(e)}",
        ) from e


@router.get(
    "/{breakout_data_id}",
    response_model=BreakoutDataResponse,
    summary="Get breakout data by ID",
)
async def get_breakout_data(
    breakout_data_id: UUID,
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Retrieve specific breakout data by its ID.

    - **breakout_data_id**: UUID of the breakout data to retrieve
    """
    try:
        breakout_data = await repository.get_by_id(
            breakout_data_id, load_relationships=["stock"]
        )
        if not breakout_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breakout data with ID {breakout_data_id} not found",
            )

        response_data = BreakoutDataResponse.model_validate(breakout_data)
        if breakout_data.stock:
            response_data.stock_symbol = breakout_data.stock.symbol
            response_data.stock_company_name = breakout_data.stock.company_name

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get breakout data",
            breakout_data_id=breakout_data_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve breakout data: {str(e)}",
        ) from e


@router.get(
    "/symbol/{symbol}/date/{trade_date}",
    response_model=BreakoutDataResponse,
    summary="Get breakout data by symbol and date",
)
async def get_breakout_data_by_symbol_and_date(
    symbol: str,
    trade_date: date,
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Retrieve breakout data by stock symbol and trade date.

    - **symbol**: Stock symbol (e.g., RELIANCE, TCS)
    - **trade_date**: Trading date (YYYY-MM-DD)
    """
    try:
        breakout_data = await repository.get_by_symbol_and_date(
            symbol, trade_date, load_relationships=["stock"]
        )
        if not breakout_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breakout data for '{symbol}' on {trade_date} not found",
            )

        response_data = BreakoutDataResponse.model_validate(breakout_data)
        if breakout_data.stock:
            response_data.stock_symbol = breakout_data.stock.symbol
            response_data.stock_company_name = breakout_data.stock.company_name

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get breakout data by symbol and date",
            symbol=symbol,
            trade_date=trade_date,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve breakout data: {str(e)}",
        ) from e


@router.post(
    "/",
    response_model=BreakoutDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new breakout data",
)
async def create_breakout_data(
    breakout_data: BreakoutDataCreate,
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Create new breakout data.

    - **stock_id**: UUID of the stock
    - **trade_date**: Trading date
    - **open_price**, **high_price**, **low_price**, **close_price**: OHLC prices
    - **volume**: Trading volume
    - **pivot**, **bc**, **tc**: CPR calculations
    - **candle_indicator**, **volume_indicator**: Technical indicators
    - **breakout_status**: Breakout analysis result
    """
    try:
        # Validate OHLC constraints
        breakout_data.validate_ohlc_constraints()

        # Check if data already exists for this stock and date
        existing_data = await repository.get_by_symbol_and_date(
            # This would need the symbol from stock_id - simplified for now
            "CHECK",
            breakout_data.trade_date,
        )
        if existing_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Breakout data already exists for this stock on {breakout_data.trade_date}",
            )

        # Create the breakout data
        created_data = await repository.create(breakout_data.model_dump())

        logger.info(
            "Breakout data created successfully", trade_date=breakout_data.trade_date
        )
        return BreakoutDataResponse.model_validate(created_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create breakout data",
            trade_date=breakout_data.trade_date,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create breakout data: {str(e)}",
        ) from e


@router.put(
    "/{breakout_data_id}",
    response_model=BreakoutDataResponse,
    summary="Update breakout data",
)
async def update_breakout_data(
    breakout_data_id: UUID,
    breakout_data: BreakoutDataUpdate,
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Update existing breakout data.

    - **breakout_data_id**: UUID of the breakout data to update
    - Provide only the fields you want to update
    """
    try:
        # Check if breakout data exists
        existing_data = await repository.get_by_id(breakout_data_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breakout data with ID {breakout_data_id} not found",
            )

        # Update the breakout data
        update_data = breakout_data.model_dump(exclude_unset=True)
        updated_data = await repository.update(breakout_data_id, update_data)

        logger.info(
            "Breakout data updated successfully", breakout_data_id=breakout_data_id
        )
        return BreakoutDataResponse.model_validate(updated_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update breakout data",
            breakout_data_id=breakout_data_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update breakout data: {str(e)}",
        ) from e


@router.delete(
    "/{breakout_data_id}",
    response_model=SuccessResponse,
    summary="Delete breakout data",
)
async def delete_breakout_data(
    breakout_data_id: UUID,
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Delete breakout data.

    - **breakout_data_id**: UUID of the breakout data to delete
    """
    try:
        # Check if breakout data exists
        existing_data = await repository.get_by_id(breakout_data_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Breakout data with ID {breakout_data_id} not found",
            )

        # Delete the breakout data
        await repository.delete(breakout_data_id)

        logger.info(
            "Breakout data deleted successfully", breakout_data_id=breakout_data_id
        )
        return SuccessResponse(
            message=f"Breakout data for {existing_data.trade_date} deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete breakout data",
            breakout_data_id=breakout_data_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete breakout data: {str(e)}",
        ) from e


@router.get(
    "/summary/", response_model=BreakoutDataSummary, summary="Get breakout data summary"
)
async def get_breakout_data_summary(
    from_date: date | None = Query(None, description="Summary from date"),
    to_date: date | None = Query(None, description="Summary to date"),
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Get summary statistics for breakout data.

    - **from_date**: Optional start date for summary
    - **to_date**: Optional end date for summary

    Returns counts by status, date range, and analysis statistics.
    """
    try:
        # Get breakout counts by status
        breakout_counts = await repository.get_breakout_counts_by_status(
            from_date, to_date
        )

        # Calculate summary statistics
        total_records = sum(breakout_counts.values())
        breakout_percentage = 0.0
        if total_records > 0:
            no_breakout_count = breakout_counts.get("NO_BREAKOUT", 0)
            breakout_percentage = (
                (total_records - no_breakout_count) / total_records
            ) * 100

        summary = BreakoutDataSummary(
            total_records=total_records,
            analyzed_records=0,  # This would need additional query
            unanalyzed_records=0,  # This would need additional query
            breakout_counts=breakout_counts,
            breakout_percentage=breakout_percentage,
            earliest_date=from_date,
            latest_date=to_date,
            avg_price=None,  # This would need additional query
            min_price=None,  # This would need additional query
            max_price=None,  # This would need additional query
            avg_volume=None,  # This would need additional query
            total_volume=None,  # This would need additional query
            analysis_success_rate=100.0,  # Placeholder
        )

        return summary

    except Exception as e:
        logger.error("Failed to get breakout data summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get breakout data summary: {str(e)}",
        ) from e


@router.get(
    "/summary/daily/",
    response_model=list[DailyBreakoutSummary],
    summary="Get daily breakout summaries",
)
async def get_daily_breakout_summaries(
    from_date: date = Query(..., description="Start date for daily summaries"),
    to_date: date = Query(..., description="End date for daily summaries"),
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Get daily breakout summaries for a date range.

    - **from_date**: Start date for summaries
    - **to_date**: End date for summaries

    Returns daily statistics including counts, percentages, and averages.
    """
    try:
        daily_summaries = await repository.get_daily_breakout_summary(
            from_date, to_date
        )

        # Convert to response format
        response_summaries = []
        for summary in daily_summaries:
            daily_summary = DailyBreakoutSummary(
                trade_date=summary["trade_date"],
                total_records=summary["total_records"],
                breakout_count=summary["breakout_count"],
                analyzed_count=summary["analyzed_count"],
                breakout_percentage=summary["breakout_percentage"],
                analysis_percentage=summary["analysis_percentage"],
                avg_volume=summary["avg_volume"],
                avg_price=summary["avg_price"],
                avg_breakout_strength=None,  # Would need to be calculated
                candle_indicators={},  # Would need additional query
                volume_indicators={},  # Would need additional query
            )
            response_summaries.append(daily_summary)

        return response_summaries

    except Exception as e:
        logger.error("Failed to get daily breakout summaries", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily breakout summaries: {str(e)}",
        ) from e


@router.get(
    "/unanalyzed/",
    response_model=BreakoutDataList,
    summary="Get unanalyzed breakout data",
)
async def get_unanalyzed_breakout_data(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    from_date: date | None = Query(None, description="From date"),
    to_date: date | None = Query(None, description="To date"),
    repository: BreakoutDataRepository = Depends(get_breakout_data_repository),
):
    """
    Get unanalyzed breakout data for processing.

    - **page**: Page number (1-based)
    - **limit**: Number of items per page (max 1000)
    - **from_date**: Optional start date
    - **to_date**: Optional end date
    """
    try:
        pagination = PaginationParams(page=page, limit=limit)

        unanalyzed_data = await repository.get_unanalyzed_data(
            from_date=from_date,
            to_date=to_date,
            pagination=pagination,
        )

        # Create response
        items = [BreakoutDataResponse.model_validate(data) for data in unanalyzed_data]

        return BreakoutDataList.create(
            items=items,
            total=len(items),  # This would need a proper count method
            pagination=pagination,
        )

    except Exception as e:
        logger.error("Failed to get unanalyzed breakout data", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unanalyzed breakout data: {str(e)}",
        ) from e
