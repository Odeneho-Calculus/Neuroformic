"""
CAPTCHA solving functionality.
"""
import time
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.logger import get_logger
from utils.helpers import random_delay
from config import CAPTCHA_API_KEY, USE_CAPTCHA_SOLVER

logger = get_logger()

def solve_captcha(driver: WebDriver) -> bool:
    """
    Attempt to solve CAPTCHA on the page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if solved successfully, False otherwise
    """
    # First, detect the type of CAPTCHA
    captcha_type = detect_captcha_type(driver)
    
    if not captcha_type:
        logger.warning("Could not determine CAPTCHA type")
        return False
    
    logger.info(f"Detected CAPTCHA type: {captcha_type}")
    
    if captcha_type == "recaptcha":
        return solve_recaptcha(driver)
    elif captcha_type == "image_captcha":
        return solve_image_captcha(driver)
    elif captcha_type == "text_captcha":
        return solve_text_captcha(driver)
    else:
        logger.warning(f"No solver available for CAPTCHA type: {captcha_type}")
        return prompt_manual_captcha(driver)

def detect_captcha_type(driver: WebDriver) -> Optional[str]:
    """
    Detect the type of CAPTCHA on the page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Optional[str]: CAPTCHA type or None if not detected
    """
    # Check for reCAPTCHA
    try:
        if driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']") or \
           driver.find_elements(By.CSS_SELECTOR, "div.g-recaptcha"):
            return "recaptcha"
    except:
        pass
    
    # Check for image CAPTCHA
    try:
        if driver.find_elements(By.CSS_SELECTOR, "img[alt*='captcha' i]") or \
           driver.find_elements(By.CSS_SELECTOR, "img[src*='captcha' i]"):
            return "image_captcha"
    except:
        pass
    
    # Check for text CAPTCHA
    try:
        if driver.find_elements(By.CSS_SELECTOR, "input[name*='captcha' i]") or \
           driver.find_elements(By.XPATH, "//label[contains(text(), 'captcha' i)]"):
            return "text_captcha"
    except:
        pass
    
    return None

def solve_recaptcha(driver: WebDriver) -> bool:
    """
    Solve reCAPTCHA using 2Captcha API or prompt for manual solving.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if solved successfully, False otherwise
    """
    if USE_CAPTCHA_SOLVER and CAPTCHA_API_KEY:
        try:
            from twocaptcha import TwoCaptcha
            
            # Find the sitekey
            sitekey = None
            try:
                sitekey = driver.find_element(By.CSS_SELECTOR, "div.g-recaptcha").get_attribute("data-sitekey")
            except:
                try:
                    # Alternative way to find sitekey
                    page_source = driver.page_source
                    import re
                    sitekey_match = re.search(r'data-sitekey="([^"]*)"', page_source)
                    if sitekey_match:
                        sitekey = sitekey_match.group(1)
                except:
                    pass
            
            if not sitekey:
                logger.error("Could not find reCAPTCHA sitekey")
                return prompt_manual_captcha(driver)
            
            # Solve using 2Captcha
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            result = solver.recaptcha(
                sitekey=sitekey,
                url=driver.current_url
            )
            
            # Apply the solution
            driver.execute_script(
                f'document.getElementById("g-recaptcha-response").innerHTML="{result["code"]}";'
            )
            
            # Trigger the callback function
            driver.execute_script("___grecaptcha_cfg.clients[0].aa.l.callback('{}');".format(result["code"]))
            
            logger.info("reCAPTCHA solved with 2Captcha")
            return True
            
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA with 2Captcha: {str(e)}")
            return prompt_manual_captcha(driver)
    else:
        return prompt_manual_captcha(driver)

def solve_image_captcha(driver: WebDriver) -> bool:
    """
    Solve image CAPTCHA using 2Captcha API or prompt for manual solving.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if solved successfully, False otherwise
    """
    if USE_CAPTCHA_SOLVER and CAPTCHA_API_KEY:
        try:
            from twocaptcha import TwoCaptcha
            import base64
            
            # Find the CAPTCHA image
            captcha_img = driver.find_element(By.CSS_SELECTOR, "img[alt*='captcha' i], img[src*='captcha' i]")
            
            # Get the image as base64
            img_base64 = driver.execute_script("""
                var img = arguments[0];
                var canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/png').substring(22);
            """, captcha_img)
            
            # Solve using 2Captcha
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            result = solver.normal(img_base64)
            
            # Find the input field
            input_field = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha' i]")
            input_field.clear()
            input_field.send_keys(result["code"])
            
            logger.info("Image CAPTCHA solved with 2Captcha")
            return True
            
        except Exception as e:
            logger.error(f"Error solving image CAPTCHA with 2Captcha: {str(e)}")
            return prompt_manual_captcha(driver)
    else:
        return prompt_manual_captcha(driver)

def solve_text_captcha(driver: WebDriver) -> bool:
    """
    Solve text CAPTCHA using 2Captcha API or prompt for manual solving.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if solved successfully, False otherwise
    """
    # For text CAPTCHA, we need to extract the question/challenge
    try:
        # Try to find the CAPTCHA question/instruction
        captcha_text = None
        for selector in [
            "//label[contains(text(), 'captcha' i)]",
            "//div[contains(text(), 'captcha' i)]",
            "//p[contains(text(), 'captcha' i)]"
        ]:
            try:
                captcha_element = driver.find_element(By.XPATH, selector)
                captcha_text = captcha_element.text
                break
            except:
                continue
        
        if not captcha_text:
            logger.warning("Could not find CAPTCHA text/instruction")
            return prompt_manual_captcha(driver)
        
        if USE_CAPTCHA_SOLVER and CAPTCHA_API_KEY:
            from twocaptcha import TwoCaptcha
            
            # Solve using 2Captcha
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            result = solver.text(text=captcha_text)
            
            # Find the input field
            input_field = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha' i]")
            input_field.clear()
            input_field.send_keys(result["code"])
            
            logger.info("Text CAPTCHA solved with 2Captcha")
            return True
        else:
            return prompt_manual_captcha(driver)
            
    except Exception as e:
        logger.error(f"Error solving text CAPTCHA: {str(e)}")
        return prompt_manual_captcha(driver)

def prompt_manual_captcha(driver: WebDriver) -> bool:
    """
    Prompt the user to manually solve the CAPTCHA.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if user indicates CAPTCHA is solved, False otherwise
    """
    logger.info("Prompting user to solve CAPTCHA manually")
    
    # Display message to the user
    driver.execute_script("""
        var div = document.createElement('div');
        div.id = 'manual_captcha_notice';
        div.style.position = 'fixed';
        div.style.top = '10px';
        div.style.left = '10px';
        div.style.padding = '10px';
        div.style.background = 'rgba(255, 255, 0, 0.8)';
        div.style.border = '2px solid red';
        div.style.zIndex = '9999';
        div.style.borderRadius = '5px';
        div.innerHTML = '<p>Please solve the CAPTCHA manually.</p><button id="captcha_solved_btn" style="padding: 5px 10px;">I\'ve Solved It</button>';
        document.body.appendChild(div);
    """)
    
    # Wait for user to solve the CAPTCHA and click the button
    try:
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "captcha_solved_btn"))
        ).click()
        
        # Remove the notice
        driver.execute_script("""
            var notice = document.getElementById('manual_captcha_notice');
            if (notice) {
                notice.parentNode.removeChild(notice);
            }
        """)
        
        logger.info("User indicated CAPTCHA is solved manually")
        return True
    except TimeoutException:
        logger.error("Timeout waiting for user to solve CAPTCHA")
        return False