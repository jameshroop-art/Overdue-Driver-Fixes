#!/bin/bash
# Start script for driver-mgt
# Activates virtual environment and launches the application

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "driver-mgt Startup"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in development mode (running from repo) or installed mode
if [ -d "$SCRIPT_DIR/src" ] && [ -f "$SCRIPT_DIR/driver-mgt" ]; then
    # Development mode - running from repository
    INSTALL_DIR="$SCRIPT_DIR"
    VENV_DIR="$SCRIPT_DIR/venv"
    DRIVER_MGT_BIN="$SCRIPT_DIR/driver-mgt"
    MODE="development"
else
    # Try installed location
    INSTALL_DIR="/opt/driver-mgt"
    VENV_DIR="/opt/driver-mgt/venv"
    DRIVER_MGT_BIN="/opt/driver-mgt/driver-mgt"
    MODE="installed"
fi

echo -e "${BLUE}Mode: $MODE${NC}"
echo -e "${BLUE}Location: $INSTALL_DIR${NC}"
echo ""

# Check if driver-mgt exists
if [ ! -f "$DRIVER_MGT_BIN" ]; then
    echo -e "${RED}Error: driver-mgt not found${NC}"
    echo ""
    if [ "$MODE" = "development" ]; then
        echo "This appears to be a development environment."
        echo "Ensure you're running from the repository root directory."
    else
        echo "driver-mgt does not appear to be installed."
        echo "Please install it first with: sudo bash install.sh"
    fi
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found at: $VENV_DIR${NC}"
    echo ""
    
    if [ "$MODE" = "development" ]; then
        echo "Creating virtual environment for development..."
        
        # Check if python3-venv is installed
        if ! python3 -m venv --help >/dev/null 2>&1; then
            echo -e "${RED}Error: python3-venv is not installed${NC}"
            echo ""
            echo "Install it with:"
            echo "  Debian/Ubuntu: sudo apt-get install python3-venv"
            echo "  Fedora: sudo dnf install python3"
            echo "  Arch: sudo pacman -S python"
            echo ""
            exit 1
        fi
        
        # Create venv
        echo "Creating virtual environment..."
        if ! python3 -m venv "$VENV_DIR"; then
            echo -e "${RED}Failed to create virtual environment${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Virtual environment created${NC}"
        echo ""
        
        # Install dependencies
        echo "Installing dependencies from requirements.txt..."
        if ! "$VENV_DIR/bin/pip" install --upgrade pip; then
            echo -e "${RED}Failed to upgrade pip${NC}"
            exit 1
        fi
        
        if ! "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"; then
            echo -e "${RED}Failed to install dependencies${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        echo ""
    else
        echo -e "${RED}Please run the installation script first:${NC}"
        echo "  sudo bash install.sh"
        echo ""
        exit 1
    fi
fi

# Verify Python exists in venv
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo -e "${RED}Error: Python not found in virtual environment${NC}"
    echo "Expected: $VENV_DIR/bin/python"
    echo ""
    echo "Try recreating the virtual environment."
    exit 1
fi

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
MISSING_DEPS=0

# Check each dependency
for dep in PyQt6 psutil requests yaml; do
    if ! "$VENV_DIR/bin/python" -c "import $dep" 2>/dev/null; then
        echo -e "${RED}✗ $dep (missing)${NC}"
        MISSING_DEPS=1
    else
        echo -e "${GREEN}✓ $dep${NC}"
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Some dependencies are missing. Installing...${NC}"
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    echo ""
fi

# Parse command line arguments
ARGS=("$@")

# Check if GUI mode is requested (default)
GUI_MODE=1
for arg in "${ARGS[@]}"; do
    if [[ "$arg" == "status" ]] || [[ "$arg" == "scan" ]] || [[ "$arg" == "ai-status" ]] || [[ "$arg" == "--help" ]] || [[ "$arg" == "-h" ]]; then
        GUI_MODE=0
        break
    fi
done

echo ""
echo -e "${BLUE}Starting driver-mgt...${NC}"
echo ""

# Run driver-mgt with venv Python
cd "$INSTALL_DIR"

# Check if running with sudo/root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Running with elevated privileges${NC}"
    echo ""
fi

# Execute driver-mgt
"$VENV_DIR/bin/python" "$DRIVER_MGT_BIN" "${ARGS[@]}"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Application exited successfully${NC}"
else
    echo -e "${YELLOW}Application exited with code: $EXIT_CODE${NC}"
fi
echo ""

exit $EXIT_CODE
