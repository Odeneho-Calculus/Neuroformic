"""
Authentication handler for web form login.
"""
from typing import Dict, Optional, Tuple
import time
import json

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from auth.cookie_manager import save_cookies, load_cookies
from auth.captcha_solver import solve_captcha
from utils.logger import get_logger
from utils.helpers import random_delay
from config import DEFAULT_USERNAME, DEFAULT_PASSWORD, USE_SAVED_CREDENTIALS

logger = get_logger()

class LoginHandler:
    """Handle authentication for web forms."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize login handler.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def detect_login_form(self) -> Dict[str, str]:
        """
        Detect login form elements on the current page.
        
        Returns:
            Dict[str, str]: Dictionary with selectors for username, password, and submit button
        """
        logger.info("Detecting login form elements")
        
        # Common attributes for login forms
        username_selectors = [
            "input[type='text'][id*='user' i]",
            "input[type='email']",
            "input[name*='user' i]",
            "input[name*='email' i]",
            "input[id*='login' i]",
            "input[name*='login' i]"
        ]
        
        password_selectors = [
            "input[type='password']"
        ]
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button[id*='login' i]",
            "button[class*='login' i]",
            "button[name*='login' i]",
            "a[id*='login' i]",
            "a[class*='login' i]"
        ]
        
        form_elements = {}
        
        # Try to find username field
        for selector in username_selectors:
            try:
                username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                form_elements['username_selector'] = selector
                break
            except NoSuchElementException:
                continue
        
        # Try to find password field
        for selector in password_selectors:
            try:
                password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                form_elements['password_selector'] = selector
                break
            except NoSuchElementException:
                continue
        
        # Try to find submit button
        for selector in submit_selectors:
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                form_elements['submit_selector'] = selector
                break
            except NoSuchElementException:
                continue
        
        if len(form_elements) >= 2:  # Found at least username/email and password fields
            logger.info("Login form detected successfully")
            return form_elements
        else:
            logger.warning("Could not detect login form completely")
            return {}
    
    def login(self, url: str, username: str = None, password: str = None) -> bool:
        """
        Perform login using provided credentials.
        
        Args:
            url: URL to navigate to
            username: Optional username (uses configured default if not provided)
            password: Optional password (uses configured default if not provided)
            
        Returns:
            bool: True if login successful, False otherwise
        """
        username = username or DEFAULT_USERNAME
        password = password or DEFAULT_PASSWORD
        
        if not username or not password:
            logger.error("No login credentials provided")
            return False
        
        logger.info(f"Attempting to log in to {url}")
        
        # Navigate to the login page
        self.driver.get(url)
        random_delay(1, 2)
        
        # Detect login form elements
        form_elements = self.detect_login_form()
        if not form_elements:
            logger.error("Could not detect login form elements")
            return False
        
        try:
            # Fill in username
            username_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, form_elements['username_selector']))
            )
            username_field.clear()
            username_field.send_keys(username)
            random_delay(0.5, 1.5)
            
            # Fill in password
            password_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, form_elements['password_selector']))
            )
            password_field.clear()
            password_field.send_keys(password)
            random_delay(0.5, 1.5)
            
            # Check for CAPTCHA
            if self._detect_captcha():
                logger.info("CAPTCHA detected, attempting to solve")
                if not solve_captcha(self.driver):
                    logger.error("Failed to solve CAPTCHA")
                    return False
                random_delay(1, 2)
            
            # Submit the form
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, form_elements['submit_selector']))
            )
            submit_button.click()
            
            # Wait for login to complete (wait for redirect or dashboard elements)
            # This will need to be customized based on the target site
            time.sleep(3)  # Basic waiting approach
            
            # Save cookies for future use
            domain = url.split('//')[1].split('/')[0]
            save_cookies(self.driver.get_cookies(), domain)
            
            # Check if login was successful
            if self._verify_login_success():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - verification check failed")
                return False
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def bypass_login_with_cookies(self, url: str, domain: str = None) -> bool:
        """
        Attempt to bypass login using saved cookies.
        
        Args:
            url: URL to navigate to
            domain: Optional domain for cookies (extracted from URL if not provided)
            
        Returns:
            bool: True if bypass successful, False otherwise
        """
        if not domain:
            domain = url.split('//')[1].split('/')[0]
        
        logger.info(f"Attempting to bypass login with cookies for {domain}")
        
        # Load cookies for the domain
        cookies = load_cookies(domain)
        if not cookies:
            logger.warning(f"No saved cookies found for {domain}")
            return False
        
        # Navigate to the site
        self.driver.get(url)
        
        # Add the cookies to the driver
        for cookie in cookies:
            try:
                # Some cookies might have additional attributes that Selenium doesn't support
                # Filter to only include the necessary attributes
                filtered_cookie = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                }
                
                # Add expiry if present (Selenium expects Unix timestamp)
                if 'expiry' in cookie:
                    filtered_cookie['expiry'] = int(cookie['expiry'])
                
                self.driver.add_cookie(filtered_cookie)
            except Exception as e:
                logger.warning(f"Error adding cookie {cookie['name']}: {str(e)}")
        
        # Refresh to apply cookies
        self.driver.refresh()
        random_delay(1, 3)
        
        # Verify if login bypass was successful
        if self._verify_login_success():
            logger.info("Login bypass with cookies successful")
            return True
        else:
            logger.warning("Login bypass with cookies failed")
            return False
    
    def _detect_captcha(self) -> bool:
        """
        Detect if CAPTCHA is present on the page.
        
        Returns:
            bool: True if CAPTCHA is detected, False otherwise
        """
        # Common CAPTCHA indicators
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            "div[class*='captcha']",
            "div[id*='captcha']",
            "input[name*='captcha']",
            "img[alt*='captcha' i]"
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"CAPTCHA detected with selector: {selector}")
                return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _verify_login_success(self) -> bool:
        """
        Verify if login was successful.
        This is a basic implementation that checks for common indicators.
        For production use, this should be customized for the specific site.
        
        Returns:
            bool: True if login appears successful, False otherwise
        """
        # Check for common indicators of successful login
        success_indicators = [
            # Absence of login form
            (By.CSS_SELECTOR, "input[type='password']", False),
            
            # Common dashboard elements
            (By.CSS_SELECTOR, "a[href*='logout']", True),
            (By.CSS_SELECTOR, "a[href*='sign-out']", True),
            (By.CSS_SELECTOR, "button[id*='logout']", True),
            (By.CSS_SELECTOR, "div[class*='dashboard']", True),
            (By.CSS_SELECTOR, "div[class*='account']", True),
            
            # Common error messages
            (By.XPATH, "//*[contains(text(), 'incorrect password')]", False),
            (By.XPATH, "//*[contains(text(), 'login failed')]", False),
            (By.XPATH, "//*[contains(text(), 'invalid credentials')]", False)
        ]
        
        for by, selector, expected_presence in success_indicators:
            try:
                element_exists = len(self.driver.find_elements(by, selector)) > 0
                if element_exists == expected_presence:
                    return True
            except:
                continue
        
        # If we can't definitively determine, check the URL
        # Many sites redirect to a dashboard or account page after login
        current_url = self.driver.current_url.lower()
        if any(term in current_url for term in ['dashboard', 'account', 'profile', 'home']):
            return True
        
        return False