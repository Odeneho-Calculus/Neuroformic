"""
Session management for the form automation process.
"""
from typing import Dict, Any, Optional
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from playwright.sync_api import sync_playwright

from auth.login_handler import LoginHandler
from utils.logger import get_logger
from utils.helpers import extract_domain, sanitize_filename
from config import (
    BROWSER_TYPE, HEADLESS, USER_AGENT, 
    DEFAULT_USERNAME, DEFAULT_PASSWORD
)

logger = get_logger()

class SessionManager:
    """Manage browser sessions for form automation."""
    
    def __init__(self, browser_type: str = None):
        """
        Initialize the session manager.
        
        Args:
            browser_type: Browser to use (chrome, firefox, edge)
        """
        self.browser_type = browser_type or BROWSER_TYPE
        self.driver = None
        self.playwright = None
        self.browser = None
        self.page = None
        self.login_handler = None
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "url": None,
            "domain": None,
            "authenticated": False,
            "form_submissions": []
        }
    
    def start_selenium(self) -> None:
        """
        Start a Selenium browser session.
        """
        logger.info(f"Starting Selenium session with {self.browser_type} browser")
        
        if self.browser_type.lower() == "chrome":
            options = ChromeOptions()
            if HEADLESS:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
        elif self.browser_type.lower() == "firefox":
            options = FirefoxOptions()
            if HEADLESS:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            options.set_preference("general.useragent.override", USER_AGENT)
            
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
        elif self.browser_type.lower() == "edge":
            options = EdgeOptions()
            if HEADLESS:
                options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(f"user-agent={USER_AGENT}")
            
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)
        
        # Initialize login handler
        self.login_handler = LoginHandler(self.driver)
        
        logger.info("Selenium session started successfully")
    
    def start_playwright(self) -> None:
        """
        Start a Playwright browser session.
        """
        logger.info(f"Starting Playwright session with {self.browser_type} browser")
        
        self.playwright = sync_playwright().start()
        
        if self.browser_type.lower() == "chrome":
            self.browser = self.playwright.chromium.launch(
                headless=HEADLESS
            )
        elif self.browser_type.lower() == "firefox":
            self.browser = self.playwright.firefox.launch(
                headless=HEADLESS
            )
        elif self.browser_type.lower() == "webkit":
            self.browser = self.playwright.webkit.launch(
                headless=HEADLESS
            )
        else:
            raise ValueError(f"Unsupported browser type for Playwright: {self.browser_type}")
        
        # Create a new page and set viewport size
        self.page = self.browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent=USER_AGENT
        )
        
        logger.info("Playwright session started successfully")
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.session_data["url"] = url
        self.session_data["domain"] = extract_domain(url)
        
        logger.info(f"Navigating to {url}")
        
        try:
            if self.driver:
                self.driver.get(url)
            elif self.page:
                self.page.goto(url)
            else:
                logger.error("No browser session started")
                return False
            
            logger.info(f"Successfully navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def authenticate(self, url: str, username: str = None, password: str = None) -> bool:
        """
        Authenticate to the website.
        
        Args:
            url: URL to navigate to
            username: Optional username
            password: Optional password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.driver:
            logger.error("No Selenium session started")
            return False
        
        # Try to bypass with cookies first
        domain = extract_domain(url)
        cookies_success = self.login_handler.bypass_login_with_cookies(url, domain)
        
        if cookies_success:
            self.session_data["authenticated"] = True
            return True
        
        # If cookie bypass failed, try normal login
        login_success = self.login_handler.login(url, username, password)
        
        if login_success:
            self.session_data["authenticated"] = True
            return True
        
        logger.error("Authentication failed")
        return False
    
    def save_session_data(self, filepath: str = None) -> None:
        """
        Save session data to a file.
        
        Args:
            filepath: Optional custom filepath
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = self.session_data.get("domain", "unknown")
            safe_domain = sanitize_filename(domain)
            filepath = f"sessions/{safe_domain}_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Update end time
        self.session_data["end_time"] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2)
        
        logger.info(f"Session data saved to {filepath}")
    
    def add_form_submission(self, form_data: Dict[str, Any]) -> None:
        """
        Add a form submission record to the session data.
        
        Args:
            form_data: Form submission data
        """
        submission = {
            "timestamp": datetime.now().isoformat(),
            **form_data
        }
        
        self.session_data["form_submissions"].append(submission)
        logger.info("Form submission recorded in session data")
    
    def close(self) -> None:
        """
        Close the browser session.
        """
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Selenium session closed")
            
            if self.browser:
                self.browser.close()
                logger.info("Playwright browser closed")
            
            if self.playwright:
                self.playwright.stop()
                logger.info("Playwright session closed")
                
        except Exception as e:
            logger.error(f"Error closing session: {str(e)}")