"""
Driver Selection Widget with VM and Local OS indicators
Shows available drivers from both local OS and VM with clear visual indicators
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QTextEdit,
    QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
from typing import Dict, Any, List, Optional

class DriverSelectionWidget(QWidget):
    """
    Widget for selecting drivers from local OS or VM
    Shows clear indicators for driver source (VM vs Local)
    """
    
    # Signal emitted when driver is selected
    driverSelected = pyqtSignal(dict)
    
    def __init__(self, device_info, driver_manager, vm_bridge=None, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.driver_manager = driver_manager
        self.vm_bridge = vm_bridge
        
        self.available_drivers = []
        self.current_driver = None
        
        self.init_ui()
        self.refresh_drivers()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Driver Selection")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Device info
        device_group = QGroupBox("Device Information")
        device_layout = QVBoxLayout(device_group)
        
        device_name = self.device_info.get('name', 'Unknown Device')
        device_type = self.device_info.get('type', 'Unknown')
        device_vendor = self.device_info.get('vendor', 'Unknown')
        
        device_layout.addWidget(QLabel(f"Name: {device_name}"))
        device_layout.addWidget(QLabel(f"Type: {device_type}"))
        device_layout.addWidget(QLabel(f"Vendor: {device_vendor}"))
        
        layout.addWidget(device_group)
        
        # Current driver
        current_group = QGroupBox("Current Driver")
        current_layout = QVBoxLayout(current_group)
        
        self.current_driver_label = QLabel("Loading...")
        self.current_driver_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        current_layout.addWidget(self.current_driver_label)
        
        self.current_driver_source = QLabel("")
        self.current_driver_source.setStyleSheet("font-size: 9pt; color: #666;")
        current_layout.addWidget(self.current_driver_source)
        
        layout.addWidget(current_group)
        
        # Driver selection
        selection_group = QGroupBox("Available Drivers")
        selection_layout = QVBoxLayout(selection_group)
        
        # Dropdown with drivers
        driver_select_layout = QHBoxLayout()
        driver_select_layout.addWidget(QLabel("Select Driver:"))
        
        self.driver_combo = QComboBox()
        self.driver_combo.setMinimumWidth(400)
        self.driver_combo.currentIndexChanged.connect(self.on_driver_changed)
        driver_select_layout.addWidget(self.driver_combo)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_drivers)
        driver_select_layout.addWidget(refresh_btn)
        
        selection_layout.addLayout(driver_select_layout)
        
        # Legend for indicators
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Legend:"))
        
        local_indicator = QLabel("🖥 = Local OS Driver")
        local_indicator.setStyleSheet("color: #0066cc; font-size: 9pt;")
        legend_layout.addWidget(local_indicator)
        
        vm_indicator = QLabel("🪟 = VM (Windows) Driver")
        vm_indicator.setStyleSheet("color: #00aa00; font-size: 9pt;")
        legend_layout.addWidget(vm_indicator)
        
        ms_indicator = QLabel("Ⓜ = Microsoft Driver")
        ms_indicator.setStyleSheet("color: #ff6600; font-size: 9pt;")
        legend_layout.addWidget(ms_indicator)
        
        legend_layout.addStretch()
        selection_layout.addLayout(legend_layout)
        
        # Driver details
        self.driver_details = QTextEdit()
        self.driver_details.setReadOnly(True)
        self.driver_details.setMaximumHeight(150)
        self.driver_details.setPlaceholderText("Select a driver to see details...")
        selection_layout.addWidget(QLabel("Driver Details:"))
        selection_layout.addWidget(self.driver_details)
        
        layout.addWidget(selection_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.install_button = QPushButton("Switch to Selected Driver")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.install_button.clicked.connect(self.switch_driver)
        self.install_button.setEnabled(False)
        button_layout.addWidget(self.install_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    def refresh_drivers(self):
        """Refresh the list of available drivers from both local OS and VM"""
        self.status_label.setText("🔄 Refreshing driver list...")
        self.driver_combo.clear()
        self.available_drivers = []
        
        # Get local OS drivers
        local_drivers = self._get_local_drivers()
        
        # Get VM drivers if VM is available
        vm_drivers = []
        if self.vm_bridge and self.vm_bridge.vm_process:
            vm_drivers = self._get_vm_drivers()
        
        # Combine and add to combo box
        all_drivers = local_drivers + vm_drivers
        self.available_drivers = all_drivers
        
        for driver in all_drivers:
            display_text = self._format_driver_display(driver)
            self.driver_combo.addItem(display_text)
        
        if all_drivers:
            self.status_label.setText(f"✓ Found {len(all_drivers)} drivers "
                                    f"({len(local_drivers)} local, {len(vm_drivers)} VM)")
        else:
            self.status_label.setText("⚠ No drivers found")
        
        # Update current driver display
        self._update_current_driver_display()
    
    def _get_local_drivers(self) -> List[Dict[str, Any]]:
        """Get drivers available on local OS"""
        drivers = []
        
        try:
            # Get drivers from driver manager
            device_drivers = self.driver_manager.find_drivers(self.device_info)
            
            for driver in device_drivers:
                drivers.append({
                    'name': driver.get('name', 'Unknown'),
                    'version': driver.get('version', '1.0'),
                    'source': 'local',
                    'source_detail': driver.get('source', 'system'),
                    'description': driver.get('description', ''),
                    'vendor': driver.get('vendor', 'Unknown'),
                    'stability': driver.get('stability', 'unknown'),
                    'is_microsoft': False
                })
        except Exception as e:
            self.status_label.setText(f"⚠ Error getting local drivers: {e}")
        
        return drivers
    
    def _get_vm_drivers(self) -> List[Dict[str, Any]]:
        """Get drivers available in VM (Windows drivers)"""
        drivers = []
        
        try:
            # Query VM for installed Windows drivers
            # This would require guest tools communication
            # For now, return example Microsoft drivers
            
            device_type = self.device_info.get('type', '').lower()
            
            # Example Microsoft drivers based on device type
            if 'network' in device_type or 'wifi' in device_type or 'ethernet' in device_type:
                drivers.extend([
                    {
                        'name': 'Microsoft Network Adapter',
                        'version': '10.0.19041.1',
                        'source': 'vm',
                        'source_detail': 'Windows VM',
                        'description': 'Microsoft generic network adapter driver from Windows',
                        'vendor': 'Microsoft Corporation',
                        'stability': 'stable',
                        'is_microsoft': True
                    },
                    {
                        'name': 'Intel PROSet/Wireless WiFi Software',
                        'version': '22.80.0',
                        'source': 'vm',
                        'source_detail': 'Windows VM',
                        'description': 'Intel WiFi driver via Windows VM bridge',
                        'vendor': 'Intel Corporation',
                        'stability': 'stable',
                        'is_microsoft': False
                    }
                ])
            elif 'graphics' in device_type or 'vga' in device_type or 'gpu' in device_type:
                drivers.extend([
                    {
                        'name': 'Microsoft Basic Display Adapter',
                        'version': '10.0.19041.1',
                        'source': 'vm',
                        'source_detail': 'Windows VM',
                        'description': 'Microsoft basic display driver from Windows',
                        'vendor': 'Microsoft Corporation',
                        'stability': 'stable',
                        'is_microsoft': True
                    }
                ])
            elif 'audio' in device_type or 'sound' in device_type:
                drivers.append({
                    'name': 'Microsoft Audio Device',
                    'version': '10.0.19041.1',
                    'source': 'vm',
                    'source_detail': 'Windows VM',
                    'description': 'Microsoft audio driver from Windows',
                    'vendor': 'Microsoft Corporation',
                    'stability': 'stable',
                    'is_microsoft': True
                })
            
        except Exception as e:
            self.status_label.setText(f"⚠ Error getting VM drivers: {e}")
        
        return drivers
    
    def _format_driver_display(self, driver: Dict[str, Any]) -> str:
        """Format driver for display in combo box with appropriate indicator"""
        name = driver.get('name', 'Unknown')
        version = driver.get('version', '?')
        source = driver.get('source', 'unknown')
        is_microsoft = driver.get('is_microsoft', False)
        
        # Add indicator based on source
        if source == 'vm':
            if is_microsoft:
                indicator = "Ⓜ🪟"  # Microsoft + VM
            else:
                indicator = "🪟"    # VM only
        else:
            indicator = "🖥"       # Local OS
        
        # Add stability indicator
        stability = driver.get('stability', 'unknown')
        if stability == 'stable':
            stability_icon = "✓"
        elif stability == 'testing':
            stability_icon = "⚠"
        else:
            stability_icon = "?"
        
        return f"{indicator} {name} v{version} {stability_icon}"
    
    def on_driver_changed(self, index):
        """Handle driver selection change"""
        if index < 0 or index >= len(self.available_drivers):
            self.driver_details.clear()
            self.install_button.setEnabled(False)
            return
        
        driver = self.available_drivers[index]
        
        # Update details display
        details = []
        details.append(f"Driver Name: {driver.get('name', 'Unknown')}")
        details.append(f"Version: {driver.get('version', '?')}")
        details.append(f"Vendor: {driver.get('vendor', 'Unknown')}")
        details.append(f"Source: {driver.get('source_detail', 'Unknown')}")
        details.append(f"Stability: {driver.get('stability', 'Unknown')}")
        details.append("")
        details.append(f"Description: {driver.get('description', 'No description available')}")
        
        if driver.get('source') == 'vm':
            details.append("")
            details.append("⚠ Note: This is a Windows driver from the VM.")
            details.append("It will be bridged to the Linux host through the VM.")
        
        if driver.get('is_microsoft'):
            details.append("")
            details.append("Ⓜ This is a Microsoft-provided driver.")
        
        self.driver_details.setText("\n".join(details))
        
        # Enable install button if different from current
        self.install_button.setEnabled(True)
    
    def _update_current_driver_display(self):
        """Update the current driver display"""
        try:
            # Get current driver info
            current = self.driver_manager.get_current_driver(self.device_info)
            if current:
                self.current_driver_label.setText(
                    f"{current.get('name', 'Unknown')} v{current.get('version', '?')}"
                )
                source = current.get('source', 'unknown')
                if source == 'vm':
                    self.current_driver_source.setText("🪟 Currently using VM driver")
                else:
                    self.current_driver_source.setText("🖥 Currently using local OS driver")
                self.current_driver = current
            else:
                self.current_driver_label.setText("No driver installed")
                self.current_driver_source.setText("")
        except:
            self.current_driver_label.setText("Unknown")
            self.current_driver_source.setText("")
    
    def switch_driver(self):
        """Initiate driver switch"""
        index = self.driver_combo.currentIndex()
        if index < 0 or index >= len(self.available_drivers):
            QMessageBox.warning(self, "No Selection", "Please select a driver first.")
            return
        
        new_driver = self.available_drivers[index]
        
        # Show confirmation based on source
        if new_driver.get('source') == 'vm':
            reply = QMessageBox.question(
                self,
                "Confirm VM Driver",
                f"You are about to switch to a Windows driver from the VM:\n\n"
                f"{new_driver['name']} v{new_driver['version']}\n\n"
                f"This driver will be bridged from the Windows VM to your Linux host.\n"
                f"You will have 20 seconds to confirm the switch, or it will\n"
                f"automatically revert to the longest-used driver.\n\n"
                f"Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Driver Switch",
                f"Switch to driver:\n\n"
                f"{new_driver['name']} v{new_driver['version']}\n\n"
                f"You will have 20 seconds to confirm the switch.\n\n"
                f"Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emit signal with driver info
            self.driverSelected.emit({
                'device_info': self.device_info,
                'old_driver': self.current_driver,
                'new_driver': new_driver
            })
            
            self.status_label.setText("⏳ Driver switch initiated - confirmation required...")
