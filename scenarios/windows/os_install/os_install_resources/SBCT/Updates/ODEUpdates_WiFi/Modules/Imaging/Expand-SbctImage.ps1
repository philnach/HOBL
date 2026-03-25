#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
function Expand-SbctImage {
<#
.SYNOPSIS
    Expands/Applys an image captured with SurfaceBlockCaptureTool to a disk

.DESCRIPTION
    Normally used on a device

.PARAMETER DiskIndex
    Which disk (0-based) to use

.PARAMETER UefiDebug
    Really save the messages to a UEFI Variable

.PARAMETER Imagepath
    Path to the base image (do not include the .sbct and beyond parts)

.PARAMETER EFI
    Flag to indicate if the EFI partition should be restored from SBCT

.EXAMPLE
    Expand-SbctImage -DiskIndex 0 -Imagepath .\mteos

#>
    param(
	    [Parameter(Mandatory=$false)]
		[boolean] $InstallToVHD = $false,

        [Parameter(Mandatory=$true)]
		[uint32] $DiskIndex,

        [Parameter(Mandatory=$false)]
		[switch] $UefiDebug,

        [Parameter(Mandatory=$true)]
		[string] $Imagepath,

        [Parameter(Mandatory=$false)]
		[switch] $EFI
    )

    begin {
        $ThisFunction = Trace-FunctionBegin $MyInvocation
        Start-BuildTiming -ActionName $ThisFunction
        $SBCTPath = Find-DeviceExecutable "SurfaceBlockCaptureTool.exe"
        if (!$SBCTPath) {
            Write-Error "SurfaceBlockCaptureTool not found" | Write-Log -NoEcho
        }
        $OSPartition = Get-PartitionCommands -format OSPartition -ForVHD $InstallToVHD
        $WinREPartition = Get-PartitionCommands -format WinREPartition -ForVHD $InstallToVHD
        $RecoveryImagePartition = Get-PartitionCommands -format RecoveryImagePartition -ForVHD $InstallToVHD
        $RecoveryImagePartitionDest = $RecoveryImagePartition
    }

    process {
        "- Installing SBCT Image" | Write-Log
        "- Installing SBCT Image" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        $imageSectorSize = Get-ImageSetting -XPath "/DiskConfig/SectorSize"
        if ($imageSectorSize) {
            $disk = Get-Disk | Where-Object Number -eq $DiskIndex
            if ($disk) {
                [uint32] $diskSectorSize = $disk.LogicalSectorSize
                if ($imageSectorSize.InnerText.Contains("$diskSectorSize")) {
                    $Imagepath += "." + $diskSectorSize.ToString()
                } else {
                    "image sector size ($($imageSectorSize.InnerText)) does not match disk ($diskSectorSize)" | Write-Log -Foreground Yellow
                    if (($imageSectorSize.InnerText.Count -eq 1) -and ($($imageSectorSize.InnerText -as [uint32]) -ge $diskSectorSize)) {
                        $Imagepath += "." + $imageSectorSize.InnerText.ToString()
                    }
                }
            } else {
                "    * Drive is lost" | Write-Log -Foreground Yellow
            }
        }
        "    * Imagepath: $Imagepath" | Write-Log

        $SBCTFlags = Get-ImageSetting SBCTFlags

        if ($EFI) {
            "    * Restore full image with EFI" | Write-Log
            "    * Restore full image with EFI" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            $sbctCMD = "$SBCTPath restore $DiskIndex $Imagepath /dnv /arsd /l:$LogDir /lh:$LogDir /efi /elp $SBCTFlags"
            $sbctCMD | Write-Log
            if ($global:LemonDebug) {
                Invoke-Expression $sbctCMD | Write-Log
            } else {
                Invoke-Expression $sbctCMD
            }
            # Handle SBCT Errors
            [int]$sbctErr = $LASTEXITCODE
            if( $sbctErr -ne 0) {
                "SBCT ERROR:$sbctErr $sbctCMD (Get-WindowsErrorDescription $sbctErr)" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug 
                Write-Error -Message "$sbctCMD" -Category InvalidResult -ErrorId (Get-WindowsErrorDescription $sbctErr) -CategoryTargetName "SurfaceBlockCaptureTool.exe" -CategoryReason "SBCT CMD FAILED" -CategoryTargetType $sbctErr | Write-Log -NoEcho
                exit $sbctErr
            }

        } else {        

            "    * Restore OS Image Partition" | Write-Log
            "    * Restore OS Image Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            $sbctCMD = "$SBCTPath restore $DiskIndex $Imagepath /dnv /arsd /la:$LogDir /lh:$LogDir /spr:$OSPartition /tpr:$OSPartition $SBCTFlags"
            $sbctCMD | Write-Log

            if ($global:LemonDebug) {
                Invoke-Expression $sbctCMD | Write-Log
            } else {
                Invoke-Expression $sbctCMD
            }            
            # Handle SBCT Errors
            [int]$sbctErr = $LASTEXITCODE
            if( $sbctErr -ne 0) {
                "SBCT ERROR:$sbctErr $sbctCMD (Get-WindowsErrorDescription $sbctErr)" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug 
                Write-Error -Message "$sbctCMD" -Category InvalidResult -ErrorId (Get-WindowsErrorDescription $sbctErr) -CategoryTargetName "SurfaceBlockCaptureTool.exe" -CategoryReason "SBCT CMD FAILED" -CategoryTargetType $sbctErr | Write-Log -NoEcho
                exit $sbctErr
            }
            "    * Restore OS Image Partition Done" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        }

        # Assign W: to Windows partition
$DiskpartCommands = @"
sel vol 0
assign letter=w
"@
        Invoke-DiskpartCommand -DiskpartCommands $DiskpartCommands -continueOnError $false
        New-PSDrive "w" -PSProvider FileSystem -Root "w:\" -Scope Global -ErrorAction Continue
        "Assigned W: to Windows OS partiton" | Write-Log
    }

    end {
        Trace-FunctionEnd $MyInvocation
        Complete-BuildTiming -ActionName $ThisFunction
    }
}
