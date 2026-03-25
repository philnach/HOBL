#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_nodejs_teardown.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

echo "-- mac_nodejs_teardown.sh started $(date)" > "$LOG_FILE"
log "-- nodejs teardown started"

# Navigate to nodejs source directory
cd $BIN_DIR/node-25.0.0

log "-- Cleaning Node.js build artifacts"
make clean

log "-- nodejs teardown completed"
exit 0