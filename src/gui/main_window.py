"""
Main Window for driver-mgt GUI
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QStatusBar, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from core.hardware_detector import HardwareDetector
from core.driver_manager import DriverManager
from ai.ollama_manager import OllamaManager
from gui.device_tab import DeviceTab

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        
        # Initialize managers
        self.hardware_detector = HardwareDetector(config_manager)
        self.driver_manager = DriverManager(config_manager)
        self.ollama_manager = OllamaManager(config_manager)
        
        # Store detected hardware and device tabs
        self.detected_hardware = []
        self.device_tabs = {}
        
        # Setup UI
        self.init_ui()
        
        # Scan hardware on startup
        QTimer.singleShot(500, self.scan_hardware)
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("driver-mgt - Advanced Linux Driver Management")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("driver-mgt")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_system_info_tab()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Apply theme
        self.apply_theme()
    
    def create_dashboard_tab(self):
        """Create driver management dashboard tab"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Driver Management Dashboard")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        # Scan button
        scan_btn = QPushButton("Scan Hardware")
        scan_btn.clicked.connect(self.scan_hardware)
        header_layout.addWidget(scan_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Hardware table
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(5)
        self.hardware_table.setHorizontalHeaderLabels([
            "Type", "Name", "Vendor", "Current Driver", "Status"
        ])
        self.hardware_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.hardware_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        update_btn = QPushButton("Update Driver")
        update_btn.clicked.connect(self.update_driver)
        button_layout.addWidget(update_btn)
        
        rollback_btn = QPushButton("Rollback Driver")
        rollback_btn.clicked.connect(self.rollback_driver)
        button_layout.addWidget(rollback_btn)
        
        test_btn = QPushButton("Test Driver")
        test_btn.clicked.connect(self.test_driver)
        button_layout.addWidget(test_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tabs.addTab(dashboard, "Dashboard")
    
    def create_system_info_tab(self):
        """Create system information tab"""
        info_tab = QWidget()
        layout = QVBoxLayout(info_tab)
        
        # System info label
        header = QLabel("System Information")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Info table
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.info_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.info_table)
        
        # AI status
        ai_status_layout = QHBoxLayout()
        self.ai_status_label = QLabel("AI Assistant: Checking...")
        ai_status_layout.addWidget(self.ai_status_label)
        
        check_ai_btn = QPushButton("Check AI Status")
        check_ai_btn.clicked.connect(self.check_ai_status)
        ai_status_layout.addWidget(check_ai_btn)
        
        ai_status_layout.addStretch()
        layout.addLayout(ai_status_layout)
        
        self.tabs.addTab(info_tab, "System Info")
        
        # Update system info
        self.update_system_info()
    
    def scan_hardware(self):
        """Scan for hardware"""
        self.statusBar.showMessage("Scanning hardware...")
        
        try:
            self.detected_hardware = self.hardware_detector.detect_all()
            self.update_hardware_table(self.detected_hardware)
            
            # Create device-specific tabs
            self.create_device_tabs()
            
            self.statusBar.showMessage(f"Found {len(self.detected_hardware)} hardware components")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error scanning hardware: {e}")
            self.statusBar.showMessage("Scan failed")
    
    def create_device_tabs(self):
        """Create tabs for each detected device"""
        # Remove old device tabs (keep Dashboard and System Info)
        for device_id, tab_index in list(self.device_tabs.items()):
            self.tabs.removeTab(tab_index)
        
        self.device_tabs.clear()
        
        # Create new device tabs
        for hardware in self.detected_hardware:
            device_name = hardware.get('name', 'Unknown Device')
            device_type = hardware.get('type', 'Device')
            
            # Create device tab
            device_tab = DeviceTab(
                hardware,
                self.driver_manager,
                self.ollama_manager,
                self.config
            )
            
            # Add tab with icon based on type
            tab_label = f"{device_type}: {device_name[:30]}"
            tab_index = self.tabs.addTab(device_tab, tab_label)
            
            # Store tab reference
            device_id = hardware.get('id', device_name)
            self.device_tabs[device_id] = tab_index
    
    def update_hardware_table(self, hardware):
        """Update hardware table with detected hardware"""
        self.hardware_table.setRowCount(len(hardware))
        
        for i, hw in enumerate(hardware):
            self.hardware_table.setItem(i, 0, QTableWidgetItem(hw.get('type', 'Unknown')))
            self.hardware_table.setItem(i, 1, QTableWidgetItem(hw.get('name', 'Unknown')))
            self.hardware_table.setItem(i, 2, QTableWidgetItem(hw.get('vendor', 'Unknown')))
            self.hardware_table.setItem(i, 3, QTableWidgetItem(hw.get('driver', 'None')))
            
            status = "Active" if hw.get('driver') else "No Driver"
            self.hardware_table.setItem(i, 4, QTableWidgetItem(status))
        
        # Add double-click handler to open device tab
        self.hardware_table.cellDoubleClicked.connect(self.open_device_tab)
    
    def update_system_info(self):
        """Update system information table"""
        import platform
        import os
        
        info = [
            ("Operating System", platform.system()),
            ("OS Release", platform.release()),
            ("OS Version", platform.version()),
            ("Machine", platform.machine()),
            ("Processor", platform.processor()),
            ("Python Version", platform.python_version()),
            ("Config Directory", str(self.config.get_config_dir())),
        ]
        
        self.info_table.setRowCount(len(info))
        for i, (key, value) in enumerate(info):
            self.info_table.setItem(i, 0, QTableWidgetItem(key))
            self.info_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def check_ai_status(self):
        """Check AI assistant status"""
        status = self.ollama_manager.get_status()
        
        if status['status'] == 'running':
            self.ai_status_label.setText(f"AI Assistant: Running ({status.get('model', 'N/A')})")
            self.ai_status_label.setStyleSheet("color: green;")
        elif status['status'] == 'not_running':
            self.ai_status_label.setText("AI Assistant: Not Running")
            self.ai_status_label.setStyleSheet("color: orange;")
        else:
            self.ai_status_label.setText(f"AI Assistant: Error - {status.get('error', 'Unknown')}")
            self.ai_status_label.setStyleSheet("color: red;")
    
    def update_driver(self):
        """Update selected driver"""
        current_row = self.hardware_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a hardware component")
            return
        
        # Open the device tab for selected hardware
        self.open_device_tab(current_row, 0)
    
    def open_device_tab(self, row, column):
        """Open device-specific tab"""
        if row < len(self.detected_hardware):
            hardware = self.detected_hardware[row]
            device_id = hardware.get('id', hardware.get('name', 'Unknown'))
            
            # Switch to device tab if it exists
            if device_id in self.device_tabs:
                self.tabs.setCurrentIndex(self.device_tabs[device_id])
    
    def rollback_driver(self):
        """Rollback selected driver"""
        current_row = self.hardware_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a hardware component")
            return
        
        # Open the device tab for selected hardware
        self.open_device_tab(current_row, 0)
    
    def test_driver(self):
        """Test selected driver"""
        current_row = self.hardware_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a hardware component")
            return
        
        # Open the device tab for selected hardware
        self.open_device_tab(current_row, 0)
    
    def apply_theme(self):
        """Apply dark theme"""
        theme = self.config.get('gui.theme', 'dark')
        
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #444444;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    padding: 8px 16px;
                    border: 1px solid #444444;
                }
                QTabBar::tab:selected {
                    background-color: #4b4b4b;
                }
                QTableWidget {
                    background-color: #3b3b3b;
                    alternate-background-color: #333333;
                    color: #ffffff;
                    gridline-color: #444444;
                }
                QHeaderView::section {
                    background-color: #4b4b4b;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #444444;
                }
                QPushButton {
                    background-color: #4b4b4b;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 6px 12px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5b5b5b;
                }
                QPushButton:pressed {
                    background-color: #3b3b3b;
                }
                QStatusBar {
                    background-color: #3b3b3b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #444444;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QTextEdit {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #444444;
                }
                QComboBox {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #444444;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #ffffff;
                }
                QProgressBar {
                    border: 1px solid #444444;
                    border-radius: 3px;
                    text-align: center;
                    background-color: #3b3b3b;
                }
                QProgressBar::chunk {
                    background-color: #4b8b4b;
                }
            """)
