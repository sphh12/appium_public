#!/bin/bash

# Appium Mobile Test Runner
# Usage: ./run_tests.sh [options]
#
# Options:
#   --platform    : android or ios (default: android)
#   --test        : specific test to run (e.g., test_Login)
#   --all         : run all tests
#   --report      : open allure report after test

PLATFORM="android"
TEST_NAME=""
OPEN_REPORT=false
RUN_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --test)
            TEST_NAME="$2"
            shift 2
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --report)
            OPEN_REPORT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Build pytest command
CMD="python -m pytest tests/test_01.py -v --platform=$PLATFORM --alluredir=allure-results --clean-alluredir --record-video"

if [[ "$RUN_ALL" == false && -n "$TEST_NAME" ]]; then
    CMD="$CMD -k $TEST_NAME"
fi

echo "========================================"
echo "Running Appium Tests"
echo "Platform: $PLATFORM"
echo "Test: ${TEST_NAME:-all}"
echo "========================================"

# Run tests
$CMD

# Open allure report if requested
if [[ "$OPEN_REPORT" == true ]]; then
    echo "Generating Allure report..."
    allure serve allure-results
fi
