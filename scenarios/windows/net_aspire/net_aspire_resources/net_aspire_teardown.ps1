param(
    [string]$logFile = ""
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\net_aspire_teardown.log" }

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

Set-Content -Path $logFile -encoding utf8 "-- net_aspire teardown started ($logSuffix version)"

if (Test-Path "$scriptDrive\aspire") {
    "-- Cleaning Aspire build artifacts" | log
    Set-Location $scriptDrive\aspire
    dotnet clean Aspire.slnx 2>&1 | Out-Null
    "   Clean completed" | log
} else {
    "-- Aspire directory not found, nothing to clean" | log
}

# Kill any lingering dotnet.exe processes
$dotnetProcs = Get-Process -Name "dotnet" -ErrorAction SilentlyContinue
if ($dotnetProcs) {
    "-- Stopping $($dotnetProcs.Count) dotnet.exe process(es)" | log
    $dotnetProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    "   dotnet.exe processes stopped" | log
} else {
    "-- No dotnet.exe processes found" | log
}

"-- net_aspire teardown completed ($logSuffix version)" | log
Exit 0