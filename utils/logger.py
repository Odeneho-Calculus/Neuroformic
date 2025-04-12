"""
Logging utility for Neuroformic.
"""
import logging
import os
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE

def setup_logger():
    """
    Set up and configure the application logger.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("neuroformic")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger():
    """
    Get the application logger.
    
    Returns:
        logging.Logger: Application logger
    """
    return logging.getLogger("neuroformic")