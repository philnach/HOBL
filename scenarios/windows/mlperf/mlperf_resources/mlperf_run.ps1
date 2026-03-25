param(
    [string]$logFile,
    [string]$mlperfConfigFile
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

if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\mlperf_run.log" }

# default config file is set to Phi3.5 WindowsML QNN NPU, which is the config for Qualcomm.
if (-not $mlperfConfigFile) { $mlperfConfigFile = "$scriptDrive\hobl_bin\mlperf\phi3.5\Config_Phi3.5_WindowsML_QNN_NPU.json" }

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

# 9F0F6E2E-8D06-4D2F-B8F5-6F1F2D5A1C01 is a custom provider we use to emit phase markers from the scenario script (optional, may not be present)
if (-not ('HoblRunPhaseProvider' -as [type])) {
    Add-Type -TypeDefinition @"
using System.Diagnostics.Tracing;

[EventSource(Name = "HOBL-Scenario-Phases", Guid = "9f0f6e2e-8d06-4d2f-b8f5-6f1f2d5a1c01")]
public sealed class HoblRunPhaseProvider : EventSource
{
    public static readonly HoblRunPhaseProvider Log = new HoblRunPhaseProvider();

    [Event(1, Level = EventLevel.Informational)]
    public void Phase(string marker, string scenario)
    {
        WriteEvent(1, marker, scenario);
    }
}
"@
}

function Write-RunPhaseMarker {
    param([string]$Marker)

    try {
        [HoblRunPhaseProvider]::Log.Phase($Marker, "mlperf")
    } catch {
    }
}

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

Set-Content -Path $logFile -encoding utf8 "-- MLPerf run started ($logSuffix version)"

"Script drive:   $scriptDrive" | log
"Script root:    $PSScriptRoot" | log
"Log file:       $logFile" | log
"Config file:    $mlperfConfigFile" | log
"Detected architecture: $arch (Processor: $processorArch)" | log
Write-RunPhaseMarker "phase.run_prep.start"

# Set working directory to mlperf
$mlperfDir = "$scriptDrive\hobl_bin\mlperf"
if (-not (Test-Path $mlperfDir)) {
    " ERROR - MLPerf directory not found: $mlperfDir" | log
    "Please run mlperf_prep.ps1 first" | log
    Exit 1
}

"Changing directory to: $mlperfDir" | log
Set-Location $mlperfDir

# Verify mlperf executable exists
$mlperfExe = Join-Path $mlperfDir "mlperf-windows.exe"
if (-not (Test-Path $mlperfExe)) {
    " ERROR - MLPerf executable not found: $mlperfExe" | log
    Exit 1
}

"MLPerf executable: $mlperfExe" | log

# Verify config file exists
if (-not (Test-Path $mlperfConfigFile)) {
    " ERROR - Config file not found: $mlperfConfigFile" | log
    Exit 1
}

"Using config file: $mlperfConfigFile" | log

# Create output directory if it doesn't exist
$outputDir = "$scriptDrive\hobl_data"

if (-not (Test-Path $outputDir)) {
    "Creating output directory: $outputDir" | log
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

# Delete existing results.json to prevent appended/corrupted results
$resultsFile = Join-Path $outputDir "results.json"
if (Test-Path $resultsFile) {
    "Deleting existing results file: $resultsFile" | log
    Remove-Item $resultsFile -Force
}

# Run MLPerf benchmark
"Running MLPerf benchmark..." | log
"Command: $mlperfExe --config $mlperfConfigFile --temp-dir . --output-dir $outputDir --download_behaviour skip_all --pause false" | log
Write-RunPhaseMarker "phase.run_prep.end"
Write-RunPhaseMarker "phase.run_build.start"

& $mlperfExe --config $mlperfConfigFile --temp-dir . --output-dir $outputDir --download_behaviour skip_all --pause false 2>&1 | log
$exitCode = $LASTEXITCODE
check $exitCode
Write-RunPhaseMarker "phase.run_build.end"
Write-RunPhaseMarker "phase.run_results.start"

"MLPerf benchmark completed successfully" | log

# Parse results.json file
$resultsFile = Join-Path $outputDir "results.json"
if (-not (Test-Path $resultsFile)) {
    "WARNING: Results file not found: $resultsFile" | log
    "-- MLPerf run completed ($logSuffix version)" | log
    Exit 0
}

"Parsing results from: $resultsFile" | log

# Read the results.json file
$jsonContent = Get-Content $resultsFile -Raw | ConvertFrom-Json

# Check if benchmark succeeded
if ($jsonContent.'Benchmark Success' -ne $true) {
    $errMsg = ($jsonContent.'Error Message' -replace "`n", " ").Trim()
    " ERROR - MLPerf benchmark failed: $errMsg" | log
    Exit 1
}

# Extract values from the JSON
$overallResults = $jsonContent.overall_results

# Parse Benchmark Duration (HH:MM:SS.mmm) to seconds
$benchmarkDuration = $jsonContent.'Benchmark Duration'
$durationParts = $benchmarkDuration -split ':'
$scenarioRuntime = [math]::Round([int]$durationParts[0] * 3600 + [int]$durationParts[1] * 60 + [double]$durationParts[2], 3)

# If overall_results is null, compute geomeans from category_results
# The 5 categories are: Code Analysis, Content Generation, Creative Writing,
# Summarization Light, Summarization Moderate
if (-not $overallResults) {
    "overall_results is null, computing geomeans from category_results" | log
    $categoryResults = $jsonContent.category_results
    if ($categoryResults) {
        $categories = $categoryResults.PSObject.Properties
        $count = ($categories | Measure-Object).Count

        # Collect per-category values
        $ttftValues = @()
        $tpsValues = @()
        $tokenCounts = @()
        foreach ($cat in $categories) {
            $ttftValues += $cat.Value.'Avg Time to First Token'
            $tpsValues += $cat.Value.'Avg 2nd+ Token Generation Rate'
            $tokenCounts += $cat.Value.'Avg Generated Tokens'
        }

        # Geometric mean = (product of values)^(1/n)
        $ttftProduct = 1.0; foreach ($v in $ttftValues) { $ttftProduct *= $v }
        $tpsProduct = 1.0; foreach ($v in $tpsValues) { $tpsProduct *= $v }
        $geomeanTTFT = [math]::Pow($ttftProduct, 1.0 / $count)
        $geomeanTPS = [math]::Pow($tpsProduct, 1.0 / $count)
        $avgTokens = [math]::Round(($tokenCounts | Measure-Object -Sum).Sum / $count, 0)

        $overallResults = [PSCustomObject]@{
            'Geomean Time to First Token' = $geomeanTTFT
            'Geomean 2nd+ Token Generation Rate' = $geomeanTPS
            'Avg Generated Tokens' = $avgTokens
        }
    } else {
        " ERROR - Neither overall_results nor category_results found in results.json" | log
        Exit 1
    }
}

# Create the output object
# Note: The Geomean fields are geometric means across the 5 prompt categories (Code Analysis,
# Content Generation, Creative Writing, Summarization Light, Summarization Moderate),
# which makes them a fair single-number summary since the categories have very different
# input/output lengths.
$output = [PSCustomObject]@{
    time_to_first_token_ms = [math]::Round($overallResults.'Geomean Time to First Token' * 1000, 2)
    time_to_first_token_s = [math]::Round($overallResults.'Geomean Time to First Token', 4)
    tokens_per_second = [math]::Round($overallResults.'Geomean 2nd+ Token Generation Rate', 2)
    total_tokens_generated = $overallResults.'Avg Generated Tokens'
    total_generation_time_s = $null
    scenario_runtime = $scenarioRuntime
    ai_model = $jsonContent.'Model Name'
    ai_device = $jsonContent.'Device Type'
}

# Print metrics summary
"" | log
"========================================" | log
"MLPerf Metrics Summary" | log
"========================================" | log
"Time to First Token: $($output.time_to_first_token_ms)ms ($($output.time_to_first_token_s)s)" | log
"Tokens per Second:   $($output.tokens_per_second)" | log
"Total Tokens:        $($output.total_tokens_generated)" | log
"Model:               $($output.ai_model)" | log
"Device:              $($output.ai_device)" | log
"Architecture:        $logSuffix" | log
"Scenario Runtime:    $($output.scenario_runtime)s" | log
"========================================" | log

# Output as JSON
"" | log
"=== Results (JSON Format) ===" | log
$jsonOutput = $output | ConvertTo-Json
$jsonOutput | log

# Output as CSV
"" | log
"=== Results (CSV Format) ===" | log
$output.PSObject.Properties | ForEach-Object {
    "$($_.Name),$($_.Value)" | log
}

# Save both formats to files
$jsonOutputFile = Join-Path $outputDir "mlperf_results.json"
$csvOutputFile = Join-Path $outputDir "mlperf_results.csv"

$output | ConvertTo-Json | Set-Content $jsonOutputFile -Encoding UTF8
"Results saved to: $jsonOutputFile" | log

$output.PSObject.Properties | ForEach-Object { "$($_.Name),$($_.Value)" } | Set-Content $csvOutputFile -Encoding UTF8
"Results saved to: $csvOutputFile" | log

"-- MLPerf run completed successfully ($logSuffix version)" | log
Write-RunPhaseMarker "phase.run_results.end"

Exit 0