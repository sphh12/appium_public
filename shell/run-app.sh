#!/bin/bash

# Appium Mobile Test Runner
# Usage: ./shell/run-app.sh [options]
#
# Options:
#   --platform    : android or ios (default: android)
#   --test        : specific test to run (e.g., test_Login)
#   --all         : run all tests
#   --report      : open allure report after test
#   --generate    : generate allure html report (without server)
#   --skip-check  : skip prerequisite checks
#   --no-auto     : don't auto-start missing prerequisites

PLATFORM="android"
TEST_NAME=""
OPEN_REPORT=false
RUN_ALL=false
GENERATE_REPORT=false
SKIP_CHECK=false
AUTO_START=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        --generate)
            GENERATE_REPORT=true
            shift
            ;;
        --skip-check)
            SKIP_CHECK=true
            shift
            ;;
        --no-auto)
            AUTO_START=false
            shift
            ;;
        --help)
            echo "Usage: ./shell/run-app.sh [options]"
            echo ""
            echo "Options:"
            echo "  --platform <android|ios>  Set test platform (default: android)"
            echo "  --test <test_name>        Run specific test (e.g., test_Login)"
            echo "  --all                     Run all tests"
            echo "  --report                  Open allure report after test (requires server)"
            echo "  --generate                Generate HTML report to allure-report folder"
            echo "  --skip-check              Skip prerequisite checks"
            echo "  --no-auto                 Don't auto-start missing prerequisites"
            echo "  --help                    Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./shell/run-app.sh --test test_Login"
            echo "  ./shell/run-app.sh --all --report"
            echo "  ./shell/run-app.sh --test test_Login --generate"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "  Appium Mobile Test Runner"
echo "========================================"
echo ""

# ========================================
# STEP 1: Prerequisite Checks & Auto-Start
# ========================================
if [[ "$SKIP_CHECK" == false ]]; then
    echo "[STEP 1] Checking prerequisites..."
    echo ""

    APPIUM_RUNNING=false
    DEVICE_CONNECTED=false
    VENV_EXISTS=false

    # Check 1: Appium Server
    echo -n "  - Appium Server (port 4723): "
    if curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
        echo -e "${GREEN}Running${NC}"
        APPIUM_RUNNING=true
    else
        echo -e "${RED}Not Running${NC}"
        if [[ "$AUTO_START" == true ]]; then
            echo -e "    ${BLUE}[AUTO] Starting Appium server...${NC}"
            npx appium > /dev/null 2>&1 &
            APPIUM_PID=$!
            echo -e "    ${BLUE}[AUTO] Waiting for Appium to start...${NC}"

            # Wait for Appium to start (max 30 seconds)
            for i in {1..30}; do
                sleep 1
                if curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
                    echo -e "    ${GREEN}[OK] Appium server started (PID: $APPIUM_PID)${NC}"
                    APPIUM_RUNNING=true
                    break
                fi
                echo -n "."
            done
            echo ""

            if [[ "$APPIUM_RUNNING" == false ]]; then
                echo -e "    ${RED}[FAIL] Could not start Appium server${NC}"
            fi
        else
            echo -e "    ${YELLOW}[FIX] Run: npx appium${NC}"
        fi
    fi

    # Check 2: Android Emulator / Device
    echo -n "  - Android Device/Emulator:  "
    if command -v adb &> /dev/null; then
        # Suppress adb daemon messages
        adb start-server > /dev/null 2>&1
        sleep 1

        DEVICE_COUNT=$(adb devices 2>/dev/null | grep -w "device" | wc -l)
        if [[ $DEVICE_COUNT -gt 0 ]]; then
            DEVICE_NAME=$(adb devices 2>/dev/null | grep -w "device" | head -1 | cut -f1)
            echo -e "${GREEN}Connected ($DEVICE_NAME)${NC}"
            DEVICE_CONNECTED=true
        else
            echo -e "${RED}Not Connected${NC}"
            if [[ "$AUTO_START" == true ]]; then
                echo -e "    ${BLUE}[AUTO] Starting Android emulator...${NC}"

                # Preferred emulator: Pixel_6, otherwise use first available
                EMULATOR_NAME=$(emulator -list-avds 2>/dev/null | grep -i "Pixel_6" | head -1)
                if [[ -z "$EMULATOR_NAME" ]]; then
                    EMULATOR_NAME=$(emulator -list-avds 2>/dev/null | head -1)
                fi

                if [[ -n "$EMULATOR_NAME" ]]; then
                    echo -e "    ${BLUE}[AUTO] Found emulator: $EMULATOR_NAME${NC}"
                    emulator -avd "$EMULATOR_NAME" -no-snapshot-load > /dev/null 2>&1 &
                    EMULATOR_PID=$!
                    echo -e "    ${BLUE}[AUTO] Waiting for emulator to boot (this may take a while)...${NC}"

                    # Wait for emulator to boot (max 120 seconds)
                    for i in {1..120}; do
                        sleep 2
                        BOOT_COMPLETED=$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
                        if [[ "$BOOT_COMPLETED" == "1" ]]; then
                            DEVICE_NAME=$(adb devices 2>/dev/null | grep -w "device" | head -1 | cut -f1)
                            echo -e "    ${GREEN}[OK] Emulator started ($DEVICE_NAME)${NC}"
                            DEVICE_CONNECTED=true

                            # Some environments report boot completed before ADB is fully in 'device' state.
                            # Wait a bit longer to avoid Appium timing out while searching for a connected device.
                            echo -e "    ${BLUE}[AUTO] Waiting for ADB to be ready...${NC}"
                            ADB_READY=false
                            for j in {1..30}; do
                                STATE=$(adb get-state 2>/dev/null | tr -d '\r')
                                if [[ "$STATE" == "device" ]]; then
                                    ADB_READY=true
                                    break
                                fi
                                sleep 2
                            done

                            if [[ "$ADB_READY" == true ]]; then
                                echo -e "    ${GREEN}[OK] ADB is ready${NC}"
                            else
                                echo -e "    ${RED}[FAIL] ADB not ready (still offline).${NC}"
                                DEVICE_CONNECTED=false
                            fi
                            break
                        fi
                        # Show progress every 10 seconds
                        if (( i % 5 == 0 )); then
                            echo -e "    ${BLUE}[AUTO] Still waiting... (${i}s)${NC}"
                        fi
                    done

                    if [[ "$DEVICE_CONNECTED" == false ]]; then
                        echo -e "    ${RED}[FAIL] Emulator boot timeout${NC}"
                    fi
                else
                    echo -e "    ${RED}[FAIL] No emulator found. Create one in Android Studio.${NC}"
                fi
            else
                echo -e "    ${YELLOW}[FIX] Start emulator from Android Studio or connect device${NC}"
            fi
        fi
    else
        echo -e "${RED}ADB not found${NC}"
        echo -e "    ${YELLOW}[FIX] Check ANDROID_HOME environment variable${NC}"
    fi

    # Check 3: Virtual Environment
    echo -n "  - Python venv:              "
    if [[ -d "venv" ]]; then
        echo -e "${GREEN}Found${NC}"
        VENV_EXISTS=true
    else
        echo -e "${RED}Not Found${NC}"
        if [[ "$AUTO_START" == true ]]; then
            echo -e "    ${BLUE}[AUTO] Creating virtual environment...${NC}"
            python -m venv venv
            if [[ -d "venv" ]]; then
                echo -e "    ${GREEN}[OK] Virtual environment created${NC}"
                VENV_EXISTS=true

                # Activate and install requirements
                echo -e "    ${BLUE}[AUTO] Installing requirements...${NC}"
                if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
                    source venv/Scripts/activate
                else
                    source venv/bin/activate
                fi
                pip install -r requirements.txt > /dev/null 2>&1
                echo -e "    ${GREEN}[OK] Requirements installed${NC}"
            else
                echo -e "    ${RED}[FAIL] Could not create virtual environment${NC}"
            fi
        else
            echo -e "    ${YELLOW}[FIX] Run: python -m venv venv${NC}"
        fi
    fi

    echo ""

    # Final check
    if [[ "$APPIUM_RUNNING" == false || "$DEVICE_CONNECTED" == false || "$VENV_EXISTS" == false ]]; then
        echo -e "${RED}[ERROR] Prerequisites not met.${NC}"
        echo ""
        if [[ "$AUTO_START" == true ]]; then
            echo "Auto-start failed for some components. Please check manually."
        else
            echo "To auto-start missing prerequisites, remove --no-auto option"
        fi
        echo "To skip checks, use: ./shell/run-app.sh --skip-check [options]"
        exit 1
    fi

    echo -e "${GREEN}[OK] All prerequisites met!${NC}"
    echo ""
fi

# ========================================
# STEP 2: Activate Virtual Environment
# ========================================
echo "[STEP 2] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# ========================================
# STEP 3: Run Tests
# ========================================
echo "[STEP 3] Running tests..."
echo ""

# Generate timestamp for folder names (YYYYMMDD_HHMMSS)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="allure-results/$TIMESTAMP"
REPORT_DIR="allure-reports/$TIMESTAMP"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Copy history from previous report for trend tracking
LATEST_FILE="allure-reports/LATEST.txt"
if [[ -f "$LATEST_FILE" ]]; then
    PREV_TIMESTAMP=$(cat "$LATEST_FILE" | tr -d '\r\n')
    PREV_HISTORY="allure-reports/$PREV_TIMESTAMP/history"
    if [[ -d "$PREV_HISTORY" ]]; then
        echo "  Copying history from previous run..."
        cp -r "$PREV_HISTORY" "$RESULTS_DIR/"
    fi
fi

# Build pytest command
CMD="python -m pytest tests/android/test_01.py -v --platform=$PLATFORM --alluredir=$RESULTS_DIR --record-video"

if [[ "$RUN_ALL" == false && -n "$TEST_NAME" ]]; then
    CMD="$CMD -k $TEST_NAME"
fi

echo "  Platform: $PLATFORM"
echo "  Test:     ${TEST_NAME:-all}"
echo "  Results:  $RESULTS_DIR"
echo ""
echo "----------------------------------------"

# Run tests
$CMD
TEST_EXIT_CODE=$?

echo "----------------------------------------"
echo ""

# ========================================
# STEP 4: Generate/Open Allure Report
# ========================================
# Always generate report to timestamp folder
echo "[STEP 4] Generating Allure HTML report..."
allure generate "$RESULTS_DIR" -o "$REPORT_DIR" --clean
echo -e "${GREEN}[OK] Report generated: $REPORT_DIR${NC}"

# Update LATEST.txt for next run's history
mkdir -p "allure-reports"
echo "$TIMESTAMP" > "$LATEST_FILE"

echo ""

if [[ "$OPEN_REPORT" == true ]]; then
    echo "Opening Allure report..."
    echo "  (Press Ctrl+C to stop the server)"
    echo ""
    allure open "$REPORT_DIR"
fi

# ========================================
# Summary
# ========================================
echo "========================================"
if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo -e "  ${GREEN}Tests completed successfully!${NC}"
else
    echo -e "  ${RED}Tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi
echo "========================================"
echo ""
echo "Results: $RESULTS_DIR"
echo "Report:  $REPORT_DIR"
echo ""
echo "To view the report:"
echo "  allure open $REPORT_DIR"
echo ""

exit $TEST_EXIT_CODE
