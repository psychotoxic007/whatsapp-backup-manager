"""Logging configuration and utilities."""

import logging
import logging.handlers
from pathlib import Path
from pythonjsonlogger import jsonlogger
import os


def setup_logger(name: str, log_file: str = None, level: str = 'INFO') -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setLevel(getattr(logging, level))
        json_formatter = jsonlogger.JsonFormatter()
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    return logger
