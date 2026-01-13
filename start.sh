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
    DRIVER_MGT_PY="$SCRIPT_DIR/driver-mgt.py"
    MODE="development"
else
    # Try installed location
    INSTALL_DIR="/opt/driver-mgt"
    VENV_DIR="/opt/driver-mgt/venv"
    DRIVER_MGT_BIN="/opt/driver-mgt/driver-mgt"
    DRIVER_MGT_PY="/opt/driver-mgt/driver-mgt.py"
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

# Check if driver-mgt.py exists
if [ ! -f "$DRIVER_MGT_PY" ]; then
    echo -e "${RED}Error: driver-mgt.py not found${NC}"
    echo ""
    echo "The Python script is missing. Please reinstall."
    exit 1
fi

# Check if virtual environment exists (for information only, wrapper handles activation)
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Note: Virtual environment not found at: $VENV_DIR${NC}"
    echo ""
    
    if [ "$MODE" = "development" ]; then
        echo "The driver-mgt wrapper will handle venv setup automatically."
        echo "If you encounter issues, create it manually with:"
        echo "  python3 -m venv $VENV_DIR"
        echo "  $VENV_DIR/bin/pip install -r requirements.txt"
    else
        echo "Please run the installation script first:"
        echo "  sudo bash install.sh"
    fi
    echo ""
fi

# Parse command line arguments
ARGS=("$@")

# List of CLI-only commands (extracted for maintainability)
CLI_COMMANDS=("status" "scan" "ai-status" "ai-signin" "monitor" "risk-assess" "--help" "-h" "--check-deps")

# Check if GUI mode is requested (default)
GUI_MODE=1
for arg in "${ARGS[@]}"; do
    for cmd in "${CLI_COMMANDS[@]}"; do
        if [[ "$arg" == "$cmd" ]]; then
            GUI_MODE=0
            break 2
        fi
    done
done

echo ""
echo -e "${BLUE}Starting driver-mgt...${NC}"
echo ""

# Check if running with sudo/root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Running with elevated privileges${NC}"
    echo ""
fi

# Execute driver-mgt (wrapper handles venv activation automatically)
"$DRIVER_MGT_BIN" "${ARGS[@]}"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Application exited successfully${NC}"
else
    echo -e "${YELLOW}Application exited with code: $EXIT_CODE${NC}"
fi
echo ""

exit $EXIT_CODE
