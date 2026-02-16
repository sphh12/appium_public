#!/bin/bash

# Android 테스트 실행 스크립트
# run-app.sh에 --platform android 옵션을 전달하는 래퍼 스크립트
#
# Usage:
#   ./shell/run-aos.sh                              # tests/android/ 전체 실행
#   ./shell/run-aos.sh --basic_01_test              # 특정 테스트 파일 실행
#   ./shell/run-aos.sh --gme1_test --test test_Login # 특정 테스트 메서드 실행
#   ./shell/run-aos.sh --stg --basic_01_test        # STG APK + 특정 테스트
#   ./shell/run-aos.sh --live --gme1_test           # Live APK + 특정 테스트
#   ./shell/run-aos.sh --report                     # 실행 후 Allure 리포트 열기

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run-app.sh" --platform android "$@"
