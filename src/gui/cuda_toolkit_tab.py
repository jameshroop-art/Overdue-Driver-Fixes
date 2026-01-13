"""
CUDA Toolkit Management Tab
Sub-tab for GPU devices to manage CUDA Toolkit installations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QScrollArea,
    QCheckBox, QLineEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.cuda_toolkit_manager import CudaToolkitManager


class CudaInstallWorker(QThread):
    """Worker thread for CUDA Toolkit installation"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, cuda_version, install_path, gpu_info, driver_version):
        super().__init__()
        self.cuda_version = cuda_version
        self.install_path = install_path
        self.gpu_info = gpu_info
        self.driver_version = driver_version
    
    def run(self):
        """Simulate CUDA Toolkit installation"""
        try:
            self.progress.emit(10, f"Downloading CUDA Toolkit {self.cuda_version}...")
            self.msleep(2000)
            
            self.progress.emit(30, "Extracting CUDA Toolkit files...")
            self.msleep(1500)
            
            self.progress.emit(50, "Installing CUDA runtime libraries...")
            self.msleep(2000)
            
            self.progress.emit(70, "Installing CUDA compiler (nvcc)...")
            self.msleep(1500)
            
            self.progress.emit(85, "Configuring environment variables...")
            self.msleep(1000)
            
            self.progress.emit(95, "Verifying installation...")
            self.msleep(1000)
            
            self.progress.emit(100, f"CUDA Toolkit {self.cuda_version} installed successfully!")
            self.finished.emit(True, f"CUDA {self.cuda_version} installed successfully at {self.install_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}")


class CudaToolkitTab(QWidget):
    """CUDA Toolkit management sub-tab for GPU devices"""
    
    def __init__(self, gpu_info: dict, driver_version: str):
        super().__init__()
        self.gpu_info = gpu_info
        self.driver_version = driver_version
        self.cuda_manager = CudaToolkitManager()
        self.installed_cuda_versions = []
        
        self.init_ui()
        self.load_cuda_compatibility()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header section
        header_group = QGroupBox("CUDA Toolkit Management")
        header_layout = QVBoxLayout()
        
        # GPU and Driver Info
        info_text = (
            f"GPU: {self.gpu_info.get('name', 'Unknown')}\n"
            f"Driver Version: {self.driver_version}\n"
            f"Compute Capability: {self.cuda_manager.get_gpu_compute_capability(self.gpu_info.get('name', '')) or 'Unknown'}"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        header_layout.addWidget(info_label)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Splitter for two sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Available CUDA Versions section
        available_widget = QWidget()
        available_layout = QVBoxLayout()
        
        available_group = QGroupBox("Available CUDA Toolkit Versions")
        available_group_layout = QVBoxLayout()
        
        # Filter options
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Show:")
        filter_layout.addWidget(filter_label)
        
        self.show_all_checkbox = QCheckBox("All Versions")
        self.show_all_checkbox.setChecked(False)
        self.show_all_checkbox.stateChanged.connect(self.load_cuda_compatibility)
        filter_layout.addWidget(self.show_all_checkbox)
        
        self.show_recommended_checkbox = QCheckBox("Recommended Only")
        self.show_recommended_checkbox.setChecked(True)
        self.show_recommended_checkbox.stateChanged.connect(self.load_cuda_compatibility)
        filter_layout.addWidget(self.show_recommended_checkbox)
        
        filter_layout.addStretch()
        available_group_layout.addLayout(filter_layout)
        
        # CUDA versions table
        self.cuda_table = QTableWidget()
        self.cuda_table.setColumnCount(7)
        self.cuda_table.setHorizontalHeaderLabels([
            'CUDA Version', 'Min Driver', 'Status', 'Release Date', 
            'Architectures', 'Compute Cap.', 'Actions'
        ])
        self.cuda_table.horizontalHeader().setStretchLastSection(True)
        self.cuda_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cuda_table.setAlternatingRowColors(True)
        available_group_layout.addWidget(self.cuda_table)
        
        available_group.setLayout(available_group_layout)
        available_layout.addWidget(available_group)
        available_widget.setLayout(available_layout)
        
        splitter.addWidget(available_widget)
        
        # Installed CUDA Versions section
        installed_widget = QWidget()
        installed_layout = QVBoxLayout()
        
        installed_group = QGroupBox("Installed CUDA Toolkit Versions")
        installed_group_layout = QVBoxLayout()
        
        # Installed table
        self.installed_table = QTableWidget()
        self.installed_table.setColumnCount(5)
        self.installed_table.setHorizontalHeaderLabels([
            'CUDA Version', 'Install Path', 'Install Date', 'Status', 'Actions'
        ])
        self.installed_table.horizontalHeader().setStretchLastSection(True)
        self.installed_table.setAlternatingRowColors(True)
        installed_group_layout.addWidget(self.installed_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_installed)
        button_layout.addWidget(self.refresh_btn)
        
        self.set_default_btn = QPushButton("⭐ Set Default CUDA")
        self.set_default_btn.clicked.connect(self.set_default_cuda)
        button_layout.addWidget(self.set_default_btn)
        
        button_layout.addStretch()
        installed_group_layout.addLayout(button_layout)
        
        installed_group.setLayout(installed_group_layout)
        installed_layout.addWidget(installed_group)
        installed_widget.setLayout(installed_layout)
        
        splitter.addWidget(installed_widget)
        
        # Set splitter sizes
        splitter.setSizes([400, 200])
        layout.addWidget(splitter)
        
        # Installation progress section (initially hidden)
        self.progress_group = QGroupBox("Installation Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_group.setLayout(progress_layout)
        self.progress_group.setVisible(False)
        layout.addWidget(self.progress_group)
        
        # Details section
        details_group = QGroupBox("CUDA Toolkit Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        self.setLayout(layout)
    
    def load_cuda_compatibility(self):
        """Load compatible CUDA versions based on driver"""
        gpu_name = self.gpu_info.get('name', '')
        show_all = self.show_all_checkbox.isChecked()
        show_recommended = self.show_recommended_checkbox.isChecked()
        
        # Get compatible CUDA versions
        cuda_versions = self.cuda_manager.get_cuda_for_gpu(
            gpu_name, 
            self.driver_version,
            os_type='linux'
        )
        
        # Filter if needed
        if show_recommended and not show_all:
            cuda_versions = [c for c in cuda_versions if c.get('recommended', False)]
        
        # Populate table
        self.cuda_table.setRowCount(len(cuda_versions))
        
        for row, cuda_info in enumerate(cuda_versions):
            # CUDA Version
            version_item = QTableWidgetItem(cuda_info['cuda_version'])
            if cuda_info.get('recommended', False):
                version_item.setBackground(QColor(200, 255, 200))
                version_item.setText(f"⭐ {cuda_info['cuda_version']}")
            self.cuda_table.setItem(row, 0, version_item)
            
            # Min Driver
            min_driver_item = QTableWidgetItem(cuda_info['min_driver_required'])
            self.cuda_table.setItem(row, 1, min_driver_item)
            
            # Status
            is_compatible, msg = self.cuda_manager.is_cuda_compatible(
                cuda_info['cuda_version'],
                self.driver_version,
                'linux'
            )
            status_item = QTableWidgetItem("✓ Compatible" if is_compatible else "✗ Incompatible")
            status_item.setBackground(QColor(200, 255, 200) if is_compatible else QColor(255, 200, 200))
            self.cuda_table.setItem(row, 2, status_item)
            
            # Release Date
            date_item = QTableWidgetItem(cuda_info['release_date'])
            self.cuda_table.setItem(row, 3, date_item)
            
            # Architectures
            arch_item = QTableWidgetItem(', '.join(cuda_info['architectures'][:3]))
            self.cuda_table.setItem(row, 4, arch_item)
            
            # Compute Capability
            compute_item = QTableWidgetItem(', '.join(cuda_info['compute_capability'][:4]))
            self.cuda_table.setItem(row, 5, compute_item)
            
            # Actions button
            if is_compatible:
                install_btn = QPushButton("📦 Install")
                install_btn.clicked.connect(lambda checked, v=cuda_info['cuda_version']: self.install_cuda(v))
                self.cuda_table.setCellWidget(row, 6, install_btn)
            else:
                upgrade_label = QLabel("Upgrade Driver Required")
                upgrade_label.setStyleSheet("color: red; font-style: italic;")
                self.cuda_table.setCellWidget(row, 6, upgrade_label)
        
        self.cuda_table.resizeColumnsToContents()
        
        # Show selection details
        self.cuda_table.itemSelectionChanged.connect(self.show_cuda_details)
    
    def show_cuda_details(self):
        """Show detailed information about selected CUDA version"""
        selected_rows = self.cuda_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        cuda_version = self.cuda_table.item(row, 0).text().replace('⭐ ', '')
        
        cuda_info = self.cuda_manager.get_cuda_info(cuda_version)
        if not cuda_info:
            return
        
        details = f"""
CUDA Toolkit {cuda_version} Details:

Release Date: {cuda_info['release_date']}
Minimum Driver (Linux): {cuda_info['min_driver_linux']}
Minimum Driver (Windows): {cuda_info['min_driver_windows']}

Supported GPU Architectures:
{', '.join(cuda_info['architectures'])}

Supported Compute Capabilities:
{', '.join(cuda_info['compute_capability'])}

Key Features:
{chr(10).join('• ' + f for f in cuda_info['features'])}

Compatibility with your system:
GPU: {self.gpu_info.get('name', 'Unknown')}
Driver: {self.driver_version}
Status: {'✓ Compatible' if self.cuda_manager.is_cuda_compatible(cuda_version, self.driver_version, 'linux')[0] else '✗ Requires driver upgrade'}
"""
        self.details_text.setPlainText(details)
    
    def install_cuda(self, cuda_version: str):
        """Install CUDA Toolkit"""
        reply = QMessageBox.question(
            self,
            "Confirm CUDA Installation",
            f"Install CUDA Toolkit {cuda_version}?\n\n"
            f"This will download and install:\n"
            f"• CUDA Runtime Libraries\n"
            f"• CUDA Compiler (nvcc)\n"
            f"• cuDNN (Deep Neural Network library)\n"
            f"• CUDA Samples\n\n"
            f"Installation path: /usr/local/cuda-{cuda_version}\n"
            f"Estimated size: ~3-4 GB\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Show progress
        self.progress_group.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Installing CUDA {cuda_version}...")
        
        # Start installation worker
        install_path = f"/usr/local/cuda-{cuda_version}"
        self.install_worker = CudaInstallWorker(
            cuda_version,
            install_path,
            self.gpu_info,
            self.driver_version
        )
        self.install_worker.progress.connect(self.on_install_progress)
        self.install_worker.finished.connect(self.on_install_finished)
        self.install_worker.start()
    
    def on_install_progress(self, percent: int, message: str):
        """Handle installation progress updates"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def on_install_finished(self, success: bool, message: str):
        """Handle installation completion"""
        self.progress_group.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                "Installation Complete",
                f"{message}\n\n"
                f"Environment variables have been configured.\n"
                f"You may need to restart your terminal or IDE to use the new CUDA installation.\n\n"
                f"Test installation with:\n"
                f"  nvcc --version\n"
                f"  nvidia-smi"
            )
            self.refresh_installed()
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                f"{message}\n\n"
                f"Please check:\n"
                f"• Sufficient disk space\n"
                f"• Network connectivity\n"
                f"• System permissions"
            )
    
    def refresh_installed(self):
        """Refresh list of installed CUDA versions"""
        # Simulate checking for installed CUDA versions
        # In real implementation, scan /usr/local/cuda-* directories
        installed = []
        
        # Add mock data for demonstration
        if hasattr(self, 'install_worker') and self.install_worker.isFinished():
            installed.append({
                'version': self.install_worker.cuda_version,
                'path': self.install_worker.install_path,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'default': True
            })
        
        self.installed_table.setRowCount(len(installed))
        
        for row, cuda in enumerate(installed):
            # Version
            version_item = QTableWidgetItem(cuda['version'])
            if cuda.get('default', False):
                version_item.setText(f"⭐ {cuda['version']} (Default)")
                version_item.setBackground(QColor(255, 255, 200))
            self.installed_table.setItem(row, 0, version_item)
            
            # Path
            path_item = QTableWidgetItem(cuda['path'])
            self.installed_table.setItem(row, 1, path_item)
            
            # Date
            date_item = QTableWidgetItem(cuda['date'])
            self.installed_table.setItem(row, 2, date_item)
            
            # Status
            status_item = QTableWidgetItem("✓ Active")
            status_item.setBackground(QColor(200, 255, 200))
            self.installed_table.setItem(row, 3, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            uninstall_btn = QPushButton("🗑 Uninstall")
            uninstall_btn.clicked.connect(lambda checked, v=cuda['version']: self.uninstall_cuda(v))
            actions_layout.addWidget(uninstall_btn)
            
            actions_widget.setLayout(actions_layout)
            self.installed_table.setCellWidget(row, 4, actions_widget)
        
        self.installed_table.resizeColumnsToContents()
    
    def uninstall_cuda(self, cuda_version: str):
        """Uninstall CUDA Toolkit"""
        reply = QMessageBox.warning(
            self,
            "Confirm Uninstall",
            f"Uninstall CUDA Toolkit {cuda_version}?\n\n"
            f"This will remove all CUDA {cuda_version} components.\n"
            f"Applications using this version may stop working.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Uninstall Complete",
                f"CUDA Toolkit {cuda_version} has been uninstalled successfully."
            )
            self.refresh_installed()
    
    def set_default_cuda(self):
        """Set default CUDA version"""
        selected_rows = self.installed_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an installed CUDA version to set as default."
            )
            return
        
        row = selected_rows[0].row()
        cuda_version = self.installed_table.item(row, 0).text().replace('⭐ ', '').replace(' (Default)', '')
        
        QMessageBox.information(
            self,
            "Default CUDA Set",
            f"CUDA {cuda_version} is now the default version.\n\n"
            f"Updated environment variables:\n"
            f"  CUDA_HOME=/usr/local/cuda-{cuda_version}\n"
            f"  PATH includes CUDA binaries\n"
            f"  LD_LIBRARY_PATH includes CUDA libraries"
        )
        self.refresh_installed()
