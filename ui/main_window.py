"""
Main window for the Neuroformic application.
"""
import os
import sys
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor

from core.session import SessionManager
from ui.styles import *
from ui.dialogs import SettingsDialog, AboutDialog
from utils.logger import get_logger

logger = get_logger()

class WorkerThread(QThread):
    """Worker thread for background processing."""
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, url):
        """
        Initialize worker thread.
        
        Args:
            url: URL to process
        """
        super().__init__()
        self.url = url
    
    def run(self):
        """
        Run the worker thread.
        """
        try:
            self.update_signal.emit("Starting session...")
            
            # Initialize session manager
            session = SessionManager()
            session.start_selenium()
            
            self.update_signal.emit(f"Navigating to {self.url}...")
            success = session.navigate(self.url)
            
            if not success:
                self.finished_signal.emit(False, f"Failed to navigate to {self.url}")
                return
            
            self.update_signal.emit("Attempting to authenticate...")
            auth_success = session.authenticate(self.url)
            
            if not auth_success:
                self.update_signal.emit("Authentication failed, continuing anyway...")
            else:
                self.update_signal.emit("Authentication successful!")
            
            self.update_signal.emit("Analyzing page for forms...")
            # Placeholder for form detection and filling logic
            # This would call to other modules to process the form
            
            self.update_signal.emit("Process completed successfully!")
            session.save_session_data()
            session.close()
            
            self.finished_signal.emit(True, "Form processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error in worker thread: {str(e)}")
            self.finished_signal.emit(False, f"Error: {str(e)}")


class NeuroformicApp(QtWidgets.QWidget):
    """Main application window for Neuroformic."""
    
    def __init__(self):
        """
        Initialize the application window.
        """
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Neuroformic")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Window dragging variables
        self.draggable = True
        self.drag_position = None
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """
        Initialize the user interface.
        """
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container frame (with background)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setStyleSheet(MAIN_CONTAINER_STYLE)
        frame_layout = QtWidgets.QVBoxLayout(self.main_frame)
        
        # Title bar
        title_bar = QtWidgets.QHBoxLayout()
        
        # Title label
        title_label = QtWidgets.QLabel("Neuroformic")
        title_label.setStyleSheet(TITLE_LABEL_STYLE)
        title_bar.addWidget(title_label)
        
        # Spacer
        title_bar.addStretch()
        
        # Settings button
        settings_button = QtWidgets.QPushButton("⚙")
        settings_button.setStyleSheet(SETTINGS_BUTTON_STYLE)
        settings_button.setFixedSize(24, 24)
        settings_button.setCursor(QCursor(Qt.PointingHandCursor))
        settings_button.clicked.connect(self.show_settings)
        title_bar.addWidget(settings_button)
        
        # Minimize button
        minimize_button = QtWidgets.QPushButton("_")
        minimize_button.setStyleSheet(MINIMIZE_BUTTON_STYLE)
        minimize_button.setFixedSize(24, 24)
        minimize_button.setCursor(QCursor(Qt.PointingHandCursor))
        minimize_button.clicked.connect(self.showMinimized)
        title_bar.addWidget(minimize_button)
        
        # Close button
        close_button = QtWidgets.QPushButton("×")
        close_button.setStyleSheet(CLOSE_BUTTON_STYLE)
        close_button.setFixedSize(24, 24)
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        frame_layout.addLayout(title_bar)
        
        # Input area
        input_layout = QtWidgets.QHBoxLayout()
        
        # URL input field
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("Enter form URL...")
        self.url_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.url_input.returnPressed.connect(self.start_process)
        input_layout.addWidget(self.url_input)
        
        # Search button
        search_button = QtWidgets.QPushButton("🔍")
        search_button.setStyleSheet(SEARCH_BUTTON_STYLE)
        search_button.setFixedSize(30, 30)
        search_button.setCursor(QCursor(Qt.PointingHandCursor))
        search_button.clicked.connect(self.start_process)
        input_layout.addWidget(search_button)
        
        frame_layout.addLayout(input_layout)
        
        # Status area
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet(STATUS_LABEL_STYLE)
        frame_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLE)
        frame_layout.addWidget(self.progress_bar)
        
        # Log output area
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(LOG_OUTPUT_STYLE)
        self.log_output.setFixedHeight(150)
        frame_layout.addWidget(self.log_output)
        
        # Button area
        button_layout = QtWidgets.QHBoxLayout()
        
        # Start button
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.setStyleSheet(BUTTON_STYLE)
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.clicked.connect(self.start_process)
        button_layout.addWidget(self.start_button)
        
        # Stop button
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.setStyleSheet(BUTTON_STYLE)
        self.stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_process)
        button_layout.addWidget(self.stop_button)
        
        frame_layout.addLayout(button_layout)
        
        # Add main frame to main layout
        main_layout.addWidget(self.main_frame)
        
        # Size and position
        self.resize(500, 400)
        self.center_on_screen()
        
        # Worker thread
        self.worker = None
    
    def center_on_screen(self):
        """
        Center the window on the screen.
        """
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def start_process(self):
        """
        Start the form automation process.
        """
        url = self.url_input.text().strip()
        
        if not url:
            self.log_output.append("Please enter a URL")
            return
        
        # Add http:// prefix if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Processing...")
        self.log_output.clear()
        self.log_output.append(f"Starting process for URL: {url}")
        
        # Start worker thread
        self.worker = WorkerThread(url)
        self.worker.update_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.process_finished)
        self.worker.start()
    
    def stop_process(self):
        """
        Stop the form automation process.
        """
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.update_log("Process stopped by user")
            self.process_finished(False, "Process stopped by user")
    
    def update_log(self, message):
        """
        Update the log output with a message.
        
        Args:
            message: Message to display
        """
        self.log_output.append(message)
        # Scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def process_finished(self, success, message):
        """
        Handle process completion.
        
        Args:
            success: Whether the process completed successfully
            message: Completion message
        """
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Completed")
        else:
            self.status_label.setText("Failed")
        
        self.update_log(message)
    
    def show_settings(self):
        """
        Show the settings dialog.
        """
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events for window dragging.
        
        Args:
            event: Mouse press event
        """
        if event.button() == Qt.LeftButton and self.draggable:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events for window dragging.
        
        Args:
            event: Mouse move event
        """
        if event.buttons() == Qt.LeftButton and self.drag_position and self.draggable:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events for window dragging.
        
        Args:
            event: Mouse release event
        """
        self.drag_position = None
        event.accept()