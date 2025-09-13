"""
Logging utilities for the Bangla News Scraper
"""

import logging
import sys
from typing import Optional
from ..config import Config


def setup_logger(
    name: str = "bangla_news_scraper",
    level: str = None,
    format_str: str = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the specified configuration
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Log message format
        log_file: Optional file to write logs to
    
    Returns:
        Configured logger instance
    """
    # Use config defaults if not provided
    level = level or Config.LOG_LEVEL
    format_str = format_str or Config.LOG_FORMAT
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(format_str)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "bangla_news_scraper") -> logging.Logger:
    """Get an existing logger or create a new one with default settings"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger