#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
<#

DCarv's Install.ps1 for installing across network.

#>
param(

    )

    $OperationStartTime = Get-Date
    $global:ErrorActionPreference = 'stop'

    ###################################################################################################
    # Global Error Handler
    ###################################################################################################
    trap {
        Write-Host "----- TRAP ----"
        Write-Host "Unhandled Exception: $_"
        $_ | Format-List -Force 
        exit 9988
    }

    if ($ENV:PROCESSOR_ARCHITECTURE -ne "ARM") {
        $host.UI.RawUI.BackgroundColor = "DarkBlue"
        $Host.UI.RawUI.ForegroundColor = "White"
        $host.UI.RawUI.WindowTitle = "$(Get-Location)"
    }
    if (-not $SkipClear) {
        Clear
    }
    $ConfirmPreference = "None"
    $scriptPath = Split-Path -parent $MyInvocation.MyCommand.Definition

    Write-Host "********************"
    Write-Host "  PLE TOAST - RE-INSTALL  "
    Write-Host "********************"

    $UEFIVer = ($(& wmic bios get SMBIOSBIOSVersion /format:table)[2])
    Write-Host "- UEFI Information: $UEFIVer"
    Write-Host "- WinPE Information"
    $RegPath = "Registry::HKEY_LOCAL_MACHINE\Software"
    $WinPEVersion = ""
    $CurrentVersion = Get-ItemProperty -Path "$RegPath\Microsoft\Surface\OSImage" -ErrorAction SilentlyContinue
    if ($CurrentVersion) {
        try {
            Write-Output "   - ImageName $($CurrentVersion.ImageName)"
            $WinPEVersion = $($CurrentVersion.ImageName)
        } catch {}
        try {
            Write-Output "   - RebasedImageName $($CurrentVersion.RebasedImageName)"
        } catch {}
    }
    $NTCurrentVersion = Get-ItemProperty -Path "$RegPath\Microsoft\Windows NT\CurrentVersion" -ErrorAction SilentlyContinue
    if ($NTCurrentVersion) {
        try {
            Write-Output "   - BuildLab $($NTCurrentVersion.BuildLab)"
            Write-Output "   - BuildLabEx $($NTCurrentVersion.BuildLabEx)"
            Write-Output "   - ProductName $($NTCurrentVersion.ProductName)"
        } catch {}
    }

    $Global:rootPath = "D:"
    Write-Host "- rootPath: $rootPath"
    pushd $rootPath

    # In case of errors, fix the drive label so USB can overwrite disk
    Set-Volume -NewFileSystemLabel "TOAST" -driveletter "D"

    $Global:LogDir = $Env:LogDir
    if (-not $Global:LogDir) {
        $Global:LogDir = "$rootPath\logs\Install"
    }
    if (-not (Test-Path -Path $Global:LogDir)) {
        New-Item $Global:LogDir -Type Directory -Force | Out-Null
    }

    $PSModuleAutoLoadingPreference = "All"
    Get-Item -Path "$rootPath\modules\*\*.psd1" | Select-Object -ExpandProperty BaseName | Remove-Module -ErrorAction Ignore
    Write-Host "- Loading Imaging Module"
    Import-Module "$rootPath\modules\InternationalExt\InternationalExt" -Scope Global
    Import-Module "$rootPath\modules\UtilityFunctions\UtilityFunctions" -Scope Global
    if (test-path ("$rootPath\modules\XmlLinqDSL")) {
        Import-Module "$rootPath\modules\XmlLinqDSL\XmlLinqDSL" -Scope Global
    } else {
        Import-Module "$rootPath\modules\XmlLinq\XmlLinq" -Scope Global
    }
    Import-Module "$rootPath\modules\Imaging\Imaging" -Scope Global

    $Global:LogPath = New-LogPath -Name "Install.log"
    Save-PreservedDeviceSettings
    $ImagesActualPath = "$rootPath\*images_actual.xml"
    "- images_actual.xml: $ImagesActualPath" | Write-Log 

    if (Test-Path -Path $ImagesActualPath) {
        "Loading images_actual.xml" | Write-Log
        $ImagesXml = $(Resolve-Path $ImagesActualPath)
        Import-ImageSettings -Path "$ImagesXml" -UseSavedValues -SkipSchemaValidation
        $ProfileNumber = Get-ImageSetting ProfileNumber
        $ProfileName = Get-ImageSetting ProfileName
        $Version = Get-ImageSetting Version
        if (Test-Path "$rootPath\Firmware\FirmwareSpecifics.psm1") {
            Import-Module $rootPath\Firmware\FirmwareSpecifics.psm1 -Scope Global
        } elseif (Test-Path "$rootPath\Firmware\FirmwareSpecifics.ps1") {
            . $rootPath\Firmware\FirmwareSpecifics.ps1
        }
        $VersionString = "Version: ($ProfileNumber) $ProfileName $Version (WinPE $WinPEVersion)"
        if( $ENV:PROCESSOR_ARCHITECTURE -ne "ARM" ) { $Host.UI.RawUI.WindowTitle = $VersionString }
        "- Installing $VersionString" | Write-Log
        "- Locating Disk Install Target" | Write-Log
        if (Wait-DeviceDiskAvailable) {
            $Disks = @(Get-NonUsbDisk)
            if ($Disks) {
                $MainDisk = New-Object PSObject -Property @{
                    Index = $Disks[0].Number
                    Model = $Disks[0].Model
                }
            $MainDiskIndex = $MainDisk.Index
            }
        }

    } else {
        "images_actual.xml not present, functionality reduced" | Write-Log -Foreground Yellow 
    }

    $VersionName = Get-Content "$rootPath\CMD_InstallSBCT.txt"
    "- Installing via SBCT, version: $VersionName" | Write-Log
    Install-CustomWindowsImage -InstallFromSbct -ImagePath $VersionName -DiskIndex $MainDiskIndex -HCKInstall:$HCKInstall -ExitAfterInstall:$ExitAfterInstall -UefiDebug:$UefiDebug

