#!/bin/bash
# Comprehensive verification script for driver-mgt setup
# Tests venv creation, dependency installation, and program functionality

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "driver-mgt Comprehensive Verification"
echo "=========================================="
echo ""

PASSED=0
FAILED=0
TOTAL=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL=$((TOTAL + 1))
    echo "[$TOTAL] Testing: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "  ✓ PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "  ✗ FAILED"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Test 1: Check if requirements.txt exists
run_test "requirements.txt exists" "[ -f requirements.txt ]"

# Test 2: Check if start.sh exists and is executable
run_test "start.sh exists and is executable" "[ -x start.sh ]"

# Test 3: Check if driver-mgt main script exists
run_test "driver-mgt main script exists" "[ -f driver-mgt ]"

# Test 4: Check if src directory exists
run_test "src directory exists" "[ -d src ]"

# Test 5: Check if venv can be created
if [ ! -d "venv" ]; then
    run_test "Virtual environment creation" "python3 -m venv test_venv_verify && rm -rf test_venv_verify"
else
    run_test "Virtual environment exists" "[ -d venv ]"
fi

# Test 6: Check if venv has Python
if [ -d "venv" ]; then
    run_test "Virtual environment has Python" "[ -f venv/bin/python ]"
    
    # Test 7: Check if dependencies are installed in venv
    run_test "PyQt6 installed in venv" "venv/bin/python -c 'import PyQt6'"
    run_test "psutil installed in venv" "venv/bin/python -c 'import psutil'"
    run_test "requests installed in venv" "venv/bin/python -c 'import requests'"
    run_test "yaml installed in venv" "venv/bin/python -c 'import yaml'"
    
    # Test 8: Check if all core modules can be imported
    export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
    run_test "core.config module" "venv/bin/python -c 'import sys; sys.path.insert(0, \"src\"); from core.config import ConfigManager'"
    run_test "core.hardware_detector module" "venv/bin/python -c 'import sys; sys.path.insert(0, \"src\"); from core.hardware_detector import HardwareDetector'"
    run_test "ai.ai_manager module" "venv/bin/python -c 'import sys; sys.path.insert(0, \"src\"); from ai.ai_manager import AIManager'"
    run_test "utils.logger module" "venv/bin/python -c 'import sys; sys.path.insert(0, \"src\"); from utils.logger import setup_logger'"
    
    # Test 9: Check if start.sh can run --check-deps
    run_test "start.sh --check-deps works" "./start.sh --no-keep-open --check-deps"
fi

# Test 10: Check if .gitignore excludes venv
run_test ".gitignore excludes venv" "grep -q '^venv/' .gitignore"

# Test 11: Check if all Python files are valid syntax
echo "[$((TOTAL + 1))] Testing: All Python files have valid syntax"
TOTAL=$((TOTAL + 1))
SYNTAX_ERRORS=0
for pyfile in $(find . -name "*.py" -not -path "./venv/*" -not -path "./test_venv/*"); do
    if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "  Syntax error in: $pyfile"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done
if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "  ✓ PASSED"
    PASSED=$((PASSED + 1))
else
    echo "  ✗ FAILED ($SYNTAX_ERRORS files with syntax errors)"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    echo ""
    echo "driver-mgt is ready to use!"
    echo "Run: ./start.sh"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    echo ""
    echo "Please review the failures above."
    exit 1
fi
