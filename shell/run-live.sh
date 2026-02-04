#!/bin/bash

# Run tests with Live APK
# Delegates to the main runner with --app option
# APK 파일명은 .env의 LIVE_APK 변수 참조

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# .env 파일에서 LIVE_APK 로드
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -E '^LIVE_APK=' "$SCRIPT_DIR/../.env" | xargs)
fi

# LIVE_APK가 설정되지 않은 경우 기본값 사용
LIVE_APK="${LIVE_APK:-GME_v7.14.0_03_02_2026 09_35-live-release.apk}"
APK_PATH="$SCRIPT_DIR/../apk/$LIVE_APK"

exec "$SCRIPT_DIR/run-app.sh" --app "$APK_PATH" "$@"
