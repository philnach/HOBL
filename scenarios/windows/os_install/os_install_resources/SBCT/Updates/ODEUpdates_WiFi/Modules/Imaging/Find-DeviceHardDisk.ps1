#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
function Find-DeviceHardDisk {
<#
.SYNOPSIS
    Finds the system hard disk on a device

.DESCRIPTION
    Long description

.PARAMETER
    none

.EXAMPLE
    $deviceDisk = Find-DeviceHardDisk

#>
    param(
    )

    begin {
        $ThisFunction = Trace-FunctionBegin $MyInvocation
        [int]$MinOSVersionForSpacesBoot = 14971
    }

    process {

        $DeviceDisk = $null
        try {
            if (Test-Path -Path "Function:\Get-ProductSpecificInstallDisk") {
                $DeviceDisk = Get-ProductSpecificInstallDisk
                if ($DeviceDisk -ne $null) {
                    "ProductSpecificInstallDisk is $($DeviceDisk.Model)" | Write-log
                }
            } else {
                $BootDiskPolicy = Get-ImageSetting BootDiskPolicy
                [string] $BootDiskID = Get-ImageSetting BootDiskID
                if (-not $BootDiskPolicy) {
                    $BootDiskPolicy = "Never"
                }
                "BootDiskPolicy is $BootDiskPolicy" | Write-Log
                $IsOSSpacesBootCapable = $false
                $IsDeviceSpacesBootCapable = $false

<#               
                $NTCurrentVersion = Get-ItemProperty -Path "Registry::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion" -ErrorAction SilentlyContinue
                if ($NTCurrentVersion) {
                    try {
                        if ($NTCurrentVersion.CurrentBuildNumber -ge $MinOSVersionForSpacesBoot) {
                            $IsOSSpacesBootCapable = $true
                        }
                    } catch {}
                }
                
                if ($IsOSSpacesBootCapable) {
                    Clear-StoragePool
                    if (Get-NonUsbDisk | Where-Object BusType -ne "Spaces" | Clear-DiskForImaging) {
                        "All disks cleared"  | Write-Log -Foreground Yellow
                        if (Test-Path -Path "Function:\Set-ProductSpecificDiskFormat") {
                            Set-ProductSpecificDiskFormat
                        }
                        $PhysicalDisks = @(Get-NonUsbPhysicalDisk | Where-Object {$_.CanPool})
                        if (($BootDiskPolicy -eq "Always") -or
                            (($BootDiskPolicy -eq "Auto") -and ($PhysicalDisks.Count -gt 1))) {
                            if (Test-Path -Path "Function:\Test-SpacesBootCapable") {
                                $IsDeviceSpacesBootCapable = Test-SpacesBootCapable
                                if ($IsDeviceSpacesBootCapable) {
                                    Enable-SpacesBootSimple -diskNumber $BootDiskID | Write-Log
                                }
                            }
                        } else {
                            "Only found $($PhysicalDisks.Count) disk that CanPool" | Write-Log
                        }
                    } else {
                        "got error clearing non-USB disk" | Write-Log -Foreground Red
                    }                        
                }
#>

                if (Wait-DeviceDiskAvailable) {
                    $Disks = @(Get-VirtualDisk | Get-Disk)
                    $DisksCount = $Disks.Count

                    if ($Disks) {
                        $DeviceDisk = New-Object PSObject -Property @{
                            Index = $Disks[0].Number
                            Model = $Disks[0].Model
                        }
                    } else {
                        $Disks = @(Get-NonUsbDisk)
                        $DisksCount = $Disks.Count
                        if ($BootDiskID) {
                            $Disks = @($Disks | Where-Object Number -eq $BootDiskID)
                        }
                        if ($Disks) {
                            $DeviceDisk = New-Object PSObject -Property @{
                                Index = $Disks[0].Number
                                Model = $Disks[0].Model
                            }
                        }
                    }

                    if ($DeviceDisk -eq $null) {
                        "    * No drives found" | Write-Log -Foreground Yellow
                    } else {
                        "Using Disk: $($DeviceDisk.Index), $($DeviceDisk.Model), $($Disks[0].Size)" | Write-Log -Foreground Green
                    }
                } else {
                        "    * No drives found" | Write-Log -Foreground Yellow
                }
            }
        } catch {
            $_ | Format-List -Force | Write-Log
            "Warning: No valid disk found!" | Write-Log -LogType Warning
        }
        
        if ($DeviceDisk -eq $null) {
            "Warning: No valid disk found!" | Write-Log -LogType Warning
        } elseif ($DisksCount -gt 1) {
            "Warning: Found multiple disks, picked one ($($DeviceDisk.Index) $($DeviceDisk.Model))" | Write-Log -LogType Warning
        }

        return $deviceDisk
    }

    end {
        Trace-FunctionEnd $MyInvocation
    }
}
