"""
Stock API endpoints
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.logging import get_logger
from ....repositories.stock import StockRepository
from ....schemas.base import ListResponse, PaginationParams, SortParams, SuccessResponse
from ....schemas.stock import (
    StockBulkCreate,
    StockCreate,
    StockFilter,
    StockImport,
    StockImportResult,
    StockList,
    StockResponse,
    StockSearch,
    StockSummary,
    StockUpdate,
)

router = APIRouter()
logger = get_logger(__name__)


async def get_stock_repository(db: AsyncSession = Depends(get_db)) -> StockRepository:
    """Dependency to get Stock repository"""
    return StockRepository(db)


@router.get("/", response_model=StockList, summary="List stocks with pagination and filtering")
async def list_stocks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("symbol", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    symbol: Optional[str] = Query(None, description="Filter by symbol (partial match)"),
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    stock_group: Optional[str] = Query(None, description="Filter by stock group"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Retrieve a paginated list of stocks with optional filtering and sorting.
    
    - **page**: Page number (1-based)
    - **limit**: Number of items per page (max 1000)
    - **sort_by**: Field to sort by (symbol, company_name, created_at, etc.)
    - **sort_order**: Sort direction (asc or desc)
    - **symbol**: Filter by stock symbol (partial match)
    - **company_name**: Filter by company name (partial match)
    - **stock_group**: Filter by NSE stock group
    - **sector**: Filter by sector
    - **is_active**: Filter by active status
    """
    try:
        # Create pagination and sorting parameters
        pagination = PaginationParams(page=page, limit=limit)
        sort = SortParams(sort_by=sort_by, sort_order=sort_order)
        
        # Create filter parameters
        filters = StockFilter(
            symbol=symbol,
            company_name=company_name,
            stock_group=stock_group,
            sector=sector,
            is_active=is_active,
        )
        
        # Get filtered stocks
        stocks = await repository.get_by_advanced_filter(
            filters=filters,
            pagination=pagination,
            sort=sort,
        )
        
        # Get total count for pagination metadata
        total_count = await repository.count_by_advanced_filter(filters)
        
        # Create response
        return StockList.create(
            items=[StockResponse.model_validate(stock) for stock in stocks],
            total=total_count,
            pagination=pagination,
        )
        
    except Exception as e:
        logger.error("Failed to list stocks", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stocks: {str(e)}"
        )


@router.get("/{stock_id}", response_model=StockResponse, summary="Get stock by ID")
async def get_stock(
    stock_id: UUID,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Retrieve a specific stock by its ID.
    
    - **stock_id**: UUID of the stock to retrieve
    """
    try:
        stock = await repository.get_by_id(stock_id)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock with ID {stock_id} not found"
            )
        
        return StockResponse.model_validate(stock)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get stock", stock_id=stock_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stock: {str(e)}"
        )


@router.get("/symbol/{symbol}", response_model=StockResponse, summary="Get stock by symbol")
async def get_stock_by_symbol(
    symbol: str,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Retrieve a stock by its symbol.
    
    - **symbol**: Stock symbol (e.g., RELIANCE, TCS)
    """
    try:
        stock = await repository.get_by_symbol(symbol)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock with symbol '{symbol}' not found"
            )
        
        return StockResponse.model_validate(stock)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get stock by symbol", symbol=symbol, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stock: {str(e)}"
        )


@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="Create new stock")
async def create_stock(
    stock_data: StockCreate,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Create a new stock.
    
    - **symbol**: Stock symbol (must be unique)
    - **company_name**: Company name
    - **stock_group**: NSE stock group/index
    - **sector**: Industry sector (optional)
    - **market_cap**: Market capitalization (optional)
    - **is_active**: Whether the stock is actively traded
    """
    try:
        # Check if stock with symbol already exists
        existing_stock = await repository.get_by_symbol(stock_data.symbol)
        if existing_stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock with symbol '{stock_data.symbol}' already exists"
            )
        
        # Create the stock
        created_stock = await repository.create(stock_data.model_dump())
        
        logger.info("Stock created successfully", symbol=stock_data.symbol)
        return StockResponse.model_validate(created_stock)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create stock", symbol=stock_data.symbol, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create stock: {str(e)}"
        )


@router.put("/{stock_id}", response_model=StockResponse, summary="Update stock")
async def update_stock(
    stock_id: UUID,
    stock_data: StockUpdate,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Update an existing stock.
    
    - **stock_id**: UUID of the stock to update
    - Provide only the fields you want to update
    """
    try:
        # Check if stock exists
        existing_stock = await repository.get_by_id(stock_id)
        if not existing_stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock with ID {stock_id} not found"
            )
        
        # If symbol is being updated, check for conflicts
        if stock_data.symbol and stock_data.symbol != existing_stock.symbol:
            symbol_conflict = await repository.get_by_symbol(stock_data.symbol)
            if symbol_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock with symbol '{stock_data.symbol}' already exists"
                )
        
        # Update the stock
        update_data = stock_data.model_dump(exclude_unset=True)
        updated_stock = await repository.update(stock_id, update_data)
        
        logger.info("Stock updated successfully", stock_id=stock_id)
        return StockResponse.model_validate(updated_stock)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update stock", stock_id=stock_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stock: {str(e)}"
        )


@router.delete("/{stock_id}", response_model=SuccessResponse, summary="Delete stock")
async def delete_stock(
    stock_id: UUID,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Delete a stock.
    
    - **stock_id**: UUID of the stock to delete
    
    Note: This will also delete all related breakout data due to cascade delete.
    """
    try:
        # Check if stock exists
        existing_stock = await repository.get_by_id(stock_id)
        if not existing_stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock with ID {stock_id} not found"
            )
        
        # Delete the stock
        await repository.delete(stock_id)
        
        logger.info("Stock deleted successfully", stock_id=stock_id, symbol=existing_stock.symbol)
        return SuccessResponse(
            message=f"Stock '{existing_stock.symbol}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete stock", stock_id=stock_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete stock: {str(e)}"
        )


@router.get("/search/", response_model=list[StockResponse], summary="Search stocks")
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query"),
    active_only: bool = Query(True, description="Search only active stocks"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Search stocks by symbol or company name.
    
    - **query**: Search query (matches symbol or company name)
    - **active_only**: Whether to search only active stocks
    - **limit**: Maximum number of results (max 100)
    """
    try:
        search_params = StockSearch(
            query=query,
            active_only=active_only,
            limit=limit,
        )
        
        stocks = await repository.search_stocks(
            query=search_params.query,
            active_only=search_params.active_only,
            limit=search_params.limit,
        )
        
        return [StockResponse.model_validate(stock) for stock in stocks]
        
    except Exception as e:
        logger.error("Failed to search stocks", query=query, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search stocks: {str(e)}"
        )


@router.get("/summary/", response_model=StockSummary, summary="Get stock summary statistics")
async def get_stock_summary(
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Get summary statistics for all stocks.
    
    Returns counts by status, groups, sectors, and market cap statistics.
    """
    try:
        # Get total counts
        total_stocks = await repository.count()
        active_stocks = await repository.count_active()
        inactive_stocks = total_stocks - active_stocks
        
        # Get breakdowns
        groups_breakdown = await repository.count_by_group()
        sectors_breakdown = await repository.count_by_sector()
        
        # Calculate market cap statistics
        # This would require additional repository methods for aggregation
        market_cap_stats = {
            "min": None,
            "max": None,
            "avg": None,
            "median": None,
        }
        
        summary = StockSummary(
            total_stocks=total_stocks,
            active_stocks=active_stocks,
            inactive_stocks=inactive_stocks,
            groups_breakdown=groups_breakdown,
            sectors_breakdown=sectors_breakdown,
            market_cap_stats=market_cap_stats,
        )
        
        return summary
        
    except Exception as e:
        logger.error("Failed to get stock summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stock summary: {str(e)}"
        )


@router.post("/bulk/", response_model=list[StockResponse], summary="Bulk create stocks")
async def bulk_create_stocks(
    bulk_data: StockBulkCreate,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Create multiple stocks in a single operation.
    
    - **stocks**: List of stocks to create (max 1000)
    
    All stocks must have unique symbols. If any conflict exists, the entire operation fails.
    """
    try:
        # Check for symbol conflicts
        symbols_to_check = [stock.symbol for stock in bulk_data.stocks]
        existing_stocks = await repository.get_by_symbols(symbols_to_check)
        
        if existing_stocks:
            conflicting_symbols = [stock.symbol for stock in existing_stocks]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stocks with symbols already exist: {', '.join(conflicting_symbols)}"
            )
        
        # Create all stocks
        stock_data_list = [stock.model_dump() for stock in bulk_data.stocks]
        created_stocks = await repository.bulk_create(stock_data_list)
        
        logger.info("Bulk created stocks", count=len(created_stocks))
        return [StockResponse.model_validate(stock) for stock in created_stocks]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to bulk create stocks", count=len(bulk_data.stocks), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create stocks: {str(e)}"
        )


@router.post("/import/", response_model=StockImportResult, summary="Import stocks from external source")
async def import_stocks(
    import_data: StockImport,
    repository: StockRepository = Depends(get_stock_repository),
):
    """
    Import stocks from external data sources.
    
    - **source**: Import source (nse, csv, manual)
    - **data**: Raw import data
    - **validate_only**: Only validate without importing
    - **overwrite_existing**: Whether to overwrite existing stocks
    """
    try:
        # This would implement the actual import logic
        # For now, return a placeholder response
        
        result = StockImportResult(
            total_processed=len(import_data.data),
            successful_imports=0,
            failed_imports=0,
            skipped_existing=0,
            errors=[],
            imported_stocks=[],
        )
        
        logger.info("Stock import completed", source=import_data.source, total=len(import_data.data))
        return result
        
    except Exception as e:
        logger.error("Failed to import stocks", source=import_data.source, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import stocks: {str(e)}"
        )