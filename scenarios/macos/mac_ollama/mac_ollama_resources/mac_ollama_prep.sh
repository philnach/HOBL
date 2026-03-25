#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_ollama_prep.log"
export SUDO_ASKPASS=$BIN_DIR/get_password.sh

# Create log directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Initialize log file
echo "-- ollama prep started" > "$LOG_FILE"

log "-- ollama prep started"

log "-- Installing XCode tools"
xcode-select --install

if [ ! -d "$BIN_DIR" ]; then
    log " ERROR - Directory $BIN_DIR does not exist"
    exit 1
fi

log "-- Changing to $BIN_DIR"
cd $BIN_DIR

log "-- Cloning repo"
git clone https://github.com/ollama/ollama.git
cd $BIN_DIR/ollama
log "-- Checkout version 0.12.1"
git checkout v0.12.1

log "-- Install Brew"
export NONINTERACTIVE=1
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

log "-- Install go"
brew install go@1.25

# go@1.25 is keg-only and not symlinked into /opt/homebrew, add to PATH
export PATH="/opt/homebrew/opt/go@1.25/bin:$PATH"

# Persist to ~/.zprofile if not already present
if ! grep -q 'go@1.25/bin' ~/.zprofile 2>/dev/null; then
    echo '' >> ~/.zprofile
    echo '# Added by ollama prep - go@1.25 is keg-only' >> ~/.zprofile
    echo 'export PATH="/opt/homebrew/opt/go@1.25/bin:$PATH"' >> ~/.zprofile
    log "-- Added go@1.25 to ~/.zprofile"
else
    log "-- go@1.25 already in ~/.zprofile"
fi

log "-- Download modules"
cd $BIN_DIR/ollama
go mod tidy

log "-- ollama prep completed"
exit 0