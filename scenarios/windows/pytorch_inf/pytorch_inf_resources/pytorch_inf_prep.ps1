param(
    [string]$logFile = ""
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not (Test-Path "$scriptDrive\hobl_data")) {
    Write-Host " ERROR - Required directory not found: $scriptDrive\hobl_data" -ForegroundColor Red
    Exit 1
}
if (-not (Test-Path "$scriptDrive\hobl_bin")) {
    Write-Host " ERROR - Required directory not found: $scriptDrive\hobl_bin" -ForegroundColor Red
    Exit 1
}
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\pytorch_inf_prep.log" }

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

function checkCmd {
    param($code)
    if ($code -ne "True") {
        " ERROR - Last command failed." | log
        Exit 1
    }
}

Set-Content -Path $logFile -encoding utf8 "-- pytorch_inf prep started"

"-- Creating $scriptDrive\hobl_bin\micromamba" | log
New-Item -ItemType Directory -Force -Path "$scriptDrive\hobl_bin\micromamba" > $null
cd "$scriptDrive\hobl_bin\micromamba"

"-- Downloading micromamba" | log
Invoke-Webrequest -URI https://micro.mamba.pm/api/micromamba/win-64/latest -OutFile micromamba.tar.bz2
checkCmd($?)

"-- Uncompressing micromamba" | log
tar xf micromamba.tar.bz2
check($lastexitcode)

"-- Move micromamba" | log
Move-Item -Force -Path Library\bin\micromamba.exe -Destination micromamba.exe
check($lastexitcode)

"-- Initialize shell" | log
$Env:MAMBA_ROOT_PREFIX="$scriptDrive\hobl_bin\micromamba"
.\micromamba.exe shell hook -s powershell | Out-String | Invoke-Expression
checkCmd($?)

"-- Setting up pytorch_inf_resources in $scriptDrive\hobl_bin\pytorch_inf_resources" | log
if ($PSScriptRoot -ne "$scriptDrive\hobl_bin\pytorch_inf_resources") {
    if (-not (Test-Path "$scriptDrive\hobl_bin\pytorch_inf_resources")) {
        New-Item -ItemType Directory -Force -Path "$scriptDrive\hobl_bin\pytorch_inf_resources" | Out-Null
    }
    Copy-Item -Path "$PSScriptRoot\*" -Destination "$scriptDrive\hobl_bin\pytorch_inf_resources" -Exclude "*.ps1" -Force
    "Resources copied from $PSScriptRoot" | log
} else {
    "Already running from target directory, skipping copy" | log
}

Set-Location "$scriptDrive\hobl_bin\pytorch_inf_resources"
checkCmd($?)

"-- Create environment" | log
micromamba create --file environment_win.yaml -y
checkCmd($?)

"-- Activate environment" | log
micromamba activate BUILD_2025_env
checkCmd($?)

"-- Setup LLM Phi-4-mini inferencing" | log
python inference.py --setup
check($lastexitcode)

"-- pytorch_inf prep completed" | log
Exit 0