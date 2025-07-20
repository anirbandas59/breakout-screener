"""
Structured logging configuration for Breakout Screener V2
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory

from .config import config


def setup_logging() -> None:
    """Configure structured logging with proper formatting and rotation"""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if config.ENVIRONMENT == "production"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=get_log_handlers(),
    )

    # Set specific logger levels
    configure_logger_levels()


def get_log_handlers() -> list:
    """Get list of log handlers based on environment"""
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))

    if config.ENVIRONMENT == "production":
        # JSON formatter for production
        console_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Human-readable formatter for development
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handlers if not in testing mode
    if not config.TESTING:
        handlers.extend(get_file_handlers())

    return handlers


def get_file_handlers() -> list:
    """Get file handlers with rotation"""
    handlers = []

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Application log file with rotation
    app_log_file = log_dir / "app.log"
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=config.LOG_FILE_MAX_SIZE,
        backupCount=config.LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    app_handler.setLevel(getattr(logging, config.LOG_LEVEL))

    # Error log file with rotation
    error_log_file = log_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=config.LOG_FILE_MAX_SIZE,
        backupCount=config.LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)

    # JSON formatter for file logs
    file_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", '
        '"function": "%(funcName)s", "line": %(lineno)d}'
    )

    app_handler.setFormatter(file_formatter)
    error_handler.setFormatter(file_formatter)

    handlers.extend([app_handler, error_handler])

    return handlers


def configure_logger_levels() -> None:
    """Configure specific logger levels"""
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Set celery logging level
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("celery.task").setLevel(logging.INFO)

    # Application loggers
    if config.DEBUG:
        logging.getLogger("breakout_screener").setLevel(logging.DEBUG)
    else:
        logging.getLogger("breakout_screener").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capability to classes"""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters"""
    logger = get_logger("function_calls")
    logger.info("Function called", function=func_name, parameters=kwargs)


def log_api_request(method: str, path: str, status_code: int,
                   duration: float, **kwargs: Any) -> None:
    """Log API request details"""
    logger = get_logger("api_requests")
    logger.info(
        "API request processed",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_database_operation(operation: str, table: str,
                          duration: float | None = None, **kwargs: Any) -> None:
    """Log database operation"""
    logger = get_logger("database")
    log_data = {
        "operation": operation,
        "table": table,
        **kwargs
    }

    if duration is not None:
        log_data["duration_ms"] = round(duration * 1000, 2)

    logger.info("Database operation", **log_data)


def log_external_api_call(service: str, endpoint: str, status_code: int,
                         duration: float, **kwargs: Any) -> None:
    """Log external API call"""
    logger = get_logger("external_apis")
    logger.info(
        "External API call",
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log error with context"""
    logger = get_logger("errors")
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True
    )


def log_security_event(event_type: str, details: dict[str, Any]) -> None:
    """Log security-related events"""
    logger = get_logger("security")
    logger.warning(
        "Security event",
        event_type=event_type,
        **details
    )


# Initialize logging when module is imported
setup_logging()
