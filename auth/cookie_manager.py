"""
Cookie management for authentication bypass.
"""
import os
import json
from typing import Dict, List, Any
import browser_cookie3

from utils.logger import get_logger
from utils.helpers import sanitize_filename
from config import COOKIE_FILE_PATH

logger = get_logger()

def get_cookie_file_path(domain: str) -> str:
    """
    Get the file path for the cookie file for a specific domain.
    
    Args:
        domain: Domain name
        
    Returns:
        str: File path
    """
    safe_domain = sanitize_filename(domain)
    cookie_dir = os.path.dirname(COOKIE_FILE_PATH)
    
    if not os.path.exists(cookie_dir) and cookie_dir:
        os.makedirs(cookie_dir)
    
    return os.path.join(cookie_dir, f"{safe_domain}_cookies.json")

def save_cookies(cookies: List[Dict[str, Any]], domain: str) -> bool:
    """
    Save cookies to a JSON file.
    
    Args:
        cookies: List of cookie dictionaries
        domain: Domain name for the cookies
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    file_path = get_cookie_file_path(domain)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Cookies saved for {domain}")
        return True
    except Exception as e:
        logger.error(f"Error saving cookies: {str(e)}")
        return False

def load_cookies(domain: str) -> List[Dict[str, Any]]:
    """
    Load cookies from a JSON file.
    
    Args:
        domain: Domain name for the cookies
        
    Returns:
        List[Dict[str, Any]]: List of cookie dictionaries
    """
    file_path = get_cookie_file_path(domain)
    
    if not os.path.exists(file_path):
        logger.warning(f"No saved cookies found for {domain}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        logger.info(f"Cookies loaded for {domain}")
        return cookies
    except Exception as e:
        logger.error(f"Error loading cookies: {str(e)}")
        return []

def extract_browser_cookies(domain: str, browser: str = "chrome") -> List[Dict[str, Any]]:
    """
    Extract cookies from the browser for a specific domain.
    
    Args:
        domain: Domain to extract cookies for
        browser: Browser to extract from (chrome, firefox, edge)
        
    Returns:
        List[Dict[str, Any]]: List of cookie dictionaries
    """
    logger.info(f"Extracting cookies from {browser} for {domain}")
    
    try:
        if browser.lower() == "chrome":
            cookie_jar = browser_cookie3.chrome(domain_name=domain)
        elif browser.lower() == "firefox":
            cookie_jar = browser_cookie3.firefox(domain_name=domain)
        elif browser.lower() == "edge":
            cookie_jar = browser_cookie3.edge(domain_name=domain)
        else:
            logger.error(f"Unsupported browser: {browser}")
            return []
        
        cookies = []
        for cookie in cookie_jar:
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'httpOnly': cookie.has_nonstandard_attr('httpOnly'),
                'expiry': cookie.expires
            }
            cookies.append(cookie_dict)
        
        # Save the extracted cookies
        save_cookies(cookies, domain)
        
        logger.info(f"Extracted {len(cookies)} cookies from {browser}")
        return cookies
    
    except Exception as e:
        logger.error(f"Error extracting cookies from {browser}: {str(e)}")
        return []