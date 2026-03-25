$ErrorActionPreference = "SilentlyContinue"
Write-Host " INFO - Stop_PerfStress_Background starting"

# Retry helper so cleanup remains robust when processes are still spinning up/down.
function Stop-PerfStressProcesses {
    $patterns = "Collect_5min_Traces\.ps1|70_percentile_stress\.py|Install_Python\.ps1"
    $attempt = 0
    while ($attempt -lt 5) {
        $found = $false
        $killedThisAttempt = 0

        Get-CimInstance Win32_Process |
            Where-Object { $_.CommandLine -and ($_.CommandLine -match $patterns) } |
            ForEach-Object {
                $found = $true
                $killedThisAttempt++
                Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            }

        # Extra guards for python launch variants.
        Get-CimInstance Win32_Process |
            Where-Object { $_.Name -match "(?i)^(python|py|pythonw)\.exe$" -and $_.CommandLine -and ($_.CommandLine -match "70_percentile_stress\.py") } |
            ForEach-Object {
                $found = $true
                $killedThisAttempt++
                Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            }

        Write-Host (" INFO - Stop attempt {0}: killed candidates={1}" -f ($attempt + 1), $killedThisAttempt)

        if (-not $found) {
            break
        }

        Start-Sleep -Milliseconds 500
        $attempt++
    }
}

function Close-ExplorerWindows {
    $explorerCount = (Get-Process explorer | Where-Object { $_.MainWindowHandle -ne 0 } | Measure-Object).Count
    Write-Host (" INFO - Explorer windows before close={0}" -f $explorerCount)

    Get-Process explorer |
        Where-Object { $_.MainWindowHandle -ne 0 } |
        ForEach-Object { $_.CloseMainWindow() | Out-Null }

    Start-Sleep -Milliseconds 700

    # Fallback close for any remaining explorer folder windows.
    try {
        $shell = New-Object -ComObject Shell.Application
        foreach ($w in $shell.Windows()) {
            if ($w -and $w.FullName -and ($w.FullName -like "*explorer.exe")) {
                $w.Quit()
            }
        }
    }
    catch {
        Write-Host " ERROR - Stop_PerfStress_Background fallback close failed."
    }

    $remainingExplorer = (Get-Process explorer | Where-Object { $_.MainWindowHandle -ne 0 } | Measure-Object).Count
    Write-Host (" INFO - Explorer windows after close={0}" -f $remainingExplorer)
}

# Stop background processes launched by perf_stress_ec setup.
Stop-PerfStressProcesses

$remainingStress = (Get-CimInstance Win32_Process |
    Where-Object {
        ($_.CommandLine -and ($_.CommandLine -match "Collect_5min_Traces\.ps1|70_percentile_stress\.py|Install_Python\.ps1")) -or
        ($_.Name -match "(?i)^(python|py|pythonw)\.exe$" -and $_.CommandLine -and ($_.CommandLine -match "70_percentile_stress\.py"))
    } |
    Measure-Object).Count

Write-Host (" INFO - Remaining stress candidates after stop={0}" -f $remainingStress)

# Close open File Explorer windows so reruns start clean.
Close-ExplorerWindows

Write-Host " INFO - Stop_PerfStress_Background completed"

exit 0
