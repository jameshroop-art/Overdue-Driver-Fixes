"""
Run All Tests Dialog
Comprehensive testing across all device tabs with AI simulation and driver conversion
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit,
    QCheckBox, QGroupBox, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime
from typing import Dict, Any, List
import time


class AllTestsWorker(QThread):
    """Worker thread for running comprehensive tests on all devices"""
    
    progress = pyqtSignal(str, int, str)  # device_name, percentage, message
    device_complete = pyqtSignal(str, dict)  # device_name, results
    all_complete = pyqtSignal(dict)  # overall_results
    
    def __init__(self, devices, driver_manager, ai_manager, config_manager):
        super().__init__()
        self.devices = devices
        self.driver_manager = driver_manager
        self.ai_manager = ai_manager
        self.config = config_manager
        self.convert_drivers = True
        self.run_stress_tests = True
        self.simulate_all = True  # AI simulation before any hardware operations
        
    def run(self):
        """Run comprehensive tests on all devices"""
        from ai.virtual_kernel_simulator import VirtualKernelSimulator
        from ai.driver_converter import DriverConverter
        from utils.driver_stress_test import DriverStressTest
        
        overall_results = {
            'started': datetime.now().isoformat(),
            'devices_tested': 0,
            'drivers_converted': 0,
            'drivers_tested': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'device_results': {},
            'simulated': self.simulate_all
        }
        
        # Initialize AI virtual kernel simulator
        virtual_kernel = VirtualKernelSimulator(self.ai_manager)
        converter = DriverConverter(self.config, self.ai_manager)
        
        total_devices = len(self.devices)
        
        for idx, (device_name, hardware) in enumerate(self.devices.items()):
            device_progress = int((idx / total_devices) * 100)
            
            self.progress.emit(device_name, device_progress, f"Testing {device_name}...")
            
            device_results = {
                'hardware': hardware,
                'drivers_tested': [],
                'drivers_converted': [],
                'stress_test_results': None,
                'simulation_results': None,
                'overall_status': 'pending'
            }
            
            try:
                # Step 1: Create virtual device for simulation
                if self.simulate_all:
                    self.progress.emit(device_name, device_progress + 5, "Creating virtual device simulation...")
                    vdev_id = virtual_kernel.create_virtual_device(hardware)
                    device_results['virtual_device_id'] = vdev_id
                
                # Step 2: Find available drivers
                self.progress.emit(device_name, device_progress + 10, "Finding available drivers...")
                drivers = self.driver_manager.find_drivers(hardware, include_cross_os=True)
                
                # Step 3: Convert cross-OS drivers to Debian-compatible Linux
                if self.convert_drivers:
                    self.progress.emit(device_name, device_progress + 20, "Converting cross-OS drivers...")
                    
                    for driver in drivers:
                        target_os = driver.get('target_os', 'linux').lower()
                        
                        if target_os != 'linux' and converter.can_convert(driver):
                            self.progress.emit(device_name, device_progress + 25, 
                                             f"Converting {driver['name']} from {target_os}...")
                            
                            # Analyze driver
                            analysis = converter.analyze_driver(driver, hardware)
                            
                            if analysis.get('feasible'):
                                # Attempt conversion
                                conversion_result = converter.attempt_conversion(driver, hardware, analysis)
                                
                                if conversion_result.get('success'):
                                    converted_driver = conversion_result['converted_driver']
                                    device_results['drivers_converted'].append({
                                        'original': driver['name'],
                                        'converted': converted_driver['name'],
                                        'source_os': target_os,
                                        'confidence': analysis.get('confidence', 0)
                                    })
                                    overall_results['drivers_converted'] += 1
                                    
                                    # Add converted driver to test list
                                    drivers.append(converted_driver)
                
                # Step 4: Test each driver in virtual kernel (simulation)
                self.progress.emit(device_name, device_progress + 40, "Testing drivers in virtual kernel...")
                
                for driver_idx, driver in enumerate(drivers):
                    driver_name = driver.get('name', 'Unknown')
                    
                    test_result = {
                        'driver': driver_name,
                        'version': driver.get('version', 'unknown'),
                        'target_os': driver.get('target_os', 'linux'),
                        'simulated': self.simulate_all,
                        'success': False
                    }
                    
                    if self.simulate_all:
                        # Simulate driver loading in virtual kernel
                        self.progress.emit(device_name, device_progress + 45, 
                                         f"Simulating {driver_name} in virtual kernel...")
                        
                        load_result = virtual_kernel.simulate_driver_load(vdev_id, driver)
                        test_result['load_simulation'] = load_result
                        test_result['success'] = load_result['success']
                        
                        if load_result['success']:
                            # Simulate driver operations
                            op_result = virtual_kernel.simulate_driver_operation(
                                vdev_id, 'stress_test', duration_seconds=5  # Short simulation
                            )
                            test_result['operation_simulation'] = op_result
                            
                            # Unload driver for next test
                            virtual_kernel.unload_driver(vdev_id)
                    else:
                        # Real hardware testing (not recommended without user confirmation)
                        test_result['note'] = 'Real hardware testing requires manual confirmation'
                        test_result['success'] = None
                    
                    device_results['drivers_tested'].append(test_result)
                    overall_results['drivers_tested'] += 1
                    
                    if test_result['success']:
                        overall_results['tests_passed'] += 1
                    elif test_result['success'] is False:
                        overall_results['tests_failed'] += 1
                
                # Step 5: Run stress test on best driver
                if self.run_stress_tests and device_results['drivers_tested']:
                    self.progress.emit(device_name, device_progress + 70, "Running stress test...")
                    
                    # Find best performing driver
                    best_driver = None
                    best_score = 0
                    
                    for test_res in device_results['drivers_tested']:
                        if test_res['success'] and 'operation_simulation' in test_res:
                            score = test_res['operation_simulation'].get('performance_score', 0)
                            if score > best_score:
                                best_score = score
                                best_driver = test_res
                    
                    if best_driver:
                        stress_tester = DriverStressTest(hardware)
                        
                        # Run shorter stress test (30 seconds for all tests)
                        stress_result = {}
                        stress_tester.start_stress_test(
                            duration_seconds=30,
                            stress_level='medium',
                            on_complete=lambda r: stress_result.update(r)
                        )
                        
                        # Wait for stress test to complete
                        time.sleep(31)
                        
                        device_results['stress_test_results'] = stress_result
                
                # Mark device as complete
                device_results['overall_status'] = 'completed'
                overall_results['devices_tested'] += 1
                
            except Exception as e:
                device_results['overall_status'] = 'failed'
                device_results['error'] = str(e)
                self.progress.emit(device_name, device_progress, f"Error: {str(e)}")
            
            # Store results and emit signal
            overall_results['device_results'][device_name] = device_results
            self.device_complete.emit(device_name, device_results)
        
        # Complete all tests
        overall_results['completed'] = datetime.now().isoformat()
        
        # Get virtual kernel simulation log
        if self.simulate_all:
            overall_results['simulation_log'] = virtual_kernel.get_simulation_log()
        
        self.all_complete.emit(overall_results)


class RunAllTestsDialog(QDialog):
    """Dialog for running comprehensive tests on all devices"""
    
    def __init__(self, devices, driver_manager, ai_manager, config_manager, parent=None):
        super().__init__(parent)
        self.devices = devices
        self.driver_manager = driver_manager
        self.ai_manager = ai_manager
        self.config = config_manager
        self.test_worker = None
        self.results = None
        
        self.setWindowTitle("Run All Tests - AI Simulation & Driver Conversion")
        self.setMinimumSize(900, 700)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("<h2>Comprehensive Driver Testing</h2>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "This will test all drivers across all device tabs using AI simulation.\n"
            "All tests are simulated before any hardware operations.\n"
            "Cross-OS drivers will be automatically converted to Debian-compatible Linux versions."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Options group
        options_group = QGroupBox("Test Options")
        options_layout = QVBoxLayout()
        
        self.simulate_checkbox = QCheckBox("AI Simulation Mode (Recommended - No Hardware Impact)")
        self.simulate_checkbox.setChecked(True)
        self.simulate_checkbox.setToolTip("All tests run in AI virtual kernel - completely safe")
        options_layout.addWidget(self.simulate_checkbox)
        
        self.convert_checkbox = QCheckBox("Convert Cross-OS Drivers to Debian Linux")
        self.convert_checkbox.setChecked(True)
        self.convert_checkbox.setToolTip("Automatically convert Windows/macOS drivers to Linux")
        options_layout.addWidget(self.convert_checkbox)
        
        self.stress_checkbox = QCheckBox("Run Stress Tests (30 seconds per device)")
        self.stress_checkbox.setChecked(True)
        self.stress_checkbox.setToolTip("Test drivers under simulated heavy load")
        options_layout.addWidget(self.stress_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox("Testing Progress")
        progress_layout = QVBoxLayout()
        
        self.overall_progress_label = QLabel("Ready to start testing")
        progress_layout.addWidget(self.overall_progress_label)
        
        self.overall_progress = QProgressBar()
        progress_layout.addWidget(self.overall_progress)
        
        # Device progress table
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(3)
        self.progress_table.setHorizontalHeaderLabels(["Device", "Status", "Progress"])
        self.progress_table.setRowCount(len(self.devices))
        
        for idx, device_name in enumerate(self.devices.keys()):
            self.progress_table.setItem(idx, 0, QTableWidgetItem(device_name))
            self.progress_table.setItem(idx, 1, QTableWidgetItem("Pending"))
            progress_bar = QProgressBar()
            self.progress_table.setCellWidget(idx, 2, progress_bar)
        
        self.progress_table.resizeColumnsToContents()
        progress_layout.addWidget(self.progress_table)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        layout.addWidget(QLabel("Test Log:"))
        layout.addWidget(self.log_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start All Tests")
        self.start_button.clicked.connect(self.start_tests)
        button_layout.addWidget(self.start_button)
        
        self.view_results_button = QPushButton("View Detailed Results")
        self.view_results_button.setEnabled(False)
        self.view_results_button.clicked.connect(self.view_results)
        button_layout.addWidget(self.view_results_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_tests(self):
        """Start comprehensive testing"""
        if not self.devices:
            QMessageBox.warning(self, "No Devices", "No devices found to test.")
            return
        
        # Confirm simulation mode
        if self.simulate_checkbox.isChecked():
            msg = QMessageBox.information(
                self,
                "AI Simulation Mode",
                "Testing will run in AI simulation mode.\n\n"
                "✓ Completely safe - no hardware operations\n"
                "✓ AI virtual kernel simulates device behavior\n"
                "✓ Drivers converted to Debian-compatible Linux\n"
                "✓ All tests are simulated before any real operations\n\n"
                "Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if msg == QMessageBox.StandardButton.No:
                return
        else:
            msg = QMessageBox.warning(
                self,
                "Real Hardware Testing",
                "⚠️ WARNING: Real hardware testing is NOT recommended!\n\n"
                "This will attempt actual driver operations on hardware.\n"
                "Use AI Simulation Mode instead.\n\n"
                "Continue with REAL hardware testing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if msg == QMessageBox.StandardButton.No:
                return
        
        # Disable controls
        self.start_button.setEnabled(False)
        self.simulate_checkbox.setEnabled(False)
        self.convert_checkbox.setEnabled(False)
        self.stress_checkbox.setEnabled(False)
        
        # Create and start worker
        self.test_worker = AllTestsWorker(
            self.devices,
            self.driver_manager,
            self.ai_manager,
            self.config
        )
        
        self.test_worker.convert_drivers = self.convert_checkbox.isChecked()
        self.test_worker.run_stress_tests = self.stress_checkbox.isChecked()
        self.test_worker.simulate_all = self.simulate_checkbox.isChecked()
        
        self.test_worker.progress.connect(self.on_progress)
        self.test_worker.device_complete.connect(self.on_device_complete)
        self.test_worker.all_complete.connect(self.on_all_complete)
        
        self.log("Starting comprehensive driver testing...")
        if self.simulate_checkbox.isChecked():
            self.log("✓ AI Simulation Mode: All tests are simulated - no hardware impact")
        
        self.test_worker.start()
    
    def on_progress(self, device_name: str, percentage: int, message: str):
        """Handle progress update"""
        # Update device row
        for row in range(self.progress_table.rowCount()):
            item = self.progress_table.item(row, 0)
            if item and item.text() == device_name:
                self.progress_table.item(row, 1).setText(message)
                progress_bar = self.progress_table.cellWidget(row, 2)
                if progress_bar:
                    progress_bar.setValue(percentage)
                break
        
        # Update overall progress
        total_devices = len(self.devices)
        completed_devices = sum(1 for row in range(self.progress_table.rowCount())
                               if self.progress_table.cellWidget(row, 2).value() == 100)
        overall_percentage = int((completed_devices / total_devices) * 100)
        self.overall_progress.setValue(overall_percentage)
        self.overall_progress_label.setText(f"Testing: {completed_devices}/{total_devices} devices complete")
        
        self.log(f"[{device_name}] {message}")
    
    def on_device_complete(self, device_name: str, results: dict):
        """Handle device testing completion"""
        status = results.get('overall_status', 'unknown')
        
        # Update device row
        for row in range(self.progress_table.rowCount()):
            item = self.progress_table.item(row, 0)
            if item and item.text() == device_name:
                status_item = self.progress_table.item(row, 1)
                
                if status == 'completed':
                    status_item.setText("✓ Complete")
                    status_item.setForeground(QColor(0, 150, 0))
                else:
                    status_item.setText("✗ Failed")
                    status_item.setForeground(QColor(200, 0, 0))
                
                progress_bar = self.progress_table.cellWidget(row, 2)
                if progress_bar:
                    progress_bar.setValue(100)
                break
        
        # Log summary
        drivers_tested = len(results.get('drivers_tested', []))
        drivers_converted = len(results.get('drivers_converted', []))
        
        self.log(f"[{device_name}] ✓ Complete: {drivers_tested} drivers tested, {drivers_converted} converted")
    
    def on_all_complete(self, results: dict):
        """Handle all testing completion"""
        self.results = results
        
        # Enable controls
        self.view_results_button.setEnabled(True)
        
        # Show summary
        devices_tested = results.get('devices_tested', 0)
        drivers_tested = results.get('drivers_tested', 0)
        drivers_converted = results.get('drivers_converted', 0)
        tests_passed = results.get('tests_passed', 0)
        tests_failed = results.get('tests_failed', 0)
        
        self.overall_progress.setValue(100)
        self.overall_progress_label.setText("All testing complete!")
        
        self.log("\n" + "="*60)
        self.log("TESTING COMPLETE")
        self.log("="*60)
        self.log(f"Devices tested: {devices_tested}")
        self.log(f"Drivers tested: {drivers_tested}")
        self.log(f"Drivers converted to Debian Linux: {drivers_converted}")
        self.log(f"Tests passed: {tests_passed}")
        self.log(f"Tests failed: {tests_failed}")
        self.log(f"Success rate: {(tests_passed/(tests_passed+tests_failed)*100 if tests_passed+tests_failed > 0 else 0):.1f}%")
        
        if results.get('simulated'):
            self.log("\n✓ All tests were simulated - NO hardware operations performed")
        
        QMessageBox.information(
            self,
            "Testing Complete",
            f"Comprehensive testing complete!\n\n"
            f"• {devices_tested} devices tested\n"
            f"• {drivers_tested} drivers tested\n"
            f"• {drivers_converted} drivers converted to Debian Linux\n"
            f"• {tests_passed} tests passed\n"
            f"• {tests_failed} tests failed\n\n"
            f"{'✓ All tests were simulated (no hardware impact)' if results.get('simulated') else ''}"
        )
    
    def view_results(self):
        """View detailed test results"""
        if not self.results:
            return
        
        # Create results dialog
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle("Detailed Test Results")
        results_dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create tabs for each device
        tabs = QTabWidget()
        
        for device_name, device_results in self.results.get('device_results', {}).items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Device info
            info_text = f"<h3>{device_name}</h3>"
            info_text += f"<p>Status: {device_results.get('overall_status', 'unknown')}</p>"
            
            info_label = QLabel(info_text)
            tab_layout.addWidget(info_label)
            
            # Drivers tested table
            drivers_table = QTableWidget()
            drivers_table.setColumnCount(4)
            drivers_table.setHorizontalHeaderLabels(["Driver", "Version", "Target OS", "Result"])
            
            drivers_tested = device_results.get('drivers_tested', [])
            drivers_table.setRowCount(len(drivers_tested))
            
            for idx, driver_result in enumerate(drivers_tested):
                drivers_table.setItem(idx, 0, QTableWidgetItem(driver_result.get('driver', '')))
                drivers_table.setItem(idx, 1, QTableWidgetItem(driver_result.get('version', '')))
                drivers_table.setItem(idx, 2, QTableWidgetItem(driver_result.get('target_os', '')))
                
                result_item = QTableWidgetItem("✓ Pass" if driver_result.get('success') else "✗ Fail")
                if driver_result.get('success'):
                    result_item.setForeground(QColor(0, 150, 0))
                else:
                    result_item.setForeground(QColor(200, 0, 0))
                
                drivers_table.setItem(idx, 3, result_item)
            
            drivers_table.resizeColumnsToContents()
            tab_layout.addWidget(QLabel("Drivers Tested:"))
            tab_layout.addWidget(drivers_table)
            
            # Converted drivers
            if device_results.get('drivers_converted'):
                conv_label = QLabel(f"<b>Converted Drivers ({len(device_results['drivers_converted'])}):</b>")
                tab_layout.addWidget(conv_label)
                
                for conv in device_results['drivers_converted']:
                    conv_text = f"• {conv['original']} ({conv['source_os']}) → {conv['converted']} (Linux) - {conv['confidence']}% confidence"
                    tab_layout.addWidget(QLabel(conv_text))
            
            tab.setLayout(tab_layout)
            tabs.addTab(tab, device_name)
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(results_dialog.accept)
        layout.addWidget(close_btn)
        
        results_dialog.setLayout(layout)
        results_dialog.exec()
    
    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
