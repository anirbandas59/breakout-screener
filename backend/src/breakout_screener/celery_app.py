"""
Celery application configuration for Breakout Screener V2
Modern async-compatible Celery setup with Redis backend
"""

from celery import Celery
from celery.signals import worker_init, worker_shutdown

from .core.config import config
from .core.logging import get_logger

logger = get_logger(__name__)

# Create Celery application
celery_app = Celery(
    "breakout_screener",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=[
        'breakout_screener.tasks.data_extraction_tasks',
        'breakout_screener.tasks.analysis_tasks',
        'breakout_screener.tasks.data_management_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'breakout_screener.tasks.data_extraction_tasks.*': {'queue': 'data_extraction'},
        'breakout_screener.tasks.analysis_tasks.*': {'queue': 'analysis'},
        'breakout_screener.tasks.data_management_tasks.*': {'queue': 'data_management'},
    },

    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task results
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'breakout-screener-redis'
    },

    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,

    # Task retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Redis connection
    broker_transport_options={
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'fanout_patterns': True
    },

    # Task time limits
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=3600,       # 1 hour

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Beat schedule (for periodic tasks)
    beat_schedule={
        'daily-symbol-refresh': {
            'task': 'breakout_screener.tasks.data_extraction_tasks.fetch_nse_symbols_task',
            'schedule': 86400.0,  # Daily at midnight
        },
    },
)


@worker_init.connect
def worker_init_handler(sender=None, conf=None, **kwargs):
    """Initialize worker resources"""
    logger.info("Celery worker initialized")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Cleanup worker resources"""
    logger.info("Celery worker shutdown")


# Health check task
@celery_app.task(bind=True)
def health_check_task(self):
    """Simple health check task for monitoring"""
    return {
        'status': 'healthy',
        'worker_id': self.request.id,
        'timestamp': str(config.current_time if hasattr(config, 'current_time') else 'unknown')
    }
