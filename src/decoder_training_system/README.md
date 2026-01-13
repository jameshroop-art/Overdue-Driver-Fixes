# Decoder and Training System

## Overview
This directory contains the Driver Operation Decoder and AI Training Data Collection system for the driver management application.

## Structure

```
decoder_training_system/
├── __init__.py                     # Package initialization
├── driver_operation_decoder.py     # Hardware-to-operation decoder
├── driver_training_data.py         # AI training data collector
└── integration.py                  # Integration with main application
```

## Components

### 1. DriverOperationDecoder (`driver_operation_decoder.py`)
Decodes hardware devices to driver operations.

**Features:**
- Decode PCI/USB devices
- Translate vendor:device IDs to operations
- Convert hardware info to driver commands
- Scan all system devices
- Provide operation details (syscalls, kernel functions, risk levels)

### 2. DriverTrainingDataCollector (`driver_training_data.py`)
Collects and exports driver operation data for AI model training.

**Features:**
- SQLite database storage
- Multiple export formats (JSON, CSV, JSONL)
- ML-ready labeled datasets
- Feature vectors for unsupervised learning
- Statistics and summaries

### 3. DecoderTrainingIntegration (`integration.py`)
Integrates decoder and training system with existing driver management programs.

**Features:**
- Seamless integration with DriverManager
- Automatic data collection during operations
- Export capabilities for training data
- Statistics and monitoring

## Installation

The system is automatically installed via `install.sh`:

```bash
sudo ./install.sh
```

The installation:
1. Creates `/opt/driver-mgt/` directory
2. Copies all source files including `decoder_training_system/`
3. Sets up Python virtual environment
4. Installs all dependencies (requirements.txt)
5. Validates decoder and training system functionality

## Dependencies

All dependencies are included in `requirements.txt` and installed in the venv:
- Python 3.9+ built-in modules (sqlite3, subprocess, pathlib, json, csv, etc.)
- PyQt6 (for GUI integration)
- psutil (for system monitoring)
- requests (for network operations)
- pyyaml (for configuration)

## Usage

### Basic Usage

```python
from decoder_training_system import DriverOperationDecoder, DriverTrainingDataCollector
from decoder_training_system.integration import create_integration

# Create integration instance
integration = create_integration(config_manager, ai_manager)

# Decode hardware
hardware_info = {'name': 'NVIDIA GPU', 'type': 'GPU', 'vendor_id': '10de', 'device_id': '1c03'}
result = integration.decode_hardware(hardware_info)
print(result['operations'])  # ['gpu_memory_alloc', 'gpu_render_frame', ...]

# Collect training data
integration.decode_and_collect(hardware_info, driver_info)

# Export training data
exported = integration.export_training_data(formats=['json', 'csv', 'ml'])
print(f"Exported files: {exported['files']}")

# Get statistics
stats = integration.get_statistics()
print(f"Total samples: {stats['samples_collected']}")
```

### Integration with Driver Manager

The system automatically integrates with the existing driver management system:

```python
from core.driver_manager import DriverManager
from decoder_training_system.integration import create_integration

driver_manager = DriverManager(config)
integration = create_integration(config, ai_manager)

# When a driver is installed, automatically decode and collect data
hardware = driver_manager.detect_hardware()
for hw in hardware:
    integration.decode_and_collect(hw)

# Export collected data
integration.export_training_data()
```

## Testing

Run the test suites:

```bash
# Test decoder
python3 tests/test_driver_decoder.py

# Test training data collection
python3 tests/test_training_data.py

# Test converter with decoding
python3 tests/test_converter_decode.py
```

## AI Training Use Cases

1. **Driver Operation Prediction**: Train models to predict operations from hardware
2. **Hardware-to-Driver Mapping**: Learn which drivers work with which hardware
3. **Conversion Feasibility**: Predict if drivers can be converted between OSes
4. **Operation Sequence Optimization**: Learn optimal operation sequences
5. **Anomaly Detection**: Detect unusual driver behavior

## Data Formats

### JSON Format
```json
{
  "metadata": {...},
  "driver_operations": [...],
  "devices": [...],
  "driver_conversions": [...],
  "driver_processes": [...]
}
```

### ML-Ready Format (JSONL)
```json
{"input": {"device": "...", "type": "GPU"}, "output": {"operation": "...", "command": "..."}}
```

## Files Location After Installation

- **Installation Directory**: `/opt/driver-mgt/`
- **Decoder System**: `/opt/driver-mgt/src/decoder_training_system/`
- **Training Data**: `~/.config/driver-mgt/training-data/`
- **Exported Data**: `~/.config/driver-mgt/training-data/` (JSON/CSV/JSONL files)
- **Database**: `~/.config/driver-mgt/training-data/training_data.db`

## Configuration

The system uses the main application's configuration. Training data location can be customized:

```python
collector = DriverTrainingDataCollector(data_dir='/custom/path')
```

## Maintenance

### Clear Training Data
```python
import os
import shutil
training_dir = os.path.expanduser('~/.config/driver-mgt/training-data')
shutil.rmtree(training_dir)
```

### Backup Training Data
```bash
cp -r ~/.config/driver-mgt/training-data ~/driver-training-backup
```

## Support

For issues or questions:
1. Check test files for usage examples
2. See `DRIVER_DECODER_AI_TRAINING.md` in repository root
3. Review integration.py for integration examples
