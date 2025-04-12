"""
Style definitions for the Neuroformic UI.
"""
from PyQt5.QtCore import Qt

# Main application styles
APP_STYLE = """
    QWidget {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
    }
"""

# Transparent window style
TRANSPARENT_WINDOW_STYLE = """
    QWidget {
        background-color: transparent;
    }
"""

# Main container style
MAIN_CONTAINER_STYLE = """
    QFrame {
        background-color: rgba(0, 0, 0, 120);
        border: 2px solid rgba(0, 255, 0, 120);
        border-radius: 15px;
    }
"""

# Search input style
SEARCH_INPUT_STYLE = """
    QLineEdit {
        background-color: rgba(0, 0, 0, 150);
        border: 1px solid rgba(0, 255, 0, 100);
        border-radius: 10px;
        padding: 8px;
        padding-right: 35px;
        color: white;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid rgba(0, 255, 0, 200);
    }
"""

# Search button style
SEARCH_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        color: rgba(0, 255, 0, 150);
        font-size: 18px;
    }
    QPushButton:hover {
        color: rgba(0, 255, 0, 200);
    }
    QPushButton:pressed {
        color: rgba(0, 255, 0, 100);
    }
"""

# Status label style
STATUS_LABEL_STYLE = """
    QLabel {
        color: rgba(255, 255, 255, 200);
        font-size: 12px;
        padding: 5px;
    }
"""

# Log output style
LOG_OUTPUT_STYLE = """
    QTextEdit {
        background-color: rgba(0, 0, 0, 150);
        border: 1px solid rgba(0, 255, 0, 100);
        border-radius: 10px;
        padding: 10px;
        color: white;
        font-family: Consolas, monospace;
        font-size: 12px;
    }
"""

# Button style
BUTTON_STYLE = """
    QPushButton {
        background-color: rgba(0, 200, 0, 100);
        border: 1px solid rgba(0, 255, 0, 100);
        border-radius: 10px;
        padding: 8px 16px;
        color: white;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: rgba(0, 200, 0, 150);
        border: 1px solid rgba(0, 255, 0, 150);
    }
    QPushButton:pressed {
        background-color: rgba(0, 150, 0, 100);
    }
    QPushButton:disabled {
        background-color: rgba(100, 100, 100, 100);
        border: 1px solid rgba(150, 150, 150, 100);
        color: rgba(200, 200, 200, 150);
    }
"""

# Title label style
TITLE_LABEL_STYLE = """
    QLabel {
        color: rgba(0, 255, 0, 200);
        font-size: 18px;
        font-weight: bold;
    }
"""

# Progress bar style
PROGRESS_BAR_STYLE = """
    QProgressBar {
        border: 1px solid rgba(0, 255, 0, 100);
        border-radius: 5px;
        text-align: center;
        background-color: rgba(0, 0, 0, 150);
    }
    QProgressBar::chunk {
        background-color: rgba(0, 255, 0, 150);
    }
"""

# Close button style
CLOSE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        color: rgba(255, 0, 0, 150);
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        color: rgba(255, 0, 0, 200);
    }
    QPushButton:pressed {
        color: rgba(255, 0, 0, 100);
    }
"""

# Minimize button style
MINIMIZE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        color: rgba(255, 255, 0, 150);
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        color: rgba(255, 255, 0, 200);
    }
    QPushButton:pressed {
        color: rgba(255, 255, 0, 100);
    }
"""

# Settings button style
SETTINGS_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        color: rgba(0, 200, 255, 150);
        font-size: 16px;
    }
    QPushButton:hover {
        color: rgba(0, 200, 255, 200);
    }
    QPushButton:pressed {
        color: rgba(0, 200, 255, 100);
    }
"""