#!/bin/bash
# Standalone Installation Script for Decoder and Training System
# This script installs only the decoder and training components

set -e

echo "=============================================="
echo "Decoder & Training System Installation"
echo "=============================================="
echo ""

# Check if running in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "⚠ WARNING: You are running inside a virtual environment"
    echo "  Virtual environment: $VIRTUAL_ENV"
    echo ""
    read -p "Do you want to continue installation in this venv? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled. Please deactivate the venv and run again."
        echo "Run: deactivate"
        exit 1
    fi
    USE_EXISTING_VENV=true
else
    USE_EXISTING_VENV=false
    echo "✓ Not running in a virtual environment"
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installation directory: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Check for existing installation
INSTALL_DIR="/opt/decoder-training-system"
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "⚠ WARNING: Installation directory already exists: $INSTALL_DIR"
    
    # Check if venv exists
    if [ -d "$INSTALL_DIR/venv" ]; then
        echo "  • Existing virtual environment detected"
        echo "  • Location: $INSTALL_DIR/venv"
        
        # Check if venv is valid
        if [ -f "$INSTALL_DIR/venv/bin/python" ]; then
            VENV_VERSION=$("$INSTALL_DIR/venv/bin/python" --version 2>&1)
            echo "  • Python version: $VENV_VERSION"
            echo ""
            read -p "Reuse existing virtual environment? (Y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                echo "Removing existing installation..."
                rm -rf "$INSTALL_DIR"
                REUSE_VENV=false
            else
                echo "✓ Reusing existing virtual environment"
                REUSE_VENV=true
            fi
        else
            echo "  • Virtual environment appears corrupted"
            echo "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
            REUSE_VENV=false
        fi
    else
        echo ""
        read -p "Remove existing installation and reinstall? (Y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            rm -rf "$INSTALL_DIR"
            REUSE_VENV=false
        else
            echo "Installation cancelled."
            exit 1
        fi
    fi
else
    REUSE_VENV=false
fi

# Detect distribution and package manager
echo ""
echo "Detecting system configuration..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="$ID"
    DISTRO_VERSION="$VERSION_ID"
    echo "Detected: $PRETTY_NAME"
else
    DISTRO_ID="unknown"
    DISTRO_VERSION="unknown"
fi

if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
else
    echo "Unsupported package manager. Please install manually."
    exit 1
fi

echo "Detected package manager: $PKG_MANAGER"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing..."
    NEED_PYTHON_INSTALL=true
else
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Python version: $PYTHON_VERSION"
    
    # Check if venv module is available
    if ! python3 -m venv --help &> /dev/null 2>&1; then
        echo "⚠ python3-venv module not found"
        NEED_PYTHON_INSTALL=true
    else
        echo "✓ python3-venv module available"
        NEED_PYTHON_INSTALL=false
    fi
fi

# Install Python and dependencies if needed
if [ "$NEED_PYTHON_INSTALL" = true ]; then
    echo ""
    echo "Installing Python and system dependencies..."
    if [ "$PKG_MANAGER" = "apt" ]; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv python3-dev \
                           pciutils lshw dmidecode usbutils
    elif [ "$PKG_MANAGER" = "dnf" ]; then
        dnf install -y python3 python3-pip python3-devel pciutils dmidecode usbutils
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        pacman -S --noconfirm python python-pip pciutils dmidecode usbutils
    fi
else
    echo "✓ Python and venv already installed"
fi

echo ""
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying decoder and training system files..."
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/"
cp "$SCRIPT_DIR"/README.md "$INSTALL_DIR/" 2>/dev/null || true

# Create __init__.py if not exists
if [ ! -f "$INSTALL_DIR/__init__.py" ]; then
    cat > "$INSTALL_DIR/__init__.py" << 'EOF'
"""
Decoder and Training System Package
Provides driver operation decoding and AI training data collection
"""

from .driver_operation_decoder import DriverOperationDecoder
from .driver_training_data import DriverTrainingDataCollector

__all__ = [
    'DriverOperationDecoder',
    'DriverTrainingDataCollector'
]

__version__ = '1.0.0'
EOF
fi

# Handle virtual environment
if [ "$USE_EXISTING_VENV" = true ]; then
    echo ""
    echo "⚠ Using your current virtual environment"
    echo "  Virtual environment: $VIRTUAL_ENV"
    echo "  Skipping venv creation and activation"
    VENV_PYTHON="python3"
    VENV_PIP="pip3"
elif [ "$REUSE_VENV" = true ]; then
    echo ""
    echo "✓ Reusing existing virtual environment"
    echo "  Activating venv..."
    
    # Activate the existing venv
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "⚠ Warning: venv activation may have failed"
        echo "  Using direct path to venv executables"
        VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
        VENV_PIP="$INSTALL_DIR/venv/bin/pip"
    else
        echo "✓ Virtual environment activated: $VIRTUAL_ENV"
        VENV_PYTHON="python"
        VENV_PIP="pip"
    fi
else
    echo ""
    echo "Creating new virtual environment..."
    cd "$INSTALL_DIR"
    
    if ! python3 -m venv venv; then
        echo "✗ Virtual environment creation failed"
        echo "  Make sure python3-venv is installed"
        exit 1
    fi
    
    if [ ! -f "$INSTALL_DIR/venv/bin/python" ]; then
        echo "✗ Virtual environment creation failed"
        exit 1
    fi
    
    echo "✓ Virtual environment created successfully"
    
    # Activate the new venv
    echo "  Activating venv..."
    source venv/bin/activate
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "⚠ Warning: venv activation may have failed"
        echo "  Using direct path to venv executables"
        VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
        VENV_PIP="$INSTALL_DIR/venv/bin/pip"
    else
        echo "✓ Virtual environment activated: $VIRTUAL_ENV"
        VENV_PYTHON="python"
        VENV_PIP="pip"
    fi
    
    # Upgrade pip
    echo ""
    echo "Upgrading pip..."
    $VENV_PIP install --upgrade pip -q
fi

# Create requirements.txt
echo ""
echo "Creating requirements.txt..."
cat > "$INSTALL_DIR/requirements.txt" << 'EOF'
# Decoder and Training System dependencies
# All dependencies use built-in Python modules

# Optional: If you want to use with the main driver management system
# PyQt6>=6.4.0
# psutil>=5.9.0
# requests>=2.28.0
# pyyaml>=6.0

# Core dependencies (built-in, listed for documentation)
# - sqlite3 (built-in)
# - subprocess (built-in)  
# - pathlib (built-in)
# - json (built-in)
# - csv (built-in)
# - datetime (built-in)
# - hashlib (built-in)
# - re (built-in)
EOF

echo "✓ Requirements file created"

# Install any optional dependencies if in venv
if [ "$USE_EXISTING_VENV" = false ] && [ -n "$VIRTUAL_ENV" ]; then
    echo ""
    echo "Checking for optional dependencies..."
    # No required external dependencies for core functionality
    echo "✓ No additional packages needed (using Python built-ins)"
fi

echo ""
echo "Setting up Python path..."
# Create a simple wrapper script for easy usage
cat > "$INSTALL_DIR/decoder_cli.py" << 'EOF'
#!/usr/bin/env python3
"""
Command-line interface for Decoder and Training System
"""

import sys
import argparse
from pathlib import Path

# Add installation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from driver_operation_decoder import DriverOperationDecoder
from driver_training_data import DriverTrainingDataCollector


def main():
    parser = argparse.ArgumentParser(description='Decoder and Training System CLI')
    parser.add_argument('command', choices=['decode', 'scan', 'collect', 'export', 'stats'],
                       help='Command to execute')
    parser.add_argument('--vendor-id', help='Vendor ID for decode (e.g., 10de)')
    parser.add_argument('--device-id', help='Device ID for decode (e.g., 1c03)')
    parser.add_argument('--pci-address', help='PCI address (e.g., 0000:01:00.0)')
    parser.add_argument('--format', choices=['json', 'csv', 'ml'], default='json',
                       help='Export format')
    parser.add_argument('--output', help='Output directory for exports')
    
    args = parser.parse_args()
    
    decoder = DriverOperationDecoder()
    collector = DriverTrainingDataCollector()
    
    if args.command == 'decode':
        if args.vendor_id and args.device_id:
            ops = decoder.translate_device_id_to_operations(args.vendor_id, args.device_id)
            print(f"Operations for {args.vendor_id}:{args.device_id}:")
            for op in ops:
                print(f"  • {op}")
        elif args.pci_address:
            result = decoder.decode_pci_device(args.pci_address)
            print(f"Device: {result.get('device', 'Unknown')}")
            print(f"Vendor: {result.get('vendor', 'Unknown')}")
            print(f"Driver: {result.get('driver', 'None')}")
            print(f"Operations: {', '.join(result.get('operations', []))}")
        else:
            print("Error: Provide --vendor-id and --device-id, or --pci-address")
            sys.exit(1)
    
    elif args.command == 'scan':
        devices = decoder.scan_all_devices()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            if device.get('operations'):
                print(f"\n  {device.get('device', 'Unknown')}")
                print(f"    Driver: {device.get('driver', 'None')}")
                print(f"    Operations: {', '.join(device['operations'][:3])}...")
    
    elif args.command == 'collect':
        summary = collector.create_training_dataset(decoder=decoder)
        print(f"Collection Summary:")
        print(f"  Devices Scanned: {summary['devices_scanned']}")
        print(f"  Operations Collected: {summary['operations_collected']}")
        print(f"  Total Samples: {summary['samples_created']}")
    
    elif args.command == 'export':
        if args.format == 'json':
            file_path = collector.export_to_json(table='all')
            print(f"Exported to: {file_path}")
        elif args.format == 'csv':
            files = collector.export_to_csv(output_dir=args.output, table='all')
            print(f"Exported {len(files)} CSV files:")
            for f in files:
                print(f"  • {f}")
        elif args.format == 'ml':
            labeled = collector.export_to_ml_format(format_type='labeled')
            features = collector.export_to_ml_format(format_type='features')
            print(f"Exported ML datasets:")
            print(f"  • Labeled: {labeled}")
            print(f"  • Features: {features}")
    
    elif args.command == 'stats':
        stats = collector.get_statistics()
        print("Training Data Statistics:")
        print(f"  Total Samples: {stats['samples_collected']}")
        print(f"  Driver Operations: {stats['tables']['driver_operations']}")
        print(f"  Devices: {stats['tables']['devices']}")
        print(f"  Unique Drivers: {stats['unique_drivers']}")
        print(f"  Unique Hardware Types: {stats['unique_hardware_types']}")
        print(f"  Operation Success Rate: {stats['operation_success_rate']:.2%}")


if __name__ == '__main__':
    main()
EOF

chmod +x "$INSTALL_DIR/decoder_cli.py"

# Create symlink for easy access
ln -sf "$INSTALL_DIR/decoder_cli.py" /usr/local/bin/decoder-cli

echo ""
echo "Running validation tests..."
if "$VENV_PYTHON" "$INSTALL_DIR/decoder_cli.py" --help > /dev/null 2>&1; then
    echo "✓ CLI tool validated"
else
    echo "⚠ Warning: CLI validation had issues"
fi

# Test imports
echo ""
echo "Testing module imports..."
if "$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from driver_operation_decoder import DriverOperationDecoder
from driver_training_data import DriverTrainingDataCollector
decoder = DriverOperationDecoder()
collector = DriverTrainingDataCollector()
print('✓ All modules imported successfully')
" 2>&1; then
    echo "✓ Module import test passed"
else
    echo "✗ Module import test failed"
    exit 1
fi

# Test basic functionality
echo ""
echo "Testing basic decoder functionality..."
if "$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from driver_operation_decoder import DriverOperationDecoder
decoder = DriverOperationDecoder()
ops = decoder.translate_device_id_to_operations('10de', '1c03')
if ops and len(ops) > 0:
    print(f'✓ Decoder test passed ({len(ops)} operations decoded)')
else:
    print('✗ Decoder returned no operations')
    sys.exit(1)
" 2>&1; then
    echo "✓ Decoder functionality test passed"
else
    echo "⚠ Warning: Decoder test had issues"
fi

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
if [ "$USE_EXISTING_VENV" = true ]; then
    echo "Using: Your current virtual environment"
    echo "  Virtual environment: $VIRTUAL_ENV"
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment: $VIRTUAL_ENV (ACTIVATED)"
    echo "  Note: Venv is currently active in this shell"
else
    echo "Virtual environment: $INSTALL_DIR/venv"
    echo "  Note: Venv was activated during installation"
fi
echo ""
echo "Usage:"
echo "  decoder-cli decode --vendor-id 10de --device-id 1c03"
echo "  decoder-cli scan"
echo "  decoder-cli collect"
echo "  decoder-cli export --format json"
echo "  decoder-cli stats"
echo ""
if [ "$USE_EXISTING_VENV" = false ]; then
    echo "To activate the venv in a new shell:"
    echo "  source $INSTALL_DIR/venv/bin/activate"
    echo ""
    echo "Or use Python directly:"
    echo "  $INSTALL_DIR/venv/bin/python"
    echo "  >>> import sys"
    echo "  >>> sys.path.insert(0, '$INSTALL_DIR')"
    echo "  >>> from driver_operation_decoder import DriverOperationDecoder"
    echo "  >>> decoder = DriverOperationDecoder()"
    echo ""
fi
echo "Training data location:"
echo "  ~/.config/driver-mgt/training-data/"
echo ""
echo "Documentation:"
echo "  $INSTALL_DIR/README.md"
echo ""
if [ "$REUSE_VENV" = true ]; then
    echo "Note: Reused existing virtual environment"
    echo "  To reinstall with a fresh venv, remove $INSTALL_DIR and run again"
    echo ""
fi
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Current Status:"
    echo "  ✓ Virtual environment is active in this shell"
    echo "  Python: $(which python)"
    echo "  Pip: $(which pip)"
    echo ""
fi

