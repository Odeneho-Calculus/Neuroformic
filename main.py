"""
Neuroformic - AI-Powered Intelligent Form Filler with Secure Login Automation
Main application entry point.
"""
import sys
import os
from PyQt5 import QtWidgets

from ui.main_window import NeuroformicApp
from utils.logger import setup_logger

def main():
    """
    Main function to initialize and run the Neuroformic application.
    """
    # Set up logging
    logger = setup_logger()
    logger.info("Starting Neuroformic application")
    
    # Create screenshot directory if it doesn't exist
    from config import SCREENSHOT_DIR
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        logger.info(f"Created screenshot directory: {SCREENSHOT_DIR}")
    
    # Initialize and run the GUI application
    app = QtWidgets.QApplication(sys.argv)
    window = NeuroformicApp()
    window.show()
    
    # Exit cleanly
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()