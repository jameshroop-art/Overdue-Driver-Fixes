"""
AI Settings Widget for model selection and configuration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QTextEdit,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

class AISettingsWidget(QWidget):
    """Widget for AI model selection and configuration"""
    
    # Signal emitted when model changes
    modelChanged = pyqtSignal(str)
    
    def __init__(self, config_manager, ai_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.ai_manager = ai_manager
        
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("AI Model Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Backend selection group
        backend_group = QGroupBox("AI Backend")
        backend_layout = QVBoxLayout(backend_group)
        
        backend_info_layout = QHBoxLayout()
        backend_info_layout.addWidget(QLabel("Current Backend:"))
        self.backend_label = QLabel("Loading...")
        self.backend_label.setStyleSheet("font-weight: bold;")
        backend_info_layout.addWidget(self.backend_label)
        backend_info_layout.addStretch()
        backend_layout.addLayout(backend_info_layout)
        
        layout.addWidget(backend_group)
        
        # Model selection group
        model_group = QGroupBox("Language Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        # Model dropdown
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("Select Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_select_layout.addWidget(self.model_combo)
        
        refresh_btn = QPushButton("Refresh Models")
        refresh_btn.clicked.connect(self.refresh_available_models)
        model_select_layout.addWidget(refresh_btn)
        
        model_select_layout.addStretch()
        model_layout.addLayout(model_select_layout)
        
        # Model info
        self.model_info_label = QLabel("Select a model to see details")
        self.model_info_label.setWordWrap(True)
        model_layout.addWidget(self.model_info_label)
        
        layout.addWidget(model_group)
        
        # Instance status (for LLM Studio)
        self.instance_group = QGroupBox("LLM Studio Instances")
        instance_layout = QVBoxLayout(self.instance_group)
        
        self.instance_info = QTextEdit()
        self.instance_info.setReadOnly(True)
        self.instance_info.setMaximumHeight(150)
        instance_layout.addWidget(self.instance_info)
        
        instance_btn_layout = QHBoxLayout()
        refresh_instances_btn = QPushButton("Refresh Instances")
        refresh_instances_btn.clicked.connect(self.refresh_instances)
        instance_btn_layout.addWidget(refresh_instances_btn)
        instance_btn_layout.addStretch()
        instance_layout.addLayout(instance_btn_layout)
        
        layout.addWidget(self.instance_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def load_current_settings(self):
        """Load current AI settings"""
        # Get backend
        backend = self.ai_manager.get_backend_name()
        self.backend_label.setText(backend.upper())
        
        # Show/hide instance group based on backend
        self.instance_group.setVisible(backend == 'lmstudio')
        
        # Refresh available models
        self.refresh_available_models()
        
        # If LLM Studio, refresh instances
        if backend == 'lmstudio':
            self.refresh_instances()
    
    def refresh_available_models(self):
        """Refresh list of available models from AI backend"""
        self.model_combo.clear()
        self.status_label.setText("Loading models...")
        
        backend = self.ai_manager.get_backend_name()
        
        try:
            if backend == 'ollama':
                # Get models from Ollama
                status = self.ai_manager.get_status()
                if status['status'] == 'running':
                    models = status.get('models', [])
                    if models:
                        for model in models:
                            model_name = model.get('name', 'unknown')
                            self.model_combo.addItem(model_name)
                    else:
                        self.model_combo.addItem("No models found")
                        self.status_label.setText("No models available. Please pull a model first.")
                else:
                    self.model_combo.addItem("Ollama not running")
                    self.status_label.setText("Ollama is not running. Please start Ollama service.")
            
            elif backend == 'lmstudio':
                # Get models from LLM Studio
                status = self.ai_manager.get_status()
                if status['status'] == 'running':
                    instances = status.get('instances', [])
                    all_models = set()
                    
                    for instance in instances:
                        if instance['status'] == 'running':
                            models = instance.get('models', [])
                            for model in models:
                                model_id = model.get('id', 'unknown')
                                all_models.add(model_id)
                    
                    if all_models:
                        for model in sorted(all_models):
                            self.model_combo.addItem(model)
                    else:
                        self.model_combo.addItem("No models loaded")
                        self.status_label.setText("No models loaded in LLM Studio. Please load a model first.")
                else:
                    self.model_combo.addItem("LLM Studio not running")
                    self.status_label.setText("LLM Studio is not running. Please start LLM Studio.")
            
            # Set current model as selected
            current_model = self.config.get_ai('monitoring.model', 'starcoder:3b')
            index = self.model_combo.findText(current_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            
            self.status_label.setText("Models loaded successfully")
            
        except Exception as e:
            self.status_label.setText(f"Error loading models: {e}")
    
    def refresh_instances(self):
        """Refresh LLM Studio instance information"""
        if self.ai_manager.get_backend_name() != 'lmstudio':
            return
        
        try:
            status = self.ai_manager.get_status()
            instances = status.get('instances', [])
            
            info_text = f"Configured Ports: {status.get('configured_ports', [])}\n"
            info_text += f"Active Port: {status.get('active_port', 'None')}\n"
            info_text += f"Running Instances: {status.get('running_count', 0)}/{len(instances)}\n\n"
            
            for instance in instances:
                port = instance['port']
                inst_status = instance['status']
                active = " (ACTIVE)" if instance.get('active', False) else ""
                
                info_text += f"Port {port}{active}: {inst_status}\n"
                if inst_status == 'running':
                    models = instance.get('models', [])
                    if models:
                        info_text += f"  Models: {len(models)} loaded\n"
                    else:
                        info_text += f"  Models: None\n"
            
            self.instance_info.setText(info_text)
            
        except Exception as e:
            self.instance_info.setText(f"Error getting instance info: {e}")
    
    def on_model_changed(self, model_name):
        """Handle model selection change"""
        if not model_name or model_name in ["No models found", "Ollama not running", "LLM Studio not running", "No models loaded"]:
            self.model_info_label.setText("No model selected")
            return
        
        # Update info label
        self.model_info_label.setText(f"Selected: {model_name}\n\nThis model will be used for driver analysis, error detection, and AI-assisted tasks.")
    
    def apply_settings(self):
        """Apply the selected model configuration"""
        model_name = self.model_combo.currentText()
        
        if not model_name or model_name in ["No models found", "Ollama not running", "LLM Studio not running", "No models loaded"]:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid model.")
            return
        
        try:
            # Update configuration
            self.config.set_ai('monitoring.model', model_name)
            
            # Update AI manager's model
            self.ai_manager.manager.model = model_name
            
            self.status_label.setText(f"✓ Model changed to: {model_name}")
            
            # Emit signal
            self.modelChanged.emit(model_name)
            
            QMessageBox.information(self, "Success", f"Model changed to: {model_name}")
            
        except Exception as e:
            self.status_label.setText(f"Error applying settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")
    
    def test_connection(self):
        """Test connection to AI backend with selected model"""
        self.status_label.setText("Testing connection...")
        
        try:
            # Test if AI is available
            if not self.ai_manager.is_available():
                QMessageBox.warning(self, "Connection Failed", "AI backend is not available. Please ensure the service is running.")
                self.status_label.setText("✗ Connection failed")
                return
            
            # Try a simple query
            result = self.ai_manager.analyze_text("Test connection. Please respond with 'OK'.")
            
            if result.get('success'):
                QMessageBox.information(self, "Connection Success", f"Successfully connected to AI backend.\n\nResponse: {result.get('analysis', 'N/A')[:100]}...")
                self.status_label.setText("✓ Connection successful")
            else:
                QMessageBox.warning(self, "Connection Failed", f"Failed to communicate with AI backend.\n\nError: {result.get('error', 'Unknown')}")
                self.status_label.setText("✗ Connection failed")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error testing connection: {e}")
            self.status_label.setText(f"✗ Error: {e}")
