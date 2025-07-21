"""
Data extraction Celery tasks
Tasks for NSE symbol extraction and historical data fetching
"""

import asyncio
from datetime import datetime

from ..celery_app import celery_app
from ..core.database import db_manager
from ..core.logging import get_logger
from ..services.nse_data_service import NSEDataService

logger = get_logger(__name__)


@celery_app.task(bind=True, name='fetch_nse_symbols_task')
def fetch_nse_symbols_task(self, group_filter: list[str] | None = None):
    """
    Celery task to fetch NSE stock symbols from all indices
    V2 implementation of V1's fetch_script_symbols_task
    
    Args:
        group_filter: Optional list of group names to fetch
        
    Returns:
        Task result with status and statistics
    """

    task_id = self.request.id
    logger.info(f"Starting NSE symbols extraction task {task_id}")

    async def run_extraction():
        """Async function to perform extraction"""
        try:
            # Initialize service
            nse_service = NSEDataService()

            # Get database session
            async with db_manager.get_session() as db:
                # Perform extraction and save
                result = await nse_service.fetch_and_save_symbols(db, group_filter)

                logger.info(f"NSE symbols task {task_id} completed: {result['status']}")
                return result

        except Exception as e:
            logger.error(f"NSE symbols task {task_id} failed: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'task_id': task_id,
                'timestamp': datetime.now()
            }

    # Run async function in event loop
    try:
        result = asyncio.run(run_extraction())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'fetch_nse_symbols_task'
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'fetch_nse_symbols_task',
            'timestamp': datetime.now()
        }


@celery_app.task(bind=True, name='fetch_historical_data_task')
def fetch_historical_data_task(
    self,
    symbols: list[str],
    start_date: str,
    end_date: str | None = None,
    days_back: int | None = None
):
    """
    Celery task to fetch historical data for multiple symbols
    
    Args:
        symbols: List of stock symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        days_back: Alternative to end_date
        
    Returns:
        Task result with fetched data summary
    """

    task_id = self.request.id
    logger.info(f"Starting historical data fetch task {task_id} for {len(symbols)} symbols")

    async def fetch_data():
        """Async function to fetch historical data"""
        try:
            from ..services.yahoo_finance_service import YahooFinanceService

            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

            # Initialize service
            yahoo_service = YahooFinanceService()

            # Fetch data
            historical_data = await yahoo_service.fetch_multiple_symbols(
                symbols=symbols,
                start_date=start_dt,
                end_date=end_dt,
                days_back=days_back
            )

            # Prepare results
            successful = sum(1 for data in historical_data.values() if data is not None)
            failed = len(symbols) - successful

            result = {
                'status': 'SUCCESS' if successful > 0 else 'FAILED',
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / len(symbols)) * 100 if symbols else 0,
                'data_summary': {
                    symbol: {
                        'available': data is not None,
                        'data_points': len(data.data_points) if data else 0,
                        'date_range': f"{data.start_date.date()} to {data.end_date.date()}" if data else None
                    }
                    for symbol, data in historical_data.items()
                }
            }

            logger.info(f"Historical data task {task_id} completed: {successful}/{len(symbols)} successful")
            return result

        except Exception as e:
            logger.error(f"Historical data task {task_id} failed: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'total_symbols': len(symbols),
                'successful': 0,
                'failed': len(symbols)
            }

    # Run async function
    try:
        result = asyncio.run(fetch_data())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'fetch_historical_data_task',
            'parameters': {
                'start_date': start_date,
                'end_date': end_date,
                'days_back': days_back
            }
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'fetch_historical_data_task',
            'timestamp': datetime.now()
        }
