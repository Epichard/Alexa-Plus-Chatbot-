"""
Logging configuration for FastAPI application
"""

import logging
import sys
from typing import Dict, Any

from .config import settings


def setup_logging() -> None:
    """Configure application logging"""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    loggers = {
        "uvicorn": logging.INFO,
        "uvicorn.error": logging.INFO,
        "uvicorn.access": logging.INFO if settings.DEBUG else logging.WARNING,
        "fastapi": logging.INFO,
        "boto3": logging.WARNING,
        "botocore": logging.WARNING,
        "websockets": logging.INFO if settings.DEBUG else logging.WARNING,
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)