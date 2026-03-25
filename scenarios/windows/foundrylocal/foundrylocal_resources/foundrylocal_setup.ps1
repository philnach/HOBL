param(
    [string]$logFile = "",
    [string]$model = "Phi-3.5-mini-instruct-generic-cpu"
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\foundrylocal_setup.log" }

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

# Determine processor architecture
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

function check {
    param($code)
    if ($code -ne 0) {
        " ERROR - Last command failed with exit code: $code" | log
        Exit $code
    }
}

Set-Content -Path $logFile -encoding utf8 "-- Foundry Local setup started ($logSuffix version)"

"Detected architecture: $arch (Processor: $processorArch)" | log
"Model to download: $model" | log

# Refresh PATH to ensure foundry is available
$Env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# ============================================================================
# Step 1: Start Foundry service
# ============================================================================
"Step 1: Starting Foundry service..." | log

"Running: foundry service start (in background)" | log
Start-Process -FilePath "foundry" -ArgumentList "service", "start" -WindowStyle Hidden

# Wait for service to be ready
"Waiting for Foundry service to be ready..." | log
$maxAttempts = 90
$attempt = 0
$serviceReady = $false

while ($attempt -lt $maxAttempts -and -not $serviceReady) {
    $attempt++
    Start-Sleep -Seconds 1
    
    $statusOutput = & foundry service status 2>&1
    $statusText = $statusOutput -join "`n"
    
    if ($statusText -match "running|Successfully|Valid EPs") {
        $serviceReady = $true
        "Foundry service ready after $attempt seconds" | log
        $statusOutput | ForEach-Object { "  $_" | log }
    } else {
        "Waiting for service... ($attempt/$maxAttempts)" | log
    }
}

if (-not $serviceReady) {
    " ERROR - Foundry service did not start within $maxAttempts seconds" | log
    "Last status output: $statusText" | log
    Exit 1
}

# ============================================================================
# Step 2: Download model to cache
# ============================================================================
"Step 2: Downloading model to local cache..." | log

"Running: foundry model download $model" | log
$startTime = Get-Date

foundry model download $model 2>&1 | ForEach-Object { "  $_" | log }
check $LASTEXITCODE

$endTime = Get-Date
$duration = $endTime - $startTime
"Model download completed in $($duration.TotalSeconds) seconds" | log

# ============================================================================
# Step 3: Verify model is cached
# ============================================================================
"Step 3: Verifying model is cached..." | log

"Listing cached models:" | log
$cacheOutput = & foundry cache list 2>&1
$cacheOutput | ForEach-Object { "  $_" | log }

$cacheText = $cacheOutput -join "`n"
if ($cacheText -match [regex]::Escape($model)) {
    "Model '$model' verified in cache" | log
} else {
    " ERROR - Model '$model' not found in cache" | log
    Exit 1
}

# ============================================================================
# Summary
# ============================================================================
"" | log
"========================================" | log
"Foundry Local setup completed successfully ($logSuffix version)" | log
"Model: $model" | log
"Download time: $($duration.TotalSeconds) seconds" | log
"========================================" | log
"Log file: $logFile" | log

Exit 0
