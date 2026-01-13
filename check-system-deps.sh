#!/bin/bash
# System library checker and troubleshooter
# Helps identify missing system dependencies for PyQt6 and OpenGL

set -e

# Get script directory and load shared utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/utils.sh" ]; then
    source "$SCRIPT_DIR/utils.sh"
fi

echo "=========================================="
echo "System Library Dependency Checker"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
IS_ROOT=0
if [ "$EUID" -eq 0 ]; then
    IS_ROOT=1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="$ID"
    DISTRO_VERSION="$VERSION_ID"
    echo -e "${BLUE}Distribution: $PRETTY_NAME${NC}"
else
    DISTRO_ID="unknown"
    DISTRO_VERSION="unknown"
    echo -e "${YELLOW}Warning: Could not detect distribution${NC}"
fi

if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
else
    PKG_MANAGER="unknown"
fi

echo -e "${BLUE}Package Manager: $PKG_MANAGER${NC}"
echo ""

# Function to check if a library is available
check_library() {
    local lib_name="$1"
    local lib_pattern="$2"
    
    if ldconfig -p 2>/dev/null | grep -q "$lib_pattern"; then
        echo -e "${GREEN}✓ $lib_name${NC}"
        return 0
    else
        echo -e "${RED}✗ $lib_name (missing)${NC}"
        return 1
    fi
}

# Function to check if a package is installed
check_package() {
    local pkg_name="$1"
    
    case "$PKG_MANAGER" in
        apt)
            if dpkg -l "$pkg_name" 2>/dev/null | grep -q "^ii"; then
                return 0
            fi
            ;;
        dnf)
            if rpm -q "$pkg_name" &>/dev/null; then
                return 0
            fi
            ;;
        pacman)
            if pacman -Q "$pkg_name" &>/dev/null; then
                return 0
            fi
            ;;
    esac
    return 1
}

echo "Checking system libraries..."
echo ""

MISSING_LIBS=0

# Check OpenGL libraries
echo "OpenGL Libraries:"
if ! check_library "libGL" "libGL\.so"; then
    MISSING_LIBS=1
fi

if ! check_library "libEGL" "libEGL\.so"; then
    MISSING_LIBS=1
fi

echo ""

# Check X11/Qt libraries
echo "X11/Qt Libraries:"
if ! check_library "libxcb-xinerama" "libxcb-xinerama\.so"; then
    MISSING_LIBS=1
fi

if ! check_library "libxcb-cursor" "libxcb-cursor\.so"; then
    MISSING_LIBS=1
fi

if ! check_library "libxkbcommon-x11" "libxkbcommon-x11\.so"; then
    MISSING_LIBS=1
fi

echo ""

# Check Python venv capability
echo "Python Environment:"
if python3 -m venv --help &>/dev/null; then
    echo -e "${GREEN}✓ python3-venv${NC}"
else
    echo -e "${RED}✗ python3-venv (missing)${NC}"
    MISSING_LIBS=1
fi

echo ""

# Check Python build dependencies (needed for building C extensions and some venv scenarios)
echo "Python Build Dependencies:"
if ! check_library "libssl" "libssl\.so"; then
    echo -e "${YELLOW}⚠ libssl-dev (recommended for SSL support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "libbz2" "libbz2\.so"; then
    echo -e "${YELLOW}⚠ libbz2-dev (recommended for bzip2 support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "liblzma" "liblzma\.so"; then
    echo -e "${YELLOW}⚠ liblzma-dev (recommended for LZMA support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "libsqlite3" "libsqlite3\.so"; then
    echo -e "${YELLOW}⚠ libsqlite3-dev (recommended for SQLite support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "libreadline" "libreadline\.so"; then
    echo -e "${YELLOW}⚠ libreadline-dev (recommended for readline support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "libgdbm" "libgdbm\.so"; then
    echo -e "${YELLOW}⚠ libgdbm-dev (recommended for GDBM support)${NC}"
    MISSING_LIBS=1
fi

if ! check_library "libffi" "libffi\.so"; then
    echo -e "${YELLOW}⚠ libffi-dev (recommended for FFI support)${NC}"
    MISSING_LIBS=1
fi

echo ""

# Provide recommendations if libraries are missing
if [ $MISSING_LIBS -eq 1 ]; then
    echo "=========================================="
    echo -e "${YELLOW}Missing Dependencies Detected${NC}"
    echo "=========================================="
    echo ""
    
    case "$PKG_MANAGER" in
        apt)
            echo "To install missing dependencies, run:"
            echo ""
            
            # Determine OpenGL package using shared utility
            if type detect_opengl_package &>/dev/null; then
                OPENGL_PKG=$(detect_opengl_package)
                if [ "$OPENGL_PKG" = "libgl1" ]; then
                    echo -e "${BLUE}Note: Using libgl1 (libgl1-mesa-glx is obsolete in Ubuntu 24.04+)${NC}"
                    echo ""
                fi
            else
                # Fallback if utils.sh not loaded
                if apt-cache show libgl1-mesa-glx 2>/dev/null | grep -q "^Package: libgl1-mesa-glx"; then
                    OPENGL_PKG="libgl1-mesa-glx"
                else
                    OPENGL_PKG="libgl1"
                    echo -e "${BLUE}Note: Using libgl1 (libgl1-mesa-glx is obsolete in Ubuntu 24.04+)${NC}"
                    echo ""
                fi
            fi
            
            if [ $IS_ROOT -eq 1 ]; then
                echo "  apt-get update"
                echo "  apt-get install -y python3-venv $OPENGL_PKG libegl1 \\"
                echo "                     libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 \\"
                echo "                     libssl-dev libbz2-dev liblzma-dev libsqlite3-dev \\"
                echo "                     libreadline-dev libgdbm-dev libffi-dev"
            else
                echo "  sudo apt-get update"
                echo "  sudo apt-get install -y python3-venv $OPENGL_PKG libegl1 \\"
                echo "                          libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 \\"
                echo "                          libssl-dev libbz2-dev liblzma-dev libsqlite3-dev \\"
                echo "                          libreadline-dev libgdbm-dev libffi-dev"
            fi
            ;;
        dnf)
            echo "To install missing dependencies, run:"
            echo ""
            if [ $IS_ROOT -eq 1 ]; then
                echo "  dnf install -y python3 mesa-libGL mesa-libEGL \\"
                echo "                 libxcb xcb-util-cursor libxkbcommon-x11 \\"
                echo "                 openssl-devel bzip2-devel xz-devel sqlite-devel \\"
                echo "                 readline-devel gdbm-devel libffi-devel"
            else
                echo "  sudo dnf install -y python3 mesa-libGL mesa-libEGL \\"
                echo "                      libxcb xcb-util-cursor libxkbcommon-x11 \\"
                echo "                      openssl-devel bzip2-devel xz-devel sqlite-devel \\"
                echo "                      readline-devel gdbm-devel libffi-devel"
            fi
            ;;
        pacman)
            echo "To install missing dependencies, run:"
            echo ""
            if [ $IS_ROOT -eq 1 ]; then
                echo "  pacman -S --noconfirm python libglvnd libxcb \\"
                echo "                        xcb-util-cursor libxkbcommon-x11 \\"
                echo "                        openssl bzip2 xz sqlite readline gdbm libffi"
            else
                echo "  sudo pacman -S --noconfirm python libglvnd libxcb \\"
                echo "                             xcb-util-cursor libxkbcommon-x11 \\"
                echo "                             openssl bzip2 xz sqlite readline gdbm libffi"
            fi
            ;;
        *)
            echo -e "${RED}Unknown package manager. Please install manually:${NC}"
            echo "  - Python 3 with venv support"
            echo "  - Python build dependencies (OpenSSL, bzip2, LZMA, SQLite, readline, GDBM, libffi)"
            echo "  - OpenGL libraries (libGL, libEGL)"
            echo "  - Qt/X11 libraries (libxcb, xcb-util-cursor, libxkbcommon-x11)"
            ;;
    esac
    
    echo ""
    echo "Alternatively, run the installation script which handles this automatically:"
    echo "  sudo bash install.sh"
    echo ""
    
    exit 1
else
    echo "=========================================="
    echo -e "${GREEN}All Dependencies Satisfied!${NC}"
    echo "=========================================="
    echo ""
    echo "Your system has all required libraries for driver-mgt."
    echo ""
    exit 0
fi
