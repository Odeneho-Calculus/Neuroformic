"""
Browser automation utilities for Neuroformic.
"""
import os
import webbrowser
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
from config import HEADLESS, USER_AGENT

logger = get_logger()

def get_default_browser() -> str:
    """
    Detect the default browser using the webbrowser module.
    Returns:
        str: Name of the default browser ('chrome', 'firefox', 'edge', 'safari', etc.)
    """
    browser_name = webbrowser.get().name.lower()
    logger.info(f"Detected default browser: {browser_name}")

    # Map browser names to supported browsers
    if "chrome" in browser_name:
        return "chrome"
    elif "firefox" in browser_name:
        return "firefox"
    elif "edge" in browser_name:
        return "edge"
    elif "safari" in browser_name:
        return "safari"
    else:
        logger.warning(f"Unsupported default browser detected: {browser_name}. Falling back to Chrome.")
        return "chrome"

def create_browser_driver(headless: bool = None) -> webdriver.Remote:
    """
    Create and configure a Selenium WebDriver instance based on the default browser.
    Args:
        headless: Whether to run in headless mode
    Returns:
        webdriver.Remote: Configured WebDriver instance
    """
    headless = headless if headless is not None else HEADLESS
    default_browser = get_default_browser()
    logger.info(f"Creating {default_browser} browser driver (headless: {headless})")

    if default_browser == 'chrome':
        return _create_chrome_driver(headless)
    elif default_browser == 'firefox':
        return _create_firefox_driver(headless)
    elif default_browser == 'edge':
        return _create_edge_driver(headless)
    else:
        logger.warning(f"Unsupported browser type: {default_browser}, falling back to Chrome")
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

    try:
        # Use ChromeDriverManager with cache_valid_range to force redownload if needed
        service = ChromeService(ChromeDriverManager(cache_valid_range=1).install())
        logger.info(f"ChromeDriver path: {service.path}")
    except Exception as e:
        logger.warning(f"Failed to install ChromeDriver using webdriver_manager: {e}")
        # Fallback: try to use Chrome directly
        logger.info("Trying to use Chrome directly...")
        driver = webdriver.Chrome(options=options)
        
        # Apply additional stealth settings
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        })
        
        logger.info("Chrome WebDriver created successfully via direct method")
        return driver

    # Create driver with the service
    try:
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
    except Exception as e:
        logger.error(f"Failed to create Chrome WebDriver with downloaded driver: {e}")
        raise

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
