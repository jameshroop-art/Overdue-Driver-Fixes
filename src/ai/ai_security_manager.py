"""
AI Security Manager - Enforces strict access controls for AI models
Limits AI access to only driver operations within program scope
"""

import re
from typing import Dict, Any, Optional, List
from pathlib import Path

class AISecurityManager:
    """
    Enforces security boundaries for AI model access
    Ensures AI can only access driver-related operations within program scope
    """
    
    # Allowed operations for AI models
    ALLOWED_OPERATIONS = {
        'analyze_driver_error',
        'assess_driver_risk',
        'suggest_driver_fix',
        'analyze_hardware_compatibility',
        'generate_driver_report',
        'monitor_driver_operation',
        'detect_driver_failure'
    }
    
    # Allowed data scopes - AI can only access these types of data
    ALLOWED_DATA_SCOPES = {
        'driver_logs',
        'hardware_info',
        'driver_version',
        'error_messages',
        'installation_status',
        'compatibility_info',
        'system_specs'
    }
    
    # Forbidden operations - AI must NEVER perform these
    FORBIDDEN_OPERATIONS = {
        'system_modification',
        'file_deletion',
        'network_access',
        'user_data_access',
        'credential_access',
        'arbitrary_command_execution',
        'privilege_escalation'
    }
    
    # Forbidden file paths - AI cannot access these
    FORBIDDEN_PATHS = {
        '/etc/passwd',
        '/etc/shadow',
        '/root',
        '/home/*/.ssh',
        '/home/*/.gnupg',
        '/home/*/.config/google-chrome',
        '/home/*/.mozilla',
        '/home/*/.local/share/keyrings'
    }
    
    # Maximum data size AI can process (prevent DoS)
    MAX_LOG_SIZE = 10000  # 10KB
    MAX_PROMPT_SIZE = 5000  # 5KB
    MAX_RESPONSE_SIZE = 20000  # 20KB
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.operation_log = []  # Track all AI operations for audit
    
    def validate_operation(self, operation: str, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate that an AI operation is allowed
        
        Args:
            operation: Operation name/type
            data: Data to be processed
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check if operation is forbidden
        if operation in self.FORBIDDEN_OPERATIONS:
            reason = f"Operation '{operation}' is forbidden for AI access"
            self._log_violation(operation, reason, data)
            return False, reason
        
        # Check if operation is explicitly allowed
        if operation not in self.ALLOWED_OPERATIONS:
            reason = f"Operation '{operation}' is not in allowed operations list"
            self._log_violation(operation, reason, data)
            return False, reason
        
        # Validate data scope
        for key in data.keys():
            if not self._is_data_scope_allowed(key):
                reason = f"Data scope '{key}' is not allowed for AI access"
                self._log_violation(operation, reason, data)
                return False, reason
        
        # Log successful validation
        self._log_operation(operation, "allowed", data)
        return True, "Operation allowed"
    
    def sanitize_prompt(self, prompt: str, data_type: str = 'driver_analysis') -> str:
        """
        Sanitize AI prompt to remove sensitive data and enforce scope
        
        Args:
            prompt: Raw prompt text
            data_type: Type of data in prompt
            
        Returns:
            Sanitized prompt safe for AI processing
        """
        # Check size limit
        if len(prompt) > self.MAX_PROMPT_SIZE:
            prompt = prompt[:self.MAX_PROMPT_SIZE] + "\n[... truncated for security]"
        
        # Remove potential sensitive patterns
        prompt = self._remove_sensitive_patterns(prompt)
        
        # Add scope enforcement to prompt
        scoped_prompt = self._add_scope_enforcement(prompt, data_type)
        
        return scoped_prompt
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitize AI response to ensure it doesn't contain forbidden content
        
        Args:
            response: Raw AI response
            
        Returns:
            Sanitized response safe for program use
        """
        # Check size limit
        if len(response) > self.MAX_RESPONSE_SIZE:
            response = response[:self.MAX_RESPONSE_SIZE] + "\n[Response truncated]"
        
        # Remove any potential command injection patterns
        response = self._remove_command_patterns(response)
        
        # Remove any potential file path leaks
        response = self._remove_sensitive_paths(response)
        
        return response
    
    def validate_file_access(self, file_path: str, operation: str = 'read') -> tuple[bool, str]:
        """
        Validate if AI can access a specific file
        
        Args:
            file_path: Path to file
            operation: Type of operation (read/write)
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        path = Path(file_path).resolve()
        
        # Check if path matches forbidden patterns
        for forbidden in self.FORBIDDEN_PATHS:
            if self._path_matches_pattern(str(path), forbidden):
                reason = f"Access to '{file_path}' is forbidden (matches {forbidden})"
                self._log_violation(f'file_access_{operation}', reason, {'path': file_path})
                return False, reason
        
        # Only allow access to driver-mgt specific directories
        allowed_dirs = [
            self.config.get_config_dir(),
            self.config.get_logs_dir(),
            self.config.get_corrections_dir(),
            self.config.get_reports_dir(),
            Path('/var/log/driver-mgt') if Path('/var/log/driver-mgt').exists() else None
        ]
        
        # Filter out None values
        allowed_dirs = [d for d in allowed_dirs if d is not None]
        
        # Check if path is within allowed directories
        is_allowed = any(self._is_path_within(path, allowed_dir) for allowed_dir in allowed_dirs)
        
        if not is_allowed:
            reason = f"File '{file_path}' is outside allowed directories"
            self._log_violation(f'file_access_{operation}', reason, {'path': file_path})
            return False, reason
        
        # Log successful validation
        self._log_operation(f'file_access_{operation}', 'allowed', {'path': file_path})
        return True, "File access allowed"
    
    def validate_command(self, command: str) -> tuple[bool, str]:
        """
        Validate if a command can be executed by AI
        
        Note: AI should generally NOT execute commands directly.
        This is for analysis/suggestion purposes only.
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        # AI should NEVER execute commands directly
        # Only allowed to analyze/suggest commands
        
        dangerous_commands = [
            'rm -rf', 'dd if=', 'mkfs', 'fdisk', 'parted',
            'iptables', 'ufw', 'firewall-cmd',
            'userdel', 'usermod', 'passwd',
            'systemctl stop', 'systemctl disable',
            'shutdown', 'reboot', 'init 0',
            'curl', 'wget', 'nc', 'netcat',
            ':(){:|:&};:'  # Fork bomb
        ]
        
        for dangerous in dangerous_commands:
            if dangerous.lower() in command.lower():
                reason = f"Command contains dangerous pattern: {dangerous}"
                self._log_violation('command_validation', reason, {'command': command})
                return False, reason
        
        return True, "Command is safe for analysis (not execution)"
    
    def get_allowed_operations_list(self) -> List[str]:
        """Get list of operations AI is allowed to perform"""
        return sorted(list(self.ALLOWED_OPERATIONS))
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent AI operation audit log"""
        return self.operation_log[-limit:]
    
    def _is_data_scope_allowed(self, data_key: str) -> bool:
        """Check if a data scope is allowed"""
        # Allow exact matches
        if data_key in self.ALLOWED_DATA_SCOPES:
            return True
        
        # Allow keys that start with allowed scopes
        for allowed_scope in self.ALLOWED_DATA_SCOPES:
            if data_key.startswith(allowed_scope):
                return True
        
        return False
    
    def _remove_sensitive_patterns(self, text: str) -> str:
        """Remove sensitive patterns from text"""
        # Remove potential passwords
        text = re.sub(r'password[=:\s]+\S+', 'password=***', text, flags=re.IGNORECASE)
        
        # Remove potential API keys/tokens
        text = re.sub(r'(api[_-]?key|token|secret)[=:\s]+\S+', r'\1=***', text, flags=re.IGNORECASE)
        
        # Remove potential email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)
        
        # Remove IP addresses (but keep localhost)
        text = re.sub(r'\b(?!127\.0\.0\.1\b)(?:\d{1,3}\.){3}\d{1,3}\b', 'XXX.XXX.XXX.XXX', text)
        
        return text
    
    def _remove_command_patterns(self, text: str) -> str:
        """Remove command injection patterns from text"""
        # Remove shell command patterns
        dangerous_patterns = [
            r'\$\([^)]*\)',  # Command substitution
            r'`[^`]*`',      # Backtick command substitution
            r';\s*\w+',      # Command chaining with semicolon
            r'\|\s*\w+',     # Pipe to command
            r'&&\s*\w+',     # Command chaining with &&
            r'\|\|\s*\w+'    # Command chaining with ||
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '[REMOVED_FOR_SECURITY]', text)
        
        return text
    
    def _remove_sensitive_paths(self, text: str) -> str:
        """Remove sensitive file paths from text"""
        for forbidden_path in self.FORBIDDEN_PATHS:
            # Convert glob pattern to regex
            pattern = forbidden_path.replace('*', '[^/\\s]+')
            text = re.sub(pattern, '[REDACTED_PATH]', text)
        
        return text
    
    def _add_scope_enforcement(self, prompt: str, data_type: str) -> str:
        """Add scope enforcement directives to prompt"""
        scope_prefix = f"""
STRICT OPERATIONAL SCOPE:
- You are assisting with driver management ONLY
- Data type: {data_type}
- You MUST NOT access files outside driver-mgt directories
- You MUST NOT suggest system modifications beyond driver operations
- You MUST NOT access user personal data
- Focus ONLY on the driver-related task at hand

TASK:
"""
        return scope_prefix + prompt
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches a glob pattern"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def _is_path_within(self, path: Path, parent: Path) -> bool:
        """Check if path is within parent directory"""
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False
    
    def _log_operation(self, operation: str, status: str, data: Dict[str, Any]):
        """Log AI operation for audit trail"""
        import datetime
        
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operation': operation,
            'status': status,
            'data_keys': list(data.keys()) if isinstance(data, dict) else [],
            'data_size': len(str(data))
        }
        
        self.operation_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.operation_log) > 1000:
            self.operation_log = self.operation_log[-500:]
    
    def _log_violation(self, operation: str, reason: str, data: Dict[str, Any]):
        """Log security violation"""
        import datetime
        
        violation_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operation': operation,
            'status': 'VIOLATION',
            'reason': reason,
            'data_keys': list(data.keys()) if isinstance(data, dict) else [],
            'data_size': len(str(data))
        }
        
        self.operation_log.append(violation_entry)
        
        # Log to file for security audit
        try:
            log_file = self.config.get_logs_dir() / 'ai_security_violations.log'
            with open(log_file, 'a') as f:
                f.write(f"{violation_entry['timestamp']} - VIOLATION - {operation}: {reason}\n")
        except Exception:
            pass  # Fail silently if logging fails
