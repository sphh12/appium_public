#!/bin/bash

# Run tests with Staging APK
# Delegates to the main runner with --app option

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_PATH="$SCRIPT_DIR/../apk/[Stg]GME_7.13.0.apk"

exec "$SCRIPT_DIR/run-app.sh" --app "$APK_PATH" "$@"
