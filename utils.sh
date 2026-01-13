#!/bin/bash
# Shared utility functions for driver-mgt scripts
# Source this file in other scripts: source utils.sh

# Function to detect the correct OpenGL package for apt-based systems
# Returns: package name (libgl1 or libgl1-mesa-glx)
detect_opengl_package() {
    local opengl_pkg="libgl1"
    
    # Check if libgl1-mesa-glx is actually installable (not just a virtual package)
    # We check for the "Package:" line which appears in real packages but not virtual ones
    if apt-cache show libgl1-mesa-glx 2>/dev/null | grep -q "^Package: libgl1-mesa-glx"; then
        opengl_pkg="libgl1-mesa-glx"
    fi
    
    echo "$opengl_pkg"
}

# Function to check if a library is available via ldconfig
# Args: lib_pattern (e.g., "libGL\.so")
# Returns: 0 if found, 1 if not found
check_library() {
    local lib_pattern="$1"
    ldconfig -p 2>/dev/null | grep -q "$lib_pattern"
}

# Function to detect distribution info
# Sets: DISTRO_ID, DISTRO_VERSION, DISTRO_NAME
detect_distribution() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID="$ID"
        DISTRO_VERSION="$VERSION_ID"
        DISTRO_NAME="$PRETTY_NAME"
    else
        DISTRO_ID="unknown"
        DISTRO_VERSION="unknown"
        DISTRO_NAME="Unknown Distribution"
    fi
}

# Function to detect package manager
# Returns: apt, dnf, pacman, or unknown
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

# Note: Function exports only work when this file is sourced with 'source' or '.'
# If the shell doesn't support function exports (some minimal shells), 
# scripts can still call the functions directly after sourcing this file.
# The 2>/dev/null suppresses errors in shells that don't support -f flag with export.
