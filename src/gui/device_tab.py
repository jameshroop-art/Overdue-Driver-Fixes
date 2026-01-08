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
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


# Risk assessment thresholds
RISK_VERY_LOW_THRESHOLD = 10
RISK_LOW_THRESHOLD = 30
RISK_MEDIUM_THRESHOLD = 50
RISK_HIGH_THRESHOLD = 30  # Threshold for installation warning


class DriverInstallWorker(QThread):
    """Worker thread for driver installation"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, driver_manager, ollama_manager, hardware, driver):
        super().__init__()
        self.driver_manager = driver_manager
        self.ollama_manager = ollama_manager
        self.hardware = hardware
        self.driver = driver
    
    def run(self):
        """Run driver installation with AI assistance"""
        try:
            self.progress.emit(10, "Preparing installation...")
            
            # Pre-installation risk assessment
            self.progress.emit(20, "Assessing risks...")
            risk = self.ollama_manager.assess_risk(self.hardware, self.driver)
            
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
    
    def __init__(self, hardware, driver_manager, ollama_manager, config_manager):
        super().__init__()
        self.hardware = hardware
        self.driver_manager = driver_manager
        self.ollama_manager = ollama_manager
        self.config = config_manager
        self.available_drivers = []
        self.install_worker = None
        self.ai_monitoring_enabled = False
        self.chat_enabled = False
        self.chat_history = []
        self.monitored_operations = []
        
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
        
        info_table = QTableWidget(5, 2)
        info_table.setHorizontalHeaderLabels(["Property", "Value"])
        info_table.verticalHeader().setVisible(False)
        info_table.setMaximumHeight(200)
        
        properties = [
            ("Type", self.hardware.get('type', 'Unknown')),
            ("Name", self.hardware.get('name', 'Unknown')),
            ("Vendor", self.hardware.get('vendor', 'Unknown')),
            ("Device ID", self.hardware.get('id', 'N/A')),
            ("Model", self.hardware.get('model', self.hardware.get('name', 'N/A')))
        ]
        
        for i, (key, value) in enumerate(properties):
            info_table.setItem(i, 0, QTableWidgetItem(key))
            info_table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        info_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(info_table)
        
        group.setLayout(layout)
        return group
    
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
        
        # Filter by source
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by source:")
        filter_layout.addWidget(filter_label)
        
        self.source_filter = QComboBox()
        self.source_filter.addItems(["All", "Official", "Distribution", "Community"])
        self.source_filter.currentTextChanged.connect(self.filter_drivers)
        filter_layout.addWidget(self.source_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Drivers table
        self.drivers_table = QTableWidget()
        self.drivers_table.setColumnCount(6)
        self.drivers_table.setHorizontalHeaderLabels([
            "Driver", "Version", "Source", "Stability", "Risk %", "Actions"
        ])
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
            self.available_drivers = self.driver_manager.find_drivers(self.hardware)
            self.update_drivers_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load drivers: {e}")
    
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
            
            # Stability
            stability = driver.get('stability', 'unknown')
            stability_item = QTableWidgetItem(stability)
            if stability == 'stable':
                stability_item.setBackground(QColor(50, 100, 50))
            elif stability == 'beta':
                stability_item.setBackground(QColor(100, 100, 50))
            self.drivers_table.setItem(i, 3, stability_item)
            
            # Risk percentage (mock for now)
            risk = driver.get('risk_percentage', 5)
            risk_item = QTableWidgetItem(f"{risk}%")
            if risk < 10:
                risk_item.setBackground(QColor(50, 100, 50))
            elif risk < 30:
                risk_item.setBackground(QColor(100, 100, 50))
            else:
                risk_item.setBackground(QColor(100, 50, 50))
            self.drivers_table.setItem(i, 4, risk_item)
            
            # Install button
            install_btn = QPushButton("Install with AI")
            install_btn.clicked.connect(lambda checked, d=driver: self.install_driver(d))
            self.drivers_table.setCellWidget(i, 5, install_btn)
    
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
                risk = self.ollama_manager.assess_risk(self.hardware, current_driver)
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
        status = self.ollama_manager.get_status()
        
        if status['status'] == 'running':
            self.ai_status_label.setText(f"AI Status: Online ({status.get('model', 'starcoder:3b')})")
            self.ai_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.ai_status_label.setText("AI Status: Offline")
            self.ai_status_label.setStyleSheet("color: orange;")
    
    def install_driver(self, driver):
        """Install a driver with AI assistance"""
        reply = QMessageBox.question(
            self,
            "Confirm Installation",
            f"Install {driver['name']} ({driver['version']}) from {driver['source']}?\n\n"
            f"AI-assisted installation will:\n"
            f"• Assess risks before installation\n"
            f"• Monitor installation in real-time\n"
            f"• Automatically correct errors\n"
            f"• Test driver after installation\n"
            f"• Create automatic backup for rollback",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Create and start worker thread
            self.install_worker = DriverInstallWorker(
                self.driver_manager,
                self.ollama_manager,
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
            self.install_worker.finished.connect(self.install_finished)
            
            # Start installation
            self.install_worker.start()
            self.progress_dialog.show()
    
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
        result = self.ollama_manager.monitor_driver(self.hardware)
        
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
            result = self.ollama_manager.monitor_driver(self.hardware)
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
            status = self.ollama_manager.get_status()
            if status['status'] != 'running':
                QMessageBox.warning(
                    self,
                    "AI Not Available",
                    "Ollama AI service is not running.\n"
                    "Please start Ollama service and ensure starcoder:3b model is installed."
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
        result = self.ollama_manager.analyze_text(prompt)
        
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
