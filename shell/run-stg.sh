#!/bin/bash

# Run tests with Staging APK
# Delegates to the main runner with --app option
# APK 파일명은 .env의 STG_APK 변수 참조

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# .env 파일에서 STG_APK 로드
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -E '^STG_APK=' "$SCRIPT_DIR/../.env" | xargs)
fi

# STG_APK가 설정되지 않은 경우 기본값 사용
STG_APK="${STG_APK:-[Stg]GME_7.13.0.apk}"
APK_PATH="$SCRIPT_DIR/../apk/$STG_APK"

exec "$SCRIPT_DIR/run-app.sh" --app "$APK_PATH" "$@"
