"""
AI Manager - Dual Backend Support (LLM Studio and Ollama)
Automatically detects and uses whichever backend is available
Supports dynamic switching between backends
"""

from typing import Dict, Any, Optional
from pathlib import Path

class AIManager:
    """
    AI Manager that supports both LLM Studio and Ollama backends
    Automatically detects and uses whichever is available at runtime
    """
    
    def __init__(self, config_manager, backend: Optional[str] = None):
        """
        Initialize AI Manager with automatic backend detection
        
        Args:
            config_manager: Configuration manager instance
            backend: Optional backend preference ('lmstudio', 'ollama', or None for auto-detect)
        """
        self.config = config_manager
        self.backend = None
        self.manager = None
        self.ollama_port = 11434  # Default Ollama port
        
        # Use OllamaManager which handles both backends automatically
        try:
            from ai.ollama_manager import OllamaManager
            self.manager = OllamaManager(config_manager)
            self.backend = self.manager.backend
            
            if self.backend:
                print(f"✓ AI Manager initialized with {self.backend} backend")
            else:
                print("⚠ Warning: No AI backend available")
                print("  Install Ollama: https://ollama.ai/")
                print("  Install LM Studio: https://lmstudio.ai/")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize AI manager: {e}")
            self.backend = None
    
    def get_backend_name(self) -> str:
        """Get the name of the active backend"""
        return self.backend or 'none'
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status"""
        if self.manager:
            return self.manager.get_status()
        return {
            'status': 'unavailable',
            'backend': 'none',
            'message': 'No AI backend available'
        }
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        if self.manager:
            return self.manager.is_available()
        return False
    
    def analyze_error(self, error_log: str) -> Dict[str, Any]:
        """Analyze error log using AI"""
        if self.manager:
            return self.manager.analyze_error(error_log)
        return {'success': False, 'error': 'No AI backend available'}
    
    def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using AI model"""
        if self.manager:
            return self.manager.analyze_text(prompt)
        return {'success': False, 'error': 'No AI backend available'}
    
    def assess_risk(self, hardware: Dict[str, Any], driver: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of installing a driver"""
        if self.manager:
            return self.manager.assess_risk(hardware, driver)
        return {'success': False, 'error': 'No AI backend available'}
    
    def monitor_driver(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor driver operation in real-time"""
        if self.manager:
            return self.manager.monitor_driver(hardware)
        return {'success': False, 'error': 'No AI backend available'}
    
    @property
    def model(self) -> str:
        """Get the current AI model name"""
        if self.manager and hasattr(self.manager, 'model'):
            return self.manager.model
        return 'starcoder:3b'  # Default model name
    
    def signin(self) -> Dict[str, Any]:
        """Sign in to AI service (if required)"""
        if self.manager and hasattr(self.manager, 'signin'):
            return self.manager.signin()
        return {'success': False, 'error': 'Sign-in not available for this backend'}
    
    def validate_url_access(self, url: str) -> tuple[bool, str]:
        """Validate that a URL is allowed by whitelist"""
        # Basic validation - only allow driver/hardware related domains
        allowed_domains = [
            'github.com',
            'gitlab.com',
            'kernel.org',
            'freedesktop.org',
            'ubuntu.com',
            'debian.org'
        ]
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        for allowed in allowed_domains:
            if allowed in domain:
                return True, "URL allowed"
        
        return False, f"Domain {domain} not in whitelist"
    
    def validate_github_search(self, query: str) -> tuple[bool, str]:
        """Validate GitHub search query is for drivers/chipsets"""
        driver_keywords = ['driver', 'chipset', 'firmware', 'kernel', 'module', 'hardware']
        query_lower = query.lower()
        
        for keyword in driver_keywords:
            if keyword in query_lower:
                return True, "Query is driver-related"
        
        return False, "Query does not appear to be driver-related"
    
    def validate_huggingface_search(self, query: str) -> tuple[bool, str]:
        """Validate HuggingFace search query is for drivers/chipsets"""
        return self.validate_github_search(query)
    
    def check_filesystem_access(self, path: str, is_critical_error: bool = False) -> tuple[bool, str]:
        """Check if AI can access filesystem path"""
        # Allow read-only access to system paths
        allowed_paths = ['/sys/', '/proc/', '/dev/', '/var/log/']
        
        for allowed in allowed_paths:
            if path.startswith(allowed):
                return True, "Path allowed for read access"
        
        if is_critical_error:
            return True, "Critical error - allowing emergency access"
        
        return False, f"Path {path} not in allowed list"
    
    def configure_for_driver_mgt(self) -> bool:
        """
        Configure the AI backend for driver-mgt use
        Legacy method - now handled by OllamaManager
        """
        return True
    
    def shutdown(self):
        """Shutdown AI service and cleanup"""
        if self.manager:
            self.manager.shutdown()
