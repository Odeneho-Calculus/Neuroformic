"""
Screenshot utilities for capturing form elements and pages.
"""
import os
import time
from datetime import datetime
from PIL import Image
import cv2
import numpy as np
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from config import SCREENSHOT_DIR
from utils.logger import get_logger

logger = get_logger()

def capture_full_page(driver: WebDriver, filename: str = None) -> str:
    """
    Capture a screenshot of the entire page.
    
    Args:
        driver: Selenium WebDriver instance
        filename: Optional custom filename
        
    Returns:
        str: Path to the saved screenshot
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"page_{timestamp}.png"
    
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(filepath)
    logger.info(f"Captured full page screenshot: {filepath}")
    return filepath

def capture_element(driver: WebDriver, element: WebElement, filename: str = None) -> str:
    """
    Capture a screenshot of a specific element.
    
    Args:
        driver: Selenium WebDriver instance
        element: WebElement to capture
        filename: Optional custom filename
        
    Returns:
        str: Path to the saved screenshot
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"element_{timestamp}.png"
    
    # Get element location and size
    location = element.location
    size = element.size
    
    # Capture full page screenshot
    temp_filepath = os.path.join(SCREENSHOT_DIR, "temp.png")
    driver.save_screenshot(temp_filepath)
    
    # Crop the element from the full screenshot
    full_img = Image.open(temp_filepath)
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    
    # Account for device pixel ratio (for high-DPI screens)
    # This is a simplified approach and might need to be adjusted
    pixel_ratio = 1
    try:
        pixel_ratio = driver.execute_script("return window.devicePixelRatio;") or 1
    except:
        pass
    
    if pixel_ratio != 1:
        left = int(left * pixel_ratio)
        top = int(top * pixel_ratio)
        right = int(right * pixel_ratio)
        bottom = int(bottom * pixel_ratio)
    
    element_img = full_img.crop((left, top, right, bottom))
    
    # Save the cropped image
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    element_img.save(filepath)
    
    # Clean up the temporary file
    os.remove(temp_filepath)
    
    logger.info(f"Captured element screenshot: {filepath}")
    return filepath

def enhance_image_for_ocr(image_path: str) -> np.ndarray:
    """
    Enhance an image for better OCR results.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        np.ndarray: Enhanced image
    """
    # Read the image
    image = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Noise removal
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Save the enhanced image
    enhanced_path = image_path.replace('.png', '_enhanced.png')
    cv2.imwrite(enhanced_path, opening)
    
    logger.debug(f"Enhanced image saved to: {enhanced_path}")
    return opening