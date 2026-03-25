#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
<#
OWNER: Dwight Carver (DCarv)

.SYNOPSIS
    Find a TOAST install partiton and remove it.
.PARAMETER -
    ----
#> 

$scriptPath = Split-Path -parent $MyInvocation.MyCommand.Definition
$CPU_Arch = $Env:Processor_Architecture
#$ToastVolExists = $FALSE
$OSIndex=$null
$OSPartition=$null
$ToastPartition=$null

Function RemoveToastVol {

    # Need to get Disk info dynamically due to StorageSpaces
    $Disks = @(Get-VirtualDisk | Get-Disk)
    if ($Disks) {
        $DeviceDisk = New-Object PSObject -Property @{
            Index = $Disks[0].Number
            Model = $Disks[0].Model
        }
    } else {
        $Disks = @(Get-Disk | Where-Object BusType -ne "USB" | Where-Object Size -gt 20GB)
        if ($Disks) {
            $DeviceDisk = New-Object PSObject -Property @{
                Index = $Disks[0].Number
                Model = $Disks[0].Model
            }
        }
    }
    $DiskNumber = $($DeviceDisk.Index)
    "Disk: $DiskNumber"

    $partNum = $null
    $partNum = (get-partition | where-object -FilterScript {$_.Type -eq "Basic"} | where-object -FilterScript {$_.Size -lt 34000000000} | where-object -FilterScript {$_.Size -gt 30000000000}).PartitionNumber
 
    if ($partNum -eq $null){
        return
    }

    "ToastPartition: $partNum"
    Get-Partition -DiskNumber $DiskNumber -PartitionNumber $partNum | Remove-Partition -Confirm:$false
    $partNum--
    $newSize = Get-PartitionSupportedSize -DiskNumber $DiskNumber -PartitionNumber $partNum
    Resize-Partition -DiskNumber $DiskNumber -PartitionNumber $partNum -Size $newSize.SizeMax

    $Script:LocalExitCode = 0

}


#region main
############################
# MAIN
############################
$Script:ErrorActionPreference = 'stop'

# Call main worker functions, trap exceptions and log
try
{
    RemoveToastVol

} catch {

    Write-Host "----- TRAP ----"
    Write-Host "Unhandled Exception: $_"
    $_ | Format-List -Force
    $Script:LocalExitCode = 1

}

# Main worker function complete, log results
exit $Script:LocalExitCode

#endregion main
