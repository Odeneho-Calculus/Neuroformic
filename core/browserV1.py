"""
Browser automation utilities for Neuroformic.
"""
import os
from typing import Optional, Dict, Any
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from utils.logger import get_logger
from config import BROWSER_TYPE, HEADLESS, USER_AGENT

logger = get_logger()

def create_browser_driver(browser_type: str = None, headless: bool = None) -> webdriver.Remote:
    """
    Create and configure a Selenium WebDriver instance.
    
    Args:
        browser_type: Type of browser ('chrome', 'firefox', 'edge')
        headless: Whether to run in headless mode
        
    Returns:
        webdriver.Remote: Configured WebDriver instance
    """
    browser_type = browser_type or BROWSER_TYPE
    headless = headless if headless is not None else HEADLESS
    
    logger.info(f"Creating {browser_type} browser driver (headless: {headless})")
    
    if browser_type.lower() == 'chrome':
        return _create_chrome_driver(headless)
    elif browser_type.lower() == 'firefox':
        return _create_firefox_driver(headless)
    elif browser_type.lower() == 'edge':
        return _create_edge_driver(headless)
    else:
        logger.warning(f"Unsupported browser type: {browser_type}, falling back to Chrome")
        return _create_chrome_driver(headless)

def _create_chrome_driver(headless: bool) -> webdriver.Chrome:
    """
    Create and configure a Chrome WebDriver.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver
    """
    options = ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")
    
    # Common options for better automation
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Attempt to disable bot detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Create driver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Apply additional stealth settings
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    })
    
    logger.info("Chrome WebDriver created successfully")
    return driver

def _create_firefox_driver(headless: bool) -> webdriver.Firefox:
    """
    Create and configure a Firefox WebDriver.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        webdriver.Firefox: Configured Firefox WebDriver
    """
    options = FirefoxOptions()
    
    if headless:
        options.add_argument("--headless")
    
    # Common options
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("general.useragent.override", USER_AGENT)
    
    # Create driver
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    
    logger.info("Firefox WebDriver created successfully")
    return driver

def _create_edge_driver(headless: bool) -> webdriver.Edge:
    """
    Create and configure an Edge WebDriver.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        webdriver.Edge: Configured Edge WebDriver
    """
    options = EdgeOptions()
    
    if headless:
        options.add_argument("--headless")
    
    # Common options
    options.add_argument("--disable-notifications")
    options.add_argument(f"user-agent={USER_AGENT}")
    
    # Create driver
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    
    logger.info("Edge WebDriver created successfully")
    return driver

def close_browser(driver: webdriver.Remote) -> None:
    """
    Safely close the browser.
    
    Args:
        driver: WebDriver instance to close
    """
    logger.info("Closing browser")
    try:
        driver.quit()
    except Exception as e:
        logger.error(f"Error closing browser: {str(e)}")