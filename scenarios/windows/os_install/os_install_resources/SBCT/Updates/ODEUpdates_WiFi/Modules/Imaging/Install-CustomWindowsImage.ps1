#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
function Install-CustomWindowsImage {
<#
.SYNOPSIS
    Install a Windows image that was created by New-CustomWindowsImage.

.DESCRIPTION
    Modified to support install from local partiton instead of USB

.PARAMETER ImagePath
    The location of the WIM or SBCT image to install

.PARAMETER InstallFromSbct
    The ImagePath is one that was captured with SBCT

.PARAMETER InstallToVHD
    Perform the install to a VHD

.PARAMETER DiskIndex
    The zero-based index of which disk to use for the destination

.PARAMETER ExitAfterInstall
    Just exit or prompt user for action

.PARAMETER HCKInstall
    Flag to indicate if this OS Install is targeted for automated testing and needs the HCK installed from the network

.PARAMETER UefiDebug
    Really save the messages to a UEFI Variable

.PARAMETER Defrag
    Flag to indicate if the OS partition should be defragged, particularly if being captured for SBCT

.PARAMETER EFI
    Flag to indicate if EFI partition should be restored from SBCT

.EXAMPLE


#>
    param(
        [Parameter(Mandatory=$false)] 
	[switch] $InstallFromSbct,

        [Parameter(Mandatory=$false)] 
        [string] $ImagePath,

        [Parameter(Mandatory=$false)] 
        [boolean] $InstallToVHD = $false,

        [Parameter(Mandatory=$false)]
        [int] $DiskIndex = -1,

        [Parameter(Mandatory=$false)] 
        [switch] $ExitAfterInstall,

        [Parameter(Mandatory=$false)]
        [switch] $HCKInstall,

        [Parameter(Mandatory=$false)]
        [switch] $UefiDebug,

        [Parameter(Mandatory=$false)]
        [switch] $Defrag,

        [Parameter(Mandatory=$false)]
        [string] $WinREPath,

        [Parameter(Mandatory=$false)]
        [switch] $EFI,

        [Parameter(Mandatory=$false)]
        [switch] $PDM
    )

    begin {
        $ThisFunction = Trace-FunctionBegin $MyInvocation
        if ($InstallToVHD) {
            Start-BuildTiming -ActionName $ThisFunction
        }
    }

    process {

        "Install-CustomWindowsImage" | Write-Log

        #if (-not $ImagePath) {
        #    $ImagePath = Find-WimFile
        #}

        $ImagePath = Get-Content "$rootPath\CMD_InstallSBCT.txt"

        $InstallDriveRoot = Split-Path -Parent $ImagePath
        $PreInstallPatch = "$InstallDriveRoot\ImagePreInstallPatch\runme.ps1"
        "- Image PreInstall Patch Check: $PreInstallPatch" | Write-Log
        "- Image PreInstall Patch Check: $PreInstallPatch" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        if (Test-Path $PreInstallPatch) {
            & $PreInstallPatch
        }

        "- Image Located: $ImagePath" | Write-Log
        "- Image Located: $ImagePath" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug

        if ($DiskIndex -lt 0) {
            $DiskIndex = $(Find-DeviceHardDisk).Index
        }
        "- Install Disk Index: $DiskIndex" | Write-Log
        "- Install Disk Index: $DiskIndex" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug

        # For Jazz, need to wipe the disk
        & format c: /Q /Y

        "- Installing Image" | Write-Log
        "- Installing Image" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        # Check if Reimage or WiFi-Install
        if (test-path "D:\ToastReimage*") {
            $OSPartition = Get-PartitionCommands -format OSPartition -ForVHD $InstallToVHD
            "D:\SurfaceBlockCaptureTool.exe -r $DiskIndex d:\ToastReimage /spr:$OSPartition /tpr:$OSPartition /arsd /dnv" | Write-Log
            start-process "D:\SurfaceBlockCaptureTool.exe" -args "-r $DiskIndex d:\ToastReimage /spr:$OSPartition /tpr:$OSPartition /arsd /dnv" -wait -NoNewWindow
        } else {
            # Expanding Normal Image (WiFi install)
            "Expand-SbctImage -InstallToVHD $InstallToVHD -ImagePath $ImagePath -DiskIndex $DiskIndex -UefiDebug:$UefiDebug -EFI:$EFI" | Write-Log
            Expand-SbctImage -InstallToVHD $InstallToVHD -ImagePath $ImagePath -DiskIndex $DiskIndex -UefiDebug:$UefiDebug -EFI:$EFI
        }

        "- Reading Partition Information" | Write-Log
        "- Reading Partition Information" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        $recoveryPath = Get-PartitionCommands -Format RecoveryImagePath -ForVHD $InstallToVHD -DiskIndex $DiskIndex
        $osLetter =  Get-PartitionCommands -Format OSLetter -ForVHD $InstallToVHD -DiskIndex $DiskIndex
        $efiLetter = Get-PartitionCommands -Format EFILetter -ForVHD $InstallToVHD -DiskIndex $DiskIndex
        $recoveryImageLetter = Get-PartitionCommands -Format RecoveryImageLetter -ForVHD $InstallToVHD -DiskIndex $DiskIndex

        #Refresh PowerShell after mount (again, since it sometimes needs it)
        Update-StorageProviderCache

        #Next lines needed so that PowerShell cmdlets recognize the new drive
        if ($recoveryImageLetter -and -not (Test-Path -Path "$recoveryImageLetter`:\") ) {
            New-PSDrive $recoveryImageLetter -PSProvider FileSystem -Root "$recoveryImageLetter`:" -Scope Global | Write-Log -LogType Debug
        }

        if ( (-not([string]::IsNullOrEmpty($efiLetter))) -and 
	     (-not (Test-Path "$efiLetter`:\"))
           ) {
            New-PSDrive $efiLetter -PSProvider FileSystem -Root "$efiLetter`:" -Scope Global | Write-Log -LogType Debug
        }

        "- Setup Recovery Configuration Files" | Write-Log
        "- Setup Recovery Configuration Files" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        if ($recoveryPath) {
            Set-BMRFiles -Path $recoveryPath
        } else {
            "- Skipping setting up recovery configuration files as RecoveryImagePath is empty" | Write-Log
        }

        $PostInstallPatch = "$InstallDriveRoot\ImagePostInstallPatch\runme.ps1"
        "- Image PostInstall Patch Check: $PostInstallPatch" | Write-Log
        "- Image PostInstall Patch Check: $PostInstallPatch" | Write-UefiDebugMessage -SaveToUefiVar $UefiDebug
        if (Test-Path $PostInstallPatch) {
            & $PostInstallPatch
        }

        "***********************" | Write-Log -ForegroundColor Green 
        "  INSTALL CUSTOM IMAGE -> COMPLETE  " | Write-Log -ForegroundColor Green 
        "***********************" | Write-Log -ForegroundColor Green 
        Trace-FunctionDuration $MyInvocation

        # Run Post Dismount commands if needed
        if (Test-Path -Path "Function:\Set-PostDismountConfiguration") {
            Set-PostDismountConfiguration
         }

        #"You can reboot now" | Write-Host -ForegroundColor White 
        #Select-UserRebootOption -PromptString  "End of Deployment" -PostInstall
    }

    end {
        Trace-FunctionEnd $MyInvocation
        if ($InstallToVHD) {
            Complete-BuildTiming -ActionName $ThisFunction
        }
    }
}

