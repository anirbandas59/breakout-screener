"""
Analysis Celery tasks
Tasks for breakout analysis and CPR calculations
"""

import asyncio
from datetime import datetime

from ..celery_app import celery_app
from ..core.database import db_manager
from ..core.logging import get_logger
from ..repositories.stock import StockRepository
from ..services.breakout_analysis_service import BreakoutAnalysisService

logger = get_logger(__name__)


@celery_app.task(bind=True, name='generate_breakout_analysis_task')
def generate_breakout_analysis_task(
    self,
    analysis_date: str,
    pivot_threshold: float = 0.5,
    group_filter: list[str] | None = None,
    active_only: bool = True
):
    """
    Celery task to generate breakout analysis for all symbols
    V2 implementation of V1's generate_bo_data_task
    
    Args:
        analysis_date: Date for analysis in YYYY-MM-DD format
        pivot_threshold: Percentage threshold for narrow gap detection  
        group_filter: Optional list of stock groups to analyze
        active_only: Only analyze active stocks
        
    Returns:
        Task result with analysis summary
    """

    task_id = self.request.id
    logger.info(f"Starting breakout analysis task {task_id} for {analysis_date}")

    async def run_analysis():
        """Async function to perform analysis"""
        try:
            # Parse analysis date
            analysis_dt = datetime.strptime(analysis_date, '%Y-%m-%d')

            # Initialize service
            analysis_service = BreakoutAnalysisService()

            # Get database session
            async with db_manager.get_session() as db:
                # Get stocks to analyze
                stock_repo = StockRepository(db)

                if group_filter:
                    stocks = []
                    for group in group_filter:
                        group_stocks = await stock_repo.get_by_group(group)
                        stocks.extend(group_stocks)
                else:
                    stocks = await stock_repo.get_active_stocks() if active_only else await stock_repo.get_all()

                if not stocks:
                    return {
                        'status': 'FAILED',
                        'error': 'No stocks found for analysis',
                        'total_symbols': 0
                    }

                symbols = [stock.symbol for stock in stocks]
                logger.info(f"Analyzing {len(symbols)} symbols")

                # Perform analysis
                result = await analysis_service.analyze_multiple_symbols(
                    db=db,
                    symbols=symbols,
                    analysis_date=analysis_dt,
                    pivot_threshold=pivot_threshold
                )

                logger.info(f"Breakout analysis task {task_id} completed: {result['status']}")
                return result

        except Exception as e:
            logger.error(f"Breakout analysis task {task_id} failed: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'task_id': task_id,
                'timestamp': datetime.now()
            }

    # Run async function
    try:
        result = asyncio.run(run_analysis())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'generate_breakout_analysis_task',
            'parameters': {
                'analysis_date': analysis_date,
                'pivot_threshold': pivot_threshold,
                'group_filter': group_filter,
                'active_only': active_only
            }
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'generate_breakout_analysis_task',
            'timestamp': datetime.now()
        }


@celery_app.task(bind=True, name='analyze_single_symbol_task')
def analyze_single_symbol_task(
    self,
    symbol: str,
    analysis_date: str,
    pivot_threshold: float = 0.5,
    save_to_db: bool = True
):
    """
    Celery task to analyze a single symbol
    
    Args:
        symbol: Stock symbol to analyze
        analysis_date: Date for analysis in YYYY-MM-DD format
        pivot_threshold: Percentage threshold for narrow gap detection
        save_to_db: Whether to save results to database
        
    Returns:
        Task result with analysis details
    """

    task_id = self.request.id
    logger.info(f"Starting single symbol analysis task {task_id} for {symbol}")

    async def run_single_analysis():
        """Async function to analyze single symbol"""
        try:
            # Parse analysis date
            analysis_dt = datetime.strptime(analysis_date, '%Y-%m-%d')

            # Initialize service
            analysis_service = BreakoutAnalysisService()

            # Perform analysis
            analysis_result = await analysis_service.analyze_symbol(
                symbol=symbol,
                analysis_date=analysis_dt,
                pivot_threshold=pivot_threshold
            )

            if not analysis_result:
                return {
                    'status': 'FAILED',
                    'error': f'Analysis failed for symbol {symbol}',
                    'symbol': symbol
                }

            # Save to database if requested
            saved = False
            if save_to_db:
                async with db_manager.get_session() as db:
                    saved = await analysis_service.save_analysis_to_db(db, analysis_result)
                    if saved:
                        await db.commit()

            # Prepare result
            result = {
                'status': 'SUCCESS',
                'symbol': symbol,
                'analysis_date': analysis_date,
                'breakout_indicator': analysis_result.breakout_indicator.value,
                'cpr_analysis': {
                    'pivot': str(analysis_result.cpr_analysis.pivot),
                    'resistance_1': str(analysis_result.cpr_analysis.resistance_1),
                    'resistance_2': str(analysis_result.cpr_analysis.resistance_2),
                    'support_1': str(analysis_result.cpr_analysis.support_1),
                    'support_2': str(analysis_result.cpr_analysis.support_2),
                    'gap_percentage': str(analysis_result.cpr_analysis.gap_percentage),
                    'is_narrow_gap': analysis_result.cpr_analysis.is_narrow_gap
                },
                'volume_analysis': {
                    'current_volume': analysis_result.volume_analysis.current_volume,
                    'average_volume': str(analysis_result.volume_analysis.average_volume),
                    'volume_ratio': str(analysis_result.volume_analysis.volume_ratio),
                    'volume_indicator': analysis_result.volume_analysis.volume_indicator.value
                },
                'candle_analysis': {
                    'candle_type': analysis_result.candle_analysis.candle_type.value,
                    'body_percentage': str(analysis_result.candle_analysis.body_percentage),
                    'upper_wick_percentage': str(analysis_result.candle_analysis.upper_wick_percentage),
                    'lower_wick_percentage': str(analysis_result.candle_analysis.lower_wick_percentage)
                },
                'ohlcv_data': {
                    key: str(value) for key, value in analysis_result.ohlcv_data.items()
                },
                'previous_high': str(analysis_result.previous_high) if analysis_result.previous_high else None,
                'analysis_summary': analysis_result.analysis_summary,
                'saved_to_db': saved
            }

            logger.info(f"Single symbol analysis task {task_id} completed for {symbol}: {analysis_result.breakout_indicator.value}")
            return result

        except Exception as e:
            logger.error(f"Single symbol analysis task {task_id} failed for {symbol}: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'symbol': symbol,
                'task_id': task_id,
                'timestamp': datetime.now()
            }

    # Run async function
    try:
        result = asyncio.run(run_single_analysis())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'analyze_single_symbol_task',
            'parameters': {
                'symbol': symbol,
                'analysis_date': analysis_date,
                'pivot_threshold': pivot_threshold,
                'save_to_db': save_to_db
            }
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'analyze_single_symbol_task',
            'timestamp': datetime.now()
        }
