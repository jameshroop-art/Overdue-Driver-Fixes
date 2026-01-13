"""
Hardware Testing Tab
Comprehensive testing interface for WiFi, Chipsets, and other hardware
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QScrollArea,
    QCheckBox, QLineEdit, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from datetime import datetime
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.driver_stress_test import DriverStressTest


class HardwareTestWorker(QThread):
    """Worker thread for hardware stress testing"""
    progress = pyqtSignal(str, str, float)  # test_name, status, elapsed_seconds
    finished = pyqtSignal(dict)  # results
    
    def __init__(self, hardware_info, duration_seconds, stress_level):
        super().__init__()
        self.hardware_info = hardware_info
        self.duration_seconds = duration_seconds
        self.stress_level = stress_level
        self.stress_tester = None
    
    def run(self):
        """Run hardware stress test"""
        self.stress_tester = DriverStressTest(self.hardware_info)
        
        test_completed = False
        final_results = None
        
        def on_progress(test_name, status, elapsed):
            self.progress.emit(test_name, status, elapsed)
        
        def on_complete(results):
            nonlocal test_completed, final_results
            test_completed = True
            final_results = results
        
        # Start stress test
        success = self.stress_tester.start_stress_test(
            duration_seconds=self.duration_seconds,
            stress_level=self.stress_level,
            on_progress=on_progress,
            on_complete=on_complete
        )
        
        if not success:
            self.finished.emit({'error': 'Failed to start stress test'})
            return
        
        # Wait for completion
        while not test_completed:
            self.msleep(100)
        
        if final_results:
            self.finished.emit(final_results)
        else:
            self.finished.emit({'error': 'Test did not complete properly'})


class WiFiTestingTab(QWidget):
    """WiFi driver and chipset testing interface"""
    
    def __init__(self):
        super().__init__()
        self.test_worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize WiFi testing UI"""
        layout = QVBoxLayout()
        
        # Configuration section
        config_group = QGroupBox("WiFi Configuration")
        config_layout = QVBoxLayout()
        
        # Chipset selection
        chipset_layout = QHBoxLayout()
        chipset_layout.addWidget(QLabel("WiFi Chipset:"))
        self.chipset_combo = QComboBox()
        self.chipset_combo.addItems([
            'Intel AX211 (WiFi 6E)',
            'Intel AX210 (WiFi 6E)',
            'Intel AX201 (WiFi 6)',
            'Intel AX200 (WiFi 6)',
            'Realtek RTL8852BE (WiFi 6E)',
            'MediaTek MT7921 (WiFi 6E)',
            'Qualcomm QCA6390 (WiFi 6)',
            'Broadcom BCM4378 (WiFi 6E)'
        ])
        self.chipset_combo.currentTextChanged.connect(self.update_chipset_info)
        chipset_layout.addWidget(self.chipset_combo)
        chipset_layout.addStretch()
        config_layout.addLayout(chipset_layout)
        
        # Chipset info display
        self.chipset_info_label = QLabel()
        self.chipset_info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        config_layout.addWidget(self.chipset_info_label)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Test configuration
        test_config_group = QGroupBox("Test Configuration")
        test_config_layout = QVBoxLayout()
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Test Duration:"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(['5 minutes', '10 minutes', '15 minutes', '30 minutes'])
        self.duration_combo.setCurrentIndex(2)  # Default to 15 minutes
        duration_layout.addWidget(self.duration_combo)
        duration_layout.addStretch()
        test_config_layout.addLayout(duration_layout)
        
        # Stress level
        stress_layout = QHBoxLayout()
        stress_layout.addWidget(QLabel("Stress Level:"))
        self.stress_combo = QComboBox()
        self.stress_combo.addItems(['Light', 'Medium', 'Heavy', 'Extreme'])
        self.stress_combo.setCurrentIndex(2)  # Default to Heavy
        stress_layout.addWidget(self.stress_combo)
        stress_layout.addStretch()
        test_config_layout.addLayout(stress_layout)
        
        test_config_group.setLayout(test_config_layout)
        layout.addWidget(test_config_group)
        
        # Test controls
        controls_layout = QHBoxLayout()
        
        self.start_test_btn = QPushButton("▶ Start WiFi Stress Test")
        self.start_test_btn.setStyleSheet("font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")
        self.start_test_btn.clicked.connect(self.start_wifi_test)
        controls_layout.addWidget(self.start_test_btn)
        
        self.stop_test_btn = QPushButton("⏹ Stop Test")
        self.stop_test_btn.setEnabled(False)
        self.stop_test_btn.clicked.connect(self.stop_test)
        controls_layout.addWidget(self.stop_test_btn)
        
        layout.addLayout(controls_layout)
        
        # Progress section
        progress_group = QGroupBox("Test Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to test")
        progress_layout.addWidget(self.progress_label)
        
        # Real-time stats
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Tests: 0 | Passed: 0 | Failed: 0 | Success Rate: 0%")
        stats_layout.addWidget(self.stats_label)
        progress_layout.addLayout(stats_layout)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Results display
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Update initial chipset info
        self.update_chipset_info()
    
    def update_chipset_info(self):
        """Update chipset information display"""
        chipset_text = self.chipset_combo.currentText()
        
        # Parse chipset info
        chipset_data = {
            'Intel AX211': {'standard': 'WiFi 6E (802.11ax)', 'bands': '2.4/5/6 GHz', 'speed': '2.4 Gbps', 'driver': 'iwlwifi'},
            'Intel AX210': {'standard': 'WiFi 6E (802.11ax)', 'bands': '2.4/5/6 GHz', 'speed': '2.4 Gbps', 'driver': 'iwlwifi'},
            'Intel AX201': {'standard': 'WiFi 6 (802.11ax)', 'bands': '2.4/5 GHz', 'speed': '2.4 Gbps', 'driver': 'iwlwifi'},
            'Intel AX200': {'standard': 'WiFi 6 (802.11ax)', 'bands': '2.4/5 GHz', 'speed': '2.4 Gbps', 'driver': 'iwlwifi'},
            'Realtek RTL8852BE': {'standard': 'WiFi 6E (802.11ax)', 'bands': '2.4/5/6 GHz', 'speed': '2.4 Gbps', 'driver': 'rtw89'},
            'MediaTek MT7921': {'standard': 'WiFi 6E (802.11ax)', 'bands': '2.4/5/6 GHz', 'speed': '2.4 Gbps', 'driver': 'mt7921e'},
            'Qualcomm QCA6390': {'standard': 'WiFi 6 (802.11ax)', 'bands': '2.4/5 GHz', 'speed': '1.2 Gbps', 'driver': 'ath11k'},
            'Broadcom BCM4378': {'standard': 'WiFi 6E (802.11ax)', 'bands': '2.4/5/6 GHz', 'speed': '2.4 Gbps', 'driver': 'brcmfmac'},
        }
        
        chipset_name = chipset_text.split(' (')[0]
        info = chipset_data.get(chipset_name, {})
        
        info_text = f"""
<b>Chipset:</b> {chipset_name}<br>
<b>Standard:</b> {info.get('standard', 'Unknown')}<br>
<b>Bands:</b> {info.get('bands', 'Unknown')}<br>
<b>Max Speed:</b> {info.get('speed', 'Unknown')}<br>
<b>Driver:</b> {info.get('driver', 'Unknown')}
"""
        self.chipset_info_label.setText(info_text)
    
    def start_wifi_test(self):
        """Start WiFi stress test"""
        chipset_text = self.chipset_combo.currentText()
        chipset_name = chipset_text.split(' (')[0]
        
        # Get duration in seconds
        duration_text = self.duration_combo.currentText()
        duration_minutes = int(duration_text.split()[0])
        duration_seconds = duration_minutes * 60
        
        # Get stress level
        stress_level = self.stress_combo.currentText().lower()
        
        # Create WiFi hardware info
        wifi_hardware = {
            'name': chipset_name,
            'type': 'WiFi',
            'vendor': chipset_name.split()[0],
            'id': 'test-wifi-001',
            'driver': 'iwlwifi',  # Will be updated based on chipset
        }
        
        # Confirm start
        reply = QMessageBox.question(
            self,
            "Start WiFi Stress Test",
            f"Start {duration_minutes}-minute {stress_level} stress test?\n\n"
            f"Chipset: {chipset_name}\n"
            f"Duration: {duration_minutes} minutes\n"
            f"Stress Level: {stress_level.upper()}\n\n"
            f"This test will simulate heavy WiFi usage including:\n"
            f"• Connection stability\n"
            f"• Packet transmission\n"
            f"• Signal strength monitoring\n"
            f"• Authentication\n"
            f"• Bandwidth throughput\n"
            f"• Reconnection scenarios\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable start button, enable stop button
        self.start_test_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Starting {stress_level} WiFi stress test...")
        self.results_text.clear()
        
        # Start test worker
        self.test_worker = HardwareTestWorker(
            wifi_hardware,
            duration_seconds,
            stress_level
        )
        self.test_worker.progress.connect(self.on_test_progress)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.start()
        
        # Start timer for progress updates
        self.test_start_time = datetime.now()
        self.test_duration = duration_seconds
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        self.progress_timer.start(1000)  # Update every second
    
    def update_progress_bar(self):
        """Update progress bar based on elapsed time"""
        if not hasattr(self, 'test_start_time'):
            return
        
        elapsed = (datetime.now() - self.test_start_time).total_seconds()
        progress = min(100, int((elapsed / self.test_duration) * 100))
        self.progress_bar.setValue(progress)
        
        # Update time remaining
        remaining = max(0, self.test_duration - elapsed)
        remaining_min = int(remaining // 60)
        remaining_sec = int(remaining % 60)
        
        self.progress_label.setText(
            f"Testing... Time remaining: {remaining_min:02d}:{remaining_sec:02d}"
        )
    
    def on_test_progress(self, test_name: str, status: str, elapsed_seconds: float):
        """Handle test progress updates"""
        # This is called frequently, so we update stats label
        if hasattr(self.test_worker, 'stress_tester') and self.test_worker.stress_tester:
            results = self.test_worker.stress_tester.get_results()
            summary = results.get('summary', {})
            
            self.stats_label.setText(
                f"Tests: {summary.get('total_tests', 0)} | "
                f"Passed: {summary.get('passed_tests', 0)} | "
                f"Failed: {summary.get('failed_tests', 0)} | "
                f"Success Rate: {summary.get('success_rate', 0):.1f}%"
            )
    
    def on_test_finished(self, results: dict):
        """Handle test completion"""
        if self.progress_timer:
            self.progress_timer.stop()
        
        # Re-enable buttons
        self.start_test_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        
        self.progress_bar.setValue(100)
        self.progress_label.setText("Test completed!")
        
        if 'error' in results:
            QMessageBox.critical(
                self,
                "Test Failed",
                f"WiFi stress test failed:\n{results['error']}"
            )
            return
        
        # Display results
        summary = results.get('summary', {})
        
        success_rate = summary.get('success_rate', 0)
        if success_rate >= 99:
            assessment = "EXCELLENT - WiFi driver is highly stable"
        elif success_rate >= 97:
            assessment = "GOOD - WiFi driver is stable"
        elif success_rate >= 95:
            assessment = "ACCEPTABLE - WiFi driver shows good stability"
        elif success_rate >= 90:
            assessment = "MARGINAL - WiFi driver may have issues"
        else:
            assessment = "POOR - WiFi driver shows instability"
        
        results_text = f"""
WiFi Stress Test Complete!

Chipset: {self.chipset_combo.currentText()}
Duration: {results.get('duration_seconds', 0):.1f} seconds
Stress Level: {results.get('stress_level', 'unknown').upper()}

Results:
  Total Tests: {summary.get('total_tests', 0)}
  Passed: {summary.get('passed_tests', 0)}
  Failed: {summary.get('failed_tests', 0)}
  Success Rate: {success_rate:.2f}%

Assessment: {assessment}

Report saved to: ~/.config/driver-mgt/stress-tests/
"""
        self.results_text.setPlainText(results_text)
        
        # Show completion dialog
        QMessageBox.information(
            self,
            "Test Complete",
            f"WiFi stress test completed!\n\n{assessment}\n\n"
            f"Success Rate: {success_rate:.2f}%"
        )
    
    def stop_test(self):
        """Stop running test"""
        if self.test_worker and self.test_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Stop Test",
                "Stop the running WiFi stress test?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if hasattr(self.test_worker, 'stress_tester') and self.test_worker.stress_tester:
                    self.test_worker.stress_tester.stop_stress_test()
                
                self.start_test_btn.setEnabled(True)
                self.stop_test_btn.setEnabled(False)
                
                if self.progress_timer:
                    self.progress_timer.stop()
                
                self.progress_label.setText("Test stopped by user")


class ChipsetTestingTab(QWidget):
    """Chipset testing interface for various hardware types"""
    
    def __init__(self):
        super().__init__()
        self.test_worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize chipset testing UI"""
        layout = QVBoxLayout()
        
        # Chipset type selection
        type_group = QGroupBox("Chipset Type")
        type_layout = QHBoxLayout()
        
        type_layout.addWidget(QLabel("Select Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            'Network (Ethernet)',
            'Storage (NVMe/SATA)',
            'USB Controller',
            'Audio Codec',
            'Bluetooth'
        ])
        self.type_combo.currentTextChanged.connect(self.update_chipset_options)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Chipset model selection
        model_group = QGroupBox("Chipset Model")
        model_layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
        # Chipset info
        self.chipset_info = QLabel()
        self.chipset_info.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        model_layout.addWidget(self.chipset_info)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Similar test configuration as WiFi tab
        # (omitted for brevity - would be similar to WiFi tab)
        
        info_label = QLabel("Chipset stress testing allows comprehensive validation of:\n"
                          "• Network controllers (Ethernet)\n"
                          "• Storage controllers (NVMe, SATA)\n"
                          "• USB controllers\n"
                          "• Audio codecs\n"
                          "• Bluetooth adapters")
        info_label.setStyleSheet("padding: 15px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Initialize chipset options
        self.update_chipset_options()
    
    def update_chipset_options(self):
        """Update available chipset models based on type"""
        chipset_type = self.type_combo.currentText()
        
        models = {
            'Network (Ethernet)': [
                'Intel I225-V (2.5GbE)',
                'Intel I226-V (2.5GbE)',
                'Realtek RTL8125B (2.5GbE)',
                'Marvell AQtion AQC113 (10GbE)'
            ],
            'Storage (NVMe/SATA)': [
                'Samsung 990 Pro Controller',
                'Intel SSD Controller',
                'AMD FCH SATA Controller',
                'Phison E18 Controller'
            ],
            'USB Controller': [
                'Intel USB 3.2 Controller',
                'AMD USB 3.2 Controller',
                'ASMedia ASM3142 (USB 3.2 Gen2x2)'
            ],
            'Audio Codec': [
                'Realtek ALC4080',
                'Realtek ALC1220',
                'Creative Sound Core3D'
            ],
            'Bluetooth': [
                'Intel AX211 BT',
                'Realtek RTL8852BE BT',
                'Qualcomm QCA6390 BT'
            ]
        }
        
        self.model_combo.clear()
        self.model_combo.addItems(models.get(chipset_type, []))


class HardwareTestingWidget(QWidget):
    """Main hardware testing widget with tabs"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize main hardware testing UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Hardware Driver Testing")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget
        tabs = QTabWidget()
        
        # WiFi testing tab
        wifi_tab = WiFiTestingTab()
        tabs.addTab(wifi_tab, "📶 WiFi Testing")
        
        # Chipset testing tab
        chipset_tab = ChipsetTestingTab()
        tabs.addTab(chipset_tab, "🔌 Chipset Testing")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
