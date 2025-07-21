"""
Data management Celery tasks
Tasks for data cleanup and archival operations
"""

import asyncio
from datetime import datetime

from ..celery_app import celery_app
from ..core.database import db_manager
from ..core.logging import get_logger
from ..repositories.breakout_data import BreakoutDataRepository
from ..repositories.master_data import MasterBreakoutDataRepository

logger = get_logger(__name__)


@celery_app.task(bind=True, name='clear_analysis_data_task')
def clear_analysis_data_task(self, target_date: str, selective: bool = True):
    """
    Celery task to clear analysis data for a specific date
    V2 implementation of V1's clear_chart_data_task
    
    Args:
        target_date: Date to clear in YYYY-MM-DD format
        selective: If True, clear only calculated fields; if False, clear entire records
        
    Returns:
        Task result with clearing statistics
    """

    task_id = self.request.id
    logger.info(f"Starting data clearing task {task_id} for {target_date}")

    async def clear_data():
        """Async function to clear data"""
        try:
            # Parse target date
            clear_date = datetime.strptime(target_date, '%Y-%m-%d').date()

            # Get database session
            async with db_manager.get_session() as db:
                breakout_repo = BreakoutDataRepository(db)

                if selective:
                    # Clear only calculated analysis fields (V1 behavior)
                    cleared_count = await breakout_repo.clear_analysis_fields_by_date(clear_date)
                    operation = "selective clearing"
                else:
                    # Delete entire records for the date
                    cleared_count = await breakout_repo.delete_by_date(clear_date)
                    operation = "complete deletion"

                # Commit changes
                await db.commit()

                result = {
                    'status': 'SUCCESS',
                    'operation': operation,
                    'target_date': target_date,
                    'records_affected': cleared_count,
                    'timestamp': datetime.now()
                }

                logger.info(f"Data clearing task {task_id} completed: {cleared_count} records affected")
                return result

        except Exception as e:
            logger.error(f"Data clearing task {task_id} failed: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'target_date': target_date,
                'operation': 'selective clearing' if selective else 'complete deletion',
                'records_affected': 0,
                'task_id': task_id,
                'timestamp': datetime.now()
            }

    # Run async function
    try:
        result = asyncio.run(clear_data())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'clear_analysis_data_task',
            'parameters': {
                'target_date': target_date,
                'selective': selective
            }
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'clear_analysis_data_task',
            'timestamp': datetime.now()
        }


@celery_app.task(bind=True, name='archive_analysis_data_task')
def archive_analysis_data_task(
    self,
    archive_before_date: str | None = None,
    keep_recent_days: int = 30
):
    """
    Celery task to archive analysis data to master table
    V2 implementation of V1's clear_complete_data_task
    
    Args:
        archive_before_date: Archive data before this date (YYYY-MM-DD)
        keep_recent_days: Number of recent days to keep in active table
        
    Returns:
        Task result with archival statistics
    """

    task_id = self.request.id
    logger.info(f"Starting data archival task {task_id}")

    async def archive_data():
        """Async function to archive data"""
        try:
            # Determine cutoff date
            if archive_before_date:
                cutoff_date = datetime.strptime(archive_before_date, '%Y-%m-%d').date()
            else:
                cutoff_date = (datetime.now().date() - timedelta(days=keep_recent_days))

            # Get database session
            async with db_manager.get_session() as db:
                breakout_repo = BreakoutDataRepository(db)
                master_repo = MasterBreakoutDataRepository(db)

                # Get records to archive
                records_to_archive = await breakout_repo.get_by_date_range(
                    end_date=cutoff_date
                )

                if not records_to_archive:
                    return {
                        'status': 'SUCCESS',
                        'operation': 'archival',
                        'cutoff_date': str(cutoff_date),
                        'records_archived': 0,
                        'records_deleted': 0,
                        'message': 'No records found to archive',
                        'timestamp': datetime.now()
                    }

                # Archive records to master table
                archived_count = 0
                for record in records_to_archive:
                    try:
                        # Check if record already exists in master
                        existing_master = await master_repo.get_by_stock_and_date(
                            record.stock_id,
                            record.trade_date
                        )

                        if existing_master:
                            # Update existing master record
                            master_data = record.to_master_data()
                            await master_repo.update(existing_master.id, master_data)
                        else:
                            # Create new master record
                            master_data = record.to_master_data()
                            await master_repo.create(master_data)

                        archived_count += 1

                    except Exception as e:
                        logger.warning(f"Failed to archive record {record.id}: {str(e)}")
                        continue

                # Delete archived records from active table
                deleted_count = await breakout_repo.delete_by_date_range(
                    end_date=cutoff_date
                )

                # Commit all changes
                await db.commit()

                result = {
                    'status': 'SUCCESS',
                    'operation': 'archival',
                    'cutoff_date': str(cutoff_date),
                    'records_found': len(records_to_archive),
                    'records_archived': archived_count,
                    'records_deleted': deleted_count,
                    'timestamp': datetime.now()
                }

                logger.info(f"Data archival task {task_id} completed: {archived_count} archived, {deleted_count} deleted")
                return result

        except Exception as e:
            logger.error(f"Data archival task {task_id} failed: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'operation': 'archival',
                'cutoff_date': str(cutoff_date) if 'cutoff_date' in locals() else 'unknown',
                'records_archived': 0,
                'records_deleted': 0,
                'task_id': task_id,
                'timestamp': datetime.now()
            }

    # Run async function
    try:
        from datetime import timedelta  # Import needed for keep_recent_days calculation

        result = asyncio.run(archive_data())

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'archive_analysis_data_task',
            'parameters': {
                'archive_before_date': archive_before_date,
                'keep_recent_days': keep_recent_days
            }
        })

        return result

    except Exception as e:
        logger.error(f"Task {task_id} execution failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'archive_analysis_data_task',
            'timestamp': datetime.now()
        }


@celery_app.task(bind=True, name='suspend_analysis_task')
def suspend_analysis_task(self):
    """
    Task to suspend ongoing analysis operations
    V2 implementation of V1's suspend_action
    
    Returns:
        Task result confirming suspension
    """

    task_id = self.request.id
    logger.info(f"Starting analysis suspension task {task_id}")

    try:
        # In V2, we can implement suspension by:
        # 1. Setting a Redis flag that analysis tasks check
        # 2. Revoking running tasks
        # 3. Clearing task queues

        from ..core.redis import redis_manager

        async def set_suspension_flag():
            """Set suspension flag in Redis"""
            try:
                await redis_manager.set_cache('analysis_suspended', 'true', ttl=3600)
                await redis_manager.set_cache('suspension_timestamp', str(datetime.now()), ttl=3600)
                return True
            except Exception as e:
                logger.error(f"Failed to set suspension flag: {str(e)}")
                return False

        # Set suspension flag
        suspension_set = asyncio.run(set_suspension_flag())

        if suspension_set:
            # Revoke active analysis tasks (if any)
            try:
                celery_app.control.revoke(
                    ['generate_breakout_analysis_task', 'analyze_single_symbol_task'],
                    terminate=True
                )
                revoked = True
            except Exception as e:
                logger.warning(f"Failed to revoke tasks: {str(e)}")
                revoked = False

            result = {
                'status': 'SUCCESS',
                'operation': 'suspension',
                'suspension_flag_set': suspension_set,
                'active_tasks_revoked': revoked,
                'timestamp': datetime.now(),
                'message': 'Analysis operations suspended'
            }
        else:
            result = {
                'status': 'PARTIAL_SUCCESS',
                'operation': 'suspension',
                'suspension_flag_set': False,
                'active_tasks_revoked': False,
                'error': 'Failed to set suspension flag',
                'timestamp': datetime.now()
            }

        # Update task metadata
        result.update({
            'task_id': task_id,
            'task_name': 'suspend_analysis_task'
        })

        logger.info(f"Analysis suspension task {task_id} completed: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"Suspension task {task_id} failed: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': task_id,
            'task_name': 'suspend_analysis_task',
            'timestamp': datetime.now()
        }
