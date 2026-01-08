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

# Detect package manager
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
    apt-get install -y python3 python3-pip python3-venv lspci pciutils
elif [ "$PKG_MANAGER" = "dnf" ]; then
    dnf install -y python3 python3-pip pciutils
elif [ "$PKG_MANAGER" = "pacman" ]; then
    pacman -S --noconfirm python python-pip pciutils
fi

echo ""
echo "Installing Python packages..."
pip3 install -r requirements.txt

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
cp -r src config driver-mgt "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/driver-mgt"

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
echo "You can now run driver-mgt with:"
echo "  driver-mgt         (GUI mode)"
echo "  driver-mgt status  (CLI mode)"
echo ""
echo "Optional: Install Ollama for AI-assisted management"
echo "  Visit: https://ollama.ai"
echo ""
