#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# AI Foundry Local run script for macOS
# Runs inference with the specified model and prompt

BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_foundrylocal_run.log"
MODEL="${1:-Phi-3.5-mini-instruct-generic-cpu}"
PROMPT="${2:-What is the meaning of life?}"

# Remove surrounding quotes from prompt if present
PROMPT=$(echo "$PROMPT" | sed 's/^"//;s/"$//')

# Create log directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

check() {
    if [ $1 -ne 0 ]; then
        log " ERROR - Last command failed with exit code: $1"
        exit $1
    fi
}

# Clear log file
echo "-- Foundry Local run started" > "$LOG_FILE"

log "-- Foundry Local run started"

# Detect architecture
ARCH=$(uname -m)
log "Detected architecture: $ARCH"
log "Model: $MODEL"
log "Prompt: $PROMPT"

# Load environment (homebrew)
if [ -f ~/.zprofile ]; then
    source ~/.zprofile
fi
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

# Add foundry to PATH (installed via install-foundry.command)
export PATH="$HOME/bin:$PATH"

# ============================================================================
# Run inference
# ============================================================================
log "Running inference..."
log "Command: foundry model run $MODEL --prompt \"$PROMPT\""

START_TIME=$(date +%s.%N)

# Run the model and capture output
OUTPUT_FILE="$LOG_DIR/mac_foundrylocal_output.txt"
foundry model run "$MODEL" --prompt "$PROMPT" > "$OUTPUT_FILE" 2>&1
EXIT_CODE=$?

END_TIME=$(date +%s.%N)

# Calculate duration
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

# Log the output
log ""
log "=== Model Output ==="
while read line; do log "  $line"; done < "$OUTPUT_FILE"
log "===================="

check $EXIT_CODE

SCENARIO_RUNTIME=$(printf "%.2f" $DURATION)

log ""
log "Scenario completed in $SCENARIO_RUNTIME seconds"

# ============================================================================
# Save results
# ============================================================================
RESULTS_FILE="$LOG_DIR/mac_foundrylocal_results.csv"

# Save results file (HOBL convention: *_results.csv with key,value pairs for rollup)
# scenario_runtime is the standard metric name for execution time in seconds
cat > "$RESULTS_FILE" << EOF
scenario_runtime,$SCENARIO_RUNTIME
architecture,$ARCH
model,$MODEL
prompt,$PROMPT
EOF

log "Results saved to: $RESULTS_FILE"

# ============================================================================
# Summary
# ============================================================================
log ""
log "========================================"
log "Foundry Local run completed successfully"
log "Model: $MODEL"
log "Scenario runtime: $SCENARIO_RUNTIME seconds"
log "========================================"
log "Log file: $LOG_FILE"

exit 0
