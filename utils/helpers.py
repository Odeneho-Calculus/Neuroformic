"""
Helper utilities for Neuroformic.
"""
import os
import json
import random
import time
from typing import Dict, List, Any, Union
import re
from urllib.parse import urlparse

from utils.logger import get_logger

logger = get_logger()

def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
    """
    Wait for a random amount of time to simulate human behavior.
    
    Args:
        min_seconds: Minimum wait time in seconds
        max_seconds: Maximum wait time in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Random delay: {delay:.2f} seconds")
    time.sleep(delay)

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to the output file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.debug(f"Data saved to {filepath}")

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dict[str, Any]: Loaded data
    """
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.debug(f"Data loaded from {filepath}")
    return data

def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        str: Domain name
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from a filename.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    return sanitized

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'