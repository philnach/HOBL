#!/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Set BIN_DIR to /Users/Shared/hobl_bin
BIN_DIR="/Users/Shared/hobl_bin"
export SUDO_ASKPASS=$BIN_DIR/get_password.sh
LOG_DIR="/Users/Shared/hobl_data"
LOG_FILE="$LOG_DIR/mac_spring_petclinic_prep.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$1"
    echo "$1" >> "$LOG_FILE"
}

# Helper function for error checking
check_status() {
    if [ $? -ne 0 ]; then
        log " ERROR - $1 failed"
        exit 1
    fi
    log "✓ $1 successful"
}

# Helper function to verify command exists
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        log "✓ $1 is available"
        return 0
    else
        log " ERROR - $1 is not available"
        return 1
    fi
}

echo "-- mac_spring_petclinic_prep.sh started $(date)" > "$LOG_FILE"
log "-- Spring Petclinic prep started"

# Check if BIN_DIR exists
if [ ! -d "$BIN_DIR" ]; then
    log " ERROR - $BIN_DIR does not exist"
    exit 1
fi
log "✓ BIN_DIR exists: $BIN_DIR"

# Installing XCode tools
log "-- Installing XCode tools"
if xcode-select -p >/dev/null 2>&1; then
    log "✓ XCode tools already installed"
else
    xcode-select --install 2>/dev/null || true
    
    # Wait for installation to complete (up to 10 minutes)
    log "Waiting for XCode tools installation to complete..."
    MAX_WAIT=600  # 10 minutes
    ELAPSED=0
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        if xcode-select -p >/dev/null 2>&1; then
            log "✓ XCode tools installation completed"
            break
        fi
        sleep 10
        ELAPSED=$((ELAPSED + 10))
        log "  Still waiting... ($ELAPSED seconds elapsed)"
    done
    
    # Final verification
    if ! xcode-select -p >/dev/null 2>&1; then
        log " ERROR - XCode tools installation did not complete within $MAX_WAIT seconds"
        log "Please install XCode tools manually and re-run this script"
        exit 1
    fi
fi

cd $BIN_DIR || {
    log " ERROR - Failed to change to $BIN_DIR"
    exit 1
}

# Clone repo (or verify it exists)
log "-- Cloning repo"
if [ -d "$BIN_DIR/spring-petclinic" ]; then
    log "✓ Spring Petclinic repo already exists"
    cd $BIN_DIR/spring-petclinic
    git pull origin main 2>/dev/null || true
else
    git clone https://github.com/spring-projects/spring-petclinic.git
    check_status "Git clone"
    cd $BIN_DIR/spring-petclinic
fi

# Install Brew (or verify it exists at default location)
log "-- Installing Brew"
if [ -x /opt/homebrew/bin/brew ]; then
    log "✓ Brew already installed at /opt/homebrew/bin/brew"
else
    export NONINTERACTIVE=1
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    check_status "Brew installation"
fi

# Verify brew is installed at expected location
if [ ! -x /opt/homebrew/bin/brew ]; then
    log " ERROR - Homebrew not found at /opt/homebrew/bin/brew"
    exit 1
fi
log "✓ Homebrew verified at /opt/homebrew/bin/brew"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify brew command is available
check_command "brew" || exit 1

log "-- Installing Microsoft OpenJDK 25"
if brew list --cask microsoft-openjdk@25 >/dev/null 2>&1; then
    log "✓ Microsoft OpenJDK 25 already installed"
else
    brew install --cask microsoft-openjdk@25
    if [ $? -ne 0 ]; then
        log " ERROR - Failed to install Microsoft OpenJDK 25"
        log "You may need to manually run this script to enter password for sudo commands"
        exit 1
    fi
    log "✓ Microsoft OpenJDK 25 installed"
fi

# Verify Java is available
log "-- Verifying Java installation"
if [ -x /Library/Java/JavaVirtualMachines/microsoft-25.jdk/Contents/Home/bin/java ]; then
    JAVA_HOME="/Library/Java/JavaVirtualMachines/microsoft-25.jdk/Contents/Home"
    export JAVA_HOME
    export PATH="$JAVA_HOME/bin:$PATH"
    log "✓ Java found at $JAVA_HOME"
else
    log " ERROR - Java not found at expected location"
    exit 1
fi

check_command "java" || exit 1

# Verify Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | awk -F '.' '{print $1}')
if [ "$JAVA_VERSION" = "25" ]; then
    log "✓ Java version confirmed: 25"
else
    log " ERROR - Java version is $JAVA_VERSION, expected 25"
    java -version
    exit 1
fi

log "-- Create local Maven directory"
if [ ! -d "$BIN_DIR/m2-spring-petclinic" ]; then
    mkdir $BIN_DIR/m2-spring-petclinic
    check_status "Creating Maven directory"
else
    log "✓ Maven directory already exists"
fi

# Verify mvnw wrapper exists
if [ ! -f "./mvnw" ]; then
    log " ERROR - Maven wrapper (mvnw) not found in repository"
    exit 1
fi
log "✓ Maven wrapper found"

# Make mvnw executable
chmod +x ./mvnw
check_status "Making mvnw executable"

log "-- Warm Maven cache online"
./mvnw -Dmaven.repo.local=$BIN_DIR/m2-spring-petclinic -DskipTests dependency:go-offline
check_status "Maven dependency go-offline"

log "-- Clean and verify build online"
./mvnw -Dmaven.repo.local=$BIN_DIR/m2-spring-petclinic clean verify
check_status "Maven clean verify"

# Final verification
log ""
log "-- Running final verification checks --"
check_command "git" || exit 1
check_command "brew" || exit 1
check_command "java" || exit 1

# Verify target directory was created
if [ -d "./target" ]; then
    log "✓ Build target directory exists"
else
    log " ERROR - Build target directory not found"
    exit 1
fi

# Verify JAR file was created
JAR_FILE=$(find ./target -name "spring-petclinic-*.jar" -type f 2>/dev/null | head -n 1)
if [ -n "$JAR_FILE" ]; then
    log "✓ Spring Petclinic JAR found: $(basename $JAR_FILE)"
else
    log " ERROR - Spring Petclinic JAR not found in target directory"
    exit 1
fi

log ""
log "✓ All checks passed - Machine is ready to run Spring Petclinic"
log "-- Spring Petclinic prep completed successfully"
exit 0