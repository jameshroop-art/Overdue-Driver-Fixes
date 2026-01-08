#!/bin/bash
# Installation script for driver-mgt
# Advanced Linux Driver & Hardware Management System

set -e

echo "====================================="
echo "driver-mgt Installation"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script must be run as root (use sudo)"
    exit 1
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

# Install Python and pip
echo "Installing Python and dependencies..."
if [ "$PKG_MANAGER" = "apt" ]; then
    apt-get update
    
    # Debian 12 (Bookworm) specific packages
    # PEP 668 compliance requires python3-venv for proper isolation
    if [ "$DISTRO_ID" = "debian" ] && [ "$DISTRO_VERSION" = "12" ]; then
        echo "Detected Debian 12 (Bookworm) - installing required packages..."
        apt-get install -y python3 python3-pip python3-venv python3-dev \
                           build-essential pciutils lshw dmidecode \
                           libgl1-mesa-glx libxkbcommon-x11-0 libxcb-xinerama0
    else
        # General Debian/Ubuntu packages
        apt-get install -y python3 python3-pip python3-venv pciutils lshw dmidecode
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python version: $PYTHON_VERSION"
    
elif [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y python3 python3-pip python3-devel gcc pciutils dmidecode
elif [ "$PKG_MANAGER" = "pacman" ]; then
    pacman -S --noconfirm python python-pip base-devel pciutils dmidecode
fi

echo ""
echo "Creating configuration directories..."
mkdir -p /etc/driver-mgt

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

# Create user config directories as the actual user
su - "$ACTUAL_USER" -c "mkdir -p $ACTUAL_HOME/.config/driver-mgt/{profiles,curves,logs,corrections,reports}"

echo ""
echo "Installing driver-mgt..."
INSTALL_DIR="/opt/driver-mgt"
mkdir -p "$INSTALL_DIR"
cp -r src config driver-mgt requirements.txt setup.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/driver-mgt"

echo ""
echo "Creating virtual environment..."
cd "$INSTALL_DIR"

# Debian 12 uses PEP 668 - ensure we're creating a proper venv
# This avoids "externally-managed-environment" errors
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

echo ""
echo "Installing Python packages into venv..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
if ! "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"; then
    echo "✗ Failed to install Python packages"
    exit 1
fi

echo ""
echo "Verifying installation..."
if ! "$INSTALL_DIR/venv/bin/python" -c "import PyQt6, psutil, requests, yaml" 2>/dev/null; then
    echo "⚠ Warning: Some dependencies may not be properly installed"
    echo "  Attempting to install again..."
    "$INSTALL_DIR/venv/bin/pip" install --force-reinstall -r "$INSTALL_DIR/requirements.txt"
fi

# Create symlink
ln -sf "$INSTALL_DIR/driver-mgt" /usr/local/bin/driver-mgt

echo ""
echo "Creating desktop entry..."
cat > /usr/share/applications/driver-mgt.desktop <<EOF
[Desktop Entry]
Type=Application
Name=driver-mgt
Comment=Advanced Linux Driver Management
Exec=/usr/local/bin/driver-mgt
Icon=preferences-system
Terminal=true
Categories=System;Settings;
EOF

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
echo "You can now run driver-mgt with:"
echo "  driver-mgt         (GUI mode)"
echo "  driver-mgt status  (CLI mode)"
echo ""
echo "Configuration files are stored in:"
echo "  $ACTUAL_HOME/.config/driver-mgt/"
echo ""
echo "Optional: Install Ollama for AI-assisted management"
echo "  Visit: https://ollama.ai"
echo ""
