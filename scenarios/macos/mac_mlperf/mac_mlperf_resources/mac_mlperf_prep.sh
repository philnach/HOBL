#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# MLPerf Client Prep Script for macOS
# This script extracts the MLPerf client from an offline zip file

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
export SUDO_ASKPASS=$BIN_DIR/get_password.sh
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_mlperf_prep.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Get the mlperf client zip path from argument
MLPERF_CLIENT_PATH="$1"

echo "-- mac_mlperf_prep.sh started $(date)" > "$LOG_FILE"
log "-- MLPerf prep started"

# Detect processor architecture
ARCH=$(uname -m)
log "-- Detected architecture: $ARCH"

# Create mlperf directory if it doesn't exist
MLPERF_DIR="$BIN_DIR/mac_mlperf"
if [ ! -d "$MLPERF_DIR" ]; then
    log "-- Creating directory: $MLPERF_DIR"
    mkdir -p "$MLPERF_DIR"
else
    log "-- Directory already exists: $MLPERF_DIR"
fi

# Check if mlperf client path was provided
if [ -z "$MLPERF_CLIENT_PATH" ]; then
    log " ERROR - No MLPerf client zip file path provided"
    log "Usage: $0 <path_to_mlperf_client_zip>"
    exit 1
fi

# Verify the zip file exists
if [ ! -f "$MLPERF_CLIENT_PATH" ]; then
    log " ERROR - MLPerf client zip file not found: $MLPERF_CLIENT_PATH"
    exit 1
fi

log "-- Using MLPerf client zip: $MLPERF_CLIENT_PATH"

# Extract the zip file
log "-- Extracting MLPerf archive..."
log "   Source: $MLPERF_CLIENT_PATH"
log "   Destination: $MLPERF_DIR"

unzip -o "$MLPERF_CLIENT_PATH" -d "$MLPERF_DIR"
if [ $? -ne 0 ]; then
    log " ERROR - Failed to extract MLPerf archive"
    exit 1
fi

log "-- MLPerf archive extracted successfully"

# Verify extraction
MLPERF_EXE="$MLPERF_DIR/mlperf-mac"
if [ -f "$MLPERF_EXE" ]; then
    log "SUCCESS: MLPerf executable found at: $MLPERF_EXE"
    # Make executable
    chmod +x "$MLPERF_EXE"
    log "-- Made executable: $MLPERF_EXE"
else
    log " ERROR - MLPerf executable not found after extraction"
    exit 1
fi

# List contents for verification
log "-- Contents of $MLPERF_DIR:"
ls -lR "$MLPERF_DIR"

log "-- MLPerf prep completed successfully"
exit 0
