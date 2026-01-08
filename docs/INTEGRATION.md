# GUI and Program Integration

This document describes how the GUI and program components are integrated in driver-mgt and how the installation process ensures they work together.

## Overview

driver-mgt consists of several components that work together:
- **Core Program** (`src/core/`): Hardware detection, driver management, risk assessment
- **GUI** (`src/gui/`): PyQt6-based graphical interface
- **AI Integration** (`src/ai/`): Ollama/starcoder:3b integration
- **Utilities** (`src/utils/`): Logging, venv management, terminal utilities
- **Entry Point** (`driver-mgt`): Main executable script

## Integration Architecture

### 1. Entry Point (`driver-mgt`)

The `driver-mgt` script serves as the unified entry point for both CLI and GUI modes:

```python
# Automatically manages virtual environment
from utils.venv_manager import ensure_venv
ensure_venv()

# Initializes core components
from core.config import ConfigManager
from core.hardware_detector import HardwareDetector
from core.driver_manager import DriverManager

# Launches GUI if no CLI command specified
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
```

### 2. Virtual Environment Management

The `venv_manager` module ensures consistent Python environment:

- **Auto-detection**: Finds venv in installed location (`/opt/driver-mgt/venv`) or source directory
- **Auto-creation**: Creates venv if it doesn't exist
- **Auto-restart**: Restarts script in venv if not already running in one
- **Dependency verification**: Checks all required packages are installed

### 3. Configuration Management

The `ConfigManager` handles configuration across all components:

- **Multi-location templates**: Finds config templates in multiple possible locations:
  - Source directory (`config/`)
  - System install (`/opt/driver-mgt/config/`)
  - Package install (`/usr/share/driver-mgt/config/`)
  
- **Auto-initialization**: Creates user config directory (`~/.config/driver-mgt/`)
- **Template-based defaults**: Uses templates to create initial config files
- **Shared configuration**: Both GUI and CLI use the same ConfigManager

### 4. Component Integration

All components are initialized with the same `ConfigManager` instance:

```python
config = ConfigManager()
hardware_detector = HardwareDetector(config)
driver_manager = DriverManager(config)
ollama_manager = OllamaManager(config)
```

GUI components receive the same shared managers:

```python
window = MainWindow(config)
# MainWindow internally creates:
# - HardwareDetector(config)
# - DriverManager(config)
# - OllamaManager(config)
```

This ensures:
- Consistent configuration across all components
- Shared state between CLI and GUI modes
- Coordinated AI integration

## Installation Process

### install.sh Workflow

The `install.sh` script ensures complete integration:

1. **System Dependencies**
   ```bash
   # Detects package manager (apt/dnf/pacman)
   # Installs Python, pip, and system utilities
   apt-get install python3 python3-pip python3-venv pciutils
   ```

2. **Application Installation**
   ```bash
   # Copies to /opt/driver-mgt/
   cp -r src config driver-mgt requirements.txt /opt/driver-mgt/
   chmod +x /opt/driver-mgt/driver-mgt
   ```

3. **Virtual Environment Setup**
   ```bash
   # Creates isolated Python environment
   cd /opt/driver-mgt
   python3 -m venv venv
   
   # Installs dependencies
   venv/bin/pip install -r requirements.txt
   ```

4. **Verification**
   ```bash
   # Tests that all dependencies are importable
   venv/bin/python -c "import PyQt6, psutil, requests, yaml"
   
   # Runs --check-deps to verify
   driver-mgt --check-deps
   ```

5. **System Integration**
   ```bash
   # Creates symlink for system-wide access
   ln -sf /opt/driver-mgt/driver-mgt /usr/local/bin/driver-mgt
   
   # Creates desktop entry
   /usr/share/applications/driver-mgt.desktop
   ```

6. **User Configuration**
   ```bash
   # Creates user config directories
   mkdir -p ~/.config/driver-mgt/{profiles,curves,logs,corrections,reports}
   ```

### setup.py for pip install

The `setup.py` enables installation via pip:

```bash
# Install in development mode
pip install -e .

# Or install from package
pip install driver-mgt
```

Features:
- Includes config templates as package data
- Installs the `driver-mgt` script
- Declares all dependencies
- Works with or without install.sh

## Testing Integration

### Integration Test Suite

The `tests/test_integration.py` verifies:

1. **Module Imports**: All modules can be imported
2. **Component Integration**: Components initialize and work together
3. **GUI Initialization**: MainWindow can be created (if PyQt6 available)
4. **Installation Structure**: Directories and files are properly set up

Run with:
```bash
python3 tests/test_integration.py
```

### Installation Test Script

The `test-installation.sh` verifies:

1. Python version compatibility (3.9+)
2. Virtual environment creation
3. Dependency installation
4. Configuration system
5. Core functionality
6. Entry point operation

Run with:
```bash
bash test-installation.sh
```

## Usage Modes

### GUI Mode (Default)

```bash
driver-mgt
```

- Launches PyQt6 GUI
- Shows hardware dashboard
- Provides visual driver management
- Displays system information

### CLI Mode

```bash
driver-mgt status          # Check system status
driver-mgt scan --all      # Scan for drivers
driver-mgt ai-status       # Check AI assistant
driver-mgt --check-deps    # Verify dependencies
```

- Command-line interface
- Suitable for automation
- Works without display server
- Faster for simple tasks

## Troubleshooting Integration Issues

### GUI Won't Launch

**Symptom**: "No module named 'PyQt6'"

**Solution**:
```bash
# Check if PyQt6 is installed in venv
/opt/driver-mgt/venv/bin/python -c "import PyQt6"

# If not, reinstall
/opt/driver-mgt/venv/bin/pip install PyQt6
```

### Configuration Not Found

**Symptom**: "Config templates not found"

**Solution**: ConfigManager automatically searches multiple locations. Verify templates exist:
```bash
ls /opt/driver-mgt/config/
ls ~/.config/driver-mgt/
```

### Virtual Environment Issues

**Symptom**: "Failed to set up virtual environment"

**Solution**: 
```bash
# Skip venv (use system Python)
driver-mgt --no-venv status

# Or recreate venv
rm -rf /opt/driver-mgt/venv
bash install.sh
```

### CLI and GUI Use Different Config

**Issue**: Changes in CLI don't appear in GUI

**Cause**: Running from different locations with different config instances

**Solution**: Ensure both use same executable:
```bash
which driver-mgt  # Should be /usr/local/bin/driver-mgt
```

## Development Mode

For development without system installation:

```bash
# Clone repository
git clone https://github.com/jameshroop-art/driver-mgt.git
cd driver-mgt

# Install in development mode
pip install -e .

# Or run directly
./driver-mgt status
./driver-mgt  # GUI mode
```

The `venv_manager` will automatically:
- Detect source directory
- Create local `venv/` if needed
- Use source `config/` templates

## Best Practices

### For Users

1. **Use install.sh for system install**: Ensures proper integration
2. **Don't modify installed files**: Use config files instead
3. **Run with same user**: Avoid mixing root/user configs

### For Developers

1. **Test both CLI and GUI**: Ensure changes work in both modes
2. **Use ConfigManager**: Don't access config files directly
3. **Run integration tests**: Before committing changes
4. **Test installation**: Verify install.sh still works

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    driver-mgt (Entry Point)             │
│  - Manages venv                                         │
│  - Parses arguments                                     │
│  - Routes to GUI or CLI                                 │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    ┌────▼────┐    ┌────▼────┐
    │   GUI   │    │   CLI   │
    │  Mode   │    │  Mode   │
    └────┬────┘    └────┬────┘
         │              │
         └──────┬───────┘
                │
    ┌───────────▼────────────┐
    │   ConfigManager        │
    │  - Finds templates     │
    │  - Manages user config │
    └───────────┬────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
┌───▼────┐  ┌────▼────┐  ┌──▼──────┐
│Hardware│  │ Driver  │  │   AI    │
│Detector│  │ Manager │  │ Manager │
└────────┘  └─────────┘  └─────────┘
```

## Summary

The integration ensures:

✅ **Unified Entry Point**: Single `driver-mgt` command for all modes
✅ **Consistent Environment**: Virtual environment management
✅ **Shared Configuration**: Same config for GUI and CLI
✅ **Flexible Installation**: Works with install.sh or pip
✅ **Graceful Degradation**: CLI works without GUI dependencies
✅ **Comprehensive Testing**: Integration and installation tests
✅ **Developer-Friendly**: Works in source directory or installed
