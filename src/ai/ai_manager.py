"""
AI Manager - Unified interface for AI backends (Ollama or LLM Studio)
Handles backend selection and delegation
"""

from typing import Dict, Any, Optional
from ai.ollama_manager import OllamaManager
from ai.llm_studio_manager import LLMStudioManager

class AIManager:
    """
    Unified AI Manager that delegates to either Ollama or LLM Studio
    based on configuration
    """
    
    def __init__(self, config_manager, backend: Optional[str] = None):
        """
        Initialize AI Manager
        
        Args:
            config_manager: Configuration manager instance
            backend: Override backend selection ('ollama' or 'lmstudio')
                    If None, uses config setting
        """
        self.config = config_manager
        
        # Determine which backend to use
        if backend:
            self.backend = backend
        else:
            self.backend = self.config.get_ai('backend', 'ollama')
        
        # Initialize the appropriate backend
        if self.backend == 'lmstudio':
            self.manager = LLMStudioManager(config_manager)
        else:
            self.manager = OllamaManager(config_manager)
    
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
        Only applicable to LLM Studio (backs up config)
        """
        if hasattr(self.manager, 'configure_for_driver_mgt'):
            return self.manager.configure_for_driver_mgt()
        return True  # Ollama doesn't need special configuration
    
    def shutdown(self):
        """
        Shutdown AI service and cleanup
        For LLM Studio, this restores the previous configuration
        """
        self.manager.shutdown()
