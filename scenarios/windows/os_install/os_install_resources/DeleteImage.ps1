# Adimistrator escalation
If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))

{   
$arguments = "& '" + $myinvocation.mycommand.definition + "'"
Start-Process powershell -Verb runAs -ArgumentList $arguments
Break
}

# Clear all error before starting script. We'll check for error after each command and halt execution on unexpected failures.
$error.clear()
$ErrorActionPreference = 'Stop'

[UInt64]$TargetWinRESize = 2GB
[UInt64]$WinRECreateSlack = 64MB
$RecoveryGptType = '{de94bba4-06d1-4d40-a16a-bfd50179d6ac}'

function Disable-PageFileIfConfigured {
    Write-Host "Disabling pagefile configuration..." -ForegroundColor Cyan

    $computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop
    if ($computerSystem.AutomaticManagedPagefile) {
        Set-CimInstance -InputObject $computerSystem -Property @{ AutomaticManagedPagefile = $false } | Out-Null
        Write-Host "Disabled automatic pagefile management." -ForegroundColor Green
    } else {
        Write-Host "Automatic pagefile management is already disabled." -ForegroundColor Green
    }

    $pageFileSettings = Get-CimInstance -ClassName Win32_PageFileSetting -ErrorAction SilentlyContinue
    if ($pageFileSettings) {
        foreach ($setting in $pageFileSettings) {
            Write-Host "Removing pagefile setting: $($setting.Name)" -ForegroundColor Yellow
            Remove-CimInstance -InputObject $setting -ErrorAction Stop
        }
    } else {
        Write-Host "No explicit pagefile settings found." -ForegroundColor Green
    }

    # Keep registry values aligned with disabled pagefile configuration.
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -Name 'PagingFiles' -Type MultiString -Value @() -ErrorAction Stop
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -Name 'ExistingPageFiles' -Type MultiString -Value @() -ErrorAction SilentlyContinue

    if (Test-Path 'C:\pagefile.sys') {
        try {
            Remove-Item 'C:\pagefile.sys' -Force -ErrorAction Stop
            Write-Host "Removed C:\pagefile.sys immediately." -ForegroundColor Green
        } catch {
            Write-Host "C:\pagefile.sys is currently in use; full removal requires reboot or running this script from WinPE/offline OS." -ForegroundColor Yellow
        }
    } else {
        Write-Host "No C:\pagefile.sys present." -ForegroundColor Green
    }
}

function Resize-PartitionIfNeeded {
    param(
        [char]$DriveLetter,
        [UInt64]$TargetSize,
        [string]$Reason
    )

    $partition = Get-Partition -DriveLetter $DriveLetter -ErrorAction Stop
    if ($partition.Size -eq $TargetSize) {
        Write-Host "Skipping resize for ${DriveLetter}: already at target size $TargetSize ($Reason)." -ForegroundColor Green
        return
    }

    Write-Host "Resizing ${DriveLetter}: from $($partition.Size) to $TargetSize ($Reason)" -ForegroundColor Green
    Resize-Partition -DriveLetter $DriveLetter -Size $TargetSize
}

Write-Host "Current partition layout:" -ForegroundColor Cyan
Get-Partition | Format-Table -AutoSize

$osPartition = Get-Partition -DriveLetter C -ErrorAction Stop
$diskNumber = $osPartition.DiskNumber

Disable-PageFileIfConfigured

# Remove stale BOOTME/WinPE image partitions so C and WinRE can be normalized.
$imagePartitions = Get-Partition -DiskNumber $diskNumber | Where-Object {
    ($_.Type -eq 'Basic') -and
    ($_.Size -gt 21000000000) -and
    ($_.Size -lt 35000000000) -and
    ($_.PartitionNumber -ne $osPartition.PartitionNumber)
} | Sort-Object -Property PartitionNumber -Descending

# Remove stale unknown tail partitions that can remain after imaging and block C: reclaim.
$unknownTailPartitions = Get-Partition -DiskNumber $diskNumber | Where-Object {
    ($_.Type -eq 'Unknown') -and
    ($_.PartitionNumber -gt $osPartition.PartitionNumber) -and
    ($_.Size -gt 1000000000) -and
    ($_.Size -lt 50000000000)
} | Sort-Object -Property PartitionNumber -Descending

$cleanupPartitions = (@($imagePartitions) + @($unknownTailPartitions)) | Sort-Object -Property PartitionNumber -Descending

if ($cleanupPartitions) {
    foreach ($part in $cleanupPartitions) {
        Write-Host "Removing stale partition #$($part.PartitionNumber) type=$($part.Type) size=$($part.Size)" -ForegroundColor Yellow
        Remove-Partition -DiskNumber $diskNumber -PartitionNumber $part.PartitionNumber -Confirm:$false
    }
} else {
    Write-Host "No stale image/unknown tail partition found on disk $diskNumber." -ForegroundColor Green
}

# Remove existing WinRE partition(s) and recreate to exactly 2GB.
$existingRecovery = Get-Partition -DiskNumber $diskNumber | Where-Object { $_.GptType -eq $RecoveryGptType } | Sort-Object -Property PartitionNumber -Descending
if ($existingRecovery) {
    foreach ($part in $existingRecovery) {
        Write-Host "Removing existing recovery partition #$($part.PartitionNumber) size=$($part.Size)" -ForegroundColor Yellow
        Remove-Partition -DiskNumber $diskNumber -PartitionNumber $part.PartitionNumber -Confirm:$false
    }
}

# Grow C to max after removals.
$osSizeAfterCleanup = Get-PartitionSupportedSize -DriveLetter C
Write-Host "Expanding C: to $($osSizeAfterCleanup.SizeMax)" -ForegroundColor Green
Resize-PartitionIfNeeded -DriveLetter 'C' -TargetSize $osSizeAfterCleanup.SizeMax -Reason 'expand-to-max'

# Shrink C: to make exactly 2GB for WinRE at the end of disk.
$osSupportedForShrink = Get-PartitionSupportedSize -DriveLetter C
[UInt64]$newOsSize = $osSupportedForShrink.SizeMax - ($TargetWinRESize + $WinRECreateSlack)
if ($newOsSize -lt $osSupportedForShrink.SizeMin) {
    throw "Unable to reserve 2GB for WinRE. C: minimum supported size is $($osSupportedForShrink.SizeMin), requested size is $newOsSize."
}

Write-Host "Shrinking C: to $newOsSize to reserve 2GB (+$WinRECreateSlack slack) for WinRE" -ForegroundColor Green
Resize-PartitionIfNeeded -DriveLetter 'C' -TargetSize $newOsSize -Reason 'reserve-winre-space'

$diskObj = Get-Disk -Number $diskNumber
if ($diskObj.LargestFreeExtent -lt $TargetWinRESize) {
    throw "Unable to allocate WinRE. Largest free extent is $($diskObj.LargestFreeExtent), required is $TargetWinRESize."
}

# Create and format WinRE partition.
$newRecoveryPartition = New-Partition -DiskNumber $diskNumber -Size $TargetWinRESize -GptType $RecoveryGptType -ErrorAction Stop
if ($newRecoveryPartition.DriveLetter) {
    Format-Volume -DriveLetter $newRecoveryPartition.DriveLetter -FileSystem NTFS -NewFileSystemLabel 'Windows RE tools' -Confirm:$false | Out-Null
    $recoveryAccessPath = ($newRecoveryPartition.DriveLetter + ':\\')
    Remove-PartitionAccessPath -DiskNumber $diskNumber -PartitionNumber $newRecoveryPartition.PartitionNumber -AccessPath $recoveryAccessPath -ErrorAction SilentlyContinue
} else {
    $newRecoveryPartition | Format-Volume -FileSystem NTFS -NewFileSystemLabel 'Windows RE tools' -Confirm:$false | Out-Null
}

Write-Host "Final partition layout:" -ForegroundColor Cyan
Get-Partition -DiskNumber $diskNumber | Format-Table -AutoSize
Write-Host "DeleteImage preflight complete. WinRE is set to 2GB." -ForegroundColor Green