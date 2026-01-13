#!/bin/bash
# Installation script for driver-mgt
# Advanced Linux Driver & Hardware Management System

set -e

# Configuration constants
MAX_NETWORK_DEVICES_DISPLAY=3  # Maximum number of network devices to display during install

echo "====================================="
echo "driver-mgt Installation"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Load shared utilities if available
if [ -f "$SCRIPT_DIR/utils.sh" ]; then
    source "$SCRIPT_DIR/utils.sh"
fi

# Detect distribution and package manager
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

# Early venv creation in development mode (before system packages)
# This ensures venv exists for testing even if installation is interrupted
if [ -d "$SCRIPT_DIR/src" ] && [ -f "$SCRIPT_DIR/driver-mgt" ]; then
    echo "Development mode detected - creating venv in repository..."
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        python3 -m venv "$SCRIPT_DIR/venv" || {
            echo "⚠ Warning: Could not create venv in repository"
            echo "  Will create it in /opt/driver-mgt during installation"
        }
        
        if [ -d "$SCRIPT_DIR/venv" ]; then
            echo "✓ Repository venv created"
            # Install requirements in repo venv for development
            "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip -q
            "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q && \
                echo "✓ Development dependencies installed in repo venv"
        fi
    else
        echo "✓ Repository venv already exists"
    fi
    echo ""
fi

# Install Python and pip
echo "Installing Python and dependencies..."
if [ "$PKG_MANAGER" = "apt" ]; then
    # Fix missing GPG keys for Ubuntu repositories (if Ubuntu repos are configured)
    # Check if Ubuntu repositories are configured in sources
    if grep -rq "archive.ubuntu.com\|security.ubuntu.com" /etc/apt/sources.list* 2>/dev/null; then
        echo "Ubuntu repositories detected. Ensuring GPG keys are present..."
        
        # Import Ubuntu archive signing keys if missing
        # These keys are needed for Ubuntu focal and other releases
        UBUNTU_KEYS=("3B4FE6ACC0B21F32" "871920D1991BC93C")
        
        for key in "${UBUNTU_KEYS[@]}"; do
            # Check if key already exists
            KEY_EXISTS=false
            if apt-key list 2>/dev/null | grep -q "$key"; then
                KEY_EXISTS=true
            # Also check new keyring location if it exists
            elif [ -f /usr/share/keyrings/ubuntu-archive-keyring.gpg ] && \
                 gpg --no-default-keyring --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg --list-keys 2>/dev/null | grep -q "$key"; then
                KEY_EXISTS=true
            fi
            
            if [ "$KEY_EXISTS" = false ]; then
                echo "Importing Ubuntu key: $key"
                # Try multiple keyservers in case one is down
                KEYSERVERS=("keyserver.ubuntu.com" "keys.openpgp.org" "pgp.mit.edu")
                KEY_IMPORTED=false
                
                for keyserver in "${KEYSERVERS[@]}"; do
                    # Try apt-key method (works on most systems)
                    if command -v apt-key &> /dev/null; then
                        if apt-key adv --keyserver "hkp://$keyserver:80" --recv-keys "$key" 2>/dev/null; then
                            echo "✓ Successfully imported key $key from $keyserver"
                            KEY_IMPORTED=true
                            break
                        fi
                    fi
                    
                    # Try modern gpg method if keyring exists
                    if [ -f /usr/share/keyrings/ubuntu-archive-keyring.gpg ] && command -v gpg &> /dev/null; then
                        if gpg --no-default-keyring --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg \
                            --keyserver "hkp://$keyserver:80" --recv-keys "$key" 2>/dev/null; then
                            echo "✓ Successfully imported key $key from $keyserver"
                            KEY_IMPORTED=true
                            break
                        fi
                    fi
                done
                
                if [ "$KEY_IMPORTED" = false ]; then
                    echo "⚠ Warning: Could not import key $key from any keyserver"
                    echo "  This may cause repository signature verification warnings"
                    echo "  You can manually import with: sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $key"
                fi
            else
                echo "✓ Key $key already present"
            fi
        done
    fi
    
    apt-get update
    
    # Determine which OpenGL library package to use
    # Ubuntu 24.04+ and newer Debian versions replaced libgl1-mesa-glx with libgl1
    if type detect_opengl_package &>/dev/null; then
        OPENGL_PKG=$(detect_opengl_package)
        if [ "$OPENGL_PKG" = "libgl1-mesa-glx" ]; then
            echo "Using libgl1-mesa-glx for OpenGL support"
        else
            echo "Note: libgl1-mesa-glx not available (obsolete in Ubuntu 24.04+)"
            echo "Using libgl1 instead"
        fi
    else
        # Fallback if utils.sh not loaded
        OPENGL_PKG="libgl1"
        if apt-cache show libgl1-mesa-glx 2>/dev/null | grep -q "^Package: libgl1-mesa-glx"; then
            OPENGL_PKG="libgl1-mesa-glx"
            echo "Using libgl1-mesa-glx for OpenGL support"
        else
            echo "Note: libgl1-mesa-glx not available (obsolete in Ubuntu 24.04+)"
            echo "Using libgl1 instead"
        fi
    fi
    
    # Debian 12 (Bookworm) specific packages
    # PEP 668 compliance requires python3-venv for proper isolation
    if [ "$DISTRO_ID" = "debian" ] && [ "$DISTRO_VERSION" = "12" ]; then
        echo "Detected Debian 12 (Bookworm) - installing required packages..."
        apt-get install -y python3 python3-pip python3-venv python3-dev \
                           build-essential pciutils lshw dmidecode \
                           libssl-dev libbz2-dev liblzma-dev libsqlite3-dev \
                           libreadline-dev libgdbm-dev libffi-dev \
                           $OPENGL_PKG libxkbcommon-x11-0 libxcb-xinerama0 \
                           libxcb-cursor0 libegl1
    else
        # General Debian/Ubuntu packages
        apt-get install -y python3 python3-pip python3-venv pciutils lshw dmidecode \
                           libssl-dev libbz2-dev liblzma-dev libsqlite3-dev \
                           libreadline-dev libgdbm-dev libffi-dev \
                           $OPENGL_PKG libxkbcommon-x11-0 libxcb-xinerama0 \
                           libxcb-cursor0 libegl1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python version: $PYTHON_VERSION"
    
elif [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y python3 python3-pip python3-devel gcc pciutils dmidecode \
                   openssl-devel bzip2-devel xz-devel sqlite-devel \
                   readline-devel gdbm-devel libffi-devel \
                   libxcb xcb-util-cursor libxkbcommon-x11 mesa-libEGL
elif [ "$PKG_MANAGER" = "pacman" ]; then
    pacman -S --noconfirm python python-pip base-devel pciutils dmidecode \
                          openssl bzip2 xz sqlite readline gdbm libffi \
                          libxcb xcb-util-cursor libxkbcommon-x11 libglvnd
fi

echo ""
echo "Creating configuration directories..."
mkdir -p /etc/driver-mgt
mkdir -p /root/driver-backups
chmod 755 /root/driver-backups

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

# Create user config directories as the actual user
su - "$ACTUAL_USER" -c "mkdir -p $ACTUAL_HOME/.config/driver-mgt/{profiles,curves,logs,corrections,reports,backups}"

echo ""
echo "Installing driver-mgt..."

# Verify required files exist
echo "Verifying required files..."
REQUIRED_FILES=("src" "config" "driver-mgt" "driver-mgt.py" "requirements.txt" "setup.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "✗ Error: Required files/directories not found:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Current directory: $(pwd)"
    echo "Please run this script from the driver-mgt repository root directory."
    exit 1
fi

echo "✓ All required files found"

INSTALL_DIR="/opt/driver-mgt"
mkdir -p "$INSTALL_DIR"
cp -r src config driver-mgt driver-mgt.py requirements.txt setup.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/driver-mgt"
chmod +x "$INSTALL_DIR/driver-mgt.py"

echo ""
echo "Creating virtual environment..."
cd "$INSTALL_DIR"

# Debian 12 uses PEP 668 - ensure we're creating a proper venv
# This avoids "externally-managed-environment" errors
echo "Python version: $(python3 --version)"
echo "Creating venv at: $INSTALL_DIR/venv"

if ! python3 -m venv venv; then
    echo "✗ Failed to create virtual environment"
    echo "  This might be due to missing python3-venv package"
    echo "  On Debian 12: sudo apt-get install python3-venv"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/venv/bin/python" ]; then
    echo "✗ Virtual environment created but Python not found"
    exit 1
fi

echo "✓ Virtual environment created successfully"
echo "  Location: $INSTALL_DIR/venv"
echo "  Python: $INSTALL_DIR/venv/bin/python ($(\"$INSTALL_DIR/venv/bin/python\" --version))"

echo ""
echo "Activating virtual environment and installing Python packages..."

# Activate the venv before installing packages
source "$INSTALL_DIR/venv/bin/activate"

# Verify we're in the venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Warning: Virtual environment activation may have failed"
    echo "  Will use direct venv Python executable for installation..."
fi

# Upgrade pip in the venv
echo "Upgrading pip..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip

# Install requirements
echo "Installing Python packages from requirements.txt..."
if ! "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"; then
    echo "✗ Failed to install Python packages"
    deactivate 2>/dev/null || true
    exit 1
fi

echo ""
echo "Verifying installation..."
if ! "$INSTALL_DIR/venv/bin/python" -c "import PyQt6, psutil, requests, yaml" 2>/dev/null; then
    echo "⚠ Warning: Some dependencies may not be properly installed"
    echo "  Attempting to install again..."
    "$INSTALL_DIR/venv/bin/pip" install --force-reinstall -r "$INSTALL_DIR/requirements.txt"
    
    # Verify again after reinstall
    if ! "$INSTALL_DIR/venv/bin/python" -c "import PyQt6, psutil, requests, yaml" 2>/dev/null; then
        echo "✗ Failed to verify Python dependencies after reinstall"
        echo "  You may need to install system packages for PyQt6:"
        echo "  - For Qt libraries: libxcb-xinerama0, libxcb-cursor0, libxkbcommon-x11-0"
        echo "  - For OpenGL: libgl1 or libgl1-mesa-glx, libegl1"
        deactivate 2>/dev/null || true
        exit 1
    fi
fi

echo "✓ All Python packages installed and verified"

# Deactivate venv (we'll activate it via wrapper scripts)
deactivate 2>/dev/null || true

# Create symlink
ln -sf "$INSTALL_DIR/driver-mgt" /usr/local/bin/driver-mgt

echo ""
echo "Installing Ollama AI service..."

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama already installed"
else
    echo "Installing Ollama..."
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        echo "✓ Ollama installed successfully"
    else
        echo "⚠ Warning: Ollama installation may have failed"
        echo "  You can manually install Ollama from: https://ollama.ai"
    fi
fi

echo ""
echo "Setting up Ollama AI authentication..."

# Start Ollama service if not running
if ! systemctl is-active --quiet ollama 2>/dev/null; then
    echo "Starting Ollama service..."
    systemctl start ollama 2>/dev/null || echo "Note: Run 'systemctl start ollama' manually if needed"
    sleep 3
fi

# Prompt for Ollama sign-in (required for starcoder:3b)
if command -v ollama &> /dev/null; then
    echo ""
    echo "============================================"
    echo "Ollama Sign-In Required"
    echo "============================================"
    echo "The starcoder:3b model requires authentication."
    echo "This will open your browser for Google sign-in."
    echo ""
    read -p "Sign in to Ollama now? (Y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "Opening browser for Google authentication..."
        echo "Please complete the sign-in process in your browser."
        echo ""
        
        # Run ollama signin as the actual user (not root)
        if su - "$ACTUAL_USER" -c "ollama signin"; then
            echo "✓ Successfully signed in to Ollama"
        else
            echo "⚠ Warning: Sign-in may have failed"
            echo "  You can sign in later with: ollama signin"
        fi
    else
        echo "Skipping sign-in. You can sign in later with: ollama signin"
    fi
fi

echo ""
echo "Pulling starcoder:3b AI model..."

# Pull starcoder:3b model
if command -v ollama &> /dev/null; then
    echo "Pulling starcoder:3b model (this may take several minutes)..."
    if su - "$ACTUAL_USER" -c "ollama pull starcoder:3b"; then
        echo "✓ starcoder:3b model installed successfully"
    else
        echo "⚠ Warning: Failed to pull starcoder:3b model"
        echo "  This may be due to authentication requirement."
        echo "  Sign in with: ollama signin"
        echo "  Then pull manually with: ollama pull starcoder:3b"
    fi
else
    echo "⚠ Ollama not available, skipping model pull"
    echo "  Install Ollama and run: ollama signin && ollama pull starcoder:3b"
fi

echo ""
echo "============================================"
echo "Alternative AI Backend: LM Studio"
echo "============================================"
echo "driver-mgt supports LM Studio as an alternative to Ollama."
echo ""
echo "LM Studio Features:"
echo "  ✓ Easy-to-use graphical interface"
echo "  ✓ Download models from online repositories"
echo "  ✓ OpenAI-compatible API on localhost"
echo "  ✓ No authentication required"
echo "  ✓ GPU acceleration support"
echo ""
echo "For detailed installation and setup instructions, see:"
echo "  📖 LMSTUDIO_SETUP.md"
echo ""
echo "Quick installation:"
echo "  wget https://lmstudio.ai/download/latest/linux/x64 -O lm-studio.AppImage"
echo "  chmod +x lm-studio.AppImage"
echo "  ./lm-studio.AppImage"
echo ""
read -p "Would you like to view the LM Studio setup guide now? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v less &> /dev/null; then
        less "$SCRIPT_DIR/LMSTUDIO_SETUP.md"
    elif command -v more &> /dev/null; then
        more "$SCRIPT_DIR/LMSTUDIO_SETUP.md"
    else
        cat "$SCRIPT_DIR/LMSTUDIO_SETUP.md"
    fi
    echo ""
    echo "Press Enter to continue installation..."
    read
else
    echo "You can read the guide anytime: cat LMSTUDIO_SETUP.md"
    echo "Or online: https://github.com/jameshroop-art/driver-mgt/blob/main/LMSTUDIO_SETUP.md"
fi

echo ""
echo "Creating desktop entry..."
cat > /usr/share/applications/driver-mgt.desktop <<EOF
[Desktop Entry]
Type=Application
Name=driver-mgt
Comment=Advanced Linux Driver Management
Exec=pkexec env DISPLAY=\$DISPLAY XAUTHORITY=\$XAUTHORITY /usr/local/bin/driver-mgt
Icon=preferences-system
Terminal=true
Categories=System;Settings;
EOF

echo ""
echo "Creating LLM Studio desktop launcher..."
# Copy the LLM Studio wrapper script
cp "$SCRIPT_DIR/driver-mgt-lmstudio" /usr/local/bin/driver-mgt-lmstudio
chmod +x /usr/local/bin/driver-mgt-lmstudio

# Install the desktop entry
cp "$SCRIPT_DIR/driver-mgt-lmstudio.desktop" /usr/share/applications/driver-mgt-lmstudio.desktop
chmod 644 /usr/share/applications/driver-mgt-lmstudio.desktop

echo "✓ LLM Studio launcher installed"
echo "  Desktop entry: /usr/share/applications/driver-mgt-lmstudio.desktop"
echo "  Wrapper script: /usr/local/bin/driver-mgt-lmstudio"

echo ""
echo "Installation complete!"
echo ""
echo "A virtual environment has been created at $INSTALL_DIR/venv"
echo "The application will automatically use this venv when started."
echo ""

# Test the installation
echo "Testing installation..."
if "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/driver-mgt" --check-deps --no-venv --no-keep-open >/dev/null 2>&1; then
    echo "✓ Installation verified successfully"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 1 ]; then
        # Exit codes 0 or 1 are acceptable (0=success, 1=some missing but not critical)
        echo "✓ Installation completed (check with: driver-mgt --check-deps)"
    else
        echo "⚠ Warning: Installation verification had issues"
        echo "  You can manually check with: driver-mgt --check-deps"
    fi
fi

echo ""
echo "Running backup and timer validation tests..."
# Test backup and timer functionality in single Python execution
if "$INSTALL_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/src')
from utils.driver_backup import DriverBackupManager
from utils.driver_test_timer import DriverTestTimer
import tempfile

print('=' * 50)
print('BACKUP SYSTEM VALIDATION')
print('=' * 50)
with tempfile.TemporaryDirectory() as tmpdir:
    backup_mgr = DriverBackupManager(backup_dir=tmpdir)
    
    # Test 1: None hardware name
    test_hw = {'name': None, 'type': 'GPU', 'vendor': 'Test'}
    test_drv = {'name': 'test-driver', 'version': '1.0'}
    try:
        backup_mgr.create_backup(test_hw, test_drv)
        print('✓ Backup handles None hardware name')
    except AttributeError as e:
        print(f'✗ Backup failed with None hardware: {e}')
        sys.exit(1)
    
    # Test 2: None driver name
    test_hw2 = {'name': 'Test Device', 'type': 'GPU'}
    test_drv2 = {'name': None, 'version': '1.0'}
    try:
        backup_mgr.create_backup(test_hw2, test_drv2)
        print('✓ Backup handles None driver name')
    except AttributeError as e:
        print(f'✗ Backup failed with None driver: {e}')
        sys.exit(1)
    
    # Test 3: get_latest_backup with None
    try:
        backup_mgr.get_latest_backup({'name': None})
        print('✓ get_latest_backup handles None')
    except AttributeError as e:
        print(f'✗ get_latest_backup failed: {e}')
        sys.exit(1)
    
    # Test 4: list_backups with None
    try:
        backup_mgr.list_backups({'name': None})
        print('✓ list_backups handles None')
    except AttributeError as e:
        print(f'✗ list_backups failed: {e}')
        sys.exit(1)

print('✓ All backup tests passed')
print('')

print('=' * 50)
print('TIMER SYSTEM VALIDATION')
print('=' * 50)
# Test initialization
timer = DriverTestTimer(test_duration_minutes=5)
if timer.test_duration_minutes != 5:
    print('✗ Timer initialization failed - duration not set correctly')
    sys.exit(1)
if timer.test_duration_seconds != 300:
    print('✗ Timer initialization failed - duration in seconds incorrect')
    sys.exit(1)
print('✓ Timer initialized correctly')

# Test timer state
if timer.is_test_active():
    print('✗ Timer should not be active initially')
    sys.exit(1)
print('✓ Timer state check works')

# Test remaining time when not active
minutes, seconds = timer.get_remaining_time()
if minutes != 0 or seconds != 0:
    print('✗ Remaining time should be (0,0) when not active')
    sys.exit(1)
print('✓ Remaining time calculation works')

print('✓ All timer tests passed')
print('')
print('=' * 50)
print('ALL VALIDATION TESTS PASSED')
print('=' * 50)
" 2>&1; then
    echo "✓ Backup and timer systems validated"
else
    echo "⚠ Warning: Validation tests failed"
    echo "  The backup or timer system may have issues"
fi

echo ""
echo "Checking current active drivers..."
# Backup directory already created during configuration setup

echo ""
echo "Testing Decoder and Training System..."
# Test decoder_training_system integration
if "$INSTALL_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/src')

print('=' * 50)
print('DECODER & TRAINING SYSTEM VALIDATION')
print('=' * 50)

# Test 1: Import modules
try:
    from decoder_training_system import DriverOperationDecoder, DriverTrainingDataCollector
    print('✓ Decoder and Training modules imported')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)

# Test 2: Initialize decoder
try:
    decoder = DriverOperationDecoder()
    print('✓ DriverOperationDecoder initialized')
except Exception as e:
    print(f'✗ Decoder initialization failed: {e}')
    sys.exit(1)

# Test 3: Initialize collector
try:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = DriverTrainingDataCollector(data_dir=tmpdir)
        print('✓ DriverTrainingDataCollector initialized')
except Exception as e:
    print(f'✗ Collector initialization failed: {e}')
    sys.exit(1)

# Test 4: Test integration module
try:
    from decoder_training_system.integration import DecoderTrainingIntegration, create_integration
    print('✓ Integration module loaded')
except ImportError as e:
    print(f'✗ Integration import failed: {e}')
    sys.exit(1)

# Test 5: Test basic decoding
try:
    decoder = DriverOperationDecoder()
    ops = decoder.translate_device_id_to_operations('10de', '1c03')
    if ops and len(ops) > 0:
        print(f'✓ Device ID decoding works ({len(ops)} operations found)')
    else:
        print('✗ Device ID decoding returned empty results')
        sys.exit(1)
except Exception as e:
    print(f'✗ Decoding test failed: {e}')
    sys.exit(1)

print('')
print('✓ All decoder & training system tests passed')
print('=' * 50)
" 2>&1; then
    echo "✓ Decoder and Training System validated"
else
    echo "⚠ Warning: Decoder and Training System tests had issues"
    echo "  System will still function but training features may be limited"
fi

echo ""
echo "Checking current active drivers..."
# Backup directory already created during configuration setup

# Check and list current active drivers
"$INSTALL_DIR/venv/bin/python" -c "
import sys
import subprocess
import re

MAX_NET_DEVICES = $MAX_NETWORK_DEVICES_DISPLAY

print('Scanning for active drivers...')
print('')

# Check GPU drivers
gpu_info = []
try:
    lspci_out = subprocess.check_output(['lspci', '-k'], text=True)
    gpu_section = ''
    capture = False
    for line in lspci_out.split('\n'):
        if 'VGA' in line or '3D' in line or 'Display' in line:
            capture = True
            gpu_section = line + '\n'
        elif capture:
            if line and not line.startswith('\t'):
                # End of this device section
                gpu_info.append(gpu_section)
                gpu_section = ''
                capture = False
            else:
                gpu_section += line + '\n'
    if gpu_section:
        gpu_info.append(gpu_section)
except Exception as e:
    print(f'⚠ Could not check GPU drivers: {e}')

if gpu_info:
    print('GPU Drivers:')
    for gpu in gpu_info:
        lines = gpu.strip().split('\n')
        device_line = lines[0] if lines else ''
        print(f'  • {device_line}')
        for line in lines[1:]:
            if 'Kernel driver in use' in line:
                driver = line.split(':')[-1].strip()
                print(f'    → Driver: {driver}')
else:
    print('  No GPU devices detected')

print('')

# Check network drivers
net_info = []
try:
    lspci_out = subprocess.check_output(['lspci', '-k'], text=True)
    net_section = ''
    capture = False
    for line in lspci_out.split('\n'):
        if 'Network' in line or 'Ethernet' in line or 'Wireless' in line:
            capture = True
            net_section = line + '\n'
        elif capture:
            if line and not line.startswith('\t'):
                net_info.append(net_section)
                net_section = ''
                capture = False
            else:
                net_section += line + '\n'
    if net_section:
        net_info.append(net_section)
except Exception as e:
    print(f'⚠ Could not check network drivers: {e}')

if net_info:
    print('Network Drivers:')
    for net in net_info[:MAX_NET_DEVICES]:  # Use configurable limit
        lines = net.strip().split('\n')
        device_line = lines[0] if lines else ''
        print(f'  • {device_line}')
        for line in lines[1:]:
            if 'Kernel driver in use' in line:
                driver = line.split(':')[-1].strip()
                print(f'    → Driver: {driver}')
else:
    print('  No network devices detected')

print('')
print('✓ Driver scan complete')
print('  You can view detailed driver info in the GUI')
" 2>&1 || echo "⚠ Could not scan drivers (this is normal on some systems)"

echo ""
echo "You can now run driver-mgt with:"
echo "  driver-mgt         (GUI mode with Ollama)"
echo "  driver-mgt status  (CLI mode)"
echo ""
echo "Or use the LLM Studio launcher:"
echo "  driver-mgt-lmstudio         (Command line)"
echo "  Desktop launcher available in applications menu: 'Driver Manager (LLM Studio)'"
echo "  Note: LLM Studio must be running on http://localhost:1234 before using this launcher"
echo ""
echo "Configuration files are stored in:"
echo "  $ACTUAL_HOME/.config/driver-mgt/"
echo ""
echo "AI Features:"
echo "  Ollama service: $(command -v ollama &> /dev/null && echo 'Installed' || echo 'Not installed')"
echo "  starcoder:3b model: $(ollama list 2>/dev/null | grep -q starcoder && echo 'Available' || echo 'Not pulled')"
echo "  LLM Studio launcher: Installed (requires LLM Studio to be running separately)"
echo "  AI monitoring and chat interface available in GUI"
echo ""
