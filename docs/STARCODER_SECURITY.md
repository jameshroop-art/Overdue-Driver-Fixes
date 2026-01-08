# Starcoder Domain Boundaries & Security

This document details the security boundaries and access restrictions for the starcoder:3b AI model used in driver-mgt.

## Overview

starcoder:3b is an AI assistant integrated into driver-mgt specifically for:
- Driver wellbeing monitoring
- Driver operation oversight
- Upgrade and update management
- Risk assessment for driver installations
- Proactive error prevention

To ensure security and prevent misuse, starcoder:3b operates under strict domain and filesystem access restrictions.

## Domain Whitelist

starcoder:3b can ONLY access the following whitelisted domains:

### 1. ASUS Support & Download Center
- **Domain**: `www.asus.com`, `asus.com`
- **Allowed Paths**: `/support/`, `/download-center/`, `/download/`
- **Purpose**: Download chipset drivers, BIOS updates, Wi-Fi 6 drivers, Ethernet drivers
- **Example URLs**:
  - `https://www.asus.com/support/download-center/`
  - `https://asus.com/support/drivers/`

### 2. Phoronix Hardware Reviews
- **Domain**: `www.phoronix.com`, `phoronix.com`
- **Allowed Paths**: `/review/`
- **Purpose**: Hardware compatibility information, Linux performance reviews
- **Example URLs**:
  - `https://www.phoronix.com/review/amd-ryzen-7-9800x3d-linux`

### 3. Dev.to Technical Articles
- **Domain**: `dev.to`
- **Allowed Paths**: All article paths
- **Purpose**: Linux kernel updates, hardware support information
- **Example URLs**:
  - `https://dev.to/nolunchbreaks_22/linux-kernel-613-breaking-new-ground-in-hardware-support-and-system-performance-15g1`

### 4. GitHub Repository Search
- **Domain**: `github.com`, `api.github.com`
- **Allowed Paths**: All repository and API paths
- **Purpose**: Search for Linux-compatible driver repositories
- **Search Restrictions**: Queries must contain driver/chipset/firmware/linux keywords
- **Example URLs**:
  - `https://github.com/user/repo`
  - `https://api.github.com/search/repositories`

### 5. HuggingFace Repository Search
- **Domain**: `huggingface.co`, `www.huggingface.co`
- **Allowed Paths**: All model/dataset paths
- **Purpose**: Search for driver and firmware repositories
- **Search Restrictions**: Queries must contain driver/hardware/firmware/linux keywords
- **Example URLs**:
  - `https://huggingface.co/models`
  - `https://huggingface.co/datasets`

## Filesystem Access Restrictions

### Default Behavior
**starcoder DOES NOT access the filesystem** under normal operation.

### Critical Error Exception
Filesystem access is ONLY allowed when a critical error occurs that would cause a complete system crash.

### Allowed Directories (Critical Error Only)
When a critical error is detected, starcoder may access:

1. **Logs Directory**: `~/.config/driver-mgt/logs/`
   - For writing error logs
   - For reading previous error patterns

2. **Corrections Directory**: `~/.config/driver-mgt/corrections/`
   - For writing correction event logs
   - For documenting remediation actions

3. **Reports Directory**: `~/.config/driver-mgt/reports/`
   - For generating manufacturer bug reports
   - For saving diagnostic information

### Prohibited Directories
All other filesystem locations are prohibited, including:
- System directories (`/etc/`, `/sys/`, `/proc/`, etc.)
- User home directories (except the allowed subdirectories)
- Root filesystem (`/`)
- Other application directories

## Search Query Validation

### GitHub Search Requirements
GitHub searches must contain at least one of:
- `driver`
- `chipset`
- `linux`
- `firmware`
- `bios`

**Valid Examples:**
- "nvidia linux driver"
- "ASUS motherboard chipset"
- "WiFi firmware linux"

**Invalid Examples:**
- "javascript tutorial" (blocked)
- "python web framework" (blocked)

### HuggingFace Search Requirements
HuggingFace searches must contain at least one of:
- `driver`
- `chipset`
- `linux`
- `firmware`
- `hardware`

**Valid Examples:**
- "AMD linux driver"
- "hardware firmware collection"
- "chipset drivers linux"

**Invalid Examples:**
- "text generation model" (blocked)
- "image classification" (blocked)

## Configuration

Domain whitelist and security settings are configured in `~/.config/driver-mgt/ai-config.json`:

```json
{
  "security": {
    "domain_whitelist": [
      "www.asus.com",
      "asus.com",
      "www.phoronix.com",
      "phoronix.com",
      "dev.to",
      "github.com",
      "api.github.com",
      "huggingface.co",
      "www.huggingface.co"
    ],
    "allowed_paths": [
      "/support/download-center/",
      "/review/",
      "/search/repositories"
    ],
    "filesystem_access": {
      "enabled": false,
      "allow_on_critical_error_only": true,
      "allowed_directories": [
        "~/.config/driver-mgt/logs/",
        "~/.config/driver-mgt/corrections/",
        "~/.config/driver-mgt/reports/"
      ]
    },
    "enforce_whitelist": true
  }
}
```

### Configuration Options

- **enforce_whitelist**: If `true`, strictly enforces domain whitelist (default: `true`)
- **filesystem_access.enabled**: If `true`, allows general filesystem access (default: `false`)
- **filesystem_access.allow_on_critical_error_only**: If `true`, only allows filesystem access during critical errors (default: `true`)

## Validation Process

All URL and filesystem access requests go through validation:

1. **URL Validation**:
   - Parse URL to extract domain and path
   - Check if domain is in whitelist
   - For specific domains (ASUS, Phoronix), validate path requirements
   - Log and block if validation fails

2. **Search Query Validation**:
   - Check if query contains required keywords
   - Block queries unrelated to drivers/hardware
   - Log blocked attempts

3. **Filesystem Validation**:
   - Check if critical error flag is set
   - Verify path is in allowed directories
   - Normalize paths to prevent directory traversal
   - Block and log unauthorized access attempts

## Security Auditing

All access attempts (allowed and blocked) are logged for auditing:

- **Location**: `~/.config/driver-mgt/logs/security-audit.log`
- **Contents**: Timestamp, request type, URL/path, validation result, reason

## Enforcement

The security boundaries are enforced by the `DomainValidator` class in `src/utils/security.py`.

All modules that perform web requests or filesystem operations must use the validator:
- `src/ai/ollama_manager.py` - AI operations
- `src/core/hardware_detector.py` - Hardware detection and repo searches
- `src/core/driver_manager.py` - Driver downloads and installations

## Testing

Security boundaries are tested in `tests/test_security_boundaries.py`:

Run tests:
```bash
python3 tests/test_security_boundaries.py
```

Tests verify:
- ✓ Whitelisted domains are allowed
- ✓ Non-whitelisted domains are blocked
- ✓ GitHub searches require driver keywords
- ✓ HuggingFace searches require hardware keywords
- ✓ Filesystem access requires critical error flag
- ✓ Only allowed directories are accessible
- ✓ Path-specific restrictions (ASUS, Phoronix) work correctly

## Compliance

This implementation ensures:
- ✓ starcoder only accesses approved domains for driver information
- ✓ starcoder does not access filesystem except for critical errors
- ✓ All access is logged and auditable
- ✓ User data and privacy are protected
- ✓ System security is maintained

## Violation Handling

If starcoder attempts to access a blocked resource:
1. Access is immediately denied
2. Attempt is logged with details
3. User is notified (optional)
4. Operation continues safely without the blocked resource

No system crashes or errors occur due to blocked access attempts.
