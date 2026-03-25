# Simple Node.js build cleanup script

$scriptDrive = Split-Path -Qualifier $PSScriptRoot

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

# Determine processor architecture for vcbuild parameters
$osInfo = Get-CimInstance Win32_OperatingSystem
$arch = $osInfo.OSArchitecture
$processorArch = $env:PROCESSOR_ARCHITECTURE

if ($arch -eq "64-bit" -and $processorArch -eq "AMD64") {
    $pythonVersion = "3.12.10"
    $arch_version = "x64"
} elseif ($arch -match "ARM" -or $processorArch -match "ARM") {
    $pythonVersion = "3.12.10-arm"
    $arch_version = "arm64"
} else {
    Write-Host " ERROR - Unsupported architecture: $arch (Processor: $processorArch)" -ForegroundColor Red
    Exit 1
}

# Setup pyenv environment (needed for vcbuild.bat to find Python)
$pyenvRoot = "$env:USERPROFILE\.pyenv"
$env:PATH = "$pyenvRoot\pyenv-win\bin;$pyenvRoot\pyenv-win\shims;$env:PATH"

# Navigate to nodejs build directory
cd "$scriptDrive\hobl_bin\nodejs\node-25.0.0"

# Set Python version for vcbuild.bat
pyenv global $pythonVersion

# Get Python paths and set environment variables
$pythonPath = & pyenv which python
$pythonDir = Split-Path $pythonPath -Parent

# Keep WindowsApps in PATH, but de-duplicate the explicit Python directory before prepending
$cleanPath = ($env:PATH -split ';' | Where-Object { $_ -and ($_ -ne $pythonDir) }) -join ';'
$env:PATH = "$pythonDir;$cleanPath"

# Set environment variables for vcbuild.bat
$env:PYTHON = $pythonPath
$env:PYTHONHOME = $pythonDir

Write-Host "Cleaning Node.js build artifacts..."

# Run vcbuild.bat clean
.\vcbuild.bat clean $arch_version openssl-no-asm

# Remove build directories to save space
$dirs_to_remove = @("out", "Release", "Debug")
foreach ($dir in $dirs_to_remove) {
    if (Test-Path $dir) {
        $dirSize = (Get-ChildItem $dir -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Remove-Item -Recurse -Force $dir
        Write-Host "Removed directory: $dir (freed ~$([math]::Round($dirSize, 2)) MB)"
    }
}

Write-Host "Node.js build cleanup completed"