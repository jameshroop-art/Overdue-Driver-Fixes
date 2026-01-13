# Driver Operation Decoder & AI Training System

## Overview
Complete system for decoding driver operations and collecting training data for AI models.

## Components

### 1. Driver Operation Decoder (`src/utils/driver_operation_decoder.py`)

Decodes hardware information and translates it to driver operations.

**Features:**
- **PCI Device Decoding**: Decode PCI devices with vendor/device IDs to operations
- **USB Device Decoding**: Parse USB device information and capabilities
- **Driver Binary Analysis**: Extract metadata from kernel modules (.ko files)
- **Hardware-to-Command Translation**: Convert device info to executable commands
- **System-wide Scanning**: Scan all PCI devices and decode operations
- **Operation Details**: Get syscalls, kernel functions, and risk levels

**Example Usage:**
```python
from utils.driver_operation_decoder import DriverOperationDecoder

decoder = DriverOperationDecoder()

# Decode NVIDIA GPU
ops = decoder.translate_device_id_to_operations('10de', '1c03')
# Returns: ['gpu_memory_alloc', 'gpu_compute_execute', 'gpu_render_frame', ...]

# Scan all devices
devices = decoder.scan_all_devices()
for device in devices:
    print(f"{device['device']}: {device['operations']}")

# Get operation details
details = decoder.get_operation_details('gpu_memory_alloc')
# Returns: {'description': '...', 'syscalls': [...], 'risk_level': 'medium'}
```

### 2. Enhanced Driver Converter (`src/ai/driver_converter.py`)

Extended with driver process decoding capabilities.

**New Methods:**
- `decode_driver_process(driver_info, hardware)` - Decode driver processes
- `decode_running_driver_processes(driver_name)` - Analyze running modules

**Features:**
- Integrates with DriverOperationDecoder
- AI-enhanced process analysis
- Module information (size, usage, dependencies)
- Kernel thread detection
- Open file/device tracking
- Process recommendations

**Example Usage:**
```python
from ai.driver_converter import DriverConverter

converter = DriverConverter(config, ai_manager)

# Decode driver process
result = converter.decode_driver_process(driver_info, hardware_info)
print(result['decoded_operations'])
print(result['ai_insights'])

# Analyze running driver
info = converter.decode_running_driver_processes('nvidia')
print(f"Module loaded: {info['module_loaded']}")
print(f"Processes: {info['processes']}")
```

### 3. AI Training Data Collector (`src/utils/driver_training_data.py`)

Collects and exports driver operation data for AI model training.

**Storage:**
- SQLite database with 4 tables:
  - `driver_operations` - Driver operation samples
  - `devices` - Device information
  - `driver_conversions` - Conversion attempts
  - `driver_processes` - Process information

**Export Formats:**
- **JSON**: Complete dataset with metadata
- **CSV**: Separate CSV per table
- **JSONL**: ML-ready labeled pairs or feature vectors

**Features:**
- Automatic dataset generation from system scan
- Statistics and summaries
- Supervised learning format (input-output pairs)
- Unsupervised learning format (feature vectors)
- Session tracking

**Example Usage:**
```python
from utils.driver_training_data import DriverTrainingDataCollector
from utils.driver_operation_decoder import DriverOperationDecoder

collector = DriverTrainingDataCollector()
decoder = DriverOperationDecoder()

# Collect operation sample
operation = {
    'driver_name': 'nvidia',
    'hardware_type': 'GPU',
    'operation_name': 'gpu_memory_alloc',
    'operation_command': 'nvidia-smi --query-gpu=memory.used',
    'success': True
}
collector.collect_operation_sample(operation)

# Create dataset from system
summary = collector.create_training_dataset(decoder=decoder)
print(f"Created {summary['samples_created']} samples")

# Export for AI training
json_file = collector.export_to_json(table='all')
csv_files = collector.export_to_csv(table='all')
ml_file = collector.export_to_ml_format(format_type='labeled')

# Get statistics
stats = collector.get_statistics()
print(f"Success rate: {stats['operation_success_rate']:.2%}")
```

## AI Training Use Cases

### 1. Driver Operation Prediction
Train models to predict which operations a driver supports based on hardware.

**Input**: Device type, vendor, hardware ID
**Output**: List of supported operations

### 2. Hardware-to-Driver Mapping
Learn which drivers work with which hardware.

**Input**: Hardware specifications
**Output**: Compatible driver names and versions

### 3. Conversion Feasibility Prediction
Predict if a Windows driver can be converted to Linux.

**Input**: Driver metadata, source OS, hardware type
**Output**: Feasibility score, complexity, effort estimate

### 4. Operation Sequence Optimization
Learn optimal sequences of driver operations.

**Input**: Current state, desired outcome
**Output**: Sequence of operations to execute

### 5. Anomaly Detection
Detect unusual driver behavior or failures.

**Input**: Driver operations over time
**Output**: Anomaly scores, failure predictions

## Data Format Examples

### Labeled Training Data (JSONL)
```json
{
  "input": {
    "device": "NVIDIA GeForce GTX 1080",
    "type": "GPU",
    "vendor": "NVIDIA",
    "driver": "nvidia"
  },
  "output": {
    "operation": "gpu_memory_alloc",
    "command": "nvidia-smi --query-gpu=memory.used",
    "success": true
  }
}
```

### Feature Vector Format (JSONL)
```json
{
  "features": {
    "device_name": "Intel Wi-Fi 6 AX200",
    "device_type": "WiFi",
    "vendor": "Intel",
    "driver_name": "iwlwifi",
    "operation_name": "wifi_scan",
    "has_command": true,
    "success_rate": 1.0
  }
}
```

## Testing

Run the test suite:

```bash
# Test decoder
python3 tests/test_driver_decoder.py

# Test converter with decoding
python3 tests/test_converter_decode.py

# Test training data collection
python3 tests/test_training_data.py
```

## Architecture

```
Driver System
    ↓
DriverOperationDecoder
    ↓ (decodes)
Hardware Info → Operations & Commands
    ↓
DriverConverter (enhanced)
    ↓ (analyzes with AI)
Process Details & Insights
    ↓
DriverTrainingDataCollector
    ↓ (stores & exports)
AI Training Datasets (JSON/CSV/JSONL)
    ↓
AI Model Training
    ↓
Trained Models for:
- Operation prediction
- Driver mapping
- Conversion feasibility
- Anomaly detection
```

## Benefits

1. **Automated Decoding**: Automatically decode any hardware device to operations
2. **Process Understanding**: Deep insight into driver processes and behavior
3. **AI Training Ready**: Structured data in ML-friendly formats
4. **Comprehensive Coverage**: Operations, devices, conversions, processes
5. **Integration Ready**: Works with existing driver management system
6. **Extensible**: Easy to add new operation types and hardware support

## Future Enhancements

- Real-time operation monitoring
- Performance metrics collection
- Error pattern recognition
- Cross-driver compatibility analysis
- Automated driver selection based on ML models
