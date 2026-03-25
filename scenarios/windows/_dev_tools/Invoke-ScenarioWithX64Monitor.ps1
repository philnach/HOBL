<#
.SYNOPSIS
    Wrapper script that runs a developer scenario's run.ps1 while monitoring
    for x64 emulated processes on ARM64 Windows.

.DESCRIPTION
    This script:
    1. Starts an ETW trace (sequential/non-circular) capturing process creation events
    2. Executes the specified scenario run script
    3. Stops the ETW trace
    4. Parses the ETL to identify any x64 (emulated) processes that ran
    5. Appends findings to the scenario log and generates an x64 process report

    The ETW trace uses the Microsoft-Windows-Kernel-Process provider (GUID
    {22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}) which fires event ID 1 for
    process start.  The trace uses a sequential (non-circular) buffer so it
    can grow for long-running scenarios.

    On x64 machines this script simply runs the scenario without monitoring
    (there are no emulated processes to detect).

.PARAMETER ScenarioScript
    Full path to the scenario's run script (e.g. ollama_run.ps1).

.PARAMETER ScenarioArgs
    Optional hashtable of arguments to pass through to the scenario script.

.PARAMETER LogFile
    Path for this wrapper's own log.  Defaults to <drive>\hobl_data\x64monitor.log.

.EXAMPLE
    .\Invoke-ScenarioWithX64Monitor.ps1 -ScenarioScript "C:\hobl_data\ollama_resources\ollama_run.ps1"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ScenarioScript,

    [hashtable]$ScenarioArgs = @{},

    [string]$LogFile = ""
)

# ---------------------------------------------------------------------------
# Basics
# ---------------------------------------------------------------------------
$scriptDrive = Split-Path -Qualifier $PSScriptRoot

$scenarioName = [System.IO.Path]::GetFileNameWithoutExtension($ScenarioScript)
if ($scenarioName -match '^(?<base>.+)_run$') {
    $scenarioName = $Matches['base']
}
$scenarioName = ($scenarioName -replace '[^A-Za-z0-9._-]', '_').ToLowerInvariant()

if (-not $LogFile) { $LogFile = "$scriptDrive\hobl_data\x64monitor.log" }

# Ensure output directory exists
$logDir = Split-Path $LogFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---------------------------------------------------------------------------
# Architecture detection
# ---------------------------------------------------------------------------
$osInfo = Get-CimInstance Win32_OperatingSystem
$arch = $osInfo.OSArchitecture
$processorArch = $env:PROCESSOR_ARCHITECTURE

if ($arch -eq "64-bit" -and $processorArch -eq "AMD64") {
    $isARM64 = $false
    $logSuffix = "x64"
} elseif ($arch -match "ARM" -or $processorArch -match "ARM") {
    $isARM64 = $true
    $logSuffix = "ARM64"
} else {
    Write-Host " ERROR - Unsupported architecture: $arch (Processor: $processorArch)" -ForegroundColor Red
    Exit 1
}

$LogFile = $LogFile -replace "\.log$", "_${scenarioName}_$($logSuffix.ToLower()).log"

# ---------------------------------------------------------------------------
# Helpers (standard HOBL pattern)
# ---------------------------------------------------------------------------
function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match " ERROR - ") {
            Write-Host $msg -ForegroundColor Red
        } else {
            Write-Host $msg
        }
        Add-Content -Path $LogFile -encoding utf8 "$msg"
    }
}

function Convert-DevicePathToDosPath {
    param([string]$Path)

    if (-not $Path) { return $Path }
    if ($Path -notmatch '^\\Device\\') { return $Path }

    if (-not ('HoblNativeMethods' -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class HoblNativeMethods
{
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern uint QueryDosDevice(string lpDeviceName, StringBuilder lpTargetPath, int ucchMax);
}
"@
    }

    foreach ($drive in [System.IO.DriveInfo]::GetDrives()) {
        $driveName = $drive.Name.TrimEnd('\\')
        if ($driveName.Length -ne 2 -or $driveName[1] -ne ':') { continue }

        $buffer = New-Object System.Text.StringBuilder 1024
        $result = [HoblNativeMethods]::QueryDosDevice($driveName, $buffer, $buffer.Capacity)
        if ($result -eq 0) { continue }

        $targets = $buffer.ToString().Split([char]0, [System.StringSplitOptions]::RemoveEmptyEntries)
        foreach ($target in $targets) {
            if ($Path.StartsWith($target, [System.StringComparison]::OrdinalIgnoreCase)) {
                return "$driveName$($Path.Substring($target.Length))"
            }
        }
    }

    return $Path
}

# ---------------------------------------------------------------------------
# ETW constants
# ---------------------------------------------------------------------------
$sessionName = "HOBLx64ProcessMonitor"
# Microsoft-Windows-Kernel-Process provider — fires event ID 1 on process start
$kernelProcessGuid = "{22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}"
# 9F0F6E2E-8D06-4D2F-B8F5-6F1F2D5A1C01 is a custom provider we use to emit phase markers from the scenario script (optional, may not be present)
$phaseProviderGuid = "{9F0F6E2E-8D06-4D2F-B8F5-6F1F2D5A1C01}"

$etlFile = Join-Path $logDir "x64_process_monitor_${scenarioName}_$($logSuffix.ToLower()).etl"
$instanceReportFile = Join-Path $logDir "process_instances_${scenarioName}_$($logSuffix.ToLower()).csv"

# ---------------------------------------------------------------------------
# Validate scenario script exists
# ---------------------------------------------------------------------------
if (-not (Test-Path $ScenarioScript)) {
    " ERROR - Scenario script not found: $ScenarioScript" | log
    Exit 1
}

Set-Content -Path $LogFile -encoding utf8 "-- x64 process monitor started ($logSuffix version)"
"Scenario script: $ScenarioScript" | log
"ETL output:      $etlFile" | log
"Instance output: $instanceReportFile" | log
"Phase provider:  $phaseProviderGuid" | log
"Architecture:    $logSuffix" | log
"" | log

# ---------------------------------------------------------------------------
# Start ETW trace (ARM64 only — on x64 there's nothing to monitor)
# ---------------------------------------------------------------------------
$traceStarted = $false

if ($isARM64) {
    "-- Starting ETW trace for process creation events (sequential buffer)" | log

    # Stop any leftover session from a previous interrupted run
    logman stop $sessionName -ets 2>$null | Out-Null

    # Remove stale ETL if present
    if (Test-Path $etlFile) { Remove-Item $etlFile -Force }

    # Start a sequential (non-circular) trace so long-running scenarios don't lose events.
    # -bs 64  = 64 KB buffer size per buffer
    # -nb 16 256 = min 16 / max 256 buffers (16 MB max, grows as needed)
    # -f bincirc is NOT used — sequential is the default
    logman create trace $sessionName -ets `
        -o $etlFile `
        -p $kernelProcessGuid 0x10 `
        -bs 64 -nb 16 256 `
        -mode Sequential

    $createExitCode = $LASTEXITCODE

    if ($createExitCode -eq 0) {
        logman update trace $sessionName -ets -p $phaseProviderGuid 0xFFFFFFFFFFFFFFFF 0x5 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            " WARNING - Could not enable optional phase marker provider (exit code: $LASTEXITCODE). Continuing with process-only tracing." | log
        }
    }

    if ($createExitCode -eq 0) {
        $traceStarted = $true
        "ETW trace started: session=$sessionName" | log
    } else {
        " ERROR - Failed to start ETW trace (exit code: $createExitCode). Continuing without monitoring." | log
    }
} else {
    "-- Skipping x64 process monitoring (not ARM64)" | log
}

# ---------------------------------------------------------------------------
# Run the scenario script
# ---------------------------------------------------------------------------
"" | log
"========================================" | log
"Running scenario: $(Split-Path $ScenarioScript -Leaf)" | log
"========================================" | log
"" | log

$scenarioExitCode = 0
try {
    # Build splat args — forward any caller-provided scenario arguments
    $fwdArgs = @{}
    foreach ($key in $ScenarioArgs.Keys) {
        $fwdArgs[$key] = $ScenarioArgs[$key]
    }

    & $ScenarioScript @fwdArgs
    $scenarioExitCode = $LASTEXITCODE
} catch {
    " ERROR - Scenario script threw an exception: $_" | log
    $scenarioExitCode = 1
}

"" | log
"Scenario exited with code: $scenarioExitCode" | log

# ---------------------------------------------------------------------------
# Stop ETW trace
# ---------------------------------------------------------------------------
if ($traceStarted) {
    "" | log
    "-- Stopping ETW trace" | log
    logman stop $sessionName -ets
    if ($LASTEXITCODE -eq 0) {
        "ETW trace stopped" | log
    } else {
        " ERROR - Failed to stop ETW trace (exit code: $LASTEXITCODE)" | log
    }

    # -----------------------------------------------------------------------
    # Parse ETL — find x64 emulated processes
    # -----------------------------------------------------------------------
    if (Test-Path $etlFile) {
        "" | log
        "-- Parsing ETL for x64 emulated processes" | log

        $etlSizeMB = [math]::Round((Get-Item $etlFile).Length / 1MB, 2)
        "ETL file size: ${etlSizeMB} MB" | log

        try {
            # Get process-start events (Event ID 1) from the Kernel-Process provider
            # -Oldest is required for .etl files (must be read in forward chronological order)
            $events = Get-WinEvent -Path $etlFile -Oldest -FilterXPath "*[System[Provider[@Guid='$kernelProcessGuid'] and EventID=1]]" -ErrorAction Stop

            $phaseMarkerEvents = Get-WinEvent -Path $etlFile -Oldest -FilterXPath "*[System[Provider[@Guid='$phaseProviderGuid'] and EventID=1]]" -ErrorAction SilentlyContinue

            function Convert-HexPayloadToText {
                param([string]$Value)

                if (-not $Value) { return $null }

                $compact = ($Value -replace '^0x', '' -replace '[^0-9A-Fa-f]', '')
                if ($compact.Length -lt 2 -or ($compact.Length % 2) -ne 0) {
                    return $null
                }

                try {
                    $bytes = New-Object byte[] ($compact.Length / 2)
                    for ($idx = 0; $idx -lt $bytes.Length; $idx++) {
                        $bytes[$idx] = [Convert]::ToByte($compact.Substring($idx * 2, 2), 16)
                    }

                    $decodedUnicode = [System.Text.Encoding]::Unicode.GetString($bytes).Trim([char]0)
                    if ($decodedUnicode) {
                        return $decodedUnicode
                    }

                    $decodedUtf8 = [System.Text.Encoding]::UTF8.GetString($bytes).Trim([char]0)
                    if ($decodedUtf8) {
                        return $decodedUtf8
                    }
                } catch {
                }

                return $null
            }

            function Get-PhaseMarkerFromText {
                param([string]$Text)

                if (-not $Text) { return $null }

                if ($Text -match '(phase\.run_[^\.]+\.(start|end))') {
                    return $Matches[1]
                }

                $segments = $Text -split "`0"
                foreach ($segment in $segments) {
                    if ($segment -and $segment -match '^phase\.run_[^\.]+\.(start|end)$') {
                        return $segment
                    }
                }

                return $null
            }

            function Get-PhaseMarkerFromEvent {
                param($EventRecord)

                try {
                    $eventXml = [xml]$EventRecord.ToXml()
                    $ns = New-Object System.Xml.XmlNamespaceManager($eventXml.NameTable)
                    $ns.AddNamespace("e", "http://schemas.microsoft.com/win/2004/08/events/event")

                    $dataNodes = $eventXml.SelectNodes("//e:EventData/e:Data", $ns)
                    foreach ($dataNode in $dataNodes) {
                        $candidate = [string]$dataNode.'#text'
                        $candidateMarker = Get-PhaseMarkerFromText -Text $candidate
                        if ($candidateMarker) {
                            return $candidateMarker
                        }

                        $decodedCandidate = Convert-HexPayloadToText -Value $candidate
                        $decodedCandidateMarker = Get-PhaseMarkerFromText -Text $decodedCandidate
                        if ($decodedCandidateMarker) {
                            return $decodedCandidateMarker
                        }
                    }

                    $processingPayloadNode = $eventXml.SelectSingleNode("//e:ProcessingErrorData/e:EventPayload", $ns)
                    if ($processingPayloadNode -and $processingPayloadNode.'#text') {
                        $decodedProcessingPayload = Convert-HexPayloadToText -Value ([string]$processingPayloadNode.'#text')
                        $decodedProcessingMarker = Get-PhaseMarkerFromText -Text $decodedProcessingPayload
                        if ($decodedProcessingMarker) {
                            return $decodedProcessingMarker
                        }
                    }

                    $renderedMessage = $EventRecord.Message
                    $messageMarker = Get-PhaseMarkerFromText -Text $renderedMessage
                    if ($messageMarker) {
                        return $messageMarker
                    }

                    $decodedMessage = Convert-HexPayloadToText -Value $renderedMessage
                    $decodedMessageMarker = Get-PhaseMarkerFromText -Text $decodedMessage
                    if ($decodedMessageMarker) {
                        return $decodedMessageMarker
                    }
                } catch {
                }

                return $null
            }

            $phaseMarkers = @()
            foreach ($phaseEvt in $phaseMarkerEvents) {
                $phaseMarker = Get-PhaseMarkerFromEvent -EventRecord $phaseEvt
                if ($phaseMarker) {
                    $phaseMarkers += [PSCustomObject]@{
                        Time   = $phaseEvt.TimeCreated
                        Marker = $phaseMarker
                    }
                }
            }

            # Fallback: if provider-specific lookup returns nothing, scan all EventID=1 events
            # and extract only payloads that match phase marker syntax.
            if ($phaseMarkers.Count -eq 0) {
                $allEventId1Events = Get-WinEvent -Path $etlFile -Oldest -FilterXPath "*[System[EventID=1]]" -ErrorAction SilentlyContinue
                foreach ($candidateEvt in $allEventId1Events) {
                    $phaseMarker = Get-PhaseMarkerFromEvent -EventRecord $candidateEvt
                    if ($phaseMarker) {
                        $phaseMarkers += [PSCustomObject]@{
                            Time   = $candidateEvt.TimeCreated
                            Marker = $phaseMarker
                        }
                    }
                }
            }
            $phaseMarkers = $phaseMarkers | Sort-Object Time

            function Get-RunPhaseAtTime {
                param(
                    [datetime]$Timestamp,
                    $Markers
                )

                $activePhase = "run_unphased"
                foreach ($markerEvent in $Markers) {
                    if ($markerEvent.Time -gt $Timestamp) { break }

                    if ($markerEvent.Marker -match '^phase\.run_(?<name>[^\.]+)\.start$') {
                        $activePhase = "run_$($Matches['name'])"
                    } elseif ($markerEvent.Marker -match '^phase\.run_(?<name>[^\.]+)\.end$') {
                        if ($activePhase -eq "run_$($Matches['name'])") {
                            $activePhase = "run_unphased"
                        }
                    }
                }

                return $activePhase
            }

            "Total process-start events captured: $($events.Count)" | log
            "Total phase markers captured: $($phaseMarkers.Count)" | log

            # ---- Helper: read PE machine type from a file ----
            function Get-PEMachineType {
                param([string]$Path)
                try {
                    $fs = [System.IO.File]::OpenRead($Path)
                    try {
                        # MZ header check
                        $mz = New-Object byte[] 2
                        if ($fs.Read($mz, 0, 2) -ne 2 -or $mz[0] -ne 0x4D -or $mz[1] -ne 0x5A) { return $null }
                        # PE offset at 0x3C
                        $fs.Position = 0x3C
                        $buf = New-Object byte[] 4
                        if ($fs.Read($buf, 0, 4) -ne 4) { return $null }
                        $peOffset = [BitConverter]::ToInt32($buf, 0)
                        if ($peOffset -le 0) { return $null }
                        # Machine type at PE offset + 4
                        $fs.Position = $peOffset + 4
                        $buf2 = New-Object byte[] 2
                        if ($fs.Read($buf2, 0, 2) -ne 2) { return $null }
                        return [BitConverter]::ToUInt16($buf2, 0)
                    } finally {
                        $fs.Close()
                    }
                } catch {
                    return $null
                }
            }

            function Resolve-ExecutablePath {
                param([string]$ImageName)

                if (-not $ImageName) { return $null }

                if ([System.IO.Path]::IsPathRooted($ImageName)) {
                    if (Test-Path $ImageName -ErrorAction SilentlyContinue) {
                        return $ImageName
                    }
                }

                $candidates = @(
                    (Join-Path "$env:SystemRoot\System32" $ImageName),
                    (Join-Path "$env:SystemRoot\SysWOW64" $ImageName),
                    (Join-Path $env:SystemRoot $ImageName),
                    (Join-Path $env:ProgramFiles $ImageName),
                    (Join-Path ${env:ProgramFiles(x86)} $ImageName)
                )

                foreach ($candidate in $candidates) {
                    if (Test-Path $candidate -ErrorAction SilentlyContinue) {
                        return $candidate
                    }
                }

                $cmd = Get-Command $ImageName -ErrorAction SilentlyContinue
                if ($cmd -and $cmd.Source -and (Test-Path $cmd.Source -ErrorAction SilentlyContinue)) {
                    return $cmd.Source
                }

                return $null
            }

            function Get-ProcessClassification {
                param([string]$ImageName)

                $resolvedPath = Resolve-ExecutablePath -ImageName $ImageName
                if (-not $resolvedPath) {
                    return [PSCustomObject]@{
                        ProcessType  = "Unknown"
                        Architecture = "Unknown"
                        MachineType  = ""
                        ResolvedPath = ""
                        Reason       = "Executable not found"
                    }
                }

                $machine = Get-PEMachineType -Path $resolvedPath
                if ($null -eq $machine) {
                    return [PSCustomObject]@{
                        ProcessType  = "Unknown"
                        Architecture = "Unknown"
                        MachineType  = ""
                        ResolvedPath = $resolvedPath
                        Reason       = "PE machine type unreadable"
                    }
                }

                if ($machine -eq 0x8664) {
                    return [PSCustomObject]@{
                        ProcessType  = "Emulated"
                        Architecture = "x64"
                        MachineType  = "0x$($machine.ToString('X4'))"
                        ResolvedPath = $resolvedPath
                        Reason       = ""
                    }
                }

                if ($machine -eq 0x14C) {
                    return [PSCustomObject]@{
                        ProcessType  = "Emulated"
                        Architecture = "x86"
                        MachineType  = "0x$($machine.ToString('X4'))"
                        ResolvedPath = $resolvedPath
                        Reason       = ""
                    }
                }

                if ($machine -eq 0xAA64) {
                    return [PSCustomObject]@{
                        ProcessType  = "NativeARM64"
                        Architecture = "ARM64"
                        MachineType  = "0x$($machine.ToString('X4'))"
                        ResolvedPath = $resolvedPath
                        Reason       = ""
                    }
                }

                return [PSCustomObject]@{
                    ProcessType  = "NativeOther"
                    Architecture = "NativeOther"
                    MachineType  = "0x$($machine.ToString('X4'))"
                    ResolvedPath = $resolvedPath
                    Reason       = ""
                }
            }

            # Build per-instance process records (one row per process-start event)
            $imageClassificationCache = @{}
            $processInstanceRecords = @()

            foreach ($evt in $events) {
                $xml = [xml]$evt.ToXml()
                $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
                $ns.AddNamespace("e", "http://schemas.microsoft.com/win/2004/08/events/event")

                $imageNameRaw = [string]$xml.SelectSingleNode("//e:Data[@Name='ImageName']", $ns).'#text'
                $imageName = Convert-DevicePathToDosPath -Path $imageNameRaw
                $processId = [string]$xml.SelectSingleNode("//e:Data[@Name='ProcessID']", $ns).'#text'
                $phaseLabel = Get-RunPhaseAtTime -Timestamp $evt.TimeCreated -Markers $phaseMarkers

                if (-not $imageName) {
                    $imageName = "<UnknownImage>"
                }

                if (-not $imageClassificationCache.ContainsKey($imageName)) {
                    $imageClassificationCache[$imageName] = Get-ProcessClassification -ImageName $imageName
                }

                $classification = $imageClassificationCache[$imageName]
                $processInstanceRecords += [PSCustomObject]@{
                    EventTime     = $evt.TimeCreated.ToString("o")
                    ProcessID     = $processId
                    ImageName     = $imageName
                    Phase         = $phaseLabel
                    ProcessType   = $classification.ProcessType
                    Architecture  = $classification.Architecture
                    MachineType   = $classification.MachineType
                    ResolvedPath  = $classification.ResolvedPath
                    Reason        = $classification.Reason
                }
            }

            "Unique process images found: $($imageClassificationCache.Count)" | log

            # -----------------------------------------------------------------
            # Report
            # -----------------------------------------------------------------
            "" | log
            "========================================" | log
            "Process Instance Report ($logSuffix)" | log
            "========================================" | log

            "Total process instances: $($processInstanceRecords.Count)" | log
            foreach ($typeGroup in ($processInstanceRecords | Group-Object ProcessType | Sort-Object Name)) {
                "  $($typeGroup.Name): $($typeGroup.Count)" | log
            }

            "========================================" | log

            if ($processInstanceRecords.Count -gt 0) {
                $processInstanceRecords |
                    Sort-Object EventTime, ProcessID |
                    Export-Csv -Path $instanceReportFile -NoTypeInformation -Encoding UTF8
            } else {
                "EventTime,ProcessID,ImageName,Phase,ProcessType,Architecture,MachineType,ResolvedPath,Reason" |
                    Set-Content -Path $instanceReportFile -Encoding UTF8
            }

            "Single process instance report saved to: $instanceReportFile" | log

        } catch {
            " ERROR - Failed to parse ETL: $_" | log
        }
    } else {
        " ERROR - ETL file not found: $etlFile" | log
    }
}

"" | log
"-- x64 process monitor completed ($logSuffix version)" | log

# Exit with the scenario's exit code so the test harness sees the correct result
Exit $scenarioExitCode
