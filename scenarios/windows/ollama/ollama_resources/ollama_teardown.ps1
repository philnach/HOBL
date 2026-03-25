# Ollama cleanup/teardown script

param(
    [string]$logFile = ""
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\ollama_teardown.log" }

# Require PowerShell > 7
$required = [version]"7.0"
if (-not $PSVersionTable.PSVersion) {
    Write-Host "Cannot determine PowerShell version; aborting." -ForegroundColor Red
    Exit 1
}
if ([version]$PSVersionTable.PSVersion -le $required) {
    Write-Host "This script requires PowerShell greater than $required. Current: $($PSVersionTable.PSVersion)" -ForegroundColor Yellow
    Write-Host "Please install PowerShell 7 or later from https://aka.ms/powershell" -ForegroundColor Yellow
    Exit 1
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Determine processor architecture for log file naming
$osInfo = Get-CimInstance Win32_OperatingSystem
$arch = $osInfo.OSArchitecture
$processorArch = $env:PROCESSOR_ARCHITECTURE

if ($arch -eq "64-bit" -and $processorArch -eq "AMD64") {
    $logSuffix = "x64"
} elseif ($arch -match "ARM" -or $processorArch -match "ARM") {
    $logSuffix = "ARM64"
} else {
    Write-Host " ERROR - Unsupported architecture: $arch (Processor: $processorArch)" -ForegroundColor Red
    Exit 1
}

# Update log file name to include architecture
$logFile = $logFile -replace "\.log$", "_$($logSuffix.ToLower()).log"

# Ollama source directory
$ollamaDir = "$scriptDrive\ollama"

function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match " ERROR - ") {
            Write-Host $msg -ForegroundColor Red
        } else {
            Write-Host $msg
        }
        Add-Content -Path $logFile -encoding utf8 "$msg"
    }
}

# Refresh PATH to ensure go is available
$Env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# ============================================================================
# Step 1: Remove the gemma3 model using go run
# ============================================================================
"Step 1: Removing gemma3 model..." | log

try {
    if (Test-Path $ollamaDir) {
        Push-Location $ollamaDir
        
        # List current models before removal
        "Current models:" | log
        $models = & go run . list 2>&1
        $models | ForEach-Object { "  $_" | log }
        
        # Remove gemma3 model
        "Removing gemma3 model via 'go run . rm gemma3'..." | log
        $result = & go run . rm gemma3 2>&1
        $result | ForEach-Object { "  $_" | log }
        "gemma3 model removal attempted" | log
        
        Pop-Location
    } else {
        "Ollama source directory not found at $ollamaDir, skipping model removal" | log
    }
} catch {
    "Warning: Failed to remove gemma3 model: $_" | log
}

# ============================================================================
# Step 2: Kill ollama.exe background process
# ============================================================================
"Step 2: Killing ollama.exe process..." | log

try {
    $ollamaProcesses = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if ($ollamaProcesses) {
        $ollamaProcesses | ForEach-Object {
            "Killing ollama.exe process (PID: $($_.Id))" | log
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        "ollama.exe processes terminated" | log
    } else {
        "No ollama.exe processes found" | log
    }
    
    # Also check for ollama_llama_server or related processes
    $llamaProcesses = Get-Process -Name "*ollama*" -ErrorAction SilentlyContinue
    if ($llamaProcesses) {
        $llamaProcesses | ForEach-Object {
            "Killing $($_.Name) process (PID: $($_.Id))" | log
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
} catch {
    "Warning: Failed to kill ollama processes: $_" | log
}

# ============================================================================
# Step 3: Kill go.exe process (started the ollama server)
# ============================================================================
"Step 3: Killing go.exe process..." | log

try {
    $goProcesses = Get-Process -Name "go" -ErrorAction SilentlyContinue
    if ($goProcesses) {
        $goProcesses | ForEach-Object {
            "Killing go.exe process (PID: $($_.Id))" | log
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        "go.exe processes terminated" | log
    } else {
        "No go.exe processes found" | log
    }
} catch {
    "Warning: Failed to kill go.exe: $_" | log
}

# Give processes time to terminate
Start-Sleep -Seconds 2

# ============================================================================
# Step 4: Full cleanup - remove all Ollama data and build artifacts
# ============================================================================
"Step 4: Performing full cleanup of Ollama data and build artifacts..." | log

# Remove Ollama models directory
$ollamaModelsPath = "$env:USERPROFILE\.ollama"
if (Test-Path $ollamaModelsPath) {
    try {
        $dirSize = (Get-ChildItem $ollamaModelsPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        "Removing Ollama data directory: $ollamaModelsPath (size: ~$([math]::Round($dirSize, 2)) GB)" | log
        Remove-Item -Recurse -Force $ollamaModelsPath -ErrorAction Stop
        "Ollama data directory removed successfully" | log
    } catch {
        " ERROR - Failed to remove Ollama data directory: $_" | log
    }
} else {
    "Ollama data directory not found at $ollamaModelsPath" | log
}

# Clean only dist directory (keeps the repo, build artifacts, and Go can still `go run .`)
# Note: We preserve the cmake `build` directory because `go run . serve` may depend on
# native llama.cpp libraries compiled there
if (Test-Path $ollamaDir) {
    try {
        Push-Location $ollamaDir
        
        # Remove dist directory if it exists (standalone binary output, not needed for go run)
        $distDir = Join-Path $ollamaDir "dist"
        if (Test-Path $distDir) {
            $dirSize = (Get-ChildItem $distDir -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
            "Removing dist directory: $distDir (size: ~$([math]::Round($dirSize, 2)) MB)" | log
            Remove-Item -Recurse -Force $distDir -ErrorAction Stop
            "dist directory removed successfully" | log
        }
        
        Pop-Location
        "Ollama cleanup completed (repo, build artifacts, and Go modules preserved for next run)" | log
    } catch {
        " ERROR - Failed to clean Ollama artifacts: $_" | log
    }
} else {
    "Ollama source directory not found at $ollamaDir" | log
}

# ============================================================================
# Summary
# ============================================================================
"" | log
"========================================" | log
"Ollama teardown completed" | log
"========================================" | log
"Log file: $logFile" | log
