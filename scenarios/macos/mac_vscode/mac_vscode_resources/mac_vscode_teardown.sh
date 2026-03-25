#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

BIN_DIR="/Users/Shared/hobl_bin"
VSCODE_DIR="$BIN_DIR/vscode"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_vscode_teardown.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

echo "-- mac_vscode_teardown.sh started $(date)" > "$LOG_FILE"
log "-- vscode teardown started"

if [ ! -d "$VSCODE_DIR" ]; then
    log " ERROR - VS Code directory not found: $VSCODE_DIR"
    exit 1
fi

cd "$VSCODE_DIR" || { log " ERROR - Failed to change to $VSCODE_DIR"; exit 1; }

# Only clean build outputs that the run script recreates.
# Do NOT remove node_modules — it is installed during prep and must persist across runs.
log "-- Cleaning VS Code build artifacts"
rm -rf .build
rm -rf out

log "-- vscode teardown completed"
exit 0
