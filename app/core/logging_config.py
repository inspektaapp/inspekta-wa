"""
Logging configuration for the application
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


def setup_logging(log_dir: Optional[str] = None) -> None:
    """
    Configure application logging with console and file handlers

    Args:
        log_dir: Directory for log files (defaults to ./logs)
    """
    # Create logs directory
    if log_dir is None:
        log_dir = Path("logs")
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(exist_ok=True)

    # Configure formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.LOG_FILE_MAX_SIZE,
        backupCount=settings.LOG_FILE_BACKUP_COUNT
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)

    # Separate error log
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=settings.LOG_FILE_MAX_SIZE,
        backupCount=settings.LOG_FILE_BACKUP_COUNT
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Configure specific loggers
    setup_specific_loggers(log_dir)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")
    logger.info(f"Log directory: {log_dir.absolute()}")


def setup_specific_loggers(log_dir: Path) -> None:
    """Setup specific loggers for different components"""

    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # WhatsApp-specific logger
    whatsapp_logger = logging.getLogger("whatsapp")
    whatsapp_handler = RotatingFileHandler(
        log_dir / "whatsapp.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    whatsapp_handler.setFormatter(detailed_formatter)
    whatsapp_logger.addHandler(whatsapp_handler)
    whatsapp_logger.setLevel(logging.INFO)
    whatsapp_logger.propagate = False  # Don't propagate to root logger

    # Authentication logger
    auth_logger = logging.getLogger("auth")
    auth_handler = RotatingFileHandler(
        log_dir / "auth.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    auth_handler.setFormatter(detailed_formatter)
    auth_logger.addHandler(auth_handler)
    auth_logger.setLevel(logging.INFO)
    auth_logger.propagate = False

    # Database logger
    db_logger = logging.getLogger("database")
    db_handler = RotatingFileHandler(
        log_dir / "database.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    db_handler.setFormatter(detailed_formatter)
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.INFO)
    db_logger.propagate = False

    # Celery logger
    celery_logger = logging.getLogger("celery")
    celery_handler = RotatingFileHandler(
        log_dir / "celery.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    celery_handler.setFormatter(detailed_formatter)
    celery_logger.addHandler(celery_handler)
    celery_logger.setLevel(logging.INFO)
    celery_logger.propagate = False

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)