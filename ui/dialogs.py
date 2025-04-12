"""
Dialog windows for the Neuroformic application.
"""
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar
from PyQt5.QtCore import Qt, QTimer

from config import (
    UI_BACKGROUND_COLOR,
    UI_ACCENT_COLOR,
    UI_ACCENT_COLOR_HOVER,
    UI_BORDER_RADIUS,
    UI_FONT_COLOR
)
from utils.logger import get_logger

logger = get_logger()

class BaseDialog(QDialog):
    """Base dialog with transparent background and styling."""
    
    def __init__(self, parent=None, title="Neuroformic"):
        """
        Initialize base dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Setup main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create title bar
        title_bar = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {UI_FONT_COLOR}; font-size: 16px; font-weight: bold;")
        
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(f"""
            QPushButton {{
                color: {UI_FONT_COLOR};
                background-color: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: rgba(255, 100, 100, 200);
            }}
        """)
        close_button.clicked.connect(self.close)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(close_button)
        
        self.main_layout.addLayout(title_bar)
        
        # Add a separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {UI_ACCENT_COLOR};")
        self.main_layout.addWidget(separator)
        
        # Create content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(self.content_layout)
        
        # Set dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {UI_BACKGROUND_COLOR};
                border: 2px solid {UI_ACCENT_COLOR};
                border-radius: {UI_BORDER_RADIUS};
            }}
            QLabel {{
                color: {UI_FONT_COLOR};
            }}
            QPushButton {{
                color: {UI_FONT_COLOR};
                background-color: rgba(0, 255, 0, 30);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {UI_ACCENT_COLOR_HOVER};
            }}
        """)
        
        # Position dialog
        self.position_center()
    
    def position_center(self):
        """Position dialog in the center of the parent or screen."""
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.x() + (parent_geo.width() - self.width()) // 2,
                parent_geo.y() + (parent_geo.height() - self.height()) // 2
            )
        else:
            # Center on screen
            screen_geo = QtWidgets.QApplication.desktop().screenGeometry()
            self.move(
                (screen_geo.width() - self.width()) // 2,
                (screen_geo.height() - self.height()) // 2
            )
    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

class StatusDialog(BaseDialog):
    """Dialog for displaying process status and logs."""
    
    def __init__(self, parent=None, title="Processing Status"):
        """
        Initialize status dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent, title)
        self.resize(500, 300)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                text-align: center;
                color: {UI_FONT_COLOR};
                background-color: rgba(0, 0, 0, 60);
            }}
            QProgressBar::chunk {{
                background-color: {UI_ACCENT_COLOR};
                border-radius: 5px;
            }}
        """)
        self.content_layout.addWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.status_label)
        
        # Add log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
            }}
        """)
        self.content_layout.addWidget(self.log_area)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.close_button)
        
        self.content_layout.addLayout(button_layout)
    
    def update_progress(self, value, status_text=None):
        """
        Update progress bar and status text.
        
        Args:
            value: Progress value (0-100)
            status_text: Optional status text to display
        """
        self.progress_bar.setValue(value)
        
        if status_text:
            self.status_label.setText(status_text)
        
        # When complete, enable close button and disable cancel
        if value == 100:
            self.close_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
    
    def add_log(self, text):
        """
        Add text to the log area.
        
        Args:
            text: Text to add
        """
        self.log_area.append(text)
        # Scroll to bottom
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class ConfirmDialog(BaseDialog):
    """Dialog for confirming actions."""
    
    def __init__(self, parent=None, title="Confirm", message="Are you sure?"):
        """
        Initialize confirmation dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Confirmation message
        """
        super().__init__(parent, title)
        self.resize(400, 150)
        
        # Add message
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.message_label)
        
        # Add spacer
        self.content_layout.addStretch()
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 255, 0, 40);
            }}
            QPushButton:hover {{
                background-color: rgba(0, 255, 0, 80);
            }}
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        self.content_layout.addLayout(button_layout)

class LoginConfigDialog(BaseDialog):
    """Dialog for configuring login settings."""
    
    def __init__(self, parent=None, title="Login Configuration", url=""):
        """
        Initialize login configuration dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            url: Target URL
        """
        super().__init__(parent, title)
        self.resize(450, 280)
        
        from PyQt5.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QComboBox
        
        # Create form layout
        form_layout = QFormLayout()
        
        # URL field
        self.url_field = QLineEdit(url)
        self.url_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
        """)
        form_layout.addRow("URL:", self.url_field)
        
        # Authentication type
        self.auth_type = QComboBox()
        self.auth_type.addItems(["Credentials", "Cookies", "Browser Cookies"])
        self.auth_type.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(0, 0, 0, 180);
                border: 1px solid {UI_ACCENT_COLOR};
                selection-background-color: {UI_ACCENT_COLOR};
                color: {UI_FONT_COLOR};
            }}
        """)
        self.auth_type.currentIndexChanged.connect(self._on_auth_type_changed)
        form_layout.addRow("Authentication:", self.auth_type)
        
        # Login fields
        self.username_field = QLineEdit()
        self.username_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
        """)
        form_layout.addRow("Username:", self.username_field)
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
        """)
        form_layout.addRow("Password:", self.password_field)
        
        # Browser selection (for browser cookies)
        self.browser_select = QComboBox()
        self.browser_select.addItems(["Chrome", "Firefox", "Edge"])
        self.browser_select.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(0, 0, 0, 180);
                border: 1px solid {UI_ACCENT_COLOR};
                selection-background-color: {UI_ACCENT_COLOR};
                color: {UI_FONT_COLOR};
            }}
        """)
        self.browser_select.hide()  # Hidden by default
        form_layout.addRow("Browser:", self.browser_select)
        
        # Save credentials option
        self.save_credentials = QCheckBox("Save credentials for future use")
        self.save_credentials.setStyleSheet(f"""
            QCheckBox {{
                color: {UI_FONT_COLOR};
            }}
            QCheckBox::indicator {{
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 2px;
                background-color: rgba(0, 0, 0, 60);
            }}
            QCheckBox::indicator:checked {{
                background-color: {UI_ACCENT_COLOR};
            }}
        """)
        form_layout.addRow("", self.save_credentials)
        
        self.content_layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.confirm_button = QPushButton("Connect")
        self.confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        self.content_layout.addLayout(button_layout)
        
        # Initialize visibility based on default auth type
        self._on_auth_type_changed(0)
    
    def _on_auth_type_changed(self, index):
        """
        Handle auth type selection changes.
        
        Args:
            index: Selected index
        """
        if index == 0:  # Credentials
            self.username_field.show()
            self.password_field.show()
            self.browser_select.hide()
            self.save_credentials.show()
        elif index == 1:  # Cookies
            self.username_field.hide()
            self.password_field.hide()
            self.browser_select.hide()
            self.save_credentials.hide()
        elif index == 2:  # Browser Cookies
            self.username_field.hide()
            self.password_field.hide()
            self.browser_select.show()
            self.save_credentials.show()
    
    def get_config(self):
        """
        Get the login configuration settings.
        
        Returns:
            dict: Configuration settings
        """
        auth_type = self.auth_type.currentText().lower().replace(" ", "_")
        
        config = {
            'url': self.url_field.text(),
            'auth_type': auth_type,
            'save_credentials': self.save_credentials.isChecked()
        }
        
        if auth_type == 'credentials':
            config['username'] = self.username_field.text()
            config['password'] = self.password_field.text()
        elif auth_type == 'browser_cookies':
            config['browser'] = self.browser_select.currentText().lower()
        
        return config

# Add the missing dialog classes
class SettingsDialog(BaseDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, "Settings")
        self.resize(450, 350)
        
        from PyQt5.QtWidgets import QFormLayout, QLineEdit, QCheckBox, QComboBox, QTabWidget, QWidget, QSpinBox
        
        # Create tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {UI_ACCENT_COLOR};
                background-color: rgba(0, 0, 0, 30);
                border-radius: 5px;
            }}
            QTabBar::tab {{
                background-color: rgba(0, 0, 0, 60);
                color: {UI_FONT_COLOR};
                border: 1px solid {UI_ACCENT_COLOR};
                border-bottom-color: {UI_ACCENT_COLOR};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background-color: rgba(0, 255, 0, 30);
            }}
            QTabBar::tab:selected {{
                border-bottom-color: rgba(0, 0, 0, 30);
            }}
        """)
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Default browser
        default_browser = QComboBox()
        default_browser.addItems(["Chrome", "Firefox", "Edge"])
        default_browser.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(0, 0, 0, 180);
                border: 1px solid {UI_ACCENT_COLOR};
                selection-background-color: {UI_ACCENT_COLOR};
                color: {UI_FONT_COLOR};
            }}
        """)
        general_layout.addRow("Default Browser:", default_browser)
        
        # Headless mode
        headless_mode = QCheckBox("Run browser in headless mode")
        headless_mode.setStyleSheet(f"""
            QCheckBox {{
                color: {UI_FONT_COLOR};
            }}
            QCheckBox::indicator {{
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 2px;
                background-color: rgba(0, 0, 0, 60);
            }}
            QCheckBox::indicator:checked {{
                background-color: {UI_ACCENT_COLOR};
            }}
        """)
        general_layout.addRow("", headless_mode)
        
        # Screenshot directory
        screenshot_dir = QLineEdit()
        screenshot_dir.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
        """)
        browse_button = QPushButton("Browse...")
        browse_button.setFixedWidth(80)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(screenshot_dir)
        dir_layout.addWidget(browse_button)
        
        general_layout.addRow("Screenshot Directory:", dir_layout)
        
        # AI settings tab
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        
        # AI model
        ai_model = QComboBox()
        ai_model.addItems(["GPT-4", "Claude", "Gemini", "Local LLM"])
        ai_model.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(0, 0, 0, 180);
                border: 1px solid {UI_ACCENT_COLOR};
                selection-background-color: {UI_ACCENT_COLOR};
                color: {UI_FONT_COLOR};
            }}
        """)
        ai_layout.addRow("AI Model:", ai_model)
        
        # API Key
        api_key = QLineEdit()
        api_key.setEchoMode(QLineEdit.Password)
        api_key.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
        """)
        ai_layout.addRow("API Key:", api_key)
        
        # Confidence threshold
        confidence = QSpinBox()
        confidence.setRange(50, 100)
        confidence.setValue(80)
        confidence.setSuffix("%")
        confidence.setStyleSheet(f"""
            QSpinBox {{
                background-color: rgba(0, 0, 0, 60);
                border: 1px solid {UI_ACCENT_COLOR};
                border-radius: 5px;
                color: {UI_FONT_COLOR};
                padding: 5px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {UI_ACCENT_COLOR};
                width: 16px;
                border-radius: 3px;
            }}
        """)
        ai_layout.addRow("Confidence Threshold:", confidence)
        
        # Add tabs to widget
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(ai_tab, "AI Settings")
        
        self.content_layout.addWidget(tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        self.content_layout.addLayout(button_layout)

class AboutDialog(BaseDialog):
    """Dialog for showing application information."""
    
    def __init__(self, parent=None):
        """
        Initialize about dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, "About Neuroformic")
        self.resize(450, 300)
        
        # App logo/icon (placeholder)
        logo_label = QLabel()
        logo_label.setFixedSize(100, 100)
        logo_label.setStyleSheet(f"""
            background-color: rgba(0, 255, 0, 40);
            border-radius: 50px;
            border: 2px solid {UI_ACCENT_COLOR};
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setText("🤖")
        
        # Set custom font for logo
        logo_font = QtGui.QFont()
        logo_font.setPointSize(40)
        logo_label.setFont(logo_font)
        
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        self.content_layout.addLayout(logo_layout)
        
        # App name and version
        name_label = QLabel("Neuroformic")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: rgba(0, 255, 0, 200);")
        
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        
        self.content_layout.addWidget(name_label)
        self.content_layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "Neuroformic is an AI-powered intelligent form filler with secure login automation. "
            "It uses advanced AI techniques to understand and fill out complex forms automatically."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        
        self.content_layout.addWidget(desc_label)
        
        # Copyright info
        copyright_label = QLabel("© 2025 Neuroformic Team. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 10px;")
        
        self.content_layout.addWidget(copyright_label)
        
        # Add button
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        self.content_layout.addLayout(button_layout)