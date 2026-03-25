#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# AI Foundry Local prep script for macOS
# Installs Foundry Local from GitHub release (version-controlled)

BIN_DIR="/Users/Shared/hobl_bin"
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_foundrylocal_prep.log"
FOUNDRY_DIR="$HOME/foundry"
FOUNDRY_VERSION="${1:-0.8.117}"
export SUDO_ASKPASS=$BIN_DIR/get_password.sh

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
echo "-- Foundry Local prep started" > "$LOG_FILE"

log "-- Foundry Local prep started"

# Detect architecture
ARCH=$(uname -m)
log "Detected architecture: $ARCH"

if [ "$ARCH" != "arm64" ]; then
    log " ERROR - Foundry Local for macOS is only available for Apple Silicon (arm64)"
    log "Current architecture: $ARCH"
    exit 1
fi

if [ ! -d "$BIN_DIR" ]; then
    log " ERROR - Directory $BIN_DIR does not exist"
    exit 1
fi

log "Target Foundry version: $FOUNDRY_VERSION"

# ============================================================================
# Step 1: Ensure Xcode command-line tools are installed
# ============================================================================
log "Step 1: Checking for Xcode command-line tools..."

if ! xcode-select -p &> /dev/null; then
    log "Installing Xcode command-line tools..."
    xcode-select --install
    # Wait for installation to complete
    log "Waiting for Xcode tools installation..."
    until xcode-select -p &> /dev/null; do
        sleep 5
    done
    log "Xcode command-line tools installed"
else
    log "Xcode command-line tools already installed"
fi

# ============================================================================
# Step 2: Download and install Foundry Local from GitHub release
# ============================================================================
log "Step 2: Installing AI Foundry Local version $FOUNDRY_VERSION..."

# Create foundry directory
if [ ! -d "$FOUNDRY_DIR" ]; then
    log "Creating directory: $FOUNDRY_DIR"
    mkdir -p "$FOUNDRY_DIR"
fi

cd "$FOUNDRY_DIR"

# Define download URL and filename
ZIP_FILENAME="FoundryLocal-osx-arm64-${FOUNDRY_VERSION}.zip"
DOWNLOAD_URL="https://github.com/microsoft/Foundry-Local/releases/download/v${FOUNDRY_VERSION}/${ZIP_FILENAME}"
EXTRACT_DIR="FoundryLocal-osx-arm64"

log "Downloading from: $DOWNLOAD_URL"
curl -Ls "$DOWNLOAD_URL" -o "$ZIP_FILENAME"
check $?

log "Download complete. Extracting..."
unzip -o "$ZIP_FILENAME" -d "$FOUNDRY_DIR" 2>&1 | while read line; do log "  $line"; done
check $?

# ============================================================================
# Step 3: Run the install script
# ============================================================================
log "Step 3: Running Foundry Local installer..."

INSTALL_DIR="$FOUNDRY_DIR/$EXTRACT_DIR"
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR"
    log "Running: ./install-foundry.command"
    ./install-foundry.command 2>&1 | while read line; do log "  $line"; done
    check $?
else
    log " ERROR - Install directory not found: $INSTALL_DIR"
    exit 1
fi

# ============================================================================
# Step 4: Verify installation
# ============================================================================
log "Step 4: Verifying Foundry Local installation..."

# Source .zshrc to pick up PATH changes made by install-foundry.command
if [ -f "$HOME/.zshrc" ]; then
    log "Sourcing ~/.zshrc to refresh PATH..."
    source "$HOME/.zshrc"
fi

# Also add the path directly in case sourcing doesn't work in sh
export PATH="$HOME/bin:$PATH"

if command -v foundry &> /dev/null; then
    FOUNDRY_PATH=$(which foundry)
    log "Foundry command found at: $FOUNDRY_PATH"
    
    # Get version info
    log "Getting Foundry version..."
    VERSION_OUTPUT=$(foundry --version 2>&1)
    log "  $VERSION_OUTPUT"
else
    log " ERROR - Foundry command not found after installation"
    log "Please ensure Foundry Local is installed correctly"
    exit 1
fi

# ============================================================================
# Cleanup
# ============================================================================
log "Cleaning up downloaded files..."
rm -f "$FOUNDRY_DIR/$ZIP_FILENAME"

# ============================================================================
# Summary
# ============================================================================
log ""
log "========================================"
log "Foundry Local prep completed successfully"
log "Version: $FOUNDRY_VERSION"
log "Architecture: $ARCH"
log "========================================"
log "Log file: $LOG_FILE"

exit 0
