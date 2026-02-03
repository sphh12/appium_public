#!/bin/bash

# Run tests with Live APK
# Delegates to the main runner with --app option

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_PATH="$SCRIPT_DIR/../apk/[LiveTest]GME_7.14.0.apk"

exec "$SCRIPT_DIR/run-app.sh" --app "$APK_PATH" "$@"
