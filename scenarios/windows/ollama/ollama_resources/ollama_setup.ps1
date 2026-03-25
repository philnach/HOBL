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

# [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
$logFile = "$scriptDrive\hobl_data\ollama_setup.log"

# Ensure log directory exists
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

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
        " ERROR - Last command failed." | log
        Exit $code
    }
}

function checkSetLocation {
    param($path)
    if (Test-Path $path) {
        Set-Location $path
        "Changed directory to: $path" | log
    } else {
        " ERROR - Directory does not exist: $path" | log
        Exit 1
    }
}

Set-Content -Path $logFile -encoding utf8 "-- ollama setup started"

$Env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

checkSetLocation "$scriptDrive\ollama"

# Clean up any existing Ollama processes before starting
"-- Stopping any existing Ollama processes..." | log

# Kill ollama.exe processes
$ollamaProcesses = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcesses) {
    "-- Found existing ollama.exe processes, terminating..." | log
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
} else {
    "-- No ollama.exe processes running..." | log
}

# Also check for ollama_llama_server or related processes
$llamaProcesses = Get-Process -Name "*ollama*" -ErrorAction SilentlyContinue
if ($llamaProcesses) {
    $llamaProcesses | ForEach-Object {
        "-- Terminating $($_.Name) (PID: $($_.Id))..." | log
    }
    $llamaProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    "-- No ollama_llama_server processes running..." | log
}

# Kill go.exe processes
$goProcesses = Get-Process -Name "go" -ErrorAction SilentlyContinue
if ($goProcesses) {
    "-- Found existing go.exe processes, terminating..." | log
    Stop-Process -Name "go" -Force -ErrorAction SilentlyContinue
} else {
    "-- No go.exe processes running..." | log
}

# Give processes time to terminate
Start-Sleep -Seconds 2

"-- Building ollama" | log
go run main.go
check($lastexitcode)

"-- Launching server in background" | log
start-process go.exe -ArgumentList "run . serve" -WindowStyle Hidden

"-- Waiting for server to be ready..." | log
$maxAttempts = 30
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    $attempt++
    Start-Sleep -Seconds 1
    
    try {
        # Try to connect to ollama's default endpoint
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            "-- Server ready after $attempt seconds" | log
        }
    } catch {
        "-- Waiting for server... ($attempt/$maxAttempts)" | log
    }
}

if (-not $serverReady) {
    " ERROR - Server did not start within $maxAttempts seconds" | log
    Exit 1
}

"-- Pulling gemma3" | log
go run . pull gemma3
check($lastexitcode)

Exit 0