#!/bin/bash
# Test script to verify venv setup and wrapper functionality

set +e

echo "=========================================="
echo "driver-mgt Installation Test"
echo "=========================================="
echo ""

# Get absolute path to repo directory
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "Testing in directory: $REPO_DIR"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TEST_PASSED=0
TEST_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -ne "${BLUE}Testing: $test_name...${NC} "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TEST_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TEST_FAILED++))
        return 1
    fi
}

echo "Running tests..."
echo ""

# Test 1: Check if venv exists
run_test "Virtual environment exists" "[ -d venv ]"

# Test 2: Check if venv has Python
run_test "Virtual environment has Python" "[ -f venv/bin/python ]"

# Test 3: Check if driver-mgt wrapper exists
run_test "driver-mgt wrapper exists" "[ -f driver-mgt ]"

# Test 4: Check if driver-mgt.py exists
run_test "driver-mgt.py exists" "[ -f driver-mgt.py ]"

# Test 5: Check if wrapper is executable
run_test "driver-mgt wrapper is executable" "[ -x driver-mgt ]"

# Test 6: Check if requirements.txt exists
run_test "requirements.txt exists" "[ -f requirements.txt ]"

# Test 7: Check if PyQt6 is installed in venv
run_test "PyQt6 installed in venv" "./venv/bin/python -c 'import PyQt6'"

# Test 8: Check if psutil is installed in venv
run_test "psutil installed in venv" "./venv/bin/python -c 'import psutil'"

# Test 9: Check if requests is installed in venv
run_test "requests installed in venv" "./venv/bin/python -c 'import requests'"

# Test 10: Check if pyyaml is installed in venv
run_test "pyyaml installed in venv" "./venv/bin/python -c 'import yaml'"

# Test 11: Check if wrapper can run --help
run_test "driver-mgt wrapper runs --help" "./driver-mgt --help"

# Test 12: Check if wrapper can run --check-deps
run_test "driver-mgt wrapper runs --check-deps" "./driver-mgt --check-deps --no-keep-open"

# Test 13: Check if start.sh exists
run_test "start.sh exists" "[ -f start.sh ]"

# Test 14: Check if start.sh is executable
run_test "start.sh is executable" "[ -x start.sh ]"

# Test 15: Check if start.sh can run --help
run_test "start.sh runs --help" "./start.sh --help"

# Test 16: Check if check-system-deps.sh exists
run_test "check-system-deps.sh exists" "[ -f check-system-deps.sh ]"

# Test 17: Check if check-system-deps.sh is executable
run_test "check-system-deps.sh is executable" "[ -x check-system-deps.sh ]"

# Test 18: Verify venv Python is used by wrapper
echo -ne "${BLUE}Testing: Wrapper uses venv Python...${NC} "
if ./driver-mgt --check-deps --no-keep-open 2>&1 | grep -q "All dependencies installed"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TEST_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((TEST_FAILED++))
fi

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo -e "Passed: ${GREEN}$TEST_PASSED${NC}"
echo -e "Failed: ${RED}$TEST_FAILED${NC}"
echo ""

if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo ""
    echo "The installation is working correctly."
    echo ""
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    echo ""
    echo "Please review the failures above."
    echo ""
    exit 1
fi
