"""
Driver Switch Confirmation Dialog with Countdown
Shows confirmation popup with 20-second countdown timer
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class DriverSwitchConfirmationDialog(QDialog):
    """
    Confirmation dialog for driver switching with countdown timer
    Automatically reverts if not confirmed within timeout period
    """
    
    def __init__(self, switch_info, switch_manager, parent=None):
        super().__init__(parent)
        self.switch_info = switch_info
        self.switch_manager = switch_manager
        self.confirmed = False
        self.cancelled = False
        
        self.timeout_seconds = switch_info.get('timeout_seconds', 20)
        self.remaining_seconds = self.timeout_seconds
        
        self.init_ui()
        self.start_countdown()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Driver Switch Confirmation Required")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚠ Driver Switch Confirmation")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Device info
        device_name = self.switch_info.get('device_name', 'Unknown Device')
        device_label = QLabel(f"Device: {device_name}")
        device_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(device_label)
        
        # Driver change info
        old_driver = self.switch_info.get('old_driver', {})
        new_driver = self.switch_info.get('new_driver', {})
        
        change_layout = QVBoxLayout()
        change_layout.setSpacing(5)
        
        from_label = QLabel(f"From: {old_driver.get('name', 'Unknown')} "
                           f"v{old_driver.get('version', '?')}")
        from_label.setStyleSheet("color: #888; padding-left: 20px;")
        change_layout.addWidget(from_label)
        
        to_label = QLabel(f"To:   {new_driver.get('name', 'Unknown')} "
                         f"v{new_driver.get('version', '?')}")
        to_label.setStyleSheet("color: #0a0; font-weight: bold; padding-left: 20px;")
        change_layout.addWidget(to_label)
        
        layout.addLayout(change_layout)
        
        # Warning message
        warning = QLabel(
            "⚠ Please confirm this driver change within the time limit.\n"
            "If not confirmed, the system will automatically revert to the\n"
            "driver that has been assigned the longest for stability."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 5px;")
        layout.addWidget(warning)
        
        # Countdown display
        self.countdown_label = QLabel(f"Time remaining: {self.remaining_seconds} seconds")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        countdown_font = QFont()
        countdown_font.setPointSize(14)
        countdown_font.setBold(True)
        self.countdown_label.setFont(countdown_font)
        self.countdown_label.setStyleSheet("color: #d9534f; padding: 10px;")
        layout.addWidget(self.countdown_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.timeout_seconds)
        self.progress_bar.setValue(self.timeout_seconds)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #d9534f;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.confirm_button = QPushButton("✓ Confirm Driver Switch")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.confirm_button.clicked.connect(self.confirm_switch)
        button_layout.addWidget(self.confirm_button)
        
        self.cancel_button = QPushButton("✗ Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_switch)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Info label
        info_label = QLabel(
            "System will automatically revert if time expires without confirmation."
        )
        info_label.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
    
    def start_countdown(self):
        """Start the countdown timer"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
    
    def update_countdown(self):
        """Update the countdown display"""
        self.remaining_seconds -= 1
        
        # Update labels and progress bar
        self.countdown_label.setText(f"Time remaining: {self.remaining_seconds} seconds")
        self.progress_bar.setValue(self.remaining_seconds)
        
        # Change color as time runs out
        if self.remaining_seconds <= 5:
            self.countdown_label.setStyleSheet("color: #ff0000; padding: 10px; font-size: 16pt;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #ff0000;
                    border-radius: 5px;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #ff0000;
                }
            """)
        elif self.remaining_seconds <= 10:
            self.countdown_label.setStyleSheet("color: #ff6600; padding: 10px;")
        
        # Check if time expired
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.timeout_expired()
    
    def confirm_switch(self):
        """Handle confirmation button click"""
        self.timer.stop()
        
        switch_id = self.switch_info.get('switch_id')
        result = self.switch_manager.confirm_driver_switch(switch_id)
        
        if result.get('success'):
            self.confirmed = True
            
            QMessageBox.information(
                self,
                "Driver Switch Confirmed",
                f"Driver switch confirmed successfully!\n\n"
                f"New driver: {result['new_driver']['name']} "
                f"v{result['new_driver']['version']}"
            )
            
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Confirmation Failed",
                f"Failed to confirm driver switch:\n{result.get('error', 'Unknown error')}"
            )
    
    def cancel_switch(self):
        """Handle cancel button click"""
        self.timer.stop()
        
        switch_id = self.switch_info.get('switch_id')
        result = self.switch_manager.cancel_driver_switch(switch_id)
        
        self.cancelled = True
        
        QMessageBox.information(
            self,
            "Driver Switch Cancelled",
            "Driver switch has been cancelled.\n"
            "System will remain on the current driver."
        )
        
        self.reject()
    
    def timeout_expired(self):
        """Handle timeout expiration"""
        # Check and revert
        revert_result = self.switch_manager.check_and_revert_expired_switch()
        
        if revert_result:
            QMessageBox.warning(
                self,
                "Driver Switch Timeout",
                f"⚠ Confirmation timeout expired!\n\n"
                f"System automatically reverted to:\n"
                f"{revert_result['reverted_to']['name']} "
                f"v{revert_result['reverted_to']['version']}\n\n"
                f"This is the driver that has been assigned the longest\n"
                f"for maximum stability."
            )
        
        self.reject()
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        if not self.confirmed and not self.cancelled:
            # User tried to close without confirming
            reply = QMessageBox.question(
                self,
                "Confirm Close",
                "Closing this dialog without confirming will cancel the driver switch.\n"
                "Are you sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.timer.stop()
                switch_id = self.switch_info.get('switch_id')
                self.switch_manager.cancel_driver_switch(switch_id)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
