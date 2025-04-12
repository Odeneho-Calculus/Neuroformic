"""
Form handling module for interacting with web forms.
"""
from typing import List, Dict, Any, Optional, Tuple
import time
import re

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

from core.nlp import QuestionAnalyzer
from utils.logger import get_logger
from utils.helpers import random_delay
from utils.screenshot import capture_element, enhance_image_for_ocr
import pytesseract

logger = get_logger()

class FormHandler:
    """Handle interaction with web forms."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize form handler.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.nlp = QuestionAnalyzer()
    
    def detect_form_elements(self) -> Dict[str, List[WebElement]]:
        """
        Detect form elements on the current page.
        
        Returns:
            Dict[str, List[WebElement]]: Dictionary of form elements by type
        """
        logger.info("Detecting form elements")
        
        form_elements = {
            "text_inputs": self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='number']"),
            "radio_buttons": self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']"),
            "checkboxes": self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"),
            "dropdowns": self.driver.find_elements(By.TAG_NAME, "select"),
            "textareas": self.driver.find_elements(By.TAG_NAME, "textarea"),
            "submit_buttons": self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        }
        
        # Log the number of elements found
        for element_type, elements in form_elements.items():
            logger.info(f"Found {len(elements)} {element_type}")
        
        return form_elements
    
    def extract_question_from_element(self, element: WebElement) -> str:
        """
        Extract the question text associated with a form element.
        
        Args:
            element: WebElement to extract question from
            
        Returns:
            str: Extracted question text
        """
        question_text = ""
        
        # Method 1: Check for label element
        element_id = element.get_attribute("id")
        if element_id:
            # Try to find label with for attribute
            try:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                question_text = label.text.strip()
                logger.debug(f"Found question from label: {question_text}")
            except NoSuchElementException:
                pass
        
        # Method 2: Check parent elements for text
        if not question_text:
            try:
                # Try to get text from parent element
                parent = element.find_element(By.XPATH, "..")
                parent_text = parent.text.strip()
                
                # If parent contains the element's text as well, try to extract just the question
                if parent_text:
                    # Remove the element's own text/value if present
                    element_text = element.get_attribute("value") or element.text
                    if element_text and element_text in parent_text:
                        parent_text = parent_text.replace(element_text, "").strip()
                    
                    question_text = parent_text
                    logger.debug(f"Found question from parent: {question_text}")
            except:
                pass
        
        # Method 3: Check nearby heading elements
        if not question_text:
            try:
                # Look for nearby heading elements
                heading = element.find_element(By.XPATH, "./preceding::h1[1] | ./preceding::h2[1] | ./preceding::h3[1] | ./preceding::h4[1]")
                question_text = heading.text.strip()
                logger.debug(f"Found question from heading: {question_text}")
            except:
                pass
        
        # Method 4: OCR as a last resort
        if not question_text:
            try:
                # Take a screenshot of the surrounding area
                screenshot_path = capture_element(self.driver, element.find_element(By.XPATH, ".."))
                
                # Enhance the image for OCR
                enhanced_image = enhance_image_for_ocr(screenshot_path)
                
                # Extract text using OCR
                ocr_text = pytesseract.image_to_string(enhanced_image)
                if ocr_text:
                    question_text = ocr_text.strip()
                    logger.debug(f"Found question using OCR: {question_text}")
            except Exception as e:
                logger.warning(f"OCR failed: {str(e)}")
        
        # Cleanup the question text
        if question_text:
            # Remove any trailing colons, asterisks (required field indicators), etc.
            question_text = re.sub(r'[\:|\*|\n]+$', '', question_text).strip()
        
        return question_text
    
    def extract_options_from_radio_group(self, radio_buttons: List[WebElement]) -> List[str]:
        """
        Extract option text from a group of radio buttons.
        
        Args:
            radio_buttons: List of radio button WebElements
            
        Returns:
            List[str]: List of option texts
        """
        options = []
        
        for radio in radio_buttons:
            option_text = ""
            
            # Method 1: Check for label
            radio_id = radio.get_attribute("id")
            if radio_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                    option_text = label.text.strip()
                except:
                    pass
            
            # Method 2: Check for nearby text node
            if not option_text:
                try:
                    option_text = radio.find_element(By.XPATH, "following-sibling::text()[1]").strip()
                except:
                    pass
            
            # Method A3: If we still don't have the text, use the value attribute
            if not option_text:
                option_text = radio.get_attribute("value") or ""
            
            if option_text:
                options.append(option_text)
        
        return options
    
    def identify_radio_groups(self) -> List[Dict[str, Any]]:
        """
        Identify groups of radio buttons and their associated questions.
        
        Returns:
            List[Dict[str, Any]]: List of radio groups with questions and options
        """
        logger.info("Identifying radio button groups")
        
        # Get all radio buttons
        all_radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        
        # Group radio buttons by name attribute
        radio_groups = {}
        for radio in all_radio_buttons:
            name = radio.get_attribute("name")
            if name:
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)
        
        # Process each group
        result = []
        for name, radios in radio_groups.items():
            if len(radios) > 1:  # Only consider groups with multiple options
                # Extract question
                question_text = self.extract_question_from_element(radios[0])
                
                # Extract options
                options = self.extract_options_from_radio_group(radios)
                
                if question_text and options:
                    result.append({
                        "name": name,
                        "question": question_text,
                        "options": options,
                        "elements": radios
                    })
                    logger.info(f"Identified radio group '{name}' with question: {question_text}")
                    logger.debug(f"Options: {options}")
        
        logger.info(f"Identified {len(result)} radio button groups")
        return result
    
    def auto_fill_form(self, submit: bool = False) -> Dict[str, Any]:
        """
        Automatically fill the form with intelligent responses.
        
        Args:
            submit: Whether to submit the form after filling
            
        Returns:
            Dict[str, Any]: Summary of actions taken
        """
        logger.info("Starting auto-fill process")
        
        # Track actions for reporting
        actions = {
            "radio_groups_answered": 0,
            "checkboxes_checked": 0,
            "text_inputs_filled": 0,
            "dropdowns_selected": 0,
            "textareas_filled": 0,
            "submitted": False,
            "details": []
        }
        
        # Identify radio button groups
        radio_groups = self.identify_radio_groups()
        
        # Process each radio group
        for group in radio_groups:
            try:
                # Analyze the question and predict the best answer
                best_index, confidence = self.nlp.predict_best_answer(group["question"], group["options"])
                
                # Select the radio button
                if 0 <= best_index < len(group["elements"]):
                    element = group["elements"][best_index]
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    random_delay(0.5, 1.5)
                    
                    try:
                        element.click()
                        actions["radio_groups_answered"] += 1
                        
                        # Record the action
                        actions["details"].append({
                            "type": "radio",
                            "question": group["question"],
                            "selected_option": group["options"][best_index],
                            "confidence": confidence
                        })
                        
                        logger.info(f"Selected option '{group['options'][best_index]}' for question '{group['question']}'")
                    except ElementNotInteractableException:
                        # If direct click fails, try JavaScript click
                        self.driver.execute_script("arguments[0].click();", element)
                        actions["radio_groups_answered"] += 1
                        logger.info(f"Selected option '{group['options'][best_index]}' for question '{group['question']}' using JavaScript")
            except Exception as e:
                logger.error(f"Error processing radio group '{group['name']}': {str(e)}")
        
        # Submit the form if requested
        if submit:
            try:
                # Find and click the submit button
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                if submit_buttons:
                    # Use the first submit button
                    submit_button = submit_buttons[0]
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                    random_delay(0.5, 1.5)
                    submit_button.click()
                    actions["submitted"] = True
                    logger.info("Form submitted successfully")
                else:
                    logger.warning("No submit button found")
            except Exception as e:
                logger.error(f"Error submitting form: {str(e)}")
        
        return actions