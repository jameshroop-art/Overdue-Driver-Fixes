"""
Ollama Manager - Compatibility wrapper that supports both LM Studio and Ollama
Uses whichever backend is available at runtime
"""

from typing import Dict, Any, Optional
import requests
import subprocess
import shutil
import os
import time
from pathlib import Path


class OllamaManager:
    """
    AI Manager that supports both Ollama and LM Studio backends
    Automatically detects and uses whichever backend is available
    """
    
    def __init__(self, config_manager, model: str = 'starcoder:3b'):
        """
        Initialize the manager with automatic backend detection
        
        Args:
            config_manager: Configuration manager instance
            model: Model name to use (default: starcoder:3b)
        """
        self.config = config_manager
        self.model = model
        self.backend = None
        self.backend_manager = None
        self.ollama_port = 11434
        self.lmstudio_port = 1234
        self.backend_process = None  # Track started backend processes
        
        # Detect and initialize available backend
        self._detect_and_initialize_backend()
    
    def _detect_and_initialize_backend(self):
        """
        Detect which backend is available and initialize it
        Priority: Try Ollama first (port 11434), then LM Studio (port 1234)
        """
        # Try Ollama first (default port)
        if self._check_ollama_available():
            print("✓ Using Ollama backend")
            self.backend = 'ollama'
            self._initialize_ollama()
            return
        
        # Try alternate Ollama port
        if self._check_ollama_available(port=11435):
            print("✓ Using Ollama backend (alternate port 11435)")
            self.backend = 'ollama'
            self.ollama_port = 11435
            self._initialize_ollama()
            return
        
        # Try LM Studio
        if self._check_lmstudio_available():
            print("✓ Using LM Studio backend")
            self.backend = 'lmstudio'
            self._initialize_lmstudio()
            return
        
        # Try to start Ollama if installed
        if self._try_start_ollama():
            print("✓ Started Ollama backend")
            self.backend = 'ollama'
            self._initialize_ollama()
            return
        
        # Try to start LM Studio if installed
        if self._try_start_lmstudio():
            print("✓ Started LM Studio backend")
            self.backend = 'lmstudio'
            self._initialize_lmstudio()
            return
        
        # No backend available
        print("⚠ Warning: No AI backend available (neither Ollama nor LM Studio)")
        print("  Install Ollama: https://ollama.ai/")
        print("  Install LM Studio: https://lmstudio.ai/")
        self.backend = None
    
    def _check_ollama_available(self, port: int = 11434) -> bool:
        """Check if Ollama is running on specified port"""
        try:
            response = requests.get(f'http://localhost:{port}/api/tags', timeout=2)
            return response.status_code == 200
        except (requests.RequestException, OSError):
            return False
    
    def _check_lmstudio_available(self) -> bool:
        """Check if LM Studio is running"""
        try:
            response = requests.get(f'http://localhost:{self.lmstudio_port}/v1/models', timeout=2)
            return response.status_code == 200
        except (requests.RequestException, OSError):
            return False
    
    def _try_start_ollama(self) -> bool:
        """Try to start Ollama service"""
        if not shutil.which('ollama'):
            return False
        
        try:
            print("Starting Ollama service...")
            # Try systemd first
            result = subprocess.run(['systemctl', 'is-active', 'ollama'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                subprocess.run(['systemctl', 'start', 'ollama'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            
            # Verify it started
            if self._check_ollama_available():
                return True
            
            # Try starting manually as fallback
            env = os.environ.copy()
            env['OLLAMA_HOST'] = f'127.0.0.1:{self.ollama_port}'
            self.backend_process = subprocess.Popen(
                ['ollama', 'serve'], 
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            
            return self._check_ollama_available()
        except Exception as e:
            print(f"Failed to start Ollama: {e}")
            return False
    
    def _try_start_lmstudio(self) -> bool:
        """Try to start LM Studio server"""
        possible_bins = [
            Path.home() / '.local' / 'bin' / 'lmstudio',
            Path.home() / '.local' / 'share' / 'lmstudio' / 'LM_Studio.AppImage',
        ]
        
        for lmstudio_bin in possible_bins:
            if lmstudio_bin.exists():
                try:
                    print("Starting LM Studio server...")
                    self.backend_process = subprocess.Popen(
                        [str(lmstudio_bin), 'server', 'start', '--port', str(self.lmstudio_port)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(3)
                    
                    if self._check_lmstudio_available():
                        return True
                except Exception as e:
                    print(f"Failed to start LM Studio: {e}")
        
        return False
    
    def _initialize_ollama(self):
        """Initialize Ollama backend (native implementation)"""
        self.api_url = f'http://localhost:{self.ollama_port}/api'
    
    def _initialize_lmstudio(self):
        """Initialize LM Studio backend (delegates to LLMStudioManager)"""
        try:
            from ai.llm_studio_manager import LLMStudioManager
            self.backend_manager = LLMStudioManager(self.config)
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize LM Studio manager: {e}")
            self.backend = None
    
    def is_available(self) -> bool:
        """Check if any AI backend is available"""
        if self.backend == 'ollama':
            return self._check_ollama_available(port=self.ollama_port)
        elif self.backend == 'lmstudio':
            if self.backend_manager:
                return self.backend_manager.is_available()
            return self._check_lmstudio_available()
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status"""
        if self.backend == 'ollama':
            return self._get_ollama_status()
        elif self.backend == 'lmstudio':
            if self.backend_manager:
                status = self.backend_manager.get_status()
                status['backend'] = 'lmstudio'
                return status
            return {
                'status': 'unavailable',
                'backend': 'lmstudio',
                'model': self.model
            }
        return {
            'status': 'unavailable',
            'backend': 'none',
            'model': self.model,
            'message': 'No AI backend available'
        }
    
    def _get_ollama_status(self) -> Dict[str, Any]:
        """Get Ollama status"""
        try:
            response = requests.get(f'{self.api_url}/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                return {
                    'status': 'available',
                    'backend': 'ollama',
                    'model': self.model,
                    'available_models': model_names,
                    'port': self.ollama_port
                }
        except:
            pass
        
        return {
            'status': 'unavailable',
            'backend': 'ollama',
            'model': self.model,
            'port': self.ollama_port
        }
    
    def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze text using the available AI backend
        
        Args:
            prompt: Text prompt to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'No AI backend available',
                'backend': self.backend or 'none'
            }
        
        if self.backend == 'ollama':
            return self._analyze_text_ollama(prompt)
        elif self.backend == 'lmstudio':
            if self.backend_manager:
                return self.backend_manager.analyze_text(prompt)
            return {
                'success': False,
                'error': 'LM Studio manager not initialized',
                'backend': 'lmstudio'
            }
        
        return {
            'success': False,
            'error': 'Unknown backend',
            'backend': self.backend
        }
    
    def _analyze_text_ollama(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using Ollama API"""
        try:
            response = requests.post(
                f'{self.api_url}/generate',
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
                    'response': result.get('response', ''),
                    'model': self.model,
                    'backend': 'ollama'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ollama API returned status {response.status_code}',
                    'backend': 'ollama'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'backend': 'ollama'
            }
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log"""
        prompt = f"""Analyze this driver error log and provide recommendations:

{error_log}

Provide:
1. Root cause analysis
2. Potential solutions
3. Risk assessment
"""
        return self.analyze_text(prompt)
    
    def assess_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of driver installation"""
        hw_info = hardware.get('name', 'Unknown device')
        driver_name = driver.get('name', 'Unknown driver')
        driver_version = driver.get('version', 'Unknown version')
        
        prompt = f"""Assess the risk of installing this driver:

Hardware: {hw_info}
Driver: {driver_name}
Version: {driver_version}

Provide a risk assessment with:
1. Risk level (low/medium/high)
2. Potential issues
3. Recommendations
"""
        result = self.analyze_text(prompt)
        
        if result.get('success'):
            # Parse risk level from response
            response_text = result.get('response', '').lower()
            if 'high risk' in response_text or 'high)' in response_text:
                risk_level = 'high'
            elif 'medium risk' in response_text or 'medium)' in response_text:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'success': True,
                'risk_level': risk_level,
                'analysis': result.get('response', ''),
                'backend': result.get('backend', self.backend)
            }
        
        return result
    
    def monitor_driver(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor driver operation"""
        hw_info = hardware.get('name', 'Unknown device')
        hw_driver = hardware.get('driver', 'Unknown driver')
        
        prompt = f"""Monitor this driver and provide status:

Hardware: {hw_info}
Current Driver: {hw_driver}

Provide monitoring information:
1. Driver status
2. Performance metrics
3. Any issues detected
"""
        return self.analyze_text(prompt)
    
    def signin(self) -> Dict[str, Any]:
        """
        Sign in to AI service (Ollama only)
        LM Studio doesn't require signin
        """
        if self.backend == 'lmstudio':
            return {
                'success': True,
                'message': 'LM Studio does not require sign-in',
                'backend': 'lmstudio'
            }
        
        if self.backend != 'ollama':
            return {
                'success': False,
                'error': 'No Ollama backend available',
                'backend': self.backend or 'none'
            }
        
        # Ollama signin
        if not shutil.which('ollama'):
            return {
                'success': False,
                'error': 'Ollama command not found',
                'backend': 'ollama'
            }
        
        try:
            print("Opening browser for Ollama authentication...")
            result = subprocess.run(['ollama', 'signin'], timeout=120)
            
            return {
                'success': result.returncode == 0,
                'message': 'Sign-in completed' if result.returncode == 0 else 'Sign-in failed',
                'backend': 'ollama'
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Sign-in timeout',
                'backend': 'ollama'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'backend': 'ollama'
            }
    
    def shutdown(self):
        """Shutdown AI backend and cleanup - closes localhost sessions"""
        if self.backend == 'lmstudio' and self.backend_manager:
            self.backend_manager.shutdown()
            self._stop_lmstudio_session()
        
        # Don't stop system-wide Ollama service, but cleanup any alternate port instances
        if self.backend == 'ollama' and self.ollama_port != 11434:
            self._stop_ollama_alternate_port()
        
        # Terminate backend process if we started it
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except Exception:
                try:
                    self.backend_process.kill()
                except Exception:
                    pass
            finally:
                self.backend_process = None
    
    def _stop_lmstudio_session(self):
        """Stop LM Studio server session"""
        try:
            # Try to stop via API if available
            requests.post('http://localhost:1234/server/stop', timeout=2)
        except (requests.RequestException, OSError):
            pass
        
        # Kill any LM Studio server processes we started
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'lmstudio' in proc.info['name'].lower():
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass
    
    def _stop_ollama_alternate_port(self):
        """Stop Ollama instance on alternate port (not system service)"""
        try:
            pid_file = Path.home() / '.cache' / 'driver-mgt' / 'ollama-alt.pid'
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                import signal
                os.kill(pid, signal.SIGTERM)
                pid_file.unlink()
                print(f"✓ Stopped Ollama on alternate port {self.ollama_port}")
        except (OSError, ValueError, FileNotFoundError):
            pass
    
    def ensure_backend_running(self) -> bool:
        """
        Ensure backend is running - start if needed
        Used when operations require the backend
        
        Returns:
            True if backend is running, False otherwise
        """
        if self.backend == 'ollama':
            return self._check_ollama_available(port=self.ollama_port) or self._try_start_ollama()
        elif self.backend == 'lmstudio':
            return self._check_lmstudio_available() or self._try_start_lmstudio()
        return False
    
    def stop_backend_session(self):
        """
        Stop backend session (to be called when not needed)
        Only stops sessions we started, not system services
        """
        if self.backend == 'lmstudio':
            self._stop_lmstudio_session()
        elif self.backend == 'ollama' and self.ollama_port != 11434:
            # Only stop if using alternate port (not system service)
            self._stop_ollama_alternate_port()
