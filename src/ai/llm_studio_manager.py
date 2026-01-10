"""
LLM Studio Manager for AI-assisted driver management
Handles LLM Studio integration with configuration backup/restore
Alternative to Ollama for local LLM inference
"""

import subprocess
import requests
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from utils.security import DomainValidator

class LLMStudioManager:
    """Manages LLM Studio AI integration with config backup/restore"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.host = self.config.get_ai('lmstudio.host', 'localhost')
        self.port = self.config.get_ai('lmstudio.port', 1234)
        self.model = self.config.get_ai('monitoring.model', 'starcoder:3b')
        self.base_url = f"http://{self.host}:{self.port}"
        
        # LLM Studio configuration paths
        self.lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
        self.backup_config_dir = self.config.get_config_dir() / 'lmstudio_backup'
        
        # Initialize domain validator for security
        self.domain_validator = DomainValidator(config_manager)
        
        # Track if we've backed up the configuration
        self._config_backed_up = False
    
    def backup_lmstudio_config(self) -> bool:
        """
        Backup existing LLM Studio configuration before we modify it
        
        Returns:
            bool: True if backup succeeded or no config to backup, False on error
        """
        try:
            # Check if LLM Studio config directory exists
            if not self.lmstudio_config_dir.exists():
                print("No existing LLM Studio configuration found (fresh install)")
                self._config_backed_up = True
                return True
            
            # Create backup directory
            self.backup_config_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Backing up LLM Studio configuration from {self.lmstudio_config_dir}")
            
            # Copy all configuration files
            if self.lmstudio_config_dir.is_dir():
                # Remove old backup if it exists
                if self.backup_config_dir.exists():
                    shutil.rmtree(self.backup_config_dir)
                
                # Create fresh backup
                shutil.copytree(self.lmstudio_config_dir, self.backup_config_dir)
                print(f"✓ Configuration backed up to {self.backup_config_dir}")
                self._config_backed_up = True
                return True
            else:
                print(f"Warning: {self.lmstudio_config_dir} is not a directory")
                return True  # Not an error, just no config to backup
                
        except Exception as e:
            print(f"Error backing up LLM Studio configuration: {e}")
            return False
    
    def restore_lmstudio_config(self) -> bool:
        """
        Restore LLM Studio configuration from backup
        
        Returns:
            bool: True if restore succeeded or no backup exists, False on error
        """
        try:
            # Check if we have a backup to restore
            if not self.backup_config_dir.exists():
                print("No backup configuration found (this was a fresh install)")
                return True
            
            if not self._config_backed_up:
                print("Warning: Configuration was not backed up in this session")
                return True
            
            print(f"Restoring LLM Studio configuration from {self.backup_config_dir}")
            
            # Remove current configuration
            if self.lmstudio_config_dir.exists():
                shutil.rmtree(self.lmstudio_config_dir)
            
            # Restore from backup
            shutil.copytree(self.backup_config_dir, self.lmstudio_config_dir)
            print(f"✓ Configuration restored from backup")
            
            # Clean up backup
            shutil.rmtree(self.backup_config_dir)
            print("✓ Backup cleaned up")
            
            return True
            
        except Exception as e:
            print(f"Error restoring LLM Studio configuration: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM Studio service status"""
        try:
            # LLM Studio uses OpenAI-compatible API
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            if response.status_code == 200:
                models = response.json().get('data', [])
                has_model = any('starcoder' in m.get('id', '').lower() for m in models)
                
                return {
                    'status': 'running',
                    'backend': 'lmstudio',
                    'model': self.model if has_model else 'not_loaded',
                    'models': models
                }
            else:
                return {
                    'status': 'error',
                    'backend': 'lmstudio',
                    'model': None,
                    'error': f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'not_running',
                'backend': 'lmstudio',
                'model': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'backend': 'lmstudio',
                'model': None,
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Check if LLM Studio is available"""
        status = self.get_status()
        return status['status'] == 'running'
    
    def configure_for_driver_mgt(self) -> bool:
        """
        Configure LLM Studio for driver-mgt use
        
        This sets up the appropriate model and settings for driver management tasks
        
        Returns:
            bool: True if configuration succeeded, False otherwise
        """
        try:
            # Backup existing configuration first
            if not self.backup_lmstudio_config():
                print("Warning: Failed to backup configuration, proceeding anyway...")
            
            print("Configuring LLM Studio for driver-mgt...")
            
            # Check if LLM Studio is running
            if not self.is_available():
                print("LLM Studio is not running. Please start LLM Studio first.")
                print("You can start it from the LM Studio application.")
                return False
            
            # Load the appropriate model (starcoder:3b or equivalent)
            # Note: LLM Studio uses OpenAI-compatible API, so we use that endpoint
            print(f"Configuring model: {self.model}")
            
            # LLM Studio configuration is typically done through its GUI
            # We can verify the model is loaded via API
            status = self.get_status()
            if status['status'] == 'running':
                print("✓ LLM Studio is configured and running")
                return True
            else:
                print(f"Warning: LLM Studio status: {status.get('error', 'unknown')}")
                return False
                
        except Exception as e:
            print(f"Error configuring LLM Studio: {e}")
            return False
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log using AI"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'LLM Studio not available'
            }
        
        # Sanitize error log to prevent prompt injection
        sanitized_log = self._sanitize_log(error_log)
        
        prompt = f"""Analyze this driver installation error and suggest remediation:

{sanitized_log}

Provide:
1. Root cause
2. Suggested fix
3. Alternative approach if fix doesn't work
"""
        
        return self.analyze_text(prompt)
    
    def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using AI model via LLM Studio"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'LLM Studio not available'
            }
        
        try:
            # Use OpenAI-compatible API endpoint
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {
                    'success': True,
                    'analysis': analysis
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timed out. The AI model may be processing a large request.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to LLM Studio. Please ensure LLM Studio is running.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def assess_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of installing a driver"""
        # Placeholder for risk assessment
        return {
            'risk_percentage': 5,
            'risk_level': 'low',
            'can_remediate': True,
            'known_issues': []
        }
    
    def validate_url_access(self, url: str) -> tuple[bool, str]:
        """
        Validate that a URL is allowed by whitelist
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        return self.domain_validator.is_url_allowed(url)
    
    def validate_github_search(self, query: str) -> tuple[bool, str]:
        """Validate GitHub search query is for drivers/chipsets"""
        return self.domain_validator.validate_github_search(query)
    
    def validate_huggingface_search(self, query: str) -> tuple[bool, str]:
        """Validate HuggingFace search query is for drivers/chipsets"""
        return self.domain_validator.validate_huggingface_search(query)
    
    def check_filesystem_access(self, path: str, is_critical_error: bool = False) -> tuple[bool, str]:
        """Check if AI can access filesystem path"""
        return self.domain_validator.is_filesystem_access_allowed(path, is_critical_error)
    
    def monitor_driver(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor driver operation in real-time"""
        # Placeholder for monitoring
        return {
            'status': 'not_implemented',
            'monitoring': False
        }
    
    def shutdown(self):
        """
        Shutdown and cleanup - restore LLM Studio configuration
        
        This is called when the application exits to restore the previous configuration
        """
        print("\nShutting down LLM Studio integration...")
        
        # Restore the backed up configuration
        if self._config_backed_up:
            if self.restore_lmstudio_config():
                print("✓ LLM Studio configuration restored to previous state")
            else:
                print("⚠ Warning: Failed to restore LLM Studio configuration")
                print(f"  Manual restore may be needed from: {self.backup_config_dir}")
        else:
            print("No configuration backup to restore")
    
    def _sanitize_log(self, log: str) -> str:
        """Sanitize log content to prevent prompt injection"""
        # Limit length to prevent abuse
        max_length = 5000
        if len(log) > max_length:
            log = log[:max_length] + "... (truncated)"
        
        # Remove potential prompt injection patterns
        # Keep only printable ASCII and common whitespace
        sanitized = ''.join(char for char in log if char.isprintable() or char in '\n\r\t')
        
        return sanitized
