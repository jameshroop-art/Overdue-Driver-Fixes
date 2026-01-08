"""
Configuration Manager for driver-mgt
Handles loading and saving configuration files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Manages application configuration"""
    
    # Path to config templates (multiple possible locations)
    CONFIG_TEMPLATE_PATHS = [
        Path(__file__).parent.parent.parent / 'config',  # Running from source
        Path('/opt/driver-mgt/config'),  # Installed system-wide
        Path('/usr/share/driver-mgt/config'),  # Installed via setup.py
        Path('/usr/local/share/driver-mgt/config'),  # Alternate install location
    ]
    
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'driver-mgt'
        self.config_file = self.config_dir / 'config.json'
        self.ai_config_file = self.config_dir / 'ai-config.json'
        
        # Find the config template directory
        self.template_dir = self._find_template_dir()
        
        # Initialize directories
        self._init_directories()
        
        # Load configuration
        self.config = self._load_config()
        self.ai_config = self._load_ai_config()
    
    def _find_template_dir(self):
        """Find the configuration template directory"""
        for path in self.CONFIG_TEMPLATE_PATHS:
            if path.exists() and path.is_dir():
                return path
        # Return None if not found
        return None
    
    def _init_directories(self):
        """Initialize configuration directories"""
        directories = [
            self.config_dir,
            self.config_dir / 'profiles',
            self.config_dir / 'curves',
            self.config_dir / 'logs',
            self.config_dir / 'corrections',
            self.config_dir / 'reports'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load main configuration file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Load default configuration from template
            if self.template_dir:
                template_path = self.template_dir / 'config.json.template'
                if template_path.exists():
                    with open(template_path, 'r') as f:
                        config = json.load(f)
                    # Save default configuration
                    self._save_config(config)
                    return config
            
            # Return minimal default if template not found
            return self._get_default_config()
    
    def _load_ai_config(self) -> Dict[str, Any]:
        """Load AI configuration file"""
        if self.ai_config_file.exists():
            with open(self.ai_config_file, 'r') as f:
                return json.load(f)
        else:
            # Load default AI configuration from template
            if self.template_dir:
                template_path = self.template_dir / 'ai-config.json.template'
                if template_path.exists():
                    with open(template_path, 'r') as f:
                        config = json.load(f)
                    # Save default configuration
                    self._save_ai_config(config)
                    return config
            
            # Return minimal default if template not found
            return self._get_default_ai_config()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save main configuration file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _save_ai_config(self, config: Dict[str, Any]):
        """Save AI configuration file"""
        with open(self.ai_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get minimal default configuration"""
        return {
            "version": "1.0.0",
            "general": {
                "auto_update_check": True,
                "notification_enabled": True,
                "log_level": "INFO"
            },
            "hardware": {
                "scan_interval": 300,
                "auto_detect": True
            },
            "drivers": {
                "auto_install": False,
                "preferred_sources": ["official", "distribution", "community"],
                "backup_on_install": True,
                "test_after_install": True
            },
            "gui": {
                "theme": "dark",
                "start_minimized": False,
                "show_tray_icon": True
            }
        }
    
    def _get_default_ai_config(self) -> Dict[str, Any]:
        """Get minimal default AI configuration"""
        return {
            "monitoring": {
                "enabled": False,
                "model": "starcoder:3b",
                "sensitivity": "medium",
                "performance_impact": "low"
            },
            "risk_assessment": {
                "enabled": True,
                "check_on_scan": True,
                "error_database_update": "daily",
                "show_percentage": True,
                "ai_remediation_check": True
            },
            "privacy": {
                "localhost_only": True,
                "no_external_transmission": True,
                "user_consent_required": True
            }
        }
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_ai(self, key: str, default=None) -> Any:
        """Get AI configuration value"""
        keys = key.split('.')
        value = self.ai_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def set_ai(self, key: str, value: Any):
        """Set AI configuration value"""
        keys = key.split('.')
        config = self.ai_config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_ai_config(self.ai_config)
    
    def get_config_dir(self) -> Path:
        """Get configuration directory path"""
        return self.config_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory path"""
        return self.config_dir / 'logs'
    
    def get_corrections_dir(self) -> Path:
        """Get corrections directory path"""
        return self.config_dir / 'corrections'
    
    def get_reports_dir(self) -> Path:
        """Get reports directory path"""
        return self.config_dir / 'reports'
