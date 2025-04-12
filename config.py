"""
Configuration settings for Neuroformic application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Browser settings
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "edge")  # chrome, firefox, edge
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

# Authentication settings
DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")
COOKIE_FILE_PATH = os.getenv("COOKIE_FILE_PATH", "cookies.json")
USE_SAVED_CREDENTIALS = os.getenv("USE_SAVED_CREDENTIALS", "False").lower() == "true"

# OCR settings
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")  # Update according to OS
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "60"))

# NLP settings
NLP_MODEL = os.getenv("NLP_MODEL", "en_core_web_md")  # Default spaCy model
TRANSFORMERS_MODEL = os.getenv("TRANSFORMERS_MODEL", "distilbert-base-uncased")

# CAPTCHA settings
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY", "")
USE_CAPTCHA_SOLVER = os.getenv("USE_CAPTCHA_SOLVER", "False").lower() == "true"

# UI settings
UI_STYLE = "dark"  # dark or light
UI_ACCENT_COLOR = "rgba(0, 255, 0, 120)"  # Green accent
UI_ACCENT_COLOR_HOVER = "rgba(0, 255, 0, 180)"
UI_BACKGROUND_COLOR = "rgba(0, 0, 0, 120)"
UI_BORDER_RADIUS = "15px"
UI_FONT_COLOR = "white"

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "neuroformic.log")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")