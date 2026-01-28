#!/bin/bash
# Live/Production 환경용 테스트 실행 스크립트
# 사용법: ./shell/run-live.sh [옵션]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_PATH="$SCRIPT_DIR/../apk/your_live_app.apk"

# run-app.sh에 APK 경로 전달
"$SCRIPT_DIR/run-app.sh" --app "$APK_PATH" "$@"
