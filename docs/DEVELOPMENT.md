# Developer Documentation

## Project Structure

```
driver-mgt/
├── driver-mgt              # Main entry point (executable)
├── setup.py                # Python package setup
├── install.sh              # System installation script
├── requirements.txt        # Python dependencies
├── README.md               # User documentation
├── config/                 # Configuration templates
│   ├── config.json.template
│   └── ai-config.json.template
├── src/                    # Source code
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── hardware_detector.py # Hardware detection
│   │   ├── driver_manager.py   # Driver management
│   │   └── risk_assessor.py    # Risk assessment
│   ├── gui/               # GUI components
│   │   ├── __init__.py
│   │   └── main_window.py      # Main window
│   ├── ai/                # AI integration
│   │   ├── __init__.py
│   │   └── ollama_manager.py   # Ollama integration
│   └── utils/             # Utility modules
│       ├── __init__.py
│       └── logger.py           # Logging utility
├── tests/                 # Test files
│   └── test_basic.py
└── docs/                  # Additional documentation
    └── DEVELOPMENT.md
```

## Core Modules

### config.py
Manages application configuration. Handles loading/saving config files and provides access to configuration values.

### hardware_detector.py
Detects hardware components using system tools (lspci, dmi info). Identifies GPUs, WiFi adapters, motherboards, and cooling devices.

### driver_manager.py
Manages driver operations including finding available drivers, installation, testing, and rollback.

### risk_assessor.py
Assesses risk for hardware and driver combinations. Calculates risk percentages and provides recommendations.

### ollama_manager.py
Manages AI integration through Ollama. Handles error analysis, risk assessment, and monitoring.

### main_window.py
Main GUI application using PyQt6. Provides tabbed interface for driver management and system information.

## Adding New Features

### Adding a New Hardware Type

1. Add detection logic in `hardware_detector.py`:
```python
def _detect_new_hardware(self):
    # Detection logic
    return hardware_list
```

2. Call it from `detect_all()`:
```python
hardware.extend(self._detect_new_hardware())
```

3. Add driver finding logic in `driver_manager.py`:
```python
if hw_type == 'NewType':
    drivers.extend(self._find_new_drivers())
```

### Adding a New GUI Tab

1. Create tab method in `main_window.py`:
```python
def create_new_tab(self):
    tab = QWidget()
    layout = QVBoxLayout(tab)
    # Add widgets
    self.tabs.addTab(tab, "New Tab")
```

2. Call from `init_ui()`:
```python
self.create_new_tab()
```

## Testing

Run tests with:
```bash
python3 tests/test_basic.py
```

## Building

Create a Python package:
```bash
python3 setup.py sdist bdist_wheel
```

## Dependencies

- PyQt6: GUI framework
- psutil: System information
- requests: HTTP requests for Ollama
- pyyaml: Configuration parsing

## Privacy & Security

- All AI processing is local (Ollama on localhost)
- No data transmitted externally
- Only starcoder:3b model is used
- Configuration stored in ~/.config/driver-mgt/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request
