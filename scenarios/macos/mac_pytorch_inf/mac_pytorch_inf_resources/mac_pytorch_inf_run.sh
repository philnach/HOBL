#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_pytorch_inf_run.log"
METRICS_FILE="$LOG_DIR/mac_pytorch_inf_results.csv"

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
echo "-- pytorch_inf run started" > "$LOG_FILE"

log "-- pytorch_inf run started"

# Detect architecture
ARCH=$(uname -m)
log "Detected architecture: $ARCH"

log "-- Initialize micromamba shell"
export MAMBA_ROOT_PREFIX=$BIN_DIR/micromamba
cd $BIN_DIR/micromamba
eval "$(./bin/micromamba shell hook -s posix)"
check $?

log "-- CD to mac_pytorch_inf_resources"
cd $BIN_DIR/mac_pytorch_inf_resources
check $?

log "-- Activate BUILD_2025_env environment"
micromamba activate BUILD_2025_env
check $?

log "-- Performing inferencing with prompt: What is the meaning of life?"

# inference.py writes pytorch_inference_info.csv to --log-dir with these metrics:
#   time_to_first_token_ms, time_to_first_token_s, tokens_per_second,
#   total_tokens_generated, total_generation_time_s, ai_model, ai_device
INFERENCE_CSV="$LOG_DIR/pytorch_inference_info.csv"

python inference.py --prompt "What is the meaning of life?" --log-dir "$LOG_DIR" > "$LOG_DIR/mac_pytorch_inf_output.txt" 2>&1
check $?

log "-- Parsing inference metrics"

# Read metrics from the CSV that inference.py produced (key,value format)
if [ -f "$INFERENCE_CSV" ]; then
    total_generation_time_s=$(grep "^total_generation_time_s," "$INFERENCE_CSV" | cut -d',' -f2)
    time_to_first_token_ms=$(grep "^time_to_first_token_ms," "$INFERENCE_CSV" | cut -d',' -f2)
    time_to_first_token_s=$(grep "^time_to_first_token_s," "$INFERENCE_CSV" | cut -d',' -f2)
    tokens_per_second=$(grep "^tokens_per_second," "$INFERENCE_CSV" | cut -d',' -f2)
    total_tokens_generated=$(grep "^total_tokens_generated," "$INFERENCE_CSV" | cut -d',' -f2)
    ai_model=$(grep "^ai_model," "$INFERENCE_CSV" | cut -d',' -f2)
    ai_device=$(grep "^ai_device," "$INFERENCE_CSV" | cut -d',' -f2)
else
    log " ERROR - Inference metrics file not found: $INFERENCE_CSV"
    exit 1
fi

# Use total_generation_time_s as scenario_runtime
SCENARIO_RUNTIME=${total_generation_time_s:-0}

# ============================================================================
# Save results
# ============================================================================
log ""
log "========================================"
log "PyTorch Inference Metrics Summary"
log "========================================"
log "Time to First Token: ${time_to_first_token_ms}ms (${time_to_first_token_s}s)"
log "Tokens per Second:   $tokens_per_second"
log "Total Tokens:        $total_tokens_generated"
log "Generation Time:     ${total_generation_time_s}s"
log "Model:               $ai_model"
log "Device:              $ai_device"
log "Architecture:        $ARCH"
log "Scenario Runtime:    ${SCENARIO_RUNTIME}s"
log "========================================"

# Write metrics CSV file (key,value format - HOBL convention)
cat > "$METRICS_FILE" << EOF
scenario_runtime,$SCENARIO_RUNTIME
time_to_first_token_ms,$time_to_first_token_ms
time_to_first_token_s,$time_to_first_token_s
tokens_per_second,$tokens_per_second
total_tokens_generated,$total_tokens_generated
total_generation_time_s,$total_generation_time_s
ai_model,$ai_model
ai_device,$ai_device
architecture,$ARCH
EOF
log "Metrics saved to: $METRICS_FILE"

log "-- pytorch_inf run completed"
exit 0