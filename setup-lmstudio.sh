#!/bin/bash
# LM Studio Quick Setup Script
# Downloads and sets up LM Studio for use with driver-mgt

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=============================================="
echo "LM Studio Quick Setup for driver-mgt"
echo "=============================================="
echo ""

# Get actual user (not root if using sudo)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
    ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
else
    ACTUAL_USER="$USER"
    ACTUAL_HOME="$HOME"
fi

# Check if already installed
if [ -f "$ACTUAL_HOME/.local/bin/lm-studio" ] || [ -f "/usr/local/bin/lm-studio" ]; then
    echo -e "${GREEN}✓ LM Studio appears to be already installed${NC}"
    echo ""
    read -p "Reinstall anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. To launch LM Studio, run: lm-studio"
        exit 0
    fi
fi

# Check system requirements
echo -e "${BLUE}Checking system requirements...${NC}"

# Check RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 8 ]; then
    echo -e "${YELLOW}⚠ Warning: Low RAM detected (${TOTAL_RAM}GB)${NC}"
    echo "  Recommended: 8GB+ for basic models, 16GB+ for better performance"
    echo ""
fi

# Check disk space
FREE_SPACE=$(df -BG "$ACTUAL_HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$FREE_SPACE" -lt 20 ]; then
    echo -e "${YELLOW}⚠ Warning: Low disk space (${FREE_SPACE}GB free)${NC}"
    echo "  Recommended: 20GB+ free for model downloads"
    echo ""
fi

# Check for FUSE (required for AppImage)
echo -e "${BLUE}Checking AppImage support...${NC}"
if ! command -v fusermount &> /dev/null; then
    echo -e "${YELLOW}⚠ FUSE not found - required for AppImage${NC}"
    echo ""
    
    # Offer to install FUSE
    if [ "$EUID" -eq 0 ] || command -v sudo &> /dev/null; then
        read -p "Install FUSE now? (Y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            echo "Installing FUSE..."
            
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y fuse libfuse2
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y fuse fuse-libs
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm fuse2
            else
                echo -e "${RED}✗ Could not install FUSE automatically${NC}"
                echo "  Please install FUSE manually for your distribution"
                exit 1
            fi
            
            echo -e "${GREEN}✓ FUSE installed${NC}"
        else
            echo -e "${RED}✗ FUSE is required to run AppImage files${NC}"
            echo "  Install manually and run this script again"
            exit 1
        fi
    else
        echo -e "${RED}✗ FUSE is required to run AppImage files${NC}"
        echo "  Install with: sudo apt-get install fuse libfuse2"
        exit 1
    fi
else
    echo -e "${GREEN}✓ FUSE is installed${NC}"
fi

echo ""
echo -e "${BLUE}Downloading LM Studio...${NC}"
echo "Source: https://lmstudio.ai/download/latest/linux/x64"
echo ""

# Download to user's Downloads or tmp
DOWNLOAD_DIR="$ACTUAL_HOME/Downloads"
if [ ! -d "$DOWNLOAD_DIR" ]; then
    DOWNLOAD_DIR="/tmp"
fi

DOWNLOAD_FILE="$DOWNLOAD_DIR/lm-studio-linux-x64.AppImage"

# Download with progress
if command -v wget &> /dev/null; then
    wget https://lmstudio.ai/download/latest/linux/x64 -O "$DOWNLOAD_FILE" || {
        echo -e "${RED}✗ Download failed${NC}"
        exit 1
    }
elif command -v curl &> /dev/null; then
    curl -L https://lmstudio.ai/download/latest/linux/x64 -o "$DOWNLOAD_FILE" || {
        echo -e "${RED}✗ Download failed${NC}"
        exit 1
    }
else
    echo -e "${RED}✗ Neither wget nor curl found${NC}"
    echo "  Please install wget or curl to download LM Studio"
    exit 1
fi

echo -e "${GREEN}✓ Downloaded successfully${NC}"
echo ""

# Make executable
chmod +x "$DOWNLOAD_FILE"
echo -e "${GREEN}✓ Made executable${NC}"
echo ""

# Ask where to install
echo "Installation Options:"
echo "  1. User installation (~/.local/bin/lm-studio) - Recommended"
echo "  2. System-wide (/usr/local/bin/lm-studio) - Requires sudo"
echo "  3. Keep in Downloads only"
echo ""
read -p "Choose installation location (1/2/3): " -n 1 -r
echo ""

case $REPLY in
    1)
        # User installation
        mkdir -p "$ACTUAL_HOME/.local/bin"
        if [ -f "$ACTUAL_HOME/.local/bin/lm-studio" ]; then
            rm "$ACTUAL_HOME/.local/bin/lm-studio"
        fi
        mv "$DOWNLOAD_FILE" "$ACTUAL_HOME/.local/bin/lm-studio"
        chown "$ACTUAL_USER:$ACTUAL_USER" "$ACTUAL_HOME/.local/bin/lm-studio" 2>/dev/null || true
        
        echo -e "${GREEN}✓ Installed to: $ACTUAL_HOME/.local/bin/lm-studio${NC}"
        
        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$ACTUAL_HOME/.local/bin:"* ]]; then
            echo ""
            echo -e "${YELLOW}⚠ Note: ~/.local/bin is not in your PATH${NC}"
            echo "  Add to your ~/.bashrc or ~/.zshrc:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo ""
            echo "  Or run with full path: $ACTUAL_HOME/.local/bin/lm-studio"
        fi
        
        INSTALL_PATH="$ACTUAL_HOME/.local/bin/lm-studio"
        ;;
    2)
        # System-wide installation
        if [ "$EUID" -ne 0 ] && ! command -v sudo &> /dev/null; then
            echo -e "${RED}✗ Root access required for system-wide installation${NC}"
            echo "  Keeping in Downloads: $DOWNLOAD_FILE"
            INSTALL_PATH="$DOWNLOAD_FILE"
        else
            if [ "$EUID" -ne 0 ]; then
                sudo mv "$DOWNLOAD_FILE" /usr/local/bin/lm-studio
                sudo chmod +x /usr/local/bin/lm-studio
            else
                mv "$DOWNLOAD_FILE" /usr/local/bin/lm-studio
                chmod +x /usr/local/bin/lm-studio
            fi
            echo -e "${GREEN}✓ Installed to: /usr/local/bin/lm-studio${NC}"
            INSTALL_PATH="/usr/local/bin/lm-studio"
        fi
        ;;
    *)
        # Keep in Downloads
        echo -e "${GREEN}✓ Kept in: $DOWNLOAD_FILE${NC}"
        INSTALL_PATH="$DOWNLOAD_FILE"
        ;;
esac

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo -e "${GREEN}✓ LM Studio is ready to use${NC}"
echo ""
echo "Next Steps:"
echo ""
echo "1. Launch LM Studio:"
echo "   $INSTALL_PATH"
echo ""
echo "2. In LM Studio application:"
echo "   • Navigate to 'Search' tab (🔍)"
echo "   • Download models (recommended: starcoder, codellama, mistral)"
echo "   • Go to 'Local Server' tab"
echo "   • Click 'Start Server' (will listen on localhost:1234)"
echo "   • Select a model to load"
echo ""
echo "3. Launch driver-mgt with LM Studio:"
echo "   driver-mgt-lmstudio"
echo "   Or use desktop launcher: 'Driver Manager (LLM Studio)'"
echo ""
echo "4. For detailed setup instructions, see:"
echo "   📖 LMSTUDIO_SETUP.md"
echo "   Or: cat $(dirname "$0")/LMSTUDIO_SETUP.md"
echo ""
echo -e "${BLUE}Recommended Models for Driver Management:${NC}"
echo "  • starcoder (3B-7B) - Code analysis specialist"
echo "  • codellama (7B-13B) - Balanced performance"
echo "  • mistral (7B) - Fast and efficient"
echo "  • phi-2 (2.7B) - Lightweight option"
echo ""
echo "Model Download:"
echo "  In LM Studio, search for models and select Q4_K_M or Q5_K_M"
echo "  quantization for best balance of quality and performance."
echo ""

# Offer to launch LM Studio now
read -p "Launch LM Studio now? (Y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Launching LM Studio..."
    echo ""
    
    # Launch as the actual user (not root)
    if [ "$EUID" -eq 0 ] && [ "$ACTUAL_USER" != "root" ]; then
        su - "$ACTUAL_USER" -c "$INSTALL_PATH" &
    else
        "$INSTALL_PATH" &
    fi
    
    echo -e "${GREEN}✓ LM Studio launched${NC}"
    echo ""
    echo "Remember to:"
    echo "  1. Download models from the 'Search' tab"
    echo "  2. Start the server in 'Local Server' tab"
    echo "  3. Load a model"
    echo ""
    echo "Then run: driver-mgt-lmstudio"
else
    echo "You can launch LM Studio anytime with: $INSTALL_PATH"
fi

echo ""
echo "For help, see LMSTUDIO_SETUP.md or visit:"
echo "  https://lmstudio.ai/docs"
echo ""
