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

.PARAMETER PDM
    Flag to indicate if the whole disk image is being restored from a SBCT physical disk capture

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
		[switch] $EFI,

        [Parameter(Mandatory=$false)]
		[switch] $PDM
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
            $sbctCMD = "$SBCTPath restore $DiskIndex '$Imagepath' /dnv /arsd /l:$LogDir /lh:$LogDir /efi /elp $SBCTFlags"
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
        } elseif ($PDM) {
            "    * Restore entire physical disk" | Write-Log
            "    * Restore entire physical disk" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            $sbctCMD = "$SBCTPath restore $DiskIndex '$Imagepath' /l:$LogDir /lh:$LogDir $SBCTFlags"
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
            } else {
                # must happen before we try to mount drive letters
                Update-StorageProviderCache
            }
        } else {        
            "    * Dismount all drive letters" | Write-Log
            Dismount-DeviceDriveLetters -ForVHD $InstallToVHD -DiskIndex $DiskIndex

            if ($RecoveryImagePartition) {
                "    * Restore Recovery Partition" | Write-Log
                "    * Restore Recovery Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
                $sbctCMD = "$SBCTPath restore $DiskIndex '$Imagepath' /dnv /arsd /l:$LogDir /lh:$LogDir /spr:$RecoveryImagePartition /tpr:$RecoveryImagePartitionDest $SBCTFlags"
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
                "    * Restore Recovery Partition Done" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            } else {
                "Skipping restoring Recovery Partition" | Write-Log
                "Skipping restoring Recovery Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            }

            if ($WinREPartition) {
                "    * Restore WinRE Partition" | Write-Log
                "    * Restore WinRE Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
                $sbctCMD = "$SBCTPath restore $DiskIndex '$Imagepath' /dnv /arsd /l:$LogDir /lh:$LogDir /spr:$WinREPartition /tpr:$WinREPartition $SBCTFlags"
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
                "    * Restore WinRE Partition Done" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            } else {
                "Skipping restoring WinRE Partition" | Write-Log
                "Skipping restoring WinRE Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
            }

            "    * Restore OS Image Partition" | Write-Log
            "    * Restore OS Image Partition" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug


            # DCARV - updated for WIM Images

            # Get root driver letter
    	    $wimPath = $rootpath

            # Assign W: to the Windows Partition
            Get-Partition -disknumber $DiskIndex -partitionNumber $OSPartition | Set-Partition -NewDriveLetter W

            # IF we have SWM files, apply
            if (gci -path $wimpath *.swm) {
                $swmFullName = (gci -path $wimPath *.swm | sort name)[0].FullName
                $swmBaseName = (gci -path $wimPath *.swm | sort name)[0].BaseName
                $dismCMD = "dism /apply-image /imagefile:$swmFullName /index:6 /applydir:W:\"
                # Update if we have mulitple SWM Files
                if ((gci -path $wimPath *.swm | sort name)[1]) {
                    $dismCMD = "dism /apply-image /imagefile:$swmFullName /SWMFile:$wimPath\$swmBaseName*.swm /index:6 /applydir:W:\"
                }
                # Call DISM command
                $dismCMD | Write-Log
          	    Invoke-Expression $dismCMD

            # IF we have WIM file, apply
            } elseif (gci -path $wimpath install.wim) {             
                $dismCMD = "dism /apply-image /imagefile:$wimPath\Install.wim /index:6 /applydir:W:\"
                # Call DISM command
                $dismCMD | Write-Log
          	    Invoke-Expression $dismCMD  
              
            } else {

                # Do the default SVCT apply
                $sbctCMD = "$SBCTPath restore $DiskIndex '$Imagepath' /dnv /arsd /l:$LogDir /lh:$LogDir /spr:$OSPartition /tpr:$OSPartition $SBCTFlags"
                # Handle SBCT Errors
                [int]$sbctErr = $LASTEXITCODE
                if( $sbctErr -ne 0) {
                    "SBCT ERROR:$sbctErr $sbctCMD (Get-WindowsErrorDescription $sbctErr)" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug 
                    Write-Error -Message "$sbctCMD" -Category InvalidResult -ErrorId (Get-WindowsErrorDescription $sbctErr) -CategoryTargetName "SurfaceBlockCaptureTool.exe" -CategoryReason "SBCT CMD FAILED" -CategoryTargetType $sbctErr | Write-Log -NoEcho
                    exit $sbctErr
                }
            }




            # Remove W: in case scripts expect it not to be present
            Remove-PartitionAccessPath -disknumber $DiskIndex -partitionNumber $OSPartition -AccessPath "w:\"



            "    * Restore OS Image Partition Done" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        }

        "    * Mounting Drive Letters" | Write-Log
        Mount-DeviceDriveLetters -ForVHD $InstallToVHD -DiskIndex $DiskIndex
    }

    end {
        Trace-FunctionEnd $MyInvocation
        Complete-BuildTiming -ActionName $ThisFunction
    }
}
