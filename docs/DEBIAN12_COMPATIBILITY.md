# Debian 12 (Bookworm) Compatibility Guide

## Overview

driver-mgt is fully compatible with Debian 12 (Bookworm). This guide covers specific considerations for Debian 12 users.

## Key Differences in Debian 12

### 1. Python Version
- **Default**: Python 3.11
- **Minimum Required**: Python 3.9
- **Compatibility**: ✅ Fully compatible

### 2. PEP 668 - Externally Managed Environments

Debian 12 implements [PEP 668](https://peps.python.org/pep-0668/), which marks the system Python as "externally managed". This prevents direct pip installations to the system Python to avoid conflicts with apt-managed packages.

**What this means for driver-mgt:**
- ✅ **No issues**: driver-mgt automatically uses virtual environments
- ✅ The `install.sh` script creates an isolated venv at `/opt/driver-mgt/venv`
- ✅ All dependencies are installed within the venv, not system-wide
- ✅ No conflicts with system Python packages

**If you see "externally-managed-environment" errors:**
- This only happens if you try to install packages system-wide with pip
- driver-mgt handles this automatically via venv
- Never use `--break-system-packages` flag

### 3. Required Packages

Debian 12 requires specific packages for Python development:

```bash
sudo apt-get install python3 python3-pip python3-venv python3-dev build-essential
```

The `install.sh` script automatically installs all required packages.

## Installation on Debian 12

### Automatic Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# Run installer (automatically detects Debian 12)
sudo bash install.sh
```

The installer will:
1. Detect Debian 12 (Bookworm)
2. Install all required system packages including:
   - python3, python3-pip, python3-venv, python3-dev
   - build-essential (for compiling any native extensions)
   - pciutils, lshw, dmidecode (hardware detection tools)
   - Qt dependencies for PyQt6
3. Create isolated virtual environment
4. Install all Python dependencies in the venv
5. Verify installation

### Manual Installation

If you prefer manual installation:

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv python3-dev \
                        build-essential pciutils lshw dmidecode \
                        libgl1-mesa-glx libxkbcommon-x11-0 libxcb-xinerama0 \
                        libxcb-cursor0 libegl1

# 2. Clone repository
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Run driver-mgt
./driver-mgt
```

## PyQt6 on Debian 12

### Compatibility
PyQt6 works perfectly on Debian 12 when installed in a virtual environment.

### System Dependencies for PyQt6

If you encounter any issues with PyQt6 GUI:

```bash
# Install Qt6 system libraries
sudo apt-get install -y libgl1-mesa-glx libxkbcommon-x11-0 libxcb-xinerama0 \
                        libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libegl1
```

These are typically installed automatically by `install.sh`, but are listed here for troubleshooting.

**Note**: From PyQt6 6.5.0+, `libxcb-cursor0` is required to load the Qt xcb platform plugin.

### Headless Systems

If running on a headless Debian 12 server without X11:
- CLI mode works perfectly without any GUI dependencies
- PyQt6 won't install, but CLI functionality is unaffected
- Use: `driver-mgt status`, `driver-mgt scan`, etc.

## Hardware Detection on Debian 12

Debian 12 requires specific tools for hardware detection:

```bash
# Automatically installed by install.sh
sudo apt-get install pciutils lshw dmidecode
```

**Permissions**: Some hardware detection requires root privileges:
```bash
# Run with sudo for full hardware detection
sudo driver-mgt status
```

## Testing on Debian 12

Run the test suite to verify compatibility:

```bash
# Basic functionality tests
python3 tests/test_basic.py

# Integration tests
python3 tests/test_integration.py

# Installation verification
bash test-installation.sh
```

## Common Issues and Solutions

### Issue: "No module named 'PyQt6'"

**Cause**: Running outside the virtual environment

**Solution**:
```bash
# Use the installed version (automatically uses venv)
driver-mgt

# Or manually activate venv
source /opt/driver-mgt/venv/bin/activate
```

### Issue: "externally-managed-environment" error

**Cause**: Trying to install packages with pip outside venv

**Solution**: 
- Don't run `pip install` directly on system Python
- driver-mgt already handles this via automatic venv
- If developing, always use a venv:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### Issue: Virtual environment creation fails

**Cause**: Missing `python3-venv` package

**Solution**:
```bash
sudo apt-get install python3-venv
```

### Issue: PyQt6 fails to start

**Cause**: Missing Qt system libraries

**Solution**:
```bash
sudo apt-get install libgl1-mesa-glx libxkbcommon-x11-0 libxcb-xinerama0 \
                     libxcb-cursor0 libegl1
```

**Common error messages:**
- "xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin"
- "Could not load the Qt platform plugin 'xcb'"
- "libEGL.so.1: cannot open shared object file"

These errors indicate missing Qt dependencies. Run the command above to install them.

### Issue: Hardware detection incomplete

**Cause**: Missing hardware detection tools or insufficient permissions

**Solution**:
```bash
# Install tools
sudo apt-get install pciutils lshw dmidecode

# Run with sudo for full detection
sudo driver-mgt status
```

## Debian 12 System Requirements

### Minimum Requirements
- Debian 12 (Bookworm)
- 2GB RAM (4GB recommended for AI features)
- 500MB disk space
- Python 3.11 (included with Debian 12)

### Recommended for Full Features
- 4GB+ RAM (for AI monitoring with Ollama)
- X11 or Wayland display server (for GUI)
- Root/sudo access (for hardware control and driver installation)

## Version Compatibility Matrix

| Component       | Debian 12 Default | driver-mgt Requirement | Status |
|----------------|-------------------|------------------------|--------|
| Python         | 3.11              | 3.9+                   | ✅ Compatible |
| pip            | Available         | Any recent version     | ✅ Compatible |
| PyQt6          | Not pre-installed | 6.4.0+                 | ✅ Via pip in venv |
| psutil         | System package    | 5.9.0+                 | ✅ Via pip in venv |
| requests       | System package    | 2.28.0+                | ✅ Pre-installed |
| pyyaml         | System package    | 6.0+                   | ✅ Pre-installed |

## Debian-Specific Features

### APT Integration
Future versions may integrate with apt for:
- Detecting apt-installed drivers
- Suggesting apt packages before pip packages
- Coordinating with system package manager

### System Service Integration
Debian 12's systemd integration works seamlessly:
```bash
# Enable as system service (future feature)
sudo systemctl enable driver-mgt
sudo systemctl start driver-mgt
```

## Security Considerations

### PEP 668 Benefits
- Prevents accidental system Python breakage
- Clear separation between system and user packages
- Better dependency management
- Easier system maintenance

### Virtual Environment Isolation
- All driver-mgt dependencies in `/opt/driver-mgt/venv`
- No interference with system Python
- Easy to uninstall (just delete `/opt/driver-mgt`)
- No system-wide package pollution

## Uninstallation on Debian 12

```bash
# Remove installed files
sudo rm -rf /opt/driver-mgt
sudo rm /usr/local/bin/driver-mgt
sudo rm /usr/share/applications/driver-mgt.desktop

# Remove user config (optional)
rm -rf ~/.config/driver-mgt

# System packages remain (they may be used by other software)
# To remove if absolutely needed:
# sudo apt-get remove python3-pip python3-venv
```

## Development on Debian 12

For developers working on driver-mgt on Debian 12:

```bash
# Clone repo
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# Create development venv
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest black flake8

# Run tests
python tests/test_basic.py
python tests/test_integration.py
```

## References

- [Debian 12 Release Notes](https://www.debian.org/releases/bookworm/)
- [Python on Debian Wiki](https://wiki.debian.org/Python)
- [PEP 668 Specification](https://peps.python.org/pep-0668/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## Support

If you encounter issues on Debian 12:

1. Check this compatibility guide
2. Run `driver-mgt --check-deps` to verify installation
3. Run `bash test-installation.sh` for comprehensive testing
4. Check logs in `~/.config/driver-mgt/logs/`
5. Report issues on GitHub with system information:
   ```bash
   cat /etc/os-release
   python3 --version
   driver-mgt --check-deps
   ```

## Summary

✅ **driver-mgt is fully compatible with Debian 12**

The installation process automatically:
- Detects Debian 12
- Installs all required packages
- Creates PEP 668-compliant virtual environment
- Handles all dependencies properly
- Works seamlessly with Debian's package management

No special configuration or workarounds needed!
