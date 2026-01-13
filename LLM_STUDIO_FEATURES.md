# LLM Studio Integration and AI Security Features

## Overview
This document describes the features added to driver-mgt for LLM Studio integration, model selection, and AI security constraints.

**📖 For installation instructions**, see the **[Complete LM Studio Setup Guide](LMSTUDIO_SETUP.md)**.

## Installation Quick Reference

```bash
# Download LM Studio for Linux
wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio.AppImage
chmod +x lm-studio.AppImage

# Launch and configure
./lm-studio.AppImage
# In LM Studio: Start Server (localhost:1234) and download models

# Use with driver-mgt
driver-mgt-lmstudio
```

**Full documentation**: [LMSTUDIO_SETUP.md](LMSTUDIO_SETUP.md) includes:
- Complete installation steps
- Localhost configuration
- Model download instructions
- Performance optimization
- Troubleshooting guide

## Integration Features

## New Features

### 1. Desktop Launcher with Sudo Support

**File**: `driver-mgt-lmstudio` (wrapper script)
**Desktop Entry**: `driver-mgt-lmstudio.desktop`

- Launches driver-mgt with elevated privileges using `pkexec`
- Automatically configures LLM Studio backend
- Backs up LLM Studio configuration on startup
- Restores previous configuration on exit
- Checks for LLM Studio availability before launching

**Usage**:
```bash
# Command line
driver-mgt-lmstudio

# Or use desktop launcher
# Search for "Driver Manager (LLM Studio)" in applications menu
```

### 2. Multiple AI Backend Support

**Files**: `src/ai/ai_manager.py`, `src/ai/llm_studio_manager.py`, `src/ai/ollama_manager.py`

- Unified interface for both Ollama and LLM Studio backends
- Switch between backends via configuration or environment variable
- Automatic backend selection based on availability

**Configuration**:
```json
{
  "backend": "ollama",  // or "lmstudio"
  "ollama": {
    "host": "localhost",
    "port": 11434
  },
  "lmstudio": {
    "host": "localhost",
    "port": 1234,
    "additional_ports": [1235, 1236]
  }
}
```

### 3. Multiple LLM Studio Instances

**Feature**: Support for up to 3 concurrent LLM Studio instances on different ports

**Configuration**:
- Primary port: 1234 (default)
- Additional ports: 1235, 1236 (configurable)
- Automatic discovery of running instances
- Ability to switch between instances

**Benefits**:
- Load balancing across multiple instances
- Different models on different ports
- Improved availability and redundancy

### 4. Model Selection Dropdown

**File**: `src/gui/ai_settings_widget.py`

A new GUI widget for selecting AI models dynamically.

**Features**:
- Displays all available models from current backend
- Real-time model switching
- Connection testing
- Instance status for LLM Studio (shows all running instances)
- Refresh functionality to detect newly loaded models

**Location**: Available in the "AI Settings" tab of the main window

**Supported Models**:
- Any model supported by Ollama (e.g., starcoder:3b, codellama, mistral, etc.)
- Any model loaded in LLM Studio
- No longer limited to starcoder:3b

### 5. AI Security Manager

**File**: `src/ai/ai_security_manager.py`

Comprehensive security system to limit AI model access to driver operations only.

#### Allowed Operations
AI models can ONLY perform these operations:
- `analyze_driver_error` - Analyze driver installation errors
- `assess_driver_risk` - Assess risk of driver installation
- `suggest_driver_fix` - Suggest fixes for driver issues
- `analyze_hardware_compatibility` - Check hardware compatibility
- `generate_driver_report` - Generate driver reports
- `monitor_driver_operation` - Monitor driver operations
- `detect_driver_failure` - Detect driver failures

#### Forbidden Operations
AI models are BLOCKED from:
- System modifications outside driver scope
- File deletion
- Network access (except local LLM endpoints)
- User data access
- Credential access
- Arbitrary command execution
- Privilege escalation

#### Data Scope Restrictions
AI can ONLY access:
- Driver logs
- Hardware information
- Driver version information
- Error messages
- Installation status
- Compatibility information
- System specifications (hardware only)

#### File Access Restrictions
AI is BLOCKED from accessing:
- `/etc/passwd`, `/etc/shadow`
- `/root` directory
- User SSH keys (`.ssh` directories)
- GPG keys (`.gnupg` directories)
- Browser data (Chrome, Firefox, etc.)
- Password managers (`keyrings`)

#### Security Features
1. **Prompt Sanitization**
   - Removes sensitive patterns (passwords, API keys, emails)
   - Limits prompt size (5KB max)
   - Adds scope enforcement directives

2. **Response Sanitization**
   - Removes command injection patterns
   - Removes sensitive file paths
   - Limits response size (20KB max)

3. **Operation Validation**
   - Every AI operation is validated against allowed list
   - Violations are logged for audit
   - Failed operations return security error

4. **Audit Logging**
   - All AI operations logged with timestamp
   - Security violations logged to file
   - Audit trail for compliance

### 6. Configuration Backup and Restore

**Feature**: Automatic backup and restoration of LLM Studio configuration

When launching with LLM Studio backend:
1. Current LLM Studio config is backed up to `~/.config/driver-mgt/lmstudio_backup/`
2. LLM Studio is configured for driver-mgt use
3. On exit, original configuration is restored
4. Backup is cleaned up after successful restore

**Benefits**:
- No permanent changes to user's LLM Studio setup
- Safe experimentation with driver-mgt
- Automatic cleanup on exit

## Usage Examples

### Launch with LLM Studio
```bash
# Start LLM Studio first, then:
driver-mgt-lmstudio

# Or set environment variable:
export DRIVER_MGT_AI_BACKEND=lmstudio
driver-mgt
```

### Check AI Status
```bash
driver-mgt ai-status
# Output includes:
# - Backend type (Ollama or LLM Studio)
# - Active model
# - Instance information (for LLM Studio)
# - Running count
```

### Change Model in GUI
1. Launch driver-mgt
2. Navigate to "AI Settings" tab
3. Click "Refresh Models" to see available models
4. Select desired model from dropdown
5. Click "Apply Changes"
6. Click "Test Connection" to verify

### Multiple LLM Studio Instances
```bash
# Start multiple LLM Studio instances on different ports:
# Instance 1: Port 1234
# Instance 2: Port 1235
# Instance 3: Port 1236

# driver-mgt will automatically discover all running instances
# and connect to the first available one
```

## Security Best Practices

1. **Model Selection**: Choose models appropriate for code/driver analysis
2. **Audit Logs**: Regularly review `~/.config/driver-mgt/logs/ai_security_violations.log`
3. **Least Privilege**: AI models run with minimal permissions
4. **Data Minimization**: Only driver-related data is sent to AI
5. **Local Processing**: All AI processing is local (no external services)

## Configuration Files

### User Configuration
- `~/.config/driver-mgt/config.json` - Main configuration
- `~/.config/driver-mgt/ai-config.json` - AI backend configuration
- `~/.config/driver-mgt/lmstudio_backup/` - LLM Studio backup (temporary)
- `~/.config/driver-mgt/logs/ai_security_violations.log` - Security audit log

### System Configuration
- `/opt/driver-mgt/config/ai-config.json.template` - Default AI configuration
- `/usr/local/bin/driver-mgt-lmstudio` - LLM Studio launcher script
- `/usr/share/applications/driver-mgt-lmstudio.desktop` - Desktop entry

## Troubleshooting

### LLM Studio Not Detected
```bash
# Check if LLM Studio is running:
curl http://localhost:1234/v1/models

# If not running, start LLM Studio application
# Ensure "Start Server" is enabled in LLM Studio
```

### Model Not Found
```bash
# Refresh models in GUI:
# AI Settings tab -> "Refresh Models" button

# Or check available models:
curl http://localhost:1234/v1/models  # For LLM Studio
ollama list  # For Ollama
```

### Security Violations
```bash
# Check security log:
cat ~/.config/driver-mgt/logs/ai_security_violations.log

# Common causes:
# - AI attempting to access forbidden files
# - Operation not in allowed list
# - Data scope outside permitted areas
```

### Configuration Not Restoring
```bash
# Manual restore if needed:
# Backup location: ~/.config/driver-mgt/lmstudio_backup/
# LLM Studio config: ~/.cache/lm-studio/

# Copy backup back:
rm -rf ~/.cache/lm-studio
cp -r ~/.config/driver-mgt/lmstudio_backup ~/.cache/lm-studio
```

## Architecture

```
driver-mgt
├── AI Manager (ai_manager.py)
│   ├── Backend Selection
│   ├── Ollama Manager
│   │   ├── Model Management
│   │   ├── Security Validation
│   │   └── Prompt/Response Sanitization
│   └── LLM Studio Manager
│       ├── Multi-Instance Support
│       ├── Config Backup/Restore
│       ├── Security Validation
│       └── Prompt/Response Sanitization
├── Security Manager (ai_security_manager.py)
│   ├── Operation Validation
│   ├── Data Scope Enforcement
│   ├── File Access Control
│   ├── Prompt Sanitization
│   ├── Response Sanitization
│   └── Audit Logging
└── GUI
    ├── Main Window
    ├── AI Settings Widget
    │   ├── Model Selection Dropdown
    │   ├── Backend Status
    │   ├── Instance Information
    │   └── Connection Testing
    └── Device Tabs
```

## API Reference

### AIManager
```python
from ai.ai_manager import AIManager

ai = AIManager(config_manager, backend='lmstudio')
status = ai.get_status()
result = ai.analyze_error(error_log)
ai.shutdown()  # Restores config for LLM Studio
```

### AISecurityManager
```python
from ai.ai_security_manager import AISecurityManager

security = AISecurityManager(config_manager)
is_allowed, reason = security.validate_operation('analyze_driver_error', data)
sanitized = security.sanitize_prompt(prompt, 'driver_analysis')
audit_log = security.get_audit_log(limit=100)
```

### LLMStudioManager
```python
from ai.llm_studio_manager import LLMStudioManager

lm = LLMStudioManager(config_manager)
instances = lm.get_all_instances()
lm.switch_to_port(1235)
lm.configure_for_driver_mgt()  # Backs up config
lm.shutdown()  # Restores config
```

## Future Enhancements

Potential future improvements:
1. Support for more AI backends (e.g., LocalAI, Text Generation WebUI)
2. Fine-tuned models specifically for driver management
3. Advanced model routing based on task complexity
4. Distributed model inference across multiple machines
5. Model performance metrics and benchmarking

## Contributing

When contributing AI-related features:
1. All AI operations MUST go through security validation
2. Add new operations to `ALLOWED_OPERATIONS` in `ai_security_manager.py`
3. Test with both Ollama and LLM Studio backends
4. Ensure sensitive data is sanitized
5. Update audit logging for new operations
6. Document security implications

## License

Same as driver-mgt main project (GPL-3.0)
