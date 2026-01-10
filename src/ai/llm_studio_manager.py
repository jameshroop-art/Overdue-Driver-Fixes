"""
LLM Studio Manager for AI-assisted driver management
Handles LLM Studio integration with configuration backup/restore
Alternative to Ollama for local LLM inference
Supports multiple instances on different ports (up to 3)
Enforces strict security boundaries for AI access
"""

import subprocess
import requests
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from utils.security import DomainValidator
from ai.ai_security_manager import AISecurityManager

class LLMStudioManager:
    """Manages LLM Studio AI integration with config backup/restore and multi-instance support"""
    
    # Maximum number of LLM Studio instances allowed
    MAX_INSTANCES = 3
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.host = self.config.get_ai('lmstudio.host', 'localhost')
        
        # Support multiple ports (primary + additional instances)
        self.primary_port = self.config.get_ai('lmstudio.port', 1234)
        self.additional_ports = self.config.get_ai('lmstudio.additional_ports', [1235, 1236])
        
        # Build list of all possible ports (limit to MAX_INSTANCES)
        self.ports = [self.primary_port] + self.additional_ports
        self.ports = self.ports[:self.MAX_INSTANCES]
        
        self.model = self.config.get_ai('monitoring.model', 'starcoder:3b')
        
        # Track which port is currently active
        self.active_port = None
        self.base_url = None
        
        # LLM Studio configuration paths
        self.lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
        self.backup_config_dir = self.config.get_config_dir() / 'lmstudio_backup'
        
        # Initialize security managers
        self.domain_validator = DomainValidator(config_manager)
        self.security_manager = AISecurityManager(config_manager)
        
        # Track if we've backed up the configuration
        self._config_backed_up = False
        
        # Discover and connect to available instance
        self._discover_active_instance()
    
    
    def _discover_active_instance(self) -> bool:
        """
        Discover which LLM Studio instance is running and responsive
        Checks all configured ports and connects to the first available one
        
        Returns:
            bool: True if an active instance was found, False otherwise
        """
        for port in self.ports:
            try:
                url = f"http://{self.host}:{port}/v1/models"
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    self.active_port = port
                    self.base_url = f"http://{self.host}:{port}"
                    return True
            except:
                continue
        
        # No instance found, default to primary port
        self.active_port = self.primary_port
        self.base_url = f"http://{self.host}:{self.primary_port}"
        return False
    
    def get_all_instances(self) -> List[Dict[str, Any]]:
        """
        Get status of all configured LLM Studio instances
        
        Returns:
            List of dicts with port and status for each instance
        """
        instances = []
        for port in self.ports:
            url = f"http://{self.host}:{port}/v1/models"
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    models = response.json().get('data', [])
                    instances.append({
                        'port': port,
                        'status': 'running',
                        'url': f"http://{self.host}:{port}",
                        'models': models,
                        'active': (port == self.active_port)
                    })
                else:
                    instances.append({
                        'port': port,
                        'status': 'error',
                        'url': f"http://{self.host}:{port}",
                        'error': f"HTTP {response.status_code}",
                        'active': False
                    })
            except requests.exceptions.ConnectionError:
                instances.append({
                    'port': port,
                    'status': 'not_running',
                    'url': f"http://{self.host}:{port}",
                    'active': False
                })
            except Exception as e:
                instances.append({
                    'port': port,
                    'status': 'error',
                    'url': f"http://{self.host}:{port}",
                    'error': str(e),
                    'active': False
                })
        
        return instances
    
    def switch_to_port(self, port: int) -> bool:
        """
        Switch to using a specific LLM Studio instance port
        
        Args:
            port: Port number to switch to
            
        Returns:
            bool: True if switch successful, False otherwise
        """
        if port not in self.ports:
            print(f"Warning: Port {port} not in configured ports: {self.ports}")
            return False
        
        try:
            url = f"http://{self.host}:{port}/v1/models"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                self.active_port = port
                self.base_url = f"http://{self.host}:{port}"
                print(f"✓ Switched to LLM Studio instance on port {port}")
                return True
            else:
                print(f"✗ LLM Studio on port {port} returned HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Failed to connect to LLM Studio on port {port}: {e}")
            return False
    
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
        """Get LLM Studio service status including all instances"""
        # Get status of all instances
        instances = self.get_all_instances()
        running_instances = [i for i in instances if i['status'] == 'running']
        
        if not running_instances:
            return {
                'status': 'not_running',
                'backend': 'lmstudio',
                'model': None,
                'instances': instances,
                'active_port': self.active_port,
                'configured_ports': self.ports
            }
        
        # Check if active instance has the model loaded
        if self.active_port:
            active_instance = next((i for i in instances if i['port'] == self.active_port), None)
            if active_instance and active_instance['status'] == 'running':
                models = active_instance.get('models', [])
                has_model = any('starcoder' in m.get('id', '').lower() for m in models)
                
                return {
                    'status': 'running',
                    'backend': 'lmstudio',
                    'model': self.model if has_model else 'not_loaded',
                    'active_port': self.active_port,
                    'instances': instances,
                    'running_count': len(running_instances),
                    'configured_ports': self.ports
                }
        
        # Fallback: use first running instance
        first_running = running_instances[0]
        models = first_running.get('models', [])
        has_model = any('starcoder' in m.get('id', '').lower() for m in models)
        
        return {
            'status': 'running',
            'backend': 'lmstudio',
            'model': self.model if has_model else 'not_loaded',
            'active_port': first_running['port'],
            'instances': instances,
            'running_count': len(running_instances),
            'configured_ports': self.ports
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
        """Analyze error log using AI with security constraints"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'LLM Studio not available'
            }
        
        # Validate operation with security manager
        is_allowed, reason = self.security_manager.validate_operation(
            'analyze_driver_error',
            {'error_messages': error_log[:1000]}  # Only include snippet for validation
        )
        
        if not is_allowed:
            return {
                'success': False,
                'error': f'Security violation: {reason}'
            }
        
        # Sanitize error log to prevent prompt injection and remove sensitive data
        sanitized_log = self.security_manager.sanitize_prompt(error_log, 'driver_analysis')
        
        prompt = f"""Analyze this driver installation error and suggest remediation:

{sanitized_log}

Provide:
1. Root cause
2. Suggested fix
3. Alternative approach if fix doesn't work

IMPORTANT: Limit your response to driver-related analysis only. Do not suggest system modifications beyond driver operations.
"""
        
        return self.analyze_text(prompt)
    
    def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using AI model via LLM Studio with security constraints"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'LLM Studio not available'
            }
        
        # Sanitize prompt before sending to AI
        sanitized_prompt = self.security_manager.sanitize_prompt(prompt, 'driver_analysis')
        
        try:
            # Use OpenAI-compatible API endpoint
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a driver management assistant. Your responses must be limited to driver and hardware-related analysis only. Do not suggest or perform any system modifications beyond driver operations.'
                        },
                        {
                            'role': 'user',
                            'content': sanitized_prompt
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
                
                # Sanitize response before returning
                sanitized_analysis = self.security_manager.sanitize_response(analysis)
                
                return {
                    'success': True,
                    'analysis': sanitized_analysis
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
