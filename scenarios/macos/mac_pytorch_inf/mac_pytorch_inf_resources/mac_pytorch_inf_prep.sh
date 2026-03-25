#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
export SUDO_ASKPASS=$BIN_DIR/get_password.sh
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_pytorch_inf_prep.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Create assets folder if it does not exist and copy all files from the current directory to it
if [ ! -d $BIN_DIR/mac_pytorch_inf_resources ]; then
    log "-- Copying resources to $BIN_DIR/mac_pytorch_inf_resources"
    mkdir -p "$BIN_DIR/mac_pytorch_inf_resources"
    cp -r "$(dirname "$0")"/* "$BIN_DIR/mac_pytorch_inf_resources/"
fi

echo "-- mac_pytorch_inf_prep.sh started $(date)" > "$LOG_FILE"
log "-- pytorch_inf prep started"

log "-- Creating $BIN_DIR/micromamba"
mkdir -p $BIN_DIR/micromamba
cd $BIN_DIR/micromamba

log "-- Downloading micromamba"
curl -Ls https://micro.mamba.pm/api/micromamba/osx-arm64/latest | tar -xvj bin/micromamba

log "-- Initialize shell"
export MAMBA_ROOT_PREFIX=$BIN_DIR/micromamba # optional, defaults to ~/micromamba
eval "$(./bin/micromamba shell hook -s posix)"

log "-- CD to resources"
cd $BIN_DIR/mac_pytorch_inf_resources
if [ $? -ne 0 ]; then
    log " ERROR - Failed to change directory to $BIN_DIR/mac_pytorch_inf_resources"
    exit 1
fi

if [ ! -f "environment_osx.yaml" ]; then
    log " ERROR - environment_osx.yaml file not found"
    exit 1
fi

log "-- Create environment"
micromamba create --file environment_osx.yaml -y
if [ $? -ne 0 ]; then
    log " ERROR - Failed to create micromamba environment from environment_osx.yaml"
    exit 1
fi

log "-- Activate environment"
micromamba activate BUILD_2025_env

log "-- Setup LLM Phi-4-mini inferencing"
python inference.py --setup

log "-- pytorch_inf prep completed"
exit 0