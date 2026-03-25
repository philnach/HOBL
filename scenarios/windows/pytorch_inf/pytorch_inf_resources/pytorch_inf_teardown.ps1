# param(
#     [string]$logFile = "c:\hobl_data\pytorch_inf_prep.log"
# )

$scriptDrive = Split-Path -Qualifier $PSScriptRoot

function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match " ERROR - ") {
            Write-Host $msg -ForegroundColor Red
        } else {
            Write-Host $msg
        }
        # Add-Content -Path $logFile -encoding utf8 "$msg"
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

# Set-Content -Path $logFile -encoding utf8 "-- pytorch_inf prep started"
"-- pytorch_inf teardown started" | log

"-- Initialize shell" | log
$Env:MAMBA_ROOT_PREFIX="$scriptDrive\hobl_bin\micromamba"
cd "$scriptDrive\hobl_bin\micromamba"
checkCmd($?)
.\micromamba.exe shell hook -s powershell | Out-String | Invoke-Expression
checkCmd($?)

"-- CD to resources" | log
cd "$scriptDrive\hobl_bin\pytorch_inf_resources"
checkCmd($?)

"-- Activate environment" | log
micromamba activate BUILD_2025_env
checkCmd($?)

"-- Cleanup GPU caching" | log
python inference.py --cleanup-gpu
check($lastexitcode)

"-- pytorch_inf teardown completed" | log
Exit 0