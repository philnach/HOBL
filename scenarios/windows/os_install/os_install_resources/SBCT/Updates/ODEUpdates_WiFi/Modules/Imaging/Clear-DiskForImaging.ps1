#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
function Clear-DiskForImaging {
<#
.SYNOPSIS
    Clear the disk(s), includes checking the sector size matches the image

.RETURN
    True for success
#>
    param(
        [Parameter(Mandatory=$true,Position=0, ValueFromPipeline=$true, ValueFromPipelinebyPropertyName=$true)]
            $disk
    )

    begin {
        $IsOkay = $true
        $imageSectorSize = $(Get-ImageSetting -Path "/DiskConfig/SectorSize")
    }

    process {
        foreach($item in $disk) {
            [uint32] $diskSectorSize = $item.LogicalSectorSize
            "Checking sector size of disk {0}: {1} ... {2}" -f $item.Number, $item.FriendlyName, $item.LogicalSectorSize | Write-Log
            if ($imageSectorSize) {
                if (-not ($imageSectorSize.InnerText.Contains("$diskSectorSize"))) {
                    "Disk has ($diskSectorSize) size sectors but image is ($($imageSectorSize.InnerText))" | Write-Log -ForegroundColor Yellow
                    if (($imageSectorSize.InnerText.Count -eq 1) -and ($imageSectorSize.InnerText -as [uint32] -ge $diskSectorSize)) {
                        "Disk has ($diskSectorSize) size sectors which is okay for for image: ($($imageSectorSize.InnerText))" | Write-Log
                        $IsOkay = $true
                    } else {
                        $IsOkay = $false
                    }
                }
            }

            if ($item.PartitionStyle -ne 'RAW') {
                "SKIPPING - Cleaning disk {0}: {1}..." -f $item.Number, $item.FriendlyName | Write-Log
                try
                {

#                    Clear-Disk -Number $item.Number -RemoveData -RemoveOEM -Confirm:$false
                } catch {
                    $_ | Format-List -Force | Write-Log
                    "Cleaning drive {0} failed" -f $item.Number | Write-Log -ForegroundColor Red 
                    $IsOkay = $false
                }
            }
        }
    }

    end {
        "Update StorageProviderCache"  | Write-Log
        Update-StorageProviderCache  | Write-Log
        return $IsOkay
    }
}
