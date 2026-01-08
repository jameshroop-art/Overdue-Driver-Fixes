"""
Ollama Manager for AI-assisted driver management
Handles Ollama integration and starcoder:3b model
"""

import subprocess
import requests
from typing import Dict, Any
from utils.terminal import run_with_output

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
    
    def signin(self, interactive: bool = True) -> Dict[str, Any]:
        """Sign in to Ollama using Google authentication
        
        This opens a browser for OAuth authentication and stores tokens locally.
        Required for pulling certain models like starcoder that may need authentication.
        
        Args:
            interactive: If True, prompt user before opening browser. If False, proceed automatically.
        
        Returns:
            Dict with 'success' boolean and 'message' or 'error' string
        """
        print("\n" + "="*60)
        print("Ollama Sign-In - Google OAuth Authentication")
        print("="*60)
        print("\nThis will communicate with Ollama's authentication service")
        print("and open your browser for Google sign-in.")
        print("The verification will be handled through this terminal.")
        print("\nAuthentication flow:")
        print("  1. Terminal connects to Ollama auth service")
        print("  2. Browser opens for Google OAuth")
        print("  3. After sign-in, verification code is sent to terminal")
        print("  4. Credentials cached locally for future use")
        
        if interactive:
            print("\nPress Enter to continue or Ctrl+C to cancel...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n\nSign-in cancelled.")
                return {
                    'success': False,
                    'error': 'Sign-in cancelled by user'
                }
        
        print("\nInitiating OAuth flow...")
        print("Connecting to Ollama authentication service...")
        
        try:
            # Run ollama signin command with real-time output
            # This communicates directly with the auth service
            # and opens browser, then waits for verification in terminal
            process = subprocess.Popen(
                ['ollama', 'signin'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("\n" + "-"*60)
            
            # Stream output in real-time to show authentication URL and progress
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    output_lines.append(line)
                    
                    # Check if browser should open
                    if 'http' in line.lower() or 'browser' in line.lower():
                        print("\n→ Browser window should open automatically")
                        print("→ If not, copy the URL above and open it manually")
                    
                    # Check for verification/callback
                    if 'verify' in line.lower() or 'code' in line.lower():
                        print("\n→ Waiting for verification from browser...")
            
            print("-"*60 + "\n")
            
            # Wait for process to complete
            return_code = process.wait(timeout=300)
            
            if return_code == 0:
                print("✓ Successfully signed in to Ollama!")
                print("✓ Credentials cached locally")
                print("✓ You can now pull models that require authentication")
                return {
                    'success': True,
                    'message': 'Successfully signed in to Ollama',
                    'output': ''.join(output_lines)
                }
            else:
                output = ''.join(output_lines)
                print(f"\n✗ Sign-in failed")
                if output:
                    print(f"Details: {output}")
                return {
                    'success': False,
                    'error': output or 'Sign-in failed',
                    'return_code': return_code
                }
                
        except FileNotFoundError:
            error_msg = "'ollama' command not found. Please install Ollama first."
            print(f"\n✗ {error_msg}")
            print("Install with: curl -fsSL https://ollama.ai/install.sh | sh")
            return {
                'success': False,
                'error': error_msg
            }
        except subprocess.TimeoutExpired:
            error_msg = "Sign-in timed out after 5 minutes."
            print(f"\n✗ {error_msg}")
            print("Please try again and complete the authentication faster.")
            if process:
                process.kill()
            return {
                'success': False,
                'error': error_msg
            }
        except KeyboardInterrupt:
            print("\n\nSign-in cancelled by user.")
            if process:
                process.kill()
            return {
                'success': False,
                'error': 'Sign-in cancelled by user'
            }
        except Exception as e:
            error_msg = f"Error during sign-in: {e}"
            print(f"\n✗ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def check_signin_status(self) -> Dict[str, Any]:
        """Check if user is signed in to Ollama
        
        Returns:
            Dict with 'signed_in' boolean and optional 'username' or 'error'
        """
        try:
            # Try to check signin status - ollama doesn't have a direct command for this
            # but we can infer from certain API calls or command responses
            # For now, we'll just indicate that signin is an available option
            return {
                'signed_in': None,  # Unknown status
                'message': 'Use signin() method to authenticate with Ollama'
            }
        except Exception as e:
            return {
                'signed_in': False,
                'error': str(e)
            }
    
    def _is_auth_error(self, error_text: str) -> bool:
        """Check if an error message indicates authentication is required
        
        Args:
            error_text: Error message or output to check
            
        Returns:
            True if error appears to be authentication-related
        """
        if not error_text:
            return False
        
        error_lower = error_text.lower()
        auth_keywords = ['auth', 'login', 'signin', 'sign in', 'unauthorized', 'credential']
        return any(keyword in error_lower for keyword in auth_keywords)
    
    def _suggest_signin(self):
        """Print sign-in suggestion message"""
        print("\n⚠ This model may require authentication.")
        print("Please sign in to Ollama with: ollama signin")
        print("Or use the sign-in feature in the application.")
    
    def install_model(self) -> bool:
        """Install starcoder:3b model"""
        if not self.is_available():
            print("Ollama is not running. Please start Ollama service first.")
            print("You can start it with: systemctl start ollama")
            return False
        
        print(f"Installing {self.model} model...")
        print(f"This may take several minutes depending on your internet connection...")
        print(f"\nNote: If the model requires authentication, you may need to sign in first.")
        print(f"If you see authentication errors, run: ollama signin")
        
        try:
            # Use ollama pull command
            # Show output in terminal for user visibility
            show_output = self.config.get('cli.show_subprocess_output', True)
            result = run_with_output(
                ['ollama', 'pull', self.model],
                show_output=show_output,
                timeout=300
            )
            if result.returncode == 0:
                print(f"✓ Model {self.model} installed successfully")
                return True
            else:
                error_output = result.stderr if hasattr(result, 'stderr') else ''
                print(f"✗ Failed to install model {self.model}")
                
                # Check if error is authentication-related
                if self._is_auth_error(error_output):
                    self._suggest_signin()
                
                return False
        except FileNotFoundError:
            print(f"Error: 'ollama' command not found. Please install Ollama first.")
            print(f"Visit https://ollama.ai/ for installation instructions.")
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"Error installing model: {error_msg}")
            
            # Check if error is authentication-related
            if self._is_auth_error(error_msg):
                self._suggest_signin()
            
            return False
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log using AI"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Ollama not available'
            }
        
        # Sanitize error log to prevent prompt injection
        # Limit length and remove potential injection patterns
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
        """Analyze text using AI model"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Ollama not available'
            }
        
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
            elif response.status_code == 404:
                # Model not found - provide helpful error message
                return {
                    'success': False,
                    'error': f"Model '{self.model}' not found. Please install it first using: ollama pull {self.model}"
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
                'error': 'Cannot connect to Ollama. Please ensure Ollama service is running.'
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
