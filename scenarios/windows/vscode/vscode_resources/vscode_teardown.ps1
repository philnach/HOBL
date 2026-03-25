param(
    [string]$logFile = ""
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\vscode_teardown.log" }
$vscodePath = "$scriptDrive\vscode"

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

Set-Content -Path $logFile -encoding utf8 "-- vscode teardown started ($logSuffix version)"

if (-not (Test-Path $vscodePath)) {
    "VS Code directory not found at $vscodePath, nothing to clean" | log
    Exit 0
}

Set-Location $vscodePath

# Only clean build outputs that the run script recreates.
# Do NOT remove node_modules — it is installed during prep and must persist across runs.
"-- Cleaning VS Code build artifacts (preserving node_modules)" | log
if (Test-Path "out") {
    Remove-Item -Recurse -Force "out"
    "Removed out/ directory" | log
}
if (Test-Path ".build") {
    Remove-Item -Recurse -Force ".build"
    "Removed .build/ directory" | log
}
"Build artifacts cleaned" | log

"-- vscode teardown completed ($logSuffix version)" | log
Exit 0
