#!/bin/bash

# Appium Mobile Test Runner
# Usage: ./shell/run-app.sh [options]
#
# Options:
#   --platform    : android or ios (default: android)
#   --stg         : use Staging APK (default for Android)
#   --live        : use Live APK
#   --app         : path to APK or IPA file (overrides --stg/--live)
#   --test        : specific test to run (e.g., test_Login)
#   --files       : space-separated test paths to run in order (quote the value)
#   --all         : run all tests
#   --report      : open allure report after test
#   --generate    : generate allure html report (without server)
#   --skip-check  : skip prerequisite checks
#   --no-auto     : don't auto-start missing prerequisites

# Windows cp949 인코딩 문제 방지 (Python UTF-8 강제)
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# ~/.zshrc 환경변수 로드 (bash에서 실행 시 ANDROID_HOME, nvm 등 PATH 누락 방지)
if [[ -f "$HOME/.zshrc" ]]; then
    source "$HOME/.zshrc" 2>/dev/null
fi

PLATFORM="android"
ENV_TYPE=""
TEST_NAME=""
TEST_FILES=""
APP_PATH=""
OPEN_REPORT=false
RUN_ALL=false
GENERATE_REPORT=false
SKIP_CHECK=false
AUTO_START=true

APPIUM_CMD="npx appium"
ALLURE_CMD="allure"

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
        --files)
            TEST_FILES="$2"
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
        --stg)
            ENV_TYPE="stg"
            shift
            ;;
        --live)
            ENV_TYPE="live"
            shift
            ;;
        --app)
            APP_PATH="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./shell/run-app.sh [options]"
            echo ""
            echo "Options:"
            echo "  --platform <android|ios>  Set test platform (default: android)"
            echo "  --stg                     Use Staging APK (default for Android)"
            echo "  --live                    Use Live APK"
            echo "  --app <path>              Path to APK or IPA file (overrides --stg/--live)"
            echo "  --test <test_name>        Run specific test (e.g., test_Login)"
            echo "  --files \"<paths...>\"     Run specific test files in given order"
            echo "  --<file>                  Shorthand for tests/<platform>/<file>.py (e.g., --xml_test or --gme1_test)"
            echo "  --all                     Run all tests"
            echo "  --report                  Open allure report after test (requires server)"
            echo "  --generate                Generate HTML report to allure-report folder"
            echo "  --skip-check              Skip prerequisite checks"
            echo "  --no-auto                 Don't auto-start missing prerequisites"
            echo "  --help                    Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./shell/run-app.sh --basic_01_test               # STG APK (default)"
            echo "  ./shell/run-app.sh --basic_01_test --stg         # STG APK (explicit)"
            echo "  ./shell/run-app.sh --basic_01_test --live        # Live APK"
            echo "  ./shell/run-app.sh --gme1_test --test test_Login # STG + specific test"
            echo "  ./shell/run-app.sh --app apk/custom.apk          # Custom APK"
            echo "  ./shell/run-app.sh --all --report                # All tests + report"
            echo ""
            echo "iOS Examples:"
            echo "  ./shell/run-ios.sh --ios_contacts_test           # iOS test"
            echo "  ./shell/run-ios.sh --all                         # All iOS tests"
            exit 0
            ;;
        *)
            # Shorthand: treat unknown --<name> as tests/<platform>/<name>.py if it exists.
            if [[ "$1" == --* ]]; then
                SHORT_NAME="${1#--}"
                if [[ -n "$SHORT_NAME" ]]; then
                    # Aliases for renamed files (keep backward compatibility)
                    if [[ "$SHORT_NAME" == "test_xml" || "$SHORT_NAME" == "test_xml.py" ]]; then
                        SHORT_NAME="xml_test"
                    fi

                    CANDIDATE="$SHORT_NAME"
                    if [[ "$CANDIDATE" != *.py ]]; then
                        CANDIDATE="$CANDIDATE.py"
                    fi
                    CANDIDATE_PATH="tests/$PLATFORM/$CANDIDATE"
                    if [[ -f "$CANDIDATE_PATH" ]]; then
                        if [[ -z "$TEST_FILES" ]]; then
                            TEST_FILES="$CANDIDATE_PATH"
                        else
                            TEST_FILES="$TEST_FILES $CANDIDATE_PATH"
                        fi
                        shift
                        continue
                    fi
                fi
            fi

            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ========================================
# APK 자동 설정 (Android 전용, --app 미지정 시)
# ========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$PLATFORM" == "android" && -z "$APP_PATH" ]]; then
    # 기본값: stg
    if [[ -z "$ENV_TYPE" ]]; then
        ENV_TYPE="stg"
    fi

    # .env 파일에서 APK 파일명 로드 (tr -d '\r'로 CRLF 방지)
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        if [[ "$ENV_TYPE" == "stg" ]]; then
            ENV_APK=$(grep -E '^STG_APK=' "$PROJECT_ROOT/.env" | cut -d'=' -f2- | tr -d '\r')
        elif [[ "$ENV_TYPE" == "live" ]]; then
            ENV_APK=$(grep -E '^LIVE_APK=' "$PROJECT_ROOT/.env" | cut -d'=' -f2- | tr -d '\r')
        fi
    fi

    # .env에서 못 읽으면 기본값 사용
    if [[ -z "$ENV_APK" ]]; then
        if [[ "$ENV_TYPE" == "stg" ]]; then
            ENV_APK="${STG_APK:-Stg_GME_7.13.0.apk}"
        elif [[ "$ENV_TYPE" == "live" ]]; then
            ENV_APK="${LIVE_APK:-GME_v7.14.0_03_02_2026 09_35-live-release.apk}"
        fi
    fi

    APP_PATH="$PROJECT_ROOT/apk/$ENV_APK"
fi

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
            $APPIUM_CMD > /dev/null 2>&1 &
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

    # Check 2: Device / Emulator / Simulator (플랫폼별 분기)
    if [[ "$PLATFORM" == "ios" ]]; then
        # ---- iOS Simulator 점검 ----
        echo -n "  - iOS Simulator:            "
        if command -v xcrun &> /dev/null; then
            BOOTED_SIM=$(xcrun simctl list devices booted 2>/dev/null | grep -c "Booted")
            if [[ $BOOTED_SIM -gt 0 ]]; then
                SIM_NAME=$(xcrun simctl list devices booted 2>/dev/null | grep "Booted" | head -1 | sed 's/^[[:space:]]*//' | sed 's/ (.*$//')
                echo -e "${GREEN}Running ($SIM_NAME)${NC}"
                DEVICE_CONNECTED=true
            else
                echo -e "${RED}Not Running${NC}"
                if [[ "$AUTO_START" == true ]]; then
                    echo -e "    ${BLUE}[AUTO] Starting iOS Simulator...${NC}"

                    # 사용 가능한 iPhone 시뮬레이터 찾기
                    SIM_UDID=$(xcrun simctl list devices available 2>/dev/null | grep "iPhone" | head -1 | grep -oE '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}')
                    SIM_NAME=$(xcrun simctl list devices available 2>/dev/null | grep "iPhone" | head -1 | sed 's/^[[:space:]]*//' | sed 's/ (.*$//')

                    if [[ -n "$SIM_UDID" ]]; then
                        echo -e "    ${BLUE}[AUTO] Found simulator: $SIM_NAME${NC}"
                        xcrun simctl boot "$SIM_UDID" 2>/dev/null
                        open -a Simulator 2>/dev/null
                        echo -e "    ${BLUE}[AUTO] Waiting for simulator to boot...${NC}"

                        # 시뮬레이터 부팅 대기 (최대 60초)
                        for i in {1..30}; do
                            sleep 2
                            BOOTED=$(xcrun simctl list devices booted 2>/dev/null | grep -c "Booted")
                            if [[ $BOOTED -gt 0 ]]; then
                                echo -e "    ${GREEN}[OK] Simulator started ($SIM_NAME)${NC}"
                                DEVICE_CONNECTED=true
                                break
                            fi
                            if (( i % 5 == 0 )); then
                                echo -e "    ${BLUE}[AUTO] Still waiting... ($((i*2))s)${NC}"
                            fi
                        done

                        if [[ "$DEVICE_CONNECTED" == false ]]; then
                            echo -e "    ${RED}[FAIL] Simulator boot timeout${NC}"
                        fi
                    else
                        echo -e "    ${RED}[FAIL] No iPhone simulator found. Create one in Xcode.${NC}"
                    fi
                else
                    echo -e "    ${YELLOW}[FIX] Open Simulator app or run: xcrun simctl boot <device_udid>${NC}"
                fi
            fi
        else
            echo -e "${RED}xcrun not found${NC}"
            echo -e "    ${YELLOW}[FIX] Install Xcode Command Line Tools: xcode-select --install${NC}"
        fi
    else
        # ---- Android Emulator / Device 점검 ----
        # ANDROID_HOME 미설정 시 기본 경로 탐색 (macOS)
        if ! command -v adb &> /dev/null; then
            for SDK_PATH in "$HOME/Library/Android/sdk" "/usr/local/share/android-sdk"; do
                if [[ -f "$SDK_PATH/platform-tools/adb" ]]; then
                    export ANDROID_HOME="$SDK_PATH"
                    export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
                    break
                fi
            done
        fi

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

    # Check 4: Appium Driver (플랫폼별 분기)
    if [[ "$PLATFORM" == "ios" ]]; then
        echo -n "  - Appium driver (XCUITest):    "
        if $APPIUM_CMD driver list --installed 2>&1 | grep -qi "xcuitest"; then
            echo -e "${GREEN}Installed${NC}"
        else
            echo -e "${RED}Not Installed${NC}"
            if [[ "$AUTO_START" == true ]]; then
                echo -e "    ${BLUE}[AUTO] Installing XCUITest driver...${NC}"
                if $APPIUM_CMD driver install xcuitest; then
                    echo -e "    ${GREEN}[OK] XCUITest driver installed${NC}"
                else
                    echo -e "    ${RED}[FAIL] Could not install XCUITest driver${NC}"
                fi
            else
                echo -e "    ${YELLOW}[FIX] Run: appium driver install xcuitest${NC}"
            fi
        fi
    else
        echo -n "  - Appium driver (UiAutomator2): "
        if $APPIUM_CMD driver list --installed 2>&1 | grep -qi "uiautomator2"; then
            echo -e "${GREEN}Installed${NC}"
        else
            echo -e "${RED}Not Installed${NC}"
            if [[ "$AUTO_START" == true ]]; then
                echo -e "    ${BLUE}[AUTO] Installing UiAutomator2 driver...${NC}"
                if $APPIUM_CMD driver install uiautomator2; then
                    echo -e "    ${GREEN}[OK] UiAutomator2 driver installed${NC}"
                else
                    echo -e "    ${RED}[FAIL] Could not install UiAutomator2 driver${NC}"
                fi
            else
                echo -e "    ${YELLOW}[FIX] Run: appium driver install uiautomator2${NC}"
            fi
        fi
    fi

    # Check 5: Allure CLI (report)
    echo -n "  - Allure CLI:               "
    if command -v allure &> /dev/null; then
        echo -e "${GREEN}Found (global)${NC}"
    else
        # Prefer local install via npm (npx)
        if npx --yes allure --version > /dev/null 2>&1; then
            ALLURE_CMD="npx --yes allure"
            echo -e "${GREEN}Found (npx/local)${NC}"
        else
            echo -e "${RED}Not Found${NC}"
            if [[ "$AUTO_START" == true ]]; then
                echo -e "    ${BLUE}[AUTO] Installing allure-commandline locally...${NC}"
                if npm install --no-audit --no-fund; then
                    ALLURE_CMD="npx --yes allure"
                    echo -e "    ${GREEN}[OK] allure-commandline installed (use npx allure)${NC}"
                else
                    echo -e "    ${RED}[FAIL] npm install failed (cannot install allure-commandline)${NC}"
                fi
            else
                echo -e "    ${YELLOW}[FIX] Run: npm install (then use npx allure) or install allure globally${NC}"
            fi
        fi
    fi

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
DEFAULT_TARGET="tests/android/gme1_test.py"
if [[ "$PLATFORM" == "ios" ]]; then
    DEFAULT_TARGET="tests/ios"
fi

TARGET="$DEFAULT_TARGET"
if [[ "$RUN_ALL" == true ]]; then
    TARGET="tests/$PLATFORM"
fi
if [[ -n "$TEST_FILES" ]]; then
    TARGET="$TEST_FILES"
fi

CMD="python -m pytest $TARGET -v --platform=$PLATFORM --alluredir=$RESULTS_DIR --record-video --allure-attach=hybrid"

if [[ -n "$APP_PATH" ]]; then
    # Convert MINGW path to Windows path if needed
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        APP_PATH=$(cygpath -w "$APP_PATH" 2>/dev/null || echo "$APP_PATH")
    fi
    CMD="$CMD --app=\"$APP_PATH\""
fi

if [[ "$RUN_ALL" == false && -n "$TEST_NAME" ]]; then
    CMD="$CMD -k $TEST_NAME"
fi

echo "  Platform: $PLATFORM"
if [[ -n "$ENV_TYPE" ]]; then
    echo "  Env:      $ENV_TYPE"
fi
if [[ -n "$APP_PATH" ]]; then
    echo "  App:      $APP_PATH"
fi
if [[ -n "$TEST_FILES" ]]; then
    echo "  Files:    $TEST_FILES"
else
    echo "  Target:   $TARGET"
fi
echo "  Filter:   ${TEST_NAME:-none}"
echo "  Results:  $RESULTS_DIR"
echo ""
echo "----------------------------------------"

# Run tests
eval $CMD
TEST_EXIT_CODE=$?

echo "----------------------------------------"
echo ""

# ========================================
# STEP 4: Generate/Open Allure Report
# ========================================
# Always generate report to timestamp folder
echo "[STEP 4] Generating Allure HTML report..."
if $ALLURE_CMD generate "$RESULTS_DIR" -o "$REPORT_DIR" --clean; then
    echo -e "${GREEN}[OK] Report generated: $REPORT_DIR${NC}"

        # Inject custom CSS to reduce oversized attachment previews (screenshots/videos)
        # without shrinking the whole page text.
        cat > "$REPORT_DIR/custom.css" <<'EOF'
/* Custom Allure overrides (project-local)
     Goal: reduce attachment media preview size without shrinking text.
*/

.attachment__media-container:not(.attachment__media-container_fullscreen) .attachment__media,
.attachment__media-container:not(.attachment__media-container_fullscreen) .attachment__embed {
    max-height: min(42vh, 460px);
    width: auto;
    height: auto;
}

.attachment__media-container:not(.attachment__media-container_fullscreen) video.attachment__media {
    max-height: min(42vh, 460px);
    width: 100%;
}

.attachment__media-container:not(.attachment__media-container_fullscreen) {
    padding: 8px 16px;
}

.attachment__iframe-container:not(.attachment__iframe-container_fullscreen) {
    max-height: min(60vh, 520px);
    overflow: auto;
}

.attachment__filename {
    padding: 10px 16px;
}
EOF

        if [[ -f "$REPORT_DIR/index.html" ]]; then
                if ! grep -q 'href="custom.css"' "$REPORT_DIR/index.html"; then
                        # Insert after styles.css link (best-effort)
                        sed -i 's|<link rel="stylesheet" type="text/css" href="styles.css">|<link rel="stylesheet" type="text/css" href="styles.css">\n    <link rel="stylesheet" type="text/css" href="custom.css">|' "$REPORT_DIR/index.html" 2>/dev/null || true
                fi
        fi
else
    echo -e "${RED}[FAIL] Report generation failed. Is Allure installed?${NC}"
fi

# Update LATEST.txt for next run's history
mkdir -p "allure-reports"
echo "$TIMESTAMP" > "$LATEST_FILE"

# Create/update a stable LATEST entry (no symlinks; works on Windows too)
mkdir -p "allure-reports/LATEST"
cat > "allure-reports/LATEST/index.html" <<EOF
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="refresh" content="0; url=../$TIMESTAMP/index.html" />
        <title>Allure Report - LATEST</title>
    </head>
    <body>
        <p>Redirecting to latest report: <a href="../$TIMESTAMP/index.html">$TIMESTAMP</a></p>
    </body>
</html>
EOF
echo "$TIMESTAMP" > "allure-reports/LATEST/LATEST_TIMESTAMP.txt"

# Generate/update history dashboard (static HTML + runs.json)
python tools/update_dashboard.py --reports-root allure-reports >/dev/null 2>&1 || true

echo ""

if [[ "$OPEN_REPORT" == true ]]; then
    echo "Opening Allure report..."
    echo "  (Press Ctrl+C to stop the server)"
    echo ""
    $ALLURE_CMD open "$REPORT_DIR"
fi

# ========================================
# STEP 5: Upload to Web Dashboard
# ========================================
UPLOAD_SCRIPT="$PROJECT_ROOT/tools/upload_to_dashboard.py"
if [[ -f "$UPLOAD_SCRIPT" ]]; then
    echo "[STEP 5] Uploading to web dashboard..."
    python "$UPLOAD_SCRIPT" "$TIMESTAMP" 2>&1 && \
        echo -e "${GREEN}[OK] Dashboard upload complete${NC}" || \
        echo -e "${YELLOW}[SKIP] Dashboard upload failed (check network or token)${NC}"
    echo ""
else
    echo "[STEP 5] Upload script not found, skipping..."
    echo ""
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
echo "Results:    $RESULTS_DIR"
echo "Report:     $REPORT_DIR"
echo "Dashboard:  https://allure-dashboard-three.vercel.app"
echo ""
echo "To view the local report:"
echo "  allure open $REPORT_DIR"
echo ""

exit $TEST_EXIT_CODE
