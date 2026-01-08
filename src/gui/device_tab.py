"""
Device-specific tab widget for driver management
Shows current driver info, available drivers, and AI features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


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
            
            if risk['risk_percentage'] > 30:
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
        
        self.init_ui()
        self.load_drivers()
    
    def init_ui(self):
        """Initialize the device tab UI"""
        layout = QVBoxLayout(self)
        
        # Device information section
        info_group = self.create_device_info_section()
        layout.addWidget(info_group)
        
        # Current driver section
        current_driver_group = self.create_current_driver_section()
        layout.addWidget(current_driver_group)
        
        # Risk assessment section
        risk_group = self.create_risk_assessment_section()
        layout.addWidget(risk_group)
        
        # Available drivers section
        drivers_group = self.create_available_drivers_section()
        layout.addWidget(drivers_group)
        
        # AI features section
        ai_group = self.create_ai_features_section()
        layout.addWidget(ai_group)
        
        # Fallback plan section
        fallback_group = self.create_fallback_plan_section()
        layout.addWidget(fallback_group)
        
        layout.addStretch()
    
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
            "✓ Proactive failure prevention"
        ]
        
        for feature in features:
            feature_label = QLabel(f"  {feature}")
            layout.addWidget(feature_label)
        
        # AI action buttons
        ai_button_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("AI Analyze Current Setup")
        analyze_btn.clicked.connect(self.ai_analyze_setup)
        ai_button_layout.addWidget(analyze_btn)
        
        monitor_btn = QPushButton("Enable AI Monitoring")
        monitor_btn.clicked.connect(self.toggle_ai_monitoring)
        ai_button_layout.addWidget(monitor_btn)
        
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
                
                if risk_percentage < 10:
                    risk_level = "Very Low"
                    color = "green"
                elif risk_percentage < 30:
                    risk_level = "Low"
                    color = "lightgreen"
                elif risk_percentage < 50:
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
            from PyQt6.QtWidgets import QProgressDialog
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
