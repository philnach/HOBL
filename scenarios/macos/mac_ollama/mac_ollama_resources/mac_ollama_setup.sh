#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_ollama_setup.log"

# Create log directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Initialize log file
echo "-- ollama setup started" > "$LOG_FILE"

log "-- ollama setup started"

# Load environment (homebrew and pyenv)
if [ -f ~/.zprofile ]; then
    source ~/.zprofile
fi
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

cd $BIN_DIR/ollama
if [ $? -ne 0 ]; then
    log " ERROR - Directory does not exist: $BIN_DIR/ollama"
    exit 1
fi

log "-- Building ollama"
go run main.go
if [ $? -ne 0 ]; then
    log " ERROR - Last command failed."
    exit 1
fi

log "-- Launching server in background"
nohup go run . serve > /dev/null 2>&1 &

log "-- Waiting for server to be ready..."
max_attempts=30
attempt=0
server_ready=false

while [ $attempt -lt $max_attempts ] && [ "$server_ready" = "false" ]; do
    attempt=$((attempt + 1))
    sleep 1
    
    # Try to connect to ollama's default endpoint
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:11434/api/tags" | grep -q "200"; then
        server_ready=true
        log "-- Server ready after $attempt seconds"
    else
        log "-- Waiting for server... ($attempt/$max_attempts)"
    fi
done

if [ "$server_ready" = "false" ]; then
    log " ERROR - Server did not start within $max_attempts seconds"
    exit 1
fi

log "-- Pulling gemma3"
go run . pull gemma3
if [ $? -ne 0 ]; then
    log " ERROR - Last command failed."
    exit 1
fi

exit 0