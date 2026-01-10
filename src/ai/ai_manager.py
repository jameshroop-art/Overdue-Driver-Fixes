"""
AI Manager - LLM Studio Only Backend
Handles LLM Studio backend exclusively (Ollama removed)
Checks for LLM Studio installation at startup and installs if needed
"""

from typing import Dict, Any, Optional
from ai.llm_studio_manager import LLMStudioManager
import subprocess
import shutil
from pathlib import Path
import requests
import tarfile
import os
import json
import webbrowser

class AIManager:
    """
    AI Manager that uses LLM Studio exclusively
    Ollama support has been completely removed
    """
    
    def __init__(self, config_manager, backend: Optional[str] = None):
        """
        Initialize AI Manager with LLM Studio
        
        Args:
            config_manager: Configuration manager instance
            backend: Ignored - always uses lmstudio
        """
        self.config = config_manager
        self.backend = 'lmstudio'  # Always use LLM Studio
        self.ollama_port = 11435  # Default to alternate port
        
        # Check and install LLM Studio if needed
        if not self.check_lmstudio_installed():
            print("LM Studio not found. Installing...")
            if not self.install_lmstudio():
                print("⚠ Warning: Could not install LM Studio automatically")
                print("Please install LM Studio manually from: https://lmstudio.ai/")
        
        # Verify Ollama is available for model access (on alternate port)
        self.verify_ollama_available()
        
        # Configure LM Studio for driver-mgt (with Ollama integration)
        self.configure_lmstudio_for_program()
        
        # Ensure LM Studio server is running
        self.ensure_lmstudio_running()
        
        # Initialize LLM Studio backend
        self.manager = LLMStudioManager(config_manager)
    
    def check_lmstudio_installed(self) -> bool:
        """
        Check if LM Studio is installed on the system
        
        Returns:
            True if LM Studio is installed, False otherwise
        """
        # Check common installation locations
        possible_locations = [
            Path.home() / '.local' / 'bin' / 'lmstudio',
            Path.home() / '.local' / 'share' / 'lmstudio' / 'lmstudio',
            Path('/opt/lmstudio/lmstudio'),
            Path('/usr/local/bin/lmstudio'),
            Path.home() / 'lmstudio' / 'lmstudio',
        ]
        
        # Check if any location exists
        for location in possible_locations:
            if location.exists():
                print(f"✓ LM Studio found at: {location}")
                return True
        
        # Check if LM Studio server is running
        try:
            response = requests.get('http://localhost:1234/v1/models', timeout=2)
            if response.status_code == 200:
                print("✓ LM Studio server is running")
                return True
        except:
            pass
        
        print("LM Studio not found on system")
        return False
    
    def install_lmstudio(self) -> bool:
        """
        Automatically install LM Studio
        
        Returns:
            True if installation successful, False otherwise
        """
        print("="*60)
        print("Installing LM Studio...")
        print("="*60)
        
        install_dir = Path.home() / '.local' / 'share' / 'lmstudio'
        install_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Detect system architecture
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            if system != 'linux':
                print(f"✗ Automatic installation only supported on Linux")
                print(f"  Your system: {system}")
                return False
            
            print("\nLM Studio Installation Options:")
            print("1. AppImage (Recommended) - Portable, no installation needed")
            print("2. Manual Download - Install from website")
            print("")
            
            # Check for AppImage
            appimage_path = install_dir / 'LM_Studio.AppImage'
            
            if not appimage_path.exists():
                print("LM Studio AppImage not found.")
                print("\nPlease download LM Studio:")
                print("1. Visit: https://lmstudio.ai/")
                print("2. Download the Linux AppImage")
                print(f"3. Save it to: {appimage_path}")
                print("4. Run this program again")
                print("")
                
                # Try to open browser
                try:
                    import webbrowser
                    print("Opening LM Studio download page in browser...")
                    webbrowser.open('https://lmstudio.ai/')
                except:
                    pass
                
                return False
            else:
                print(f"✓ Found LM Studio AppImage at: {appimage_path}")
                # Make executable
                os.chmod(appimage_path, 0o755)
                print("✓ Made AppImage executable")
                
                # Create symlink for easy access
                bin_dir = Path.home() / '.local' / 'bin'
                bin_dir.mkdir(parents=True, exist_ok=True)
                symlink = bin_dir / 'lmstudio'
                
                if not symlink.exists():
                    symlink.symlink_to(appimage_path)
                    print(f"✓ Created symlink: {symlink}")
                
                return True
            
        except Exception as e:
            print(f"✗ Error during installation: {e}")
            return False
    
    def configure_lmstudio_for_program(self) -> bool:
        """
        Configure LM Studio for driver-mgt program requirements
        Configures LM Studio to access models from Ollama on alternate port
        
        Returns:
            True if configuration successful, False otherwise
        """
        print("\nConfiguring LM Studio for driver-mgt...")
        
        try:
            # Use the Ollama port that was detected/started
            ollama_endpoint = f'http://localhost:{self.ollama_port}'
            
            # Ensure LM Studio config directory exists
            lmstudio_config_dir = Path.home() / '.cache' / 'lm-studio'
            lmstudio_config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = lmstudio_config_dir / 'config.json'
            
            # Load existing config or create new
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Configure for driver-mgt requirements
            config.update({
                'server': {
                    'enabled': True,
                    'port': 1234,
                    'cors': True,
                    'autoStart': True
                },
                'models': {
                    'recommendedForCode': 'starcoder:3b',
                    'autoLoadOnStart': True,
                    'source': 'ollama',  # Use Ollama as model source
                    'ollamaEndpoint': ollama_endpoint  # Dynamic port
                },
                'modelBackend': {
                    'type': 'ollama',
                    'endpoint': ollama_endpoint,
                    'apiPath': '/api',
                    'enabled': True,
                    'useOllamaModels': True
                },
                'telemetry': {
                    'enabled': False,
                    'allowCollection': False
                },
                'logging': {
                    'enabled': False,
                    'level': 'none'
                },
                'analytics': {
                    'enabled': False,
                    'optOut': True
                },
                'privacy': {
                    'disableTelemetry': True,
                    'disableAnalytics': True,
                    'disableCrashReports': True
                },
                'performance': {
                    'cpuThreads': 4,
                    'gpuLayers': 0,  # CPU only for low impact
                    'contextLength': 2048
                }
            })
            
            # Save configuration
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✓ LM Studio configured with:")
            print("  - Server enabled on port 1234")
            print(f"  - Using Ollama models from {ollama_endpoint}")
            print("  - Model source: Ollama")
            print("  - Auto-start enabled")
            print("  - Telemetry disabled")
            print("  - Logging disabled")
            print("  - Privacy mode enabled")
            print("  - CPU-only mode (low impact)")
            
            # Create model access configuration
            self._configure_ollama_model_access(lmstudio_config_dir, ollama_endpoint)
            
            # Create startup script with dynamic port
            startup_script = lmstudio_config_dir / 'start-server.sh'
            with open(startup_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Auto-generated startup script for LM Studio server
# Used by driver-mgt
# Configured to use Ollama models from {ollama_endpoint}

LMSTUDIO_BIN="$HOME/.local/bin/lmstudio"
OLLAMA_PORT={self.ollama_port}

# Check if Ollama is running on alternate port
if ! curl -s http://localhost:$OLLAMA_PORT/api/tags >/dev/null 2>&1; then
    echo "⚠ Warning: Ollama server not running on localhost:$OLLAMA_PORT"
    echo "Starting Ollama service on alternate port..."
    export OLLAMA_HOST=127.0.0.1:$OLLAMA_PORT
    ollama serve &
    sleep 3
fi

if [ ! -f "$LMSTUDIO_BIN" ]; then
    echo "LM Studio not found at $LMSTUDIO_BIN"
    exit 1
fi

# Start LM Studio in server mode with Ollama backend on alternate port
export LMSTUDIO_MODEL_BACKEND=ollama
export LMSTUDIO_OLLAMA_ENDPOINT=http://localhost:$OLLAMA_PORT

"$LMSTUDIO_BIN" server start --port 1234 --ollama-endpoint http://localhost:$OLLAMA_PORT &

echo "LM Studio server started on port 1234"
echo "Using Ollama models from localhost:$OLLAMA_PORT"
echo "PID: $!"
""")
            os.chmod(startup_script, 0o755)
            print(f"✓ Created startup script: {startup_script}")
            
            return True
            
        except Exception as e:
            print(f"⚠ Error configuring LM Studio: {e}")
            return False
    
    def _configure_ollama_model_access(self, config_dir: Path, ollama_endpoint: str):
        """
        Configure LM Studio to access Ollama models
        Creates model mapping and access configuration
        
        Args:
            config_dir: Configuration directory path
            ollama_endpoint: Ollama server endpoint with port
        """
        try:
            # Create Ollama integration config
            ollama_config = config_dir / 'ollama-integration.json'
            
            config = {
                'enabled': True,
                'endpoint': ollama_endpoint,
                'api_version': 'v1',
                'models': {
                    'auto_discover': True,
                    'refresh_interval': 300,  # 5 minutes
                    'preferred_models': [
                        'starcoder:3b',
                        'codellama:7b',
                        'mistral:7b'
                    ]
                },
                'api_compatibility': {
                    'use_ollama_api': True,
                    'translate_to_openai': True,  # LM Studio uses OpenAI-compatible API
                    'streaming': True
                },
                'model_mapping': {
                    # Map Ollama model names to LM Studio format
                    'starcoder:3b': {
                        'name': 'StarCoder 3B',
                        'type': 'code',
                        'provider': 'ollama',
                        'endpoint': '/api/generate'
                    },
                    'codellama:7b': {
                        'name': 'CodeLlama 7B',
                        'type': 'code',
                        'provider': 'ollama',
                        'endpoint': '/api/generate'
                    }
                }
            }
            
            with open(ollama_config, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✓ Created Ollama integration config: {ollama_config}")
            print(f"  Using endpoint: {ollama_endpoint}")
            
        except Exception as e:
            print(f"⚠ Could not create Ollama integration config: {e}")
    
    def verify_ollama_available(self) -> bool:
        """
        Verify that Ollama server is running and accessible
        Uses alternate port 11435 for localhost to avoid conflicts
        
        Returns:
            True if Ollama is available, False otherwise
        """
        # Try alternate port first (11435)
        alternate_port = 11435
        default_port = 11434
        
        # Check alternate port
        try:
            response = requests.get(f'http://localhost:{alternate_port}/api/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✓ Ollama server is running on alternate port {alternate_port} with {len(models)} models")
                self.ollama_port = alternate_port
                return True
        except:
            pass
        
        # Check default port
        try:
            response = requests.get(f'http://localhost:{default_port}/api/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✓ Ollama server is running on default port {default_port} with {len(models)} models")
                self.ollama_port = default_port
                return True
        except:
            pass
        
        # Ollama not running, try to start on alternate port
        print(f"⚠ Ollama server not found, attempting to start on alternate port {alternate_port}...")
        if self.start_ollama_on_alternate_port():
            self.ollama_port = alternate_port
            return True
        
        print("⚠ Ollama server not available")
        print("  LM Studio will need Ollama to access models")
        print("  Please ensure Ollama is installed and running")
        return False
    
    def start_ollama_on_alternate_port(self) -> bool:
        """
        Start Ollama server on alternate port 11435
        
        Returns:
            True if Ollama started successfully, False otherwise
        """
        alternate_port = 11435
        
        try:
            # Check if Ollama is installed
            if not shutil.which('ollama'):
                print("✗ Ollama not installed")
                return False
            
            print(f"Starting Ollama on alternate port {alternate_port}...")
            
            # Set environment variable for alternate port
            env = os.environ.copy()
            env['OLLAMA_HOST'] = f'127.0.0.1:{alternate_port}'
            
            # Start Ollama server in background on alternate port
            process = subprocess.Popen(
                ['ollama', 'serve'],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for server to start
            import time
            for i in range(10):
                time.sleep(1)
                try:
                    response = requests.get(f'http://localhost:{alternate_port}/api/tags', timeout=1)
                    if response.status_code == 200:
                        print(f"✓ Ollama started on port {alternate_port}")
                        
                        # Save PID for cleanup
                        pid_file = Path.home() / '.cache' / 'driver-mgt' / 'ollama-alt.pid'
                        pid_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(pid_file, 'w') as f:
                            f.write(str(process.pid))
                        
                        return True
                except:
                    continue
            
            print(f"✗ Ollama did not start on port {alternate_port}")
            return False
            
        except Exception as e:
            print(f"✗ Error starting Ollama: {e}")
            return False
            os.chmod(startup_script, 0o755)
            print(f"✓ Created startup script: {startup_script}")
            
            return True
            
        except Exception as e:
            print(f"⚠ Error configuring LM Studio: {e}")
            return False
    
    def ensure_lmstudio_running(self) -> bool:
        """
        Ensure LM Studio server is running
        Start it if not running
        
        Returns:
            True if server is running or successfully started
        """
        # Check if already running
        try:
            response = requests.get('http://localhost:1234/v1/models', timeout=2)
            if response.status_code == 200:
                print("✓ LM Studio server is already running")
                return True
        except:
            pass
        
        # Try to start server
        print("Starting LM Studio server...")
        
        try:
            # Look for LM Studio binary
            possible_bins = [
                Path.home() / '.local' / 'bin' / 'lmstudio',
                Path.home() / '.local' / 'share' / 'lmstudio' / 'LM_Studio.AppImage',
            ]
            
            lmstudio_bin = None
            for bin_path in possible_bins:
                if bin_path.exists():
                    lmstudio_bin = bin_path
                    break
            
            if not lmstudio_bin:
                print("✗ LM Studio binary not found")
                return False
            
            # Start server in background
            subprocess.Popen(
                [str(lmstudio_bin), 'server', 'start', '--port', '1234'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for server to start
            import time
            for i in range(10):
                time.sleep(1)
                try:
                    response = requests.get('http://localhost:1234/v1/models', timeout=1)
                    if response.status_code == 200:
                        print("✓ LM Studio server started successfully")
                        return True
                except:
                    continue
            
            print("⚠ LM Studio server did not start in time")
            return False
            
        except Exception as e:
            print(f"✗ Error starting LM Studio: {e}")
            return False
    
    def get_backend_name(self) -> str:
        """Get the name of the active backend"""
        return self.backend
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status"""
        status = self.manager.get_status()
        status['backend'] = self.backend
        return status
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.manager.is_available()
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log using AI"""
        return self.manager.analyze_error(error_log)
    
    def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using AI model"""
        return self.manager.analyze_text(prompt)
    
    def assess_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of installing a driver"""
        return self.manager.assess_risk(hardware, driver)
    
    def validate_url_access(self, url: str) -> tuple[bool, str]:
        """Validate that a URL is allowed by whitelist"""
        return self.manager.validate_url_access(url)
    
    def validate_github_search(self, query: str) -> tuple[bool, str]:
        """Validate GitHub search query is for drivers/chipsets"""
        return self.manager.validate_github_search(query)
    
    def validate_huggingface_search(self, query: str) -> tuple[bool, str]:
        """Validate HuggingFace search query is for drivers/chipsets"""
        return self.manager.validate_huggingface_search(query)
    
    def check_filesystem_access(self, path: str, is_critical_error: bool = False) -> tuple[bool, str]:
        """Check if AI can access filesystem path"""
        return self.manager.check_filesystem_access(path, is_critical_error)
    
    def monitor_driver(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor driver operation in real-time"""
        return self.manager.monitor_driver(hardware)
    
    def configure_for_driver_mgt(self) -> bool:
        """
        Configure the AI backend for driver-mgt use
        Backs up LLM Studio config
        """
        if hasattr(self.manager, 'configure_for_driver_mgt'):
            return self.manager.configure_for_driver_mgt()
        return True
    
    def shutdown(self):
        """
        Shutdown AI service and cleanup
        Restores LLM Studio configuration
        """
        self.manager.shutdown()
