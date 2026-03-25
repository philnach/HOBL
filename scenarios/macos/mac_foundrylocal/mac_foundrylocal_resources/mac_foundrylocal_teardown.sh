#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# AI Foundry Local teardown script for macOS
# Removes the model from cache and stops the service

BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_foundrylocal_teardown.log"
MODEL="${1:-phi-3.5-mini}"

# Create log directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Clear log file
echo "-- Foundry Local teardown started" > "$LOG_FILE"

log "-- Foundry Local teardown started"
log "Model to remove: $MODEL"

# Load environment (homebrew)
if [ -f ~/.zprofile ]; then
    source ~/.zprofile
fi
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

# Add foundry to PATH (installed via install-foundry.command)
export PATH="$HOME/bin:$PATH"

# ============================================================================
# Remove model from cache
# ============================================================================
log "Removing model from cache..."

if command -v foundry &> /dev/null; then
    FOUNDRY_PATH=$(which foundry)
    log "Foundry command found at: $FOUNDRY_PATH"
    
    # Remove model from cache
    log "Running: foundry cache remove $MODEL --yes"
    OUTPUT=$(foundry cache remove "$MODEL" --yes 2>&1)
    echo "$OUTPUT" | while read line; do log "  $line"; done
    
    if [ $? -eq 0 ]; then
        log "Model removed successfully"
    else
        log "Warning: Model removal returned non-zero exit code (model may not have been cached)"
    fi
    
    # Stop the Foundry service
    log "Running: foundry service stop"
    OUTPUT=$(foundry service stop 2>&1)
    echo "$OUTPUT" | while read line; do log "  $line"; done
    
    if [ $? -eq 0 ]; then
        log "Foundry service stopped successfully"
    else
        log "Warning: Foundry service stop returned non-zero exit code"
    fi
else
    log "Warning: Foundry command not found, skipping service stop and cache removal"
fi

# ============================================================================
# Summary
# ============================================================================
log ""
log "========================================"
log "Foundry Local teardown completed"
log "========================================"
log "Log file: $LOG_FILE"

exit 0
