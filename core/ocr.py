"""
OCR utilities for extracting text from web form elements.
"""
import os
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.logger import get_logger
from utils.screenshot import capture_element, enhance_image_for_ocr
from config import TESSERACT_PATH, OCR_CONFIDENCE_THRESHOLD

logger = get_logger()

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_element(driver: WebDriver, element: WebElement) -> str:
    """
    Extract text from a web element using OCR.
    
    Args:
        driver: Selenium WebDriver instance
        element: WebElement to extract text from
        
    Returns:
        str: Extracted text
    """
    logger.info("Extracting text from element using OCR")
    
    # First try to get text directly from the element
    direct_text = element.text.strip()
    if direct_text:
        logger.info(f"Text extracted directly from element: {direct_text}")
        return direct_text
    
    # If direct text extraction fails, use OCR
    try:
        # Capture element screenshot
        screenshot_path = capture_element(driver, element)
        
        # Enhance image for better OCR results
        enhanced_image = enhance_image_for_ocr(screenshot_path)
        
        # Perform OCR
        ocr_text = pytesseract.image_to_string(enhanced_image)
        ocr_text = ocr_text.strip()
        
        if ocr_text:
            logger.info(f"Text extracted via OCR: {ocr_text}")
            return ocr_text
        else:
            logger.warning("OCR could not extract any text from the element")
            return ""
    
    except Exception as e:
        logger.error(f"Error extracting text from element: {str(e)}")
        return ""

def extract_structured_data(driver: WebDriver, element: WebElement) -> Dict[str, Any]:
    """
    Extract structured data from an element using OCR and analysis.
    
    Args:
        driver: Selenium WebDriver instance
        element: WebElement to extract data from
        
    Returns:
        Dict[str, Any]: Structured data extracted from the element
    """
    logger.info("Extracting structured data from element")
    
    try:
        # Capture element screenshot
        screenshot_path = capture_element(driver, element)
        
        # Enhance image for better OCR results
        enhanced_image = enhance_image_for_ocr(screenshot_path)
        
        # Extract data using Tesseract's advanced features
        ocr_data = pytesseract.image_to_data(enhanced_image, output_type=pytesseract.Output.DICT)
        
        # Process the OCR data
        structured_data = {
            'text': [],
            'confidence': [],
            'boxes': []
        }
        
        for i in range(len(ocr_data['text'])):
            # Filter out empty text and low confidence results
            if ocr_data['text'][i].strip() and int(ocr_data['conf'][i]) > OCR_CONFIDENCE_THRESHOLD:
                structured_data['text'].append(ocr_data['text'][i])
                structured_data['confidence'].append(ocr_data['conf'][i])
                structured_data['boxes'].append((
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i]
                ))
        
        logger.info(f"Extracted {len(structured_data['text'])} text elements")
        return structured_data
    
    except Exception as e:
        logger.error(f"Error extracting structured data: {str(e)}")
        return {'text': [], 'confidence': [], 'boxes': []}

def extract_form_questions(driver: WebDriver) -> List[Dict[str, Any]]:
    """
    Extract questions from a form.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List[Dict[str, Any]]: List of extracted questions with their data
    """
    logger.info("Extracting questions from form")
    
    # This is a simplified approach. In a real implementation, you would need to:
    # 1. Identify different form sections
    # 2. Determine which elements are questions vs. options
    # 3. Match options to their parent questions
    
    # Here we'll look for common question containers
    from selenium.webdriver.common.by import By
    
    questions = []
    
    # Look for question containers
    question_containers = driver.find_elements(
        By.CSS_SELECTOR,
        "div.question, fieldset, .form-group, .question-container"
    )
    
    if not question_containers:
        logger.warning("No question containers found, using page elements")
        # Fallback: use general elements that might contain text
        question_containers = driver.find_elements(
            By.CSS_SELECTOR,
            "p, h1, h2, h3, h4, label, div:not(:empty)"
        )
    
    for i, container in enumerate(question_containers):
        # Check if container is visible and has content
        if not container.is_displayed() or not container.text.strip():
            continue
        
        # Extract text from the container
        question_text = extract_text_from_element(driver, container)
        if not question_text:
            continue
        
        # Check for options/radio buttons
        options = []
        try:
            # Look for radio buttons within or after this container
            radio_buttons = container.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            
            for radio in radio_buttons:
                # Try to find label for this radio button
                label = None
                
                # Try by 'for' attribute
                radio_id = radio.get_attribute("id")
                if radio_id:
                    try:
                        label_elem = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                        label = label_elem.text.strip()
                    except:
                        pass
                
                # If no label found, try to find nearest text
                if not label:
                    # Try parent or next sibling
                    try:
                        parent = radio.find_element(By.XPATH, "./..")
                        label = parent.text.strip()
                    except:
                        pass
                
                # If still no label, use value attribute
                if not label:
                    label = radio.get_attribute("value") or f"Option {len(options) + 1}"
                
                options.append({
                    'text': label,
                    'element': radio
                })
        except Exception as e:
            logger.warning(f"Error extracting options for question {i+1}: {str(e)}")
        
        # Add question to the list
        questions.append({
            'text': question_text,
            'element': container,
            'options': options
        })
    
    logger.info(f"Extracted {len(questions)} questions from the form")
    return questions