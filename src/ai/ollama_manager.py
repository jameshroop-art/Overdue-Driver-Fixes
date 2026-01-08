"""
Ollama Manager for AI-assisted driver management
Handles Ollama integration and starcoder:3b model
"""

import subprocess
import requests
from typing import Dict, Any

class OllamaManager:
    """Manages Ollama AI integration"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.host = self.config.get_ai('ollama.host', 'localhost')
        self.port = self.config.get_ai('ollama.port', 11434)
        self.model = self.config.get_ai('monitoring.model', 'starcoder:3b')
        self.base_url = f"http://{self.host}:{self.port}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get Ollama service status"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                has_starcoder = any('starcoder' in m.get('name', '') for m in models)
                
                return {
                    'status': 'running',
                    'model': self.model if has_starcoder else 'not_installed',
                    'models': models
                }
            else:
                return {
                    'status': 'error',
                    'model': None,
                    'error': f"HTTP {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'not_running',
                'model': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'model': None,
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        status = self.get_status()
        return status['status'] == 'running'
    
    def install_ollama(self) -> bool:
        """Install Ollama (requires root)"""
        print("Installing Ollama...")
        # This would perform actual Ollama installation
        # For now, it's a placeholder
        return True
    
    def install_model(self) -> bool:
        """Install starcoder:3b model"""
        if not self.is_available():
            print("Ollama is not running")
            return False
        
        print(f"Installing {self.model} model...")
        try:
            # Use ollama pull command
            result = subprocess.run(
                ['ollama', 'pull', self.model],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing model: {e}")
            return False
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log using AI"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Ollama not available'
            }
        
        prompt = f"""Analyze this driver installation error and suggest remediation:

{error_log}

Provide:
1. Root cause
2. Suggested fix
3. Alternative approach if fix doesn't work
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'analysis': result.get('response', '')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
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
    
    def monitor_driver(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor driver operation in real-time"""
        # Placeholder for monitoring
        return {
            'status': 'not_implemented',
            'monitoring': False
        }
    
    def shutdown(self):
        """Shutdown Ollama service"""
        if self.config.get_ai('ollama.auto_shutdown', True):
            try:
                subprocess.run(['systemctl', 'stop', 'ollama'], timeout=5)
                print("Ollama service stopped")
            except Exception as e:
                print(f"Error stopping Ollama: {e}")
