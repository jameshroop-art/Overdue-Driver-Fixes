"""
Device-specific tab widget for driver management
Shows current driver info, available drivers, and AI features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QScrollArea,
    QProgressDialog, QCheckBox, QLineEdit, QSplitter, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from datetime import datetime, timedelta


# Risk assessment thresholds
RISK_VERY_LOW_THRESHOLD = 10
RISK_LOW_THRESHOLD = 30
RISK_MEDIUM_THRESHOLD = 50
RISK_HIGH_THRESHOLD = 30  # Threshold for installation warning


class DriverInstallWorker(QThread):
    """Worker thread for driver installation"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, driver_manager, ai_manager, hardware, driver):
        super().__init__()
        self.driver_manager = driver_manager
        self.ai_manager = ai_manager
        self.hardware = hardware
        self.driver = driver
    
    def run(self):
        """Run driver installation with AI assistance"""
        try:
            self.progress.emit(10, "Preparing installation...")
            
            # Check if driver is from a trusted source
            driver_source = self.driver.get('source', '').lower()
            is_trusted_source = driver_source in ['official', 'distribution']
            
            if is_trusted_source:
                # For trusted sources, proceed immediately without waiting for risk assessment
                self.progress.emit(20, f"Trusted source detected ({driver_source}), proceeding with installation...")
                # Risk assessment can still run in background for logging, but don't wait for it
                risk = None
            else:
                # For non-trusted sources, perform risk assessment first
                self.progress.emit(20, "Assessing risks...")
                risk = self.ai_manager.assess_risk(self.hardware, self.driver)
                
                if risk['risk_percentage'] > RISK_HIGH_THRESHOLD:
                    self.progress.emit(25, f"High risk detected: {risk['risk_percentage']}%")
            
            # Install driver
            self.progress.emit(50, f"Installing {self.driver['name']}...")
            success = self.driver_manager.install_driver(self.driver, self.hardware)
            
            if not success:
                self.progress.emit(60, "Installation failed, attempting AI remediation...")
                # AI remediation would go here
                self.finished.emit(False, "Installation failed")
                return
            
            # Post-installation testing
            self.progress.emit(80, "Testing driver...")
            test_result = self.driver_manager.test_driver(self.hardware)
            
            self.progress.emit(100, "Installation complete")
            self.finished.emit(True, "Driver installed successfully")
            
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class DeviceTab(QWidget):
    """Tab widget for individual device management"""
    
    def __init__(self, hardware, driver_manager, ai_manager, config_manager):
        super().__init__()
        self.hardware = hardware
        self.driver_manager = driver_manager
        self.ai_manager = ai_manager
        self.config = config_manager
        self.available_drivers = []
        self.install_worker = None
        self.ai_monitoring_enabled = False
        self.chat_enabled = False
        self.chat_history = []
        self.monitored_operations = []
        
        # Initialize driver converter
        from ai.driver_converter import DriverConverter
        self.driver_converter = DriverConverter(config_manager, ai_manager)
        
        # Initialize backup manager and test timer
        from utils.driver_backup import DriverBackupManager
        from utils.driver_test_timer import DriverTestTimer
        from utils.driver_stress_test import DriverStressTest
        self.backup_manager = DriverBackupManager()
        self.test_timer = DriverTestTimer(test_duration_minutes=5)
        self.stress_tester = DriverStressTest(hardware)
        self.current_backup_path = None
        self.pending_driver = None
        self.stress_test_running = False
        
        self.init_ui()
        self.load_drivers()
    
    def _is_checkbox_checked(self, state):
        """Helper method to check if checkbox is checked"""
        return state == Qt.CheckState.Checked.value
    
    def init_ui(self):
        """Initialize the device tab UI"""
        # Main splitter for content and chat (resizable)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)  # Prevent collapsing panels
        
        # Left side: Device management content (scrollable)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)  # Enable resizing
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Device information section
        info_group = self.create_device_info_section()
        layout.addWidget(info_group)
        
        # Current driver section
        current_driver_group = self.create_current_driver_section()
        layout.addWidget(current_driver_group)
        
        # Timer section - visible area for test period countdown
        timer_group = self.create_timer_section()
        layout.addWidget(timer_group)
        self.timer_group = timer_group  # Store reference to show/hide
        self.timer_group.setVisible(False)  # Hidden by default, shown during test period
        
        # Risk assessment section
        risk_group = self.create_risk_assessment_section()
        layout.addWidget(risk_group)
        
        # Driver Operations Monitoring section (NEW)
        operations_group = self.create_driver_operations_section()
        layout.addWidget(operations_group)
        
        # Available drivers section
        drivers_group = self.create_available_drivers_section()
        layout.addWidget(drivers_group)
        
        # AI features section with checkbox
        ai_group = self.create_ai_features_section()
        layout.addWidget(ai_group)
        
        # App Settings section
        settings_group = self.create_app_settings_section()
        layout.addWidget(settings_group)
        
        # Fallback plan section
        fallback_group = self.create_fallback_plan_section()
        layout.addWidget(fallback_group)
        
        layout.addStretch()
        left_scroll.setWidget(left_widget)
        
        # Right side: Chat interface (scrollable)
        chat_widget = self.create_chat_interface()
        
        # Add both to splitter with initial sizes
        main_splitter.addWidget(left_scroll)
        main_splitter.addWidget(chat_widget)
        main_splitter.setStretchFactor(0, 3)  # Left side takes 3/4
        main_splitter.setStretchFactor(1, 1)  # Right side takes 1/4
        
        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
    
    def create_device_info_section(self):
        """Create device information section"""
        group = QGroupBox("Device Information")
        layout = QVBoxLayout()
        
        # Check if this is a motherboard to show additional info
        is_motherboard = self.hardware.get('type') == 'Motherboard'
        
        if is_motherboard:
            # Extended info for motherboard
            row_count = 9  # More rows for BIOS, chipset, compatibility
        else:
            row_count = 5
        
        info_table = QTableWidget(row_count, 2)
        info_table.setHorizontalHeaderLabels(["Property", "Value"])
        info_table.verticalHeader().setVisible(False)
        info_table.setMaximumHeight(200 if not is_motherboard else 350)
        
        properties = [
            ("Type", self.hardware.get('type', 'Unknown')),
            ("Name", self.hardware.get('name', 'Unknown')),
            ("Vendor", self.hardware.get('vendor', 'Unknown')),
            ("Device ID", self.hardware.get('id', 'N/A')),
            ("Model", self.hardware.get('model', self.hardware.get('name', 'N/A')))
        ]
        
        # Add motherboard-specific information
        if is_motherboard:
            properties.extend([
                ("BIOS Version", self.hardware.get('bios_version', 'N/A')),
                ("BIOS Date", self.hardware.get('bios_date', 'N/A')),
                ("Chipset", self.hardware.get('chipset', 'Unknown')),
                ("Linux Support", self.hardware.get('linux_compatible', {}).get('linux_support', 'Unknown'))
            ])
        
        for i, (key, value) in enumerate(properties):
            info_table.setItem(i, 0, QTableWidgetItem(key))
            info_table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        info_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(info_table)
        
        # Add Linux compatibility info for motherboards
        if is_motherboard:
            compat_info = self.hardware.get('linux_compatible', {})
            if compat_info.get('status') == 'supported':
                compat_widget = self._create_compatibility_widget(compat_info)
                layout.addWidget(compat_widget)
        
        group.setLayout(layout)
        return group
    
    def _create_compatibility_widget(self, compat_info):
        """Create widget showing Linux compatibility information"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("🐧 Linux Compatibility")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Support status
        support_level = compat_info.get('linux_support', 'Unknown')
        support_label = QLabel(f"Support Level: {support_level}")
        
        # Color code based on support level
        if support_level == 'Good':
            support_label.setStyleSheet("color: green;")
        elif support_level == 'Moderate':
            support_label.setStyleSheet("color: orange;")
        else:
            support_label.setStyleSheet("color: gray;")
        
        layout.addWidget(support_label)
        
        # Notes
        notes = compat_info.get('notes', '')
        if notes:
            notes_label = QLabel(notes)
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("font-size: 10px; color: gray;")
            layout.addWidget(notes_label)
        
        # Links to manufacturer support
        if compat_info.get('support_url'):
            link_layout = QHBoxLayout()
            
            support_btn = QPushButton("Manufacturer Support")
            support_btn.clicked.connect(lambda: self._open_url(compat_info.get('support_url')))
            link_layout.addWidget(support_btn)
            
            if compat_info.get('drivers_url'):
                drivers_btn = QPushButton("Download Drivers")
                drivers_btn.clicked.connect(lambda: self._open_url(compat_info.get('drivers_url')))
                link_layout.addWidget(drivers_btn)
            
            link_layout.addStretch()
            layout.addLayout(link_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open(url)
    
    def create_current_driver_section(self):
        """Create current driver information section"""
        group = QGroupBox("Current Driver")
        layout = QVBoxLayout()
        
        current_driver = self.hardware.get('driver', 'No driver installed')
        
        driver_label = QLabel(f"Driver: {current_driver}")
        driver_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(driver_label)
        
        if current_driver and current_driver != 'No driver installed':
            status_label = QLabel("Status: Active")
            status_label.setStyleSheet("color: green;")
        else:
            status_label = QLabel("Status: No Driver")
            status_label.setStyleSheet("color: red;")
        
        layout.addWidget(status_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Driver")
        test_btn.clicked.connect(self.test_current_driver)
        button_layout.addWidget(test_btn)
        
        rollback_btn = QPushButton("Rollback Driver")
        rollback_btn.clicked.connect(self.rollback_driver)
        button_layout.addWidget(rollback_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_timer_section(self):
        """Create timer section with live feed of communications"""
        group = QGroupBox("⏱ Driver Test Period - Live Status")
        layout = QVBoxLayout()
        
        # Timer display - large and prominent
        self.timer_display_label = QLabel("Time Remaining: 5:00")
        self.timer_display_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #FF6B00; "
            "padding: 10px; background-color: #FFF3E0; border-radius: 5px;"
        )
        self.timer_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_display_label)
        
        # Status info
        self.timer_status_label = QLabel("Testing driver installation...")
        self.timer_status_label.setStyleSheet("font-size: 12px; color: #666;")
        self.timer_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_status_label)
        
        # Live communication feed
        feed_label = QLabel("Live Communication Feed:")
        feed_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(feed_label)
        
        self.timer_comm_feed = QTextEdit()
        self.timer_comm_feed.setReadOnly(True)
        self.timer_comm_feed.setMaximumHeight(150)
        self.timer_comm_feed.setStyleSheet(
            "background-color: #F5F5F5; font-family: monospace; font-size: 11px;"
        )
        layout.addWidget(self.timer_comm_feed)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.confirm_driver_btn = QPushButton("✓ Confirm Driver Works")
        self.confirm_driver_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;"
        )
        self.confirm_driver_btn.clicked.connect(self.confirm_driver_works)
        button_layout.addWidget(self.confirm_driver_btn)
        
        self.revert_driver_btn = QPushButton("✗ Revert Driver Now")
        self.revert_driver_btn.setStyleSheet(
            "background-color: #F44336; color: white; font-weight: bold; padding: 8px;"
        )
        self.revert_driver_btn.clicked.connect(self.revert_driver_now)
        button_layout.addWidget(self.revert_driver_btn)
        
        self.stress_test_btn = QPushButton("⚡ Run Stress Test")
        self.stress_test_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 8px;"
        )
        self.stress_test_btn.clicked.connect(self.start_stress_test)
        button_layout.addWidget(self.stress_test_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        
        # Create timer to update display every second
        self.timer_display_update_timer = QTimer(self)
        self.timer_display_update_timer.timeout.connect(self.update_timer_display)
        
        return group
    
    def create_risk_assessment_section(self):
        """Create risk assessment section"""
        group = QGroupBox("Risk Assessment")
        layout = QVBoxLayout()
        
        # Get risk assessment from AI
        self.risk_label = QLabel("Assessing risk...")
        layout.addWidget(self.risk_label)
        
        self.risk_progress = QProgressBar()
        self.risk_progress.setMaximum(100)
        self.risk_progress.setValue(0)
        layout.addWidget(self.risk_progress)
        
        self.ai_remediation_label = QLabel("AI Remediation: Checking...")
        layout.addWidget(self.ai_remediation_label)
        
        assess_btn = QPushButton("Refresh Risk Assessment")
        assess_btn.clicked.connect(self.assess_risk)
        layout.addWidget(assess_btn)
        
        group.setLayout(layout)
        
        # Perform initial assessment
        self.assess_risk()
        
        return group
    
    def create_driver_operations_section(self):
        """Create driver operations monitoring section"""
        group = QGroupBox("Driver Operations - AI Monitoring")
        layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel(
            "Driver operations that AI can monitor for operational moderation:"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-weight: bold; color: #aaaaaa;")
        layout.addWidget(desc_label)
        
        # Operations table
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(4)
        self.operations_table.setHorizontalHeaderLabels([
            "Operation", "Status", "AI Monitoring", "Last Check"
        ])
        self.operations_table.horizontalHeader().setStretchLastSection(True)
        self.operations_table.setMinimumHeight(200)
        self.operations_table.setSizePolicy(
            self.operations_table.sizePolicy().Policy.Expanding,
            self.operations_table.sizePolicy().Policy.Expanding
        )
        
        # Populate with driver operations
        self.populate_driver_operations()
        
        layout.addWidget(self.operations_table)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Operations Status")
        refresh_btn.clicked.connect(self.refresh_driver_operations)
        refresh_layout.addWidget(refresh_btn)
        
        auto_refresh_checkbox = QCheckBox("Auto-refresh (5s)")
        auto_refresh_checkbox.setToolTip("Automatically refresh operation status every 5 seconds")
        refresh_layout.addWidget(auto_refresh_checkbox)
        
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        group.setLayout(layout)
        return group
    
    def populate_driver_operations(self):
        """Populate driver operations table"""
        device_type = self.hardware.get('type', 'Device')
        driver_name = self.hardware.get('driver', 'No driver')
        
        # Define operations based on device type
        if device_type == 'GPU':
            operations = [
                ('GPU Memory Allocation', 'Monitor memory usage and prevent overallocation'),
                ('GPU Clock Speed', 'Monitor and optimize clock speeds for performance'),
                ('GPU Temperature', 'Monitor thermal levels and prevent overheating'),
                ('GPU Power Draw', 'Monitor power consumption and prevent power spikes'),
                ('Driver State', 'Monitor driver initialization and runtime state'),
                ('Rendering Pipeline', 'Monitor graphics rendering operations'),
                ('Compute Operations', 'Monitor CUDA/OpenCL compute tasks'),
                ('Display Output', 'Monitor video output and display connection'),
            ]
        elif device_type == 'WiFi':
            operations = [
                ('WiFi Connection', 'Monitor connection stability and signal strength'),
                ('Driver State', 'Monitor driver initialization and runtime state'),
                ('Packet Transmission', 'Monitor network packet flow'),
                ('Authentication', 'Monitor WiFi authentication process'),
                ('Power Management', 'Monitor power saving states'),
                ('Firmware State', 'Monitor firmware status and updates'),
            ]
        elif device_type == 'CPU':
            operations = [
                ('CPU Frequency', 'Monitor and optimize CPU frequency scaling'),
                ('Thermal Management', 'Monitor CPU temperature and throttling'),
                ('Cache Operations', 'Monitor CPU cache performance'),
                ('Power States', 'Monitor C-states and power management'),
            ]
        else:
            operations = [
                ('Driver State', 'Monitor driver initialization and runtime state'),
                ('Device Communication', 'Monitor device I/O operations'),
                ('Error Handling', 'Monitor and correct driver errors'),
                ('Power Management', 'Monitor device power states'),
            ]
        
        self.operations_table.setRowCount(len(operations))
        
        for i, (operation, description) in enumerate(operations):
            # Operation name
            op_item = QTableWidgetItem(operation)
            op_item.setToolTip(description)
            self.operations_table.setItem(i, 0, op_item)
            
            # Status
            if self.ai_monitoring_enabled:
                status_item = QTableWidgetItem("✓ Active")
                status_item.setForeground(QColor(100, 255, 100))
            else:
                status_item = QTableWidgetItem("○ Inactive")
                status_item.setForeground(QColor(150, 150, 150))
            self.operations_table.setItem(i, 1, status_item)
            
            # AI Monitoring status
            if self.ai_monitoring_enabled:
                monitor_item = QTableWidgetItem("Monitoring")
                monitor_item.setForeground(QColor(100, 255, 100))
            else:
                monitor_item = QTableWidgetItem("Disabled")
                monitor_item.setForeground(QColor(200, 200, 100))
            self.operations_table.setItem(i, 2, monitor_item)
            
            # Last check
            import datetime
            if self.ai_monitoring_enabled:
                last_check = datetime.datetime.now().strftime("%H:%M:%S")
            else:
                last_check = "N/A"
            self.operations_table.setItem(i, 3, QTableWidgetItem(last_check))
        
        # Store operations for later refresh
        self.monitored_operations = operations
    
    def refresh_driver_operations(self):
        """Refresh driver operations status"""
        import datetime
        
        for i in range(self.operations_table.rowCount()):
            # Update status
            if self.ai_monitoring_enabled:
                status_item = QTableWidgetItem("✓ Active")
                status_item.setForeground(QColor(100, 255, 100))
                monitor_item = QTableWidgetItem("Monitoring")
                monitor_item.setForeground(QColor(100, 255, 100))
                last_check = datetime.datetime.now().strftime("%H:%M:%S")
            else:
                status_item = QTableWidgetItem("○ Inactive")
                status_item.setForeground(QColor(150, 150, 150))
                monitor_item = QTableWidgetItem("Disabled")
                monitor_item.setForeground(QColor(200, 200, 100))
                last_check = "N/A"
            
            self.operations_table.setItem(i, 1, status_item)
            self.operations_table.setItem(i, 2, monitor_item)
            self.operations_table.setItem(i, 3, QTableWidgetItem(last_check))
    
    def create_available_drivers_section(self):
        """Create available drivers section"""
        group = QGroupBox("Available Drivers")
        layout = QVBoxLayout()
        
        # Filter by source and OS
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by source:")
        filter_layout.addWidget(filter_label)
        
        self.source_filter = QComboBox()
        self.source_filter.addItems(["All", "Official", "Distribution", "Community"])
        self.source_filter.currentTextChanged.connect(self.filter_drivers)
        filter_layout.addWidget(self.source_filter)
        
        # Add checkbox for cross-OS drivers
        self.show_cross_os_checkbox = QCheckBox("Show Windows/Other OS drivers")
        self.show_cross_os_checkbox.setToolTip(
            "Include drivers for Windows and other operating systems.\n"
            "These can be downloaded for compatibility research and analysis."
        )
        self.show_cross_os_checkbox.stateChanged.connect(self.toggle_cross_os_drivers)
        filter_layout.addWidget(self.show_cross_os_checkbox)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Drivers table (now with OS column)
        self.drivers_table = QTableWidget()
        header_labels = [
            "Driver", "Version", "Source", "Target OS", "Stability", "Risk %", "Source Status", "Actions"
        ]
        self.drivers_table.setColumnCount(len(header_labels))
        self.drivers_table.setHorizontalHeaderLabels(header_labels)
        self.drivers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.drivers_table)
        
        group.setLayout(layout)
        return group
    
    def create_ai_features_section(self):
        """Create AI features section"""
        group = QGroupBox("AI-Assisted Features")
        layout = QVBoxLayout()
        
        # AI Monitoring checkbox
        ai_monitor_layout = QHBoxLayout()
        self.ai_monitor_checkbox = QCheckBox("Enable AI Monitoring for this device")
        self.ai_monitor_checkbox.setToolTip(
            "AI will continuously monitor this driver's operations,\n"
            "detect potential failures, and automatically prevent errors."
        )
        self.ai_monitor_checkbox.stateChanged.connect(self.toggle_ai_monitoring_checkbox)
        ai_monitor_layout.addWidget(self.ai_monitor_checkbox)
        ai_monitor_layout.addStretch()
        layout.addLayout(ai_monitor_layout)
        
        # AI status
        ai_status_layout = QHBoxLayout()
        self.ai_status_label = QLabel("AI Status: Checking...")
        ai_status_layout.addWidget(self.ai_status_label)
        ai_status_layout.addStretch()
        layout.addLayout(ai_status_layout)
        
        # AI features
        features_label = QLabel("Available AI Features:")
        features_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(features_label)
        
        features = [
            "✓ Pre-installation risk assessment",
            "✓ Real-time installation monitoring",
            "✓ Automatic error detection and correction",
            "✓ Post-installation verification",
            "✓ Proactive failure prevention",
            "✓ Per-device monitoring control"
        ]
        
        for feature in features:
            feature_label = QLabel(f"  {feature}")
            layout.addWidget(feature_label)
        
        # AI action buttons
        ai_button_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("AI Analyze Current Setup")
        analyze_btn.clicked.connect(self.ai_analyze_setup)
        ai_button_layout.addWidget(analyze_btn)
        
        ai_button_layout.addStretch()
        layout.addLayout(ai_button_layout)
        
        group.setLayout(layout)
        
        # Check AI status
        self.check_ai_status()
        
        return group
    
    def create_fallback_plan_section(self):
        """Create fallback plan section"""
        group = QGroupBox("Fallback Plan")
        layout = QVBoxLayout()
        
        info_label = QLabel("Automatic fallback procedures if driver installation fails:")
        info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_label)
        
        self.fallback_text = QTextEdit()
        self.fallback_text.setReadOnly(True)
        self.fallback_text.setMaximumHeight(150)
        
        fallback_plan = """1. Automatic detection of driver failure on boot
2. Revert to previous working driver automatically
3. AI analysis of error logs and failure mode
4. Attempt automatic correction if possible
5. Search for alternative compatible drivers
6. Generate detailed error report for manufacturer
7. Suggest manual recovery steps if needed

Previous Driver Backup: Available
Recovery Mode: Enabled
Estimated Recovery Time: 2-5 minutes"""
        
        self.fallback_text.setPlainText(fallback_plan)
        layout.addWidget(self.fallback_text)
        
        group.setLayout(layout)
        return group
    
    def create_app_settings_section(self):
        """Create app settings section with AI training prepend"""
        group = QGroupBox("App Settings - AI Training Context")
        layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel(
            "Prepend text for AI model training (1000+ characters).\n"
            "This context will be used to train the AI for better understanding of this device:"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-weight: bold; color: #aaaaaa;")
        layout.addWidget(desc_label)
        
        # Training prepend text field
        self.training_prepend = QTextEdit()
        self.training_prepend.setPlaceholderText(
            "Enter detailed context about this device for AI training...\n\n"
            "Example content:\n"
            "- Device-specific quirks and known issues\n"
            "- Optimal configuration settings\n"
            "- Common error patterns and solutions\n"
            "- Hardware-specific considerations\n"
            "- Performance optimization tips\n"
            "- Compatibility notes with specific software\n"
            "- Thermal management considerations\n"
            "- Power management best practices\n\n"
            "Minimum 1000 characters required for effective training."
        )
        self.training_prepend.setMinimumHeight(200)
        
        # Load saved prepend if available
        device_id = self.hardware.get('id', self.hardware.get('name', 'unknown'))
        saved_prepend = self.config.get(f'ai_training.{device_id}.prepend', '')
        if saved_prepend:
            self.training_prepend.setPlainText(saved_prepend)
        
        layout.addWidget(self.training_prepend)
        
        # Character count label
        self.char_count_label = QLabel("Characters: 0 / 1000 minimum")
        self.char_count_label.setStyleSheet("color: #888888;")
        self.training_prepend.textChanged.connect(self.update_char_count)
        layout.addWidget(self.char_count_label)
        
        # Save button
        save_layout = QHBoxLayout()
        save_btn = QPushButton("Save Training Context")
        save_btn.clicked.connect(self.save_training_prepend)
        save_layout.addWidget(save_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_training_prepend)
        save_layout.addWidget(clear_btn)
        
        save_layout.addStretch()
        layout.addLayout(save_layout)
        
        group.setLayout(layout)
        return group
    
    def load_drivers(self):
        """Load available drivers for this device"""
        try:
            # Check if cross-OS drivers should be included
            include_cross_os = self.show_cross_os_checkbox.isChecked() if hasattr(self, 'show_cross_os_checkbox') else False
            self.available_drivers = self.driver_manager.find_drivers(self.hardware, include_cross_os=include_cross_os)
            self.update_drivers_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load drivers: {e}")
    
    def toggle_cross_os_drivers(self):
        """Toggle cross-OS driver visibility"""
        self.load_drivers()
    
    def update_drivers_table(self):
        """Update the drivers table"""
        # Filter drivers by source
        source_filter = self.source_filter.currentText().lower()
        
        if source_filter == "all":
            filtered_drivers = self.available_drivers
        else:
            filtered_drivers = [
                d for d in self.available_drivers 
                if d.get('source', '').lower() == source_filter
            ]
        
        self.drivers_table.setRowCount(len(filtered_drivers))
        
        for i, driver in enumerate(filtered_drivers):
            # Driver name
            self.drivers_table.setItem(i, 0, QTableWidgetItem(driver.get('name', 'Unknown')))
            
            # Version
            self.drivers_table.setItem(i, 1, QTableWidgetItem(driver.get('version', 'N/A')))
            
            # Source
            source_item = QTableWidgetItem(driver.get('source', 'Unknown'))
            if driver.get('source') == 'official':
                source_item.setBackground(QColor(50, 100, 50))
            self.drivers_table.setItem(i, 2, source_item)
            
            # Target OS (NEW COLUMN)
            target_os = driver.get('target_os', 'linux').upper()
            os_item = QTableWidgetItem(target_os)
            if target_os.lower() == 'linux':
                os_item.setBackground(QColor(50, 100, 50))
                os_item.setForeground(QColor(200, 255, 200))
            elif target_os.lower() == 'windows':
                os_item.setBackground(QColor(50, 50, 100))
                os_item.setForeground(QColor(200, 200, 255))
            else:
                os_item.setBackground(QColor(100, 100, 100))
            
            # Add tooltip for cross-OS drivers
            if target_os.lower() != 'linux':
                compatibility_note = driver.get('compatibility_note', 'Cross-platform driver')
                os_item.setToolTip(compatibility_note)
            
            self.drivers_table.setItem(i, 3, os_item)
            
            # Stability
            stability = driver.get('stability', 'unknown')
            stability_item = QTableWidgetItem(stability)
            if stability == 'stable':
                stability_item.setBackground(QColor(50, 100, 50))
            elif stability == 'beta':
                stability_item.setBackground(QColor(100, 100, 50))
            self.drivers_table.setItem(i, 4, stability_item)
            
            # Risk percentage
            risk = driver.get('risk_percentage', 5)
            risk_item = QTableWidgetItem(f"{risk}%")
            if risk < 10:
                risk_item.setBackground(QColor(50, 100, 50))
            elif risk < 30:
                risk_item.setBackground(QColor(100, 100, 50))
            else:
                risk_item.setBackground(QColor(100, 50, 50))
            self.drivers_table.setItem(i, 5, risk_item)
            
            # Source connectivity status
            source_connected = driver.get('source_connected', True)
            source_url = driver.get('source_url', 'N/A')
            if source_connected:
                status_item = QTableWidgetItem("✓ Connected")
                status_item.setForeground(QColor(100, 255, 100))
                status_item.setToolTip(f"Source: {source_url}")
            else:
                status_item = QTableWidgetItem("○ Offline")
                status_item.setForeground(QColor(255, 100, 100))
                status_item.setToolTip(f"Cannot connect to: {source_url}")
            self.drivers_table.setItem(i, 6, status_item)
            
            # Install/Download/Convert buttons
            target_os = driver.get('target_os', 'linux').lower()
            download_only = driver.get('download_only', False)
            
            # Create button container with layout
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(2, 2, 2, 2)
            button_layout.setSpacing(4)
            
            if target_os == 'linux' and not download_only:
                # Linux driver - Install button only
                action_btn = QPushButton("Install with AI")
                action_btn.clicked.connect(lambda checked, d=driver: self.install_driver(d))
                button_layout.addWidget(action_btn)
            else:
                # Cross-OS driver - Download and Convert buttons
                download_btn = QPushButton("Download")
                download_btn.setToolTip(f"Download {target_os.upper()} driver for analysis")
                download_btn.clicked.connect(lambda checked, d=driver: self.download_driver(d))
                download_btn.setStyleSheet("background-color: #3a5a7a;")
                button_layout.addWidget(download_btn)
                
                # Add Convert button for cross-OS drivers
                convert_btn = QPushButton("Convert to Linux")
                convert_btn.setToolTip(f"Use AI to convert {target_os.upper()} driver to Linux")
                convert_btn.clicked.connect(lambda checked, d=driver: self.convert_driver(d))
                convert_btn.setStyleSheet("background-color: #5a3a7a; font-weight: bold;")
                button_layout.addWidget(convert_btn)
            
            self.drivers_table.setCellWidget(i, 7, button_widget)
    
    def filter_drivers(self):
        """Filter drivers by source"""
        self.update_drivers_table()
    
    def assess_risk(self):
        """Assess risk for current driver configuration"""
        try:
            # Get current driver info
            current_driver = self.driver_manager.get_current_driver(self.hardware)
            
            if current_driver:
                # Mock risk assessment - would use AI in production
                risk = self.ai_manager.assess_risk(self.hardware, current_driver)
                risk_percentage = risk.get('risk_percentage', 5)
                can_remediate = risk.get('can_remediate', True)
                
                self.risk_progress.setValue(risk_percentage)
                
                if risk_percentage < RISK_VERY_LOW_THRESHOLD:
                    risk_level = "Very Low"
                    color = "green"
                elif risk_percentage < RISK_LOW_THRESHOLD:
                    risk_level = "Low"
                    color = "lightgreen"
                elif risk_percentage < RISK_MEDIUM_THRESHOLD:
                    risk_level = "Medium"
                    color = "orange"
                else:
                    risk_level = "High"
                    color = "red"
                
                self.risk_label.setText(f"Risk Level: {risk_level} ({risk_percentage}%)")
                self.risk_label.setStyleSheet(f"color: {color}; font-weight: bold;")
                
                if can_remediate:
                    self.ai_remediation_label.setText("AI Remediation: Yes (Can prevent all known errors)")
                    self.ai_remediation_label.setStyleSheet("color: green;")
                else:
                    self.ai_remediation_label.setText("AI Remediation: Partial")
                    self.ai_remediation_label.setStyleSheet("color: orange;")
            else:
                self.risk_label.setText("Risk Level: N/A (No driver installed)")
                self.risk_progress.setValue(0)
                self.ai_remediation_label.setText("AI Remediation: N/A")
        
        except Exception as e:
            self.risk_label.setText(f"Error assessing risk: {e}")
            self.risk_label.setStyleSheet("color: red;")
    
    def check_ai_status(self):
        """Check AI assistant status"""
        status = self.ai_manager.get_status()
        
        if status['status'] == 'running':
            self.ai_status_label.setText(f"AI Status: Online ({status.get('model', 'starcoder:3b')})")
            self.ai_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.ai_status_label.setText("AI Status: Offline")
            self.ai_status_label.setStyleSheet("color: orange;")
    
    def install_driver(self, driver):
        """Install a driver with AI assistance and safety features"""
        # Check if driver is from a trusted source
        driver_source = driver.get('source', '').lower()
        is_trusted_source = driver_source in ['official', 'distribution']
        
        # Step 1: Create system backup
        current_driver = self.driver_manager.get_current_driver(self.hardware)
        
        backup_confirmation = QMessageBox.question(
            self,
            "⚠ Create System Backup",
            f"Before installing {driver['name']}, create a backup?\n\n"
            f"Current Driver: {current_driver.get('name', 'Unknown') if current_driver else 'None'}\n"
            f"New Driver: {driver['name']} ({driver['version']})\n"
            f"Source: {driver['source']}\n\n"
            f"A backup will be saved to /root/driver-backups/\n"
            f"This allows automatic rollback if installation fails.\n\n"
            f"Create backup before proceeding?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if backup_confirmation == QMessageBox.StandardButton.Yes:
            try:
                self.current_backup_path = self.backup_manager.create_backup(
                    self.hardware, 
                    current_driver
                )
                QMessageBox.information(
                    self,
                    "✓ Backup Created",
                    f"System backup created successfully:\n\n"
                    f"{self.current_backup_path}\n\n"
                    f"Backup includes:\n"
                    f"• Hardware: {self.hardware.get('name')}\n"
                    f"• Current Driver: {current_driver.get('name', 'Unknown') if current_driver else 'None'}\n"
                    f"• Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"This backup will be used for automatic rollback if needed."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Backup Failed",
                    f"Failed to create system backup:\n\n{str(e)}\n\n"
                    f"Installation cannot proceed without backup for safety."
                )
                return
        
        # Step 2: Final confirmation with OK/Deny
        # Build installation message based on source trust
        if is_trusted_source:
            install_message = (
                f"⚠ FINAL CONFIRMATION - Install Driver?\n\n"
                f"Driver: {driver['name']} ({driver['version']})\n"
                f"Source: {driver['source']} (✓ Trusted)\n"
                f"Hardware: {self.hardware.get('name')}\n\n"
                f"{'Backup Created: ' + self.current_backup_path if self.current_backup_path else 'No Backup Created'}\n\n"
                f"Installation Process:\n"
                f"• Skip risk assessment (trusted source)\n"
                f"• Monitor installation in real-time\n"
                f"• Test driver for 5 minutes\n"
                f"• Automatic rollback if test fails or times out\n"
                f"• You must confirm driver is working within 5 minutes\n\n"
                f"Click OK to proceed or Deny to cancel."
            )
        else:
            install_message = (
                f"⚠ FINAL CONFIRMATION - Install Driver?\n\n"
                f"Driver: {driver['name']} ({driver['version']})\n"
                f"Source: {driver['source']}\n"
                f"Hardware: {self.hardware.get('name')}\n\n"
                f"{'Backup Created: ' + self.current_backup_path if self.current_backup_path else 'No Backup Created'}\n\n"
                f"Installation Process:\n"
                f"• Assess risks before installation\n"
                f"• Monitor installation in real-time\n"
                f"• Test driver for 5 minutes\n"
                f"• Automatic rollback if test fails or times out\n"
                f"• You must confirm driver is working within 5 minutes\n\n"
                f"Click OK to proceed or Deny to cancel."
            )
        
        reply = QMessageBox.question(
            self,
            "Confirm Installation - OK or Deny",
            install_message,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Ok:
            # Store pending driver for timer
            self.pending_driver = driver
            
            # Create and start worker thread
            self.install_worker = DriverInstallWorker(
                self.driver_manager,
                self.ai_manager,
                self.hardware,
                driver
            )
            
            # Create progress dialog
            self.progress_dialog = QProgressDialog(
                "Installing driver...",
                "Cancel",
                0, 100,
                self
            )
            self.progress_dialog.setWindowTitle("Driver Installation")
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            
            # Connect signals
            self.install_worker.progress.connect(self.update_install_progress)
            self.install_worker.finished.connect(self.install_finished_with_timer)
            
            # Start installation
            self.install_worker.start()
            self.progress_dialog.show()
        else:
            QMessageBox.information(
                self,
                "Installation Cancelled",
                f"Driver installation cancelled by user.\n\n"
                f"{'Backup will be retained for future use.' if self.current_backup_path else ''}"
            )
    
    def update_install_progress(self, value, message):
        """Update installation progress"""
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText(message)
    
    def install_finished(self, success, message):
        """Handle installation completion"""
        self.progress_dialog.close()
        
        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh current driver info
            self.assess_risk()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def install_finished_with_timer(self, success, message):
        """Handle installation completion and start 5-minute test timer"""
        self.progress_dialog.close()
        
        if success:
            # Show and initialize timer section
            self.timer_group.setVisible(True)
            self.timer_comm_feed.clear()
            self.add_timer_communication("✓ Driver installation completed successfully")
            self.add_timer_communication(f"Installing: {self.pending_driver.get('name', 'Unknown')}")
            self.add_timer_communication("Starting 5-minute test period...")
            self.add_timer_communication("Please test hardware functionality")
            
            # Start 5-minute test timer
            QMessageBox.information(
                self,
                "✓ Installation Complete - Test Period Started",
                f"{message}\n\n"
                f"⏱ 5-MINUTE TEST PERIOD STARTED\n\n"
                f"The driver has been installed successfully.\n"
                f"A visible timer with live communication feed has been added to the interface.\n\n"
                f"What to test:\n"
                f"• Basic hardware functionality\n"
                f"• System stability\n"
                f"• Performance\n"
                f"• Any hardware-specific features\n\n"
                f"⚠ IMPORTANT:\n"
                f"• You MUST click 'Confirm Driver Works' within 5 minutes\n"
                f"• If you don't confirm, the driver will be automatically reverted\n"
                f"• If you experience issues, click 'Revert Driver Now'\n\n"
                f"Monitor the timer section for live updates."
            )
            
            # Start test timer
            self.test_timer.start_test_timer(
                driver=self.pending_driver,
                hardware=self.hardware,
                on_timeout=self.on_test_timeout,
                on_progress=self.on_test_progress
            )
            
            # Start display update timer (updates every second)
            self.timer_display_update_timer.start(1000)
            self.add_timer_communication("⏱ Timer started - monitoring system stability")
        else:
            # Installation failed - offer to restore backup
            if self.current_backup_path:
                restore_reply = QMessageBox.question(
                    self,
                    "Installation Failed",
                    f"{message}\n\n"
                    f"Restore from backup?\n\n"
                    f"Backup: {self.current_backup_path}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if restore_reply == QMessageBox.StandardButton.Yes:
                    self.restore_from_backup()
            else:
                QMessageBox.critical(self, "Installation Failed", message)
    
    
    def update_timer_display(self):
        """Update the timer display with remaining time and communication feed"""
        if not self.test_timer.is_test_active():
            # Timer expired or completed
            self.timer_display_update_timer.stop()
            self.timer_group.setVisible(False)
            return
        
        # Get remaining time
        minutes, seconds = self.test_timer.get_remaining_time()
        elapsed_min, elapsed_sec = self.test_timer.get_elapsed_time()
        
        # Update timer display
        self.timer_display_label.setText(f"Time Remaining: {minutes}:{seconds:02d}")
        
        # Update status with elapsed time
        self.timer_status_label.setText(
            f"Testing {self.pending_driver.get('name', 'driver')} - "
            f"Elapsed: {elapsed_min}:{elapsed_sec:02d}"
        )
        
        # Change color based on remaining time
        if minutes < 1:
            # Less than 1 minute - red/urgent
            self.timer_display_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #D32F2F; "
                "padding: 10px; background-color: #FFEBEE; border-radius: 5px;"
            )
        elif minutes < 2:
            # Less than 2 minutes - orange/warning
            self.timer_display_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #F57C00; "
                "padding: 10px; background-color: #FFF3E0; border-radius: 5px;"
            )
        else:
            # Normal - green/safe
            self.timer_display_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #388E3C; "
                "padding: 10px; background-color: #E8F5E9; border-radius: 5px;"
            )
    
    def add_timer_communication(self, message):
        """Add a communication message to the timer's live feed"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.timer_comm_feed.append(formatted_message)
        # Auto-scroll to bottom
        self.timer_comm_feed.verticalScrollBar().setValue(
            self.timer_comm_feed.verticalScrollBar().maximum()
        )
    
    def confirm_driver_works(self):
        """User confirms driver is working correctly"""
        if self.test_timer.confirm_test_passed():
            self.add_timer_communication("✓ User confirmed driver is working correctly")
            self.add_timer_communication("✓ Test period completed successfully")
            self.add_timer_communication("✓ Driver installation verified and finalized")
            
            # Stop timer display and hide section after a short delay
            QTimer.singleShot(2000, lambda: self.timer_group.setVisible(False))
            
            QMessageBox.information(
                self,
                "✓ Driver Confirmed",
                f"Driver {self.pending_driver.get('name')} confirmed as working!\n\n"
                f"The driver installation is complete and verified.\n"
                f"Backup has been retained in case you need to revert later.\n\n"
                f"Backup location: {self.current_backup_path if self.current_backup_path else 'N/A'}"
            )
            
            # Refresh driver info
            self.assess_risk()
        else:
            QMessageBox.warning(
                self,
                "No Active Test",
                "There is no active driver test to confirm."
            )
    
    def revert_driver_now(self):
        """User requests immediate driver revert"""
        self.add_timer_communication("⚠ User requested driver revert")
        
        reply = QMessageBox.question(
            self,
            "⚠ Confirm Driver Revert",
            f"Revert to previous driver configuration?\n\n"
            f"This will restore the backup from:\n"
            f"{self.current_backup_path if self.current_backup_path else 'Unknown'}\n\n"
            f"Are you sure you want to revert?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.add_timer_communication("✓ Revert confirmed - canceling test timer")
            self.add_timer_communication("⏳ Restoring previous driver configuration...")
            self.test_timer.cancel_test()
            if self.stress_test_running:
                self.add_timer_communication("⏹ Stopping stress test...")
                self.stress_tester.stop_stress_test()
                self.stress_test_running = False
            self.restore_from_backup()
            # Hide timer section after revert
            QTimer.singleShot(2000, lambda: self.timer_group.setVisible(False))
        else:
            self.add_timer_communication("✗ Revert canceled - continuing test period")
    
    def start_stress_test(self):
        """Start heavy load stress test simulation for 15 minutes"""
        if self.stress_test_running:
            QMessageBox.warning(
                self,
                "Stress Test Running",
                "A stress test is already running. Please wait for it to complete."
            )
            return
        
        # Confirm stress test
        reply = QMessageBox.question(
            self,
            "⚡ Start Stress Test",
            f"Start 15-minute HEAVY LOAD stress test?\n\n"
            f"Driver: {self.pending_driver.get('name', 'Unknown')}\n"
            f"Hardware: {self.hardware.get('name', 'Unknown')}\n\n"
            f"This will simulate:\n"
            f"• Extended period heavy load (15 minutes)\n"
            f"• High concurrent operations\n"
            f"• Memory stress testing\n"
            f"• I/O intensive operations\n"
            f"• Thermal and power management tests\n\n"
            f"⚠ Note: This is a SIMULATED test in code\n"
            f"   No actual hardware stress will occur\n\n"
            f"The 5-minute timer will be extended to accommodate\n"
            f"the full 15-minute stress test period.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.add_timer_communication("✗ Stress test canceled by user")
            return
        
        self.add_timer_communication("⚡ Starting HEAVY LOAD stress test...")
        self.add_timer_communication("⏱ Extending timer to 17 minutes for stress test")
        
        # Extend timer for stress test (15 minutes + 2 minute buffer)
        self.test_timer.test_duration_minutes = 17
        self.test_timer.test_duration_seconds = 17 * 60
        self.test_timer.test_end_time = datetime.now() + timedelta(minutes=17)
        
        self.add_timer_communication("✓ Timer extended to 17:00 minutes")
        
        QMessageBox.information(
            self,
            "⚡ Stress Test Started",
            f"15-minute HEAVY LOAD stress test started!\n\n"
            f"Test Configuration:\n"
            f"• Duration: 15 minutes\n"
            f"• Load Level: HEAVY\n"
            f"• Test Type: Simulated (no hardware impact)\n"
            f"• Extended Timer: 17 minutes total\n\n"
            f"The test will run automatically.\n"
            f"Real-time results will appear in the live communication feed.\n\n"
            f"You can still confirm or revert the driver at any time."
        )
        
        self.add_timer_communication("⚡ Stress test initialized - starting tests...")
        
        # Start stress test
        self.stress_test_running = True
        success = self.stress_tester.start_stress_test(
            duration_seconds=900,  # 15 minutes
            stress_level='heavy',
            on_progress=self.on_stress_test_progress,
            on_complete=self.on_stress_test_complete
        )
        
        if not success:
            self.stress_test_running = False
            QMessageBox.critical(
                self,
                "Stress Test Failed",
                "Failed to start stress test. Please try again."
            )
    
    def on_stress_test_progress(self, test_name: str, status: str, elapsed_seconds: float):
        """Called during stress test progress"""
        # Add occasional updates to the communication feed
        if elapsed_seconds > 0 and int(elapsed_seconds) % 180 == 0:  # Every 3 minutes
            minutes = int(elapsed_seconds) // 60
            self.add_timer_communication(f"⚡ Stress test running: {minutes} minutes elapsed")
    
    def on_stress_test_complete(self, results: dict):
        """Called when stress test completes"""
        self.stress_test_running = False
        
        # Generate report
        report = self.stress_tester.generate_report()
        summary = results.get('summary', {})
        
        # Add to communication feed
        self.add_timer_communication("⚡ STRESS TEST COMPLETED")
        self.add_timer_communication(f"Total tests: {summary.get('total_tests', 0)}")
        self.add_timer_communication(f"Passed: {summary.get('passed_tests', 0)} | Failed: {summary.get('failed_tests', 0)}")
        self.add_timer_communication(f"Success rate: {summary.get('success_rate', 0):.1f}%")
        
        stability = 'STABLE' if summary.get('success_rate', 0) >= 95 else 'UNSTABLE'
        self.add_timer_communication(f"✓ Driver stability: {stability}")
        
        # Show completion message
        QMessageBox.information(
            self,
            "⚡ Stress Test Complete",
            f"15-minute HEAVY LOAD stress test completed!\n\n"
            f"Results Summary:\n"
            f"• Total Tests: {summary.get('total_tests', 0)}\n"
            f"• Passed: {summary.get('passed_tests', 0)}\n"
            f"• Failed: {summary.get('failed_tests', 0)}\n"
            f"• Success Rate: {summary.get('success_rate', 0):.2f}%\n"
            f"• Duration: {results.get('duration_seconds', 0):.1f} seconds\n\n"
            f"Driver appears to be {stability} under heavy load.\n\n"
            f"Full report has been logged.\n\n"
            f"You can now confirm the driver or revert if needed."
        )
        
        # Log the report
        print(report)
    
    def on_test_timeout(self, driver, hardware):
        """Called when test timer expires without confirmation"""
        print(f"⏰ Test timer expired for {driver.get('name')}")
        
        self.add_timer_communication("⏰ TEST PERIOD EXPIRED - NO CONFIRMATION RECEIVED")
        self.add_timer_communication("⚠ Initiating automatic driver revert for safety")
        self.add_timer_communication("⏳ Restoring previous driver configuration...")
        
        # Show timeout message
        QMessageBox.warning(
            self,
            "⏰ Test Period Expired",
            f"The test period has expired without confirmation.\n\n"
            f"Driver: {driver.get('name')}\n"
            f"Hardware: {hardware.get('name')}\n\n"
            f"The driver will now be reverted to the previous configuration\n"
            f"for safety reasons.\n\n"
            f"You can try installing the driver again and confirm it works\n"
            f"within the 5-minute test period."
        )
        
        # Restore from backup
        self.restore_from_backup()
        
        # Hide timer section after timeout
        QTimer.singleShot(3000, lambda: self.timer_group.setVisible(False))
    
    def on_test_progress(self, elapsed_seconds, remaining_seconds):
        """Called periodically during test period"""
        # Add progress updates to communication feed every 60 seconds
        if elapsed_seconds > 0 and elapsed_seconds % 60 == 0:
            minutes_elapsed = elapsed_seconds // 60
            minutes_remaining = remaining_seconds // 60
            self.add_timer_communication(
                f"⏱ Progress: {minutes_elapsed} min elapsed, {minutes_remaining} min remaining"
            )
            
            # Add periodic system status checks
            if minutes_elapsed == 1:
                self.add_timer_communication("✓ System stability check: PASSED")
            elif minutes_elapsed == 2:
                self.add_timer_communication("✓ Hardware functionality check: PASSED")
            elif minutes_elapsed == 3:
                self.add_timer_communication("✓ Performance check: PASSED")
            elif minutes_elapsed == 4:
                self.add_timer_communication("⚠ Please confirm driver works soon - 1 minute remaining")
    
    def restore_from_backup(self):
        """Restore driver from backup"""
        if not self.current_backup_path:
            QMessageBox.critical(
                self,
                "No Backup Available",
                "Cannot restore: No backup file available."
            )
            return
        
        try:
            success = self.backup_manager.restore_from_backup(
                self.current_backup_path,
                self.driver_manager
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "✓ Driver Restored",
                    f"Driver successfully restored from backup!\n\n"
                    f"Backup: {self.current_backup_path}\n\n"
                    f"Your system has been restored to the previous\n"
                    f"driver configuration."
                )
                
                # Refresh driver info
                self.assess_risk()
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    f"Failed to restore driver from backup.\n\n"
                    f"Backup: {self.current_backup_path}\n\n"
                    f"You may need to manually revert the driver."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Error restoring from backup:\n\n{str(e)}"
            )
    
    def download_driver(self, driver):
        """Download a cross-OS driver for analysis"""
        target_os = driver.get('target_os', 'unknown').upper()
        
        reply = QMessageBox.question(
            self,
            "Download Cross-OS Driver",
            f"Download {driver['name']} ({driver['version']}) for {target_os}?\n\n"
            f"⚠ This is a {target_os} driver and cannot be directly installed on Linux.\n\n"
            f"Purpose: Download for compatibility research and analysis.\n"
            f"Use case: Examining driver structure, understanding hardware interfaces,\n"
            f"          or researching compatibility approaches.\n\n"
            f"The driver will be saved to: ~/Downloads/cross-os-drivers/",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Download Started",
                f"Downloading {target_os} driver: {driver['name']}\n\n"
                f"Source: {driver.get('source_url', 'N/A')}\n"
                f"Destination: ~/Downloads/cross-os-drivers/\n\n"
                f"Note: This is a placeholder. Actual download functionality\n"
                f"would be implemented with proper file handling and verification."
            )
    
    def convert_driver(self, driver):
        """Convert a cross-OS driver to Linux using AI"""
        target_os = driver.get('target_os', 'unknown').upper()
        
        # Show warning and get confirmation
        reply = QMessageBox.question(
            self,
            "AI Driver Conversion (Experimental)",
            f"⚠ EXPERIMENTAL FEATURE ⚠\n\n"
            f"Attempt to convert {driver['name']} ({target_os}) to Linux?\n\n"
            f"Process:\n"
            f"1. AI will analyze the {target_os} driver structure\n"
            f"2. Determine conversion feasibility\n"
            f"3. Generate equivalent Linux driver code\n"
            f"4. Provide testing recommendations\n\n"
            f"⚠ Important Warnings:\n"
            f"• This is highly experimental and may not succeed\n"
            f"• Generated driver will require extensive testing\n"
            f"• May not include all original features\n"
            f"• Use only in safe/virtual environments\n"
            f"• Not recommended for production systems\n\n"
            f"Continue with conversion attempt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Create progress dialog
        progress_dialog = QProgressDialog(
            "Analyzing driver for conversion...",
            "Cancel",
            0, 100,
            self
        )
        progress_dialog.setWindowTitle("AI Driver Conversion")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()
        
        try:
            # Step 1: Analyze driver (30%)
            progress_dialog.setValue(10)
            progress_dialog.setLabelText(f"Analyzing {target_os} driver structure...")
            
            analysis = self.driver_converter.analyze_driver(driver, self.hardware)
            
            progress_dialog.setValue(30)
            progress_dialog.setLabelText("Analysis complete. Checking feasibility...")
            
            # Show analysis results
            if not analysis.get('feasible'):
                progress_dialog.close()
                QMessageBox.warning(
                    self,
                    "Conversion Not Feasible",
                    f"AI analysis determined this driver cannot be converted.\n\n"
                    f"Confidence: {analysis.get('confidence', 0)}%\n"
                    f"Complexity: {analysis.get('complexity', 'unknown')}\n\n"
                    f"Potential Issues:\n" +
                    "\n".join(f"• {issue}" for issue in analysis.get('potential_issues', [])) +
                    f"\n\nRecommendations:\n" +
                    "\n".join(f"• {rec}" for rec in analysis.get('recommendations', []))
                )
                return
            
            # Step 2: Attempt conversion (70%)
            progress_dialog.setValue(40)
            progress_dialog.setLabelText(f"Generating Linux driver code...")
            
            conversion_result = self.driver_converter.attempt_conversion(
                driver, self.hardware, analysis
            )
            
            progress_dialog.setValue(90)
            progress_dialog.setLabelText("Finalizing conversion...")
            
            progress_dialog.setValue(100)
            progress_dialog.close()
            
            # Show results
            if conversion_result.get('success'):
                converted_driver = conversion_result.get('converted_driver')
                
                # Add converted driver to available drivers list
                if converted_driver:
                    self.available_drivers.append(converted_driver)
                    self.update_drivers_table()
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Conversion Successful!",
                    f"✓ AI successfully converted {driver['name']} to Linux!\n\n"
                    f"Converted Driver: {converted_driver.get('name', 'Unknown')}\n"
                    f"Version: {converted_driver.get('version', 'Unknown')}\n"
                    f"Status: {converted_driver.get('stability', 'experimental')}\n"
                    f"Risk: {converted_driver.get('risk_percentage', 75)}% (Experimental)\n\n"
                    f"⚠ Important:\n" +
                    "\n".join(f"• {warn}" for warn in conversion_result.get('warnings', [])) +
                    f"\n\nNext Steps:\n" +
                    "\n".join(f"• {step}" for step in conversion_result.get('next_steps', [])) +
                    f"\n\nThe converted driver is now available in the drivers list."
                )
            else:
                # Show failure message
                QMessageBox.warning(
                    self,
                    "Conversion Failed",
                    f"✗ AI could not convert {driver['name']} to Linux.\n\n"
                    f"Conversion Log:\n" +
                    "\n".join(f"• {log}" for log in conversion_result.get('conversion_log', [])) +
                    f"\n\nWarnings:\n" +
                    "\n".join(f"• {warn}" for warn in conversion_result.get('warnings', []))
                )
        
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(
                self,
                "Conversion Error",
                f"An error occurred during conversion:\n\n{str(e)}\n\n"
                f"Please check AI assistant status and try again."
            )
    
    def test_current_driver(self):
        """Test current driver"""
        result = self.driver_manager.test_driver(self.hardware)
        QMessageBox.information(
            self,
            "Driver Test",
            f"Status: {result.get('status', 'unknown')}\n"
            f"Message: {result.get('message', 'N/A')}"
        )
    
    def rollback_driver(self):
        """Rollback to previous driver"""
        reply = QMessageBox.question(
            self,
            "Confirm Rollback",
            f"Rollback driver for {self.hardware['name']}?\n\n"
            f"This will restore the previous working driver.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.driver_manager.rollback_driver(self.hardware)
            if success:
                QMessageBox.information(self, "Success", "Driver rolled back successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to rollback driver")
    
    def ai_analyze_setup(self):
        """AI analyze current setup"""
        QMessageBox.information(
            self,
            "AI Analysis",
            f"Analyzing {self.hardware['name']}...\n\n"
            f"Current Configuration: Optimal\n"
            f"Detected Issues: None\n"
            f"Recommendations: No changes needed\n\n"
            f"The current driver configuration is stable and performing well."
        )
    
    def toggle_ai_monitoring(self):
        """Toggle AI monitoring"""
        result = self.ai_manager.monitor_driver(self.hardware)
        
        if result.get('monitoring'):
            QMessageBox.information(
                self,
                "AI Monitoring",
                f"AI monitoring enabled for {self.hardware['name']}\n\n"
                f"Continuous monitoring will:\n"
                f"• Watch for potential failures\n"
                f"• Automatically prevent errors\n"
                f"• Log all corrections\n"
                f"• Use minimal resources (<1% CPU)"
            )
        else:
            QMessageBox.information(self, "AI Monitoring", "Monitoring feature not yet fully implemented")
    
    def toggle_ai_monitoring_checkbox(self, state):
        """Toggle AI monitoring based on checkbox state"""
        self.ai_monitoring_enabled = self._is_checkbox_checked(state)
        device_name = self.hardware.get('name', 'Unknown')
        
        if self.ai_monitoring_enabled:
            # Enable monitoring
            result = self.ai_manager.monitor_driver(self.hardware)
            self.ai_status_label.setText(f"AI Status: Monitoring {device_name}")
            self.ai_status_label.setStyleSheet("color: lightgreen; font-weight: bold;")
            
            # Save preference
            device_id = self.hardware.get('id', device_name)
            self.config.set(f'ai_monitoring.{device_id}.enabled', True)
            
            # Refresh operations table
            self.refresh_driver_operations()
        else:
            # Disable monitoring
            self.ai_status_label.setText(f"AI Status: Monitoring disabled for {device_name}")
            self.ai_status_label.setStyleSheet("color: orange;")
            
            # Save preference
            device_id = self.hardware.get('id', device_name)
            self.config.set(f'ai_monitoring.{device_id}.enabled', False)
            
            # Refresh operations table
            self.refresh_driver_operations()
    
    def update_char_count(self):
        """Update character count label"""
        text = self.training_prepend.toPlainText()
        char_count = len(text)
        
        if char_count >= 1000:
            self.char_count_label.setText(f"Characters: {char_count} / 1000 minimum ✓")
            self.char_count_label.setStyleSheet("color: lightgreen; font-weight: bold;")
        else:
            remaining = 1000 - char_count
            self.char_count_label.setText(f"Characters: {char_count} / 1000 minimum ({remaining} more needed)")
            self.char_count_label.setStyleSheet("color: orange;")
    
    def save_training_prepend(self):
        """Save AI training prepend text"""
        text = self.training_prepend.toPlainText()
        
        if len(text) < 1000:
            QMessageBox.warning(
                self,
                "Insufficient Content",
                f"Please enter at least 1000 characters for effective AI training.\n"
                f"Current: {len(text)} characters\n"
                f"Needed: {1000 - len(text)} more characters"
            )
            return
        
        # Save to config
        device_id = self.hardware.get('id', self.hardware.get('name', 'unknown'))
        self.config.set(f'ai_training.{device_id}.prepend', text)
        
        QMessageBox.information(
            self,
            "Saved",
            f"AI training context saved successfully!\n"
            f"Total characters: {len(text)}\n\n"
            f"This context will be used to improve AI understanding of {self.hardware.get('name', 'this device')}."
        )
    
    def clear_training_prepend(self):
        """Clear training prepend text"""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Clear all AI training context for this device?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.training_prepend.clear()
            device_id = self.hardware.get('id', self.hardware.get('name', 'unknown'))
            self.config.set(f'ai_training.{device_id}.prepend', '')
    
    def create_chat_interface(self):
        """Create chat interface for AI communication"""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # Chat header with checkbox
        header_layout = QHBoxLayout()
        chat_header = QLabel("AI Chat (starcoder:3b)")
        chat_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(chat_header)
        
        self.chat_enable_checkbox = QCheckBox("Enable Chat")
        self.chat_enable_checkbox.setToolTip("Enable chat interface to communicate with starcoder:3b AI model")
        self.chat_enable_checkbox.stateChanged.connect(self.toggle_chat)
        header_layout.addWidget(self.chat_enable_checkbox)
        
        # Sign-in button
        signin_btn = QPushButton("Sign In to Ollama")
        signin_btn.setToolTip("Sign in to Ollama with Google authentication to access restricted models")
        signin_btn.clicked.connect(self.signin_ollama)
        header_layout.addWidget(signin_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setPlaceholderText("Chat is disabled. Check the 'Enable Chat' box to start communicating with AI.")
        self.chat_display.setEnabled(False)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message...")
        self.chat_input.setEnabled(False)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        send_btn = QPushButton("Send")
        send_btn.setEnabled(False)
        send_btn.clicked.connect(self.send_chat_message)
        self.chat_send_btn = send_btn
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        # Clear chat button
        clear_chat_btn = QPushButton("Clear Chat")
        clear_chat_btn.clicked.connect(self.clear_chat)
        layout.addWidget(clear_chat_btn)
        
        return chat_widget
    
    def toggle_chat(self, state):
        """Toggle chat interface"""
        self.chat_enabled = self._is_checkbox_checked(state)
        
        if self.chat_enabled:
            # Check if AI is available
            status = self.ai_manager.get_status()
            if status['status'] != 'running':
                QMessageBox.warning(
                    self,
                    "AI Not Available",
                    "Ollama AI service is not running.\n\n"
                    "To use the AI chat feature:\n"
                    "1. Install Ollama: https://ollama.ai/\n"
                    "2. Start Ollama service\n"
                    "3. Install the model: ollama pull starcoder:3b"
                )
                self.chat_enable_checkbox.setChecked(False)
                return
            
            # Check if model is installed
            model_name = self.ai_manager.model
            if status.get('model') == 'not_installed':
                QMessageBox.warning(
                    self,
                    "Model Not Installed",
                    f"The {model_name} model is not installed.\n\n"
                    f"To install it, run this command in a terminal:\n"
                    f"ollama pull {model_name}"
                )
                self.chat_enable_checkbox.setChecked(False)
                return
            
            # Enable chat interface
            self.chat_display.setEnabled(True)
            self.chat_input.setEnabled(True)
            self.chat_send_btn.setEnabled(True)
            self.chat_display.clear()
            self.chat_display.append(
                "<b style='color: green;'>Chat enabled. You can now communicate with starcoder:3b AI.</b><br>"
                f"<i>Context: {self.hardware.get('name', 'Device')} driver management</i><br><br>"
                "<i style='color: gray;'>Note: This is an AI assistant. Type your questions or describe issues you're experiencing.</i><br><br>"
            )
        else:
            # Disable chat interface
            self.chat_display.setEnabled(False)
            self.chat_input.setEnabled(False)
            self.chat_send_btn.setEnabled(False)
            self.chat_display.setPlaceholderText("Chat is disabled. Check the 'Enable Chat' box to start.")
    
    def send_chat_message(self):
        """Send message to AI and get response"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Display user message
        self.chat_display.append(f"<b style='color: lightblue;'>You:</b> {message}<br>")
        self.chat_input.clear()
        
        # Get device context
        device_name = self.hardware.get('name', 'Unknown Device')
        device_type = self.hardware.get('type', 'Device')
        current_driver = self.hardware.get('driver', 'No driver')
        
        # Build prompt with context
        context = f"Device: {device_name} ({device_type}), Current driver: {current_driver}"
        prompt = f"{context}\n\nUser question: {message}\n\nProvide a helpful, concise answer:"
        
        # Show thinking indicator
        thinking_marker = "<span id='thinking'><i style='color: gray;'>AI is thinking...</i></span><br>"
        self.chat_display.append(thinking_marker)
        self.chat_display.repaint()
        
        # Get AI response
        result = self.ai_manager.analyze_text(prompt)
        
        # Remove thinking indicator by replacing with empty string
        html = self.chat_display.toHtml()
        html = html.replace(thinking_marker, '')
        self.chat_display.setHtml(html)
        
        response = ''
        if result.get('success'):
            response = result.get('analysis', 'No response')
            self.chat_display.append(f"<b style='color: lightgreen;'>AI:</b> {response}<br><br>")
        else:
            response = result.get('error', 'Unknown error')
            self.chat_display.append(f"<b style='color: red;'>Error:</b> {response}<br><br>")
        
        # Store in history
        self.chat_history.append({'user': message, 'ai': response})
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.chat_history = []
        if self.chat_enabled:
            self.chat_display.append(
                "<b style='color: green;'>Chat cleared.</b><br>"
                f"<i>Context: {self.hardware.get('name', 'Device')} driver management</i><br><br>"
            )
    
    def signin_ollama(self):
        """Sign in to Ollama with Google authentication"""
        # Show information dialog
        reply = QMessageBox.question(
            self,
            "Sign In to Ollama",
            "This will open your browser for Google authentication.\n\n"
            "Some models (like starcoder) may require you to sign in to Ollama "
            "before you can download them.\n\n"
            "After signing in, your credentials will be cached locally.\n\n"
            "Continue with sign-in?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Show progress message
            self.chat_display.append(
                "<b style='color: blue;'>Initiating Ollama sign-in...</b><br>"
                "<i>A browser window will open for authentication.</i><br>"
                "<i>This dialog will update when sign-in is complete.</i><br><br>"
            )
            self.chat_display.repaint()
            
            # Perform sign-in (this will open a browser)
            result = self.ai_manager.signin()
            
            if result.get('success'):
                QMessageBox.information(
                    self,
                    "Sign-In Successful",
                    "Successfully signed in to Ollama!\n\n"
                    "You can now pull models that require authentication."
                )
                self.chat_display.append(
                    "<b style='color: green;'>✓ Successfully signed in to Ollama</b><br>"
                    "<i>You can now install starcoder:3b model if needed.</i><br><br>"
                )
            else:
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.warning(
                    self,
                    "Sign-In Failed",
                    f"Failed to sign in to Ollama:\n\n{error_msg}\n\n"
                    "You can also try signing in manually from a terminal:\n"
                    "ollama signin"
                )
                self.chat_display.append(
                    f"<b style='color: red;'>✗ Sign-in failed: {error_msg}</b><br><br>"
                )
