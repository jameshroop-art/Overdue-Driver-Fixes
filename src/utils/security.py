"""
Security utilities for domain validation and access control
Ensures starcoder only accesses whitelisted domains and resources
"""

from typing import List, Optional
from urllib.parse import urlparse
import os
from pathlib import Path


class DomainValidator:
    """
    Validates URLs and domains against whitelist for starcoder security
    
    Ensures starcoder can only access:
    - ASUS support and download center
    - Phoronix reviews for hardware compatibility
    - Dev.to articles for Linux kernel updates
    - GitHub.com for driver repository searches
    - HuggingFace.co for driver repository searches
    """
    
    def __init__(self, config_manager):
        """Initialize with configuration manager"""
        self.config = config_manager
        self._load_whitelist()
    
    def _load_whitelist(self):
        """Load domain whitelist from configuration"""
        self.domain_whitelist = self.config.get_ai('security.domain_whitelist', [
            'www.asus.com',
            'asus.com',
            'www.phoronix.com',
            'phoronix.com',
            'dev.to',
            'github.com',
            'api.github.com',
            'huggingface.co',
            'www.huggingface.co'
        ])
        
        self.allowed_paths = self.config.get_ai('security.allowed_paths', [
            '/support/download-center/',
            '/review/',
            '/search/repositories'
        ])
        
        self.enforce_whitelist = self.config.get_ai('security.enforce_whitelist', True)
        
        # Filesystem access settings
        fs_config = self.config.get_ai('security.filesystem_access', {})
        self.filesystem_enabled = fs_config.get('enabled', False)
        self.critical_error_only = fs_config.get('allow_on_critical_error_only', True)
        self.allowed_directories = fs_config.get('allowed_directories', [
            '~/.config/driver-mgt/logs/',
            '~/.config/driver-mgt/corrections/',
            '~/.config/driver-mgt/reports/'
        ])
    
    def is_url_allowed(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check if a URL is allowed by the whitelist
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_allowed, reason)
            - is_allowed: True if URL is whitelisted
            - reason: Explanation if blocked
        """
        if not self.enforce_whitelist:
            return (True, "Whitelist enforcement disabled")
        
        if not url:
            return (False, "Empty URL provided")
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Check if domain is in whitelist
            domain_allowed = any(
                domain == wl_domain.lower() or domain.endswith('.' + wl_domain.lower())
                for wl_domain in self.domain_whitelist
            )
            
            if not domain_allowed:
                return (False, f"Domain '{domain}' is not in whitelist")
            
            # For specific domains, validate paths
            if domain in ['www.asus.com', 'asus.com']:
                # ASUS must be for support/download center
                if not any(allowed in path for allowed in ['/support/', '/download']):
                    return (False, f"ASUS URLs must be for support/download-center")
            
            elif domain in ['www.phoronix.com', 'phoronix.com']:
                # Phoronix must be for reviews
                if '/review/' not in path:
                    return (False, f"Phoronix URLs must be reviews")
            
            return (True, "URL is whitelisted")
            
        except Exception as e:
            return (False, f"Error parsing URL: {e}")
    
    def validate_github_search(self, search_query: str) -> tuple[bool, Optional[str]]:
        """
        Validate GitHub search query for driver searches
        
        Args:
            search_query: Search query string
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        if not self.enforce_whitelist:
            return (True, "Whitelist enforcement disabled")
        
        # GitHub is whitelisted for driver/chipset searches
        driver_keywords = ['driver', 'chipset', 'linux', 'firmware', 'bios']
        
        query_lower = search_query.lower()
        has_driver_keyword = any(keyword in query_lower for keyword in driver_keywords)
        
        if not has_driver_keyword:
            return (False, f"GitHub searches must be driver/chipset related")
        
        return (True, "GitHub search is for drivers/chipsets")
    
    def validate_huggingface_search(self, search_query: str) -> tuple[bool, Optional[str]]:
        """
        Validate HuggingFace search query for driver searches
        
        Args:
            search_query: Search query string
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        if not self.enforce_whitelist:
            return (True, "Whitelist enforcement disabled")
        
        # HuggingFace is whitelisted for driver/chipset searches
        driver_keywords = ['driver', 'chipset', 'linux', 'firmware', 'hardware']
        
        query_lower = search_query.lower()
        has_driver_keyword = any(keyword in query_lower for keyword in driver_keywords)
        
        if not has_driver_keyword:
            return (False, f"HuggingFace searches must be driver/chipset related")
        
        return (True, "HuggingFace search is for drivers/chipsets")
    
    def is_filesystem_access_allowed(self, path: str, is_critical_error: bool = False) -> tuple[bool, Optional[str]]:
        """
        Check if filesystem access is allowed
        
        Starcoder should NOT access filesystem unless critical error
        
        Args:
            path: Filesystem path to access
            is_critical_error: True if this is for critical error handling
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        if not self.filesystem_enabled and not (self.critical_error_only and is_critical_error):
            return (False, "Filesystem access disabled for starcoder")
        
        if self.critical_error_only and not is_critical_error:
            return (False, "Filesystem access only allowed for critical errors")
        
        # Expand user paths
        expanded_path = os.path.expanduser(path)
        normalized_path = os.path.normpath(expanded_path)
        
        # Check if path is in allowed directories
        for allowed_dir in self.allowed_directories:
            expanded_allowed = os.path.expanduser(allowed_dir)
            normalized_allowed = os.path.normpath(expanded_allowed)
            
            if normalized_path.startswith(normalized_allowed):
                return (True, "Path is in allowed directory")
        
        return (False, f"Path '{path}' is not in allowed directories")
    
    def get_whitelisted_domains(self) -> List[str]:
        """Get list of whitelisted domains"""
        return self.domain_whitelist.copy()
    
    def get_allowed_directories(self) -> List[str]:
        """Get list of allowed filesystem directories"""
        return self.allowed_directories.copy()
