#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
<#

DCarv's Install.ps1 for installing from Hidden Partition (WiFi install)

#>
param(

    )

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

    $ConfirmPreference = "None"

    Write-Host "********************"
    Write-Host "  - WIFI -  WIFI IMAGE INSTALLER - email DCarv for more info."
    Write-Host "********************"

    Write-Host "------------------------------"
    Write-Host "Install-Local image"
    Write-Host "------------------------------"
    $UsbDriveLetter = (get-volume -FriendlyName 'BOOTME' -erroraction ignore).DriveLetter
    if ($UsbDriveLetter.length -eq 0) {
        $UsbDriveLetter = (get-volume -FriendlyName 'SHIFU_SCOTT' -erroraction ignore).DriveLetter
    }
    $UsbDrivePath = "$UsbDriveLetter`:"
    if (-not (Test-Path $UsbDrivePath)) {
        Write-Host "$UsbDrivePath does not exist"
        Write-Error "Partition 'BOOTME' and 'SHIFU_SCOTT' not found"
        return
    }

    Write-Host "------------------------------"
    Write-Host " Setting Drive Label"
    Write-Host "------------------------------"
    $LocalInstallDrive = Get-CimInstance -ClassName Win32_Volume -Filter "DriveLetter = '$UsbDrivePath'"
    $LocalInstallDrive | Set-CimInstance -Property @{Label='BOOTME'}

    $Global:rootPath = "$UsbDrivePath"
    Write-Host "- rootPath: $rootPath"
    Push-Location $rootPath
    # When performing NET install log to the local machine (could be read-only access).
    if (Test-Path "$rootPath\CMD_HCKInstall.txt")
    {
        $Global:NETInstall = $true
        $Env:LogDir = "$rootPath\Logs\Install"
    }
    $Global:LogDir = $Env:LogDir
    if (-not $Global:LogDir) 
    {
        if ($HCKInstall)
        {
            [System.Guid] $guidObject = [System.Guid]::NewGuid()
            $Global:LogDir = "$rootPath\logs\Install\" + $guidObject.Guid

        } else {
            $Global:LogDir = "$rootPath\logs\Install"
        }

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
    }


    # Still need S: for WTT Files 
    $output = & mountvol s: /s
    if ($LASTEXITCODE -ne 0) {
        "Last exit code: $LASTEXITCODE`r`nMounting EFI Partition failed`r`n$output" | Write-Log -Foreground Yellow 
    }
    if( -not (Test-Path "s:\") ) {
        New-PSDrive "S" -PSProvider FileSystem -Root "S:\" -Scope Global
    }
    "- Checking for s:\HLK Folder" | Write-Log
    if (Test-Path "s:\HLK") {
        "    * Copy s:\HLK $rootPath\HLK" | Write-Log
        robocopy /mir /z /r:0 /w:0 s:\HLK $rootPath\HLK
        copy-item "W:\DC_PostOS\PostOS.HLK.cmd" -destination "W:\DC_PostOS\postos.cmd" -force
    }
    "- Checking for s:\WTT Folder" | Write-Log
    if (Test-Path "s:\WTT") {
        "    * Copy s:\WTT $rootPath\WTT" | Write-Log
            robocopy /mir /z /r:0 /w:0 s:\WTT $rootPath\WTT
   }
    "    * Dismount S:" | Write-Log
    $output = & mountvol s: /d
    if ($LASTEXITCODE -ne 0) {
        "Last exit code: $LASTEXITCODE`r`nDismounting EFI Partition failed`r`n$output" | Write-Log
        #exit 1
    }


    # remove TXT file so PostOS causes exception and we get control back to run local PostOS script
    #Remove-Item "S:\password.txt" -Force -ErrorAction Ignore
    Install-CustomWindowsImage -InstallFromSbct -ImagePath $VersionName -DiskIndex $MainDiskIndex -HCKInstall:$HCKInstall -ExitAfterInstall:$ExitAfterInstall -UefiDebug:$UefiDebug

    Write-Host "- [dcarv's] Installing Post Deployment Software"

    # Load our new file
    #$rootPath\modules\Imaging\Install-PostDeviceDeployment.ps1
    #Install-PostDeviceDeployment.ps1 -HCKInstall       

    # PostOS
    #---------------------------------------------
    $PostActions = "full"
    $KernelDebug = "false"
    # Determine CPU type
    $CPU_Arch = $Env:Processor_Architecture
    Write-host "Rootpath: $rootPath"

    # Post Install Customizations actions
    if (Test-Path "$rootPath\PostActions.txt"){
        $PostActions = gc "$rootPath\PostActions.txt" 
    }
    "    * PostActions: $PostActions" | Write-Log
    # Check to enable USB Debug
    if (Test-Path "$rootPath\KernelDebug.txt"){
        $KernelDebug = gc "$rootPath\KernelDebug.txt"
    }
    "    * KernelDebug: $KernelDebug" | Write-Log
    # Unattend.xml
    if (Test-Path "$rootPath\pcname.txt"){
        $PCName =   gc "$rootPath\pcname.txt"
    }
    "    * PC Name:    $PCName" | Write-Log

    if( -not (Test-Path "v:\") ){
        New-PSDrive "v" -PSProvider FileSystem -Root "v:\" -Scope Global
    }

    $OSPartition = Get-PartitionCommands -format OSPartition -ForVHD $False
    "OSPartition: $OSPartition"


    if( -not (Test-Path "W:") ) {
$diskpartcmd = @"
select dis $MainDiskIndex
select par $OSPartition
assign letter=w
exit
"@

        Invoke-DiskpartCommand -DiskpartCommands $diskpartcmd -ContinueOnError $false
        New-PSDrive "W" -PSProvider FileSystem -Root "W:\" -Scope Global -ErrorAction Continue
    }

    # Verify SBCT installed a new image, if not recover and reboot back to Windows.
    if (Test-Path "W:\SafeBuild"){
        $host.UI.RawUI.BackgroundColor = "RED"
        $current = "{current}"
        $output = & bcdedit /delete $current
        Write-Host $output 
        robocopy $Global:LogDir w:\Logs\Install /s
        Clear-Host
        for($i = 0; $i -lt 50; $i++){ write-host "Install.ps1 failed to apply new image!!" -Foreground Yellow }
        Start-Sleep 10
        "Install.ps1 failed to apply image, rebooting back to orginal OS." | Write-Log -LogType Warning
        Restart-Computer
    }

    # Copy Install Scripts to Windows Partiton
    "- Copying PostOS Scripts" | Write-Log
    remove-item "W:\DC_PostOS" -force -ErrorAction Ignore
    robocopy /mir /z /w:5 "$rootPath\DC_PostOS" "w:\DC_PostOS"

    # Copy build info for WTT Dimension
    "- Copy Buildinfo for WTT" | write-Log
    $BuildLink | Out-File -Encoding ASCII -FilePath "W:\DC_PostOS\buildlink.txt" -Force
    if (Test-Path "$rootPath\pcname.txt"){
        Copy-Item "$rootPath\pcname.txt" "W:\DC_PostOS\pcname.txt"
    }

    # Copy WTT or HLK Folders so job continues
    if (Test-Path "$rootPath\WTT"){
        "    - Copy WTT Folder" | Write-Log
        "    - Copy $rootPath\WTT w:\WTT" | Write-Log
        robocopy /mir /z $rootPath\WTT w:\WTT

    } elseif (Test-Path "$rootPath\HLK") {        
        "    - Copy HLK Folder" | Write-Log
        "    - Copy $rootPath\HLK w:\HLK" | Write-Log
        robocopy /mir /z $rootPath\HLK w:\HLK
        # Replace PostOS (WTT Client install) with PostOS.HLK (HLK Client install)
        copy-item "W:\DC_PostOS\PostOS.HLK.cmd" -destination "W:\DC_PostOS\postos.cmd" -force
    }

    # Check Unattend actions to skip features
    while ($true){

        if ($PostActions -match "null"){
            "Executing Unattend NULL actions and removing dirs." | Write-Log
            if (Test-Path "W:\DC_PostOS") {Remove-Item ("W:\DC_PostOS")}
            if (Test-Path "W:\WTT") {Remove-Item ("W:\WTT")}
            if (Test-Path "W:\HLK") {Remove-Item ("W:\HLK")}
            break
        }

        if ($PostActions -match "disablewu"){
            "Disabling WU using Registry." | Write-Log
            W:\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot W:\windows\system32\config -registryFilePath W:\DC_PostOS\RegFiles_OS\WU
        }

        if ( ($PostActions -match "wttclientonly") -or ($PostActions -match "clientonly") ){
            "Executing Client install, adding PostOS RunOnce Registry key." | Write-Log
            W:\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot W:\windows\system32\config -registryFilePath W:\DC_PostOS\RegFiles_OS\PostOS
            break
        }

        if ($PostActions -match "none"){
            "Executing Unattend NONE actions and exiting." | Write-Log
            if (Test-Path "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk"){
                Copy-Item "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk" "W:\Users\default\Desktop\WTTClientInstall.lnk"
            }
            if (Test-Path "$rootPath\pcname.txt"){
                Copy-Item "$rootPath\pcname.txt" "W:\DC_PostOS\pcname.txt"
            }
            break
        }

        if ( ($PostActions -match "nowttclient") -or ($PostActions -match "noclient") ){
            "Executing NO WTT CLIENT actions and removing PostOS.reg" | Write-Log
            if (Test-Path "W:\DC_PostOS\RegFiles_OS\postos.reg"){
                Remove-Item ("W:\DC_PostOS\RegFiles_OS\postos.reg")
            }
            if (Test-Path "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk"){
                Copy-Item "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk" "W:\Users\default\Desktop\WTTClientInstall.lnk"
            }
        }

        if ( ($PostActions -match "norollback") -or ($PostActions -match "norb") ){
            "Executing NO ROLLBACK, removing ROLLBACK registry policy." | Write-Log
            $filepath = "W:\DC_PostOS\RegFiles_OS"
            if (Test-Path $filepath){
                foreach ($f in gci $filepath | Where-Object {$_.name -like "rollback*.reg"}) {Remove-Item "$filepath\$($f.name)"}
            }
            if (test-path ("$rootPath\ImagePostInstallPatch\CMD_RollbackFirmware.txt")){
                remove-item ("$rootPath\ImagePostInstallPatch\CMD_RollbackFirmware.txt") -Force -ErrorAction Ignore
            }
        }

        if ( ($PostActions -notmatch "noreg") -and ($PostActions -notmatch "noregistry") ){
            "Executing Registry actions." | Write-Log
            # Add ALL custom registry keys - Expecting WTT Install & Rename computer runonce script.
            if (Test-Path "W:\DC_PostOS\Update-OfflineRegistry.ps1"){
                "Adding registry keys to image" | Write-Log
                W:\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot W:\windows\system32\config -registryFilePath W:\DC_PostOS\RegFiles_OS
            }
        }

        # Remove Dev startup script (from unattend.xml) - This is causing WTT Unexpected reboots because of the HCK Install check.
        if (Test-Path W:\Devoobe.cmd){
            "renaming DevOOBE.cmd to DevOOBE2.cmd to remove unexpected reboot when under WTT." | Write-Log
            Rename-Item -Path W:\Devoobe.cmd -NewName devoobe.org.cmd -force
        }

        # Remove Selfhost Startup Scripts and settings.
        if (Test-Path W:\Selfhost_tools){
            "Removing Selfhost Tools" | Write-Log
            remove-item -path W:\Selfhost_tools -Force -Recurse
        }

        if ( ($PostActions -notmatch "noprivatefiles") -and ($PostActions -notmatch "nowinupdates") ){
            "Executing Private File actions" | Write-Log
            # Update any private files
            " - Checking for Windows file replacements" | Write-Log
            if (Test-Path "W:\DC_PostOS\WinUpdates"){
                "Coping W:\DC_PostOS\WinUpdates\ to W:\" | Write-Log
                & robocopy W:\DC_PostOS\WinUpdates W:\ /s /NFL /NDL
            }
        }

        # Side load install
        if ( ($PostActions -notmatch "noprivatedrivers") -and ($PostActions -notmatch "nodrivers") ) {
            "Adding any private drivers." | Write-Log
            # install any Private Drivers
            if (Test-Path "W:\DC_PostOS\Drivers_OS"){
                "Found: $((Get-ChildItem -Recurse -File).count) files to replace." | Write-Log
                dism /image:W:\ /add-driver /driver:W:\DC_PostOS\Drivers_OS /recurse /forceunsigned | Write-Log
            }
        }

        $AddLocalAdmin = $true
        if ( ($PostActions -match "nolocaladmin") -or ($PostActions -match "nla") ) {
            $AddLocalAdmin = $False
            "Skipping User Create" | Write-Log
        }

        if ( ($PostActions -match "nounattend") -or ($PostActions -match "skipunattend") ) {
            "Executing NO UNATTEND - Skipping unattend modifications" | Write-Log
            break
        }
        
        #   unattend.xml
        $unattendFile = "W:\Windows\Panther\unattend.xml"
        if (test-path $unattendFile) {
            copy-Item $unattendFile "$unattendFile.org"
        } else {
            "Unattend not found, coping default" | Write-Log
            new-item "W:\Windows\Panther" -ItemType "directory" -ErrorAction Ignore
            copy-item "W:\DC_PostOS\WTT_Core\unattend.xml" -destination "W:\Windows\Panther" -Container:$True
        }

        # check for ARM images that may do sysprep on the local machine, use the unattend that gets processed after
        if (Get-Content $unattendFile | select-string -pattern sysprepToOOBE.ps1) {
            $unattendFile = $(Get-ChildItem "W:\GoldenPath\*.oobe.unattend.xml").FullName
        }
                
        if (test-path $unattendFile) {
            copy-Item $unattendFile "$unattendFile.org"
        } else {
            copy-item "W:\DC_PostOS\WTT_Core\unattend.xml" $unattendFile
        }
        
        if (Test-Path $unattendFile){
            $unattendPW = "pw"
            $unattendAdmin = "Admin"

            [xml] $unattend = get-content $unattendFile

            $xmlOobeSystem=$unattend.unattend.Settings | Where-Object {$_.pass -eq "oobeSystem"}

            # Verify or Add "Microsoft-Windows-International-Core" section
            $core = $xmlOobeSystem.component | Where-Object {$_.name -eq "Microsoft-Windows-International-Core"} | Where-Object {$_.processorArchitecture -eq "$CPU_Arch"}
            if ($core -eq $null) {
                $node = $unattend.CreateElement("component", $xmlOobeSystem.NamespaceURI)
                $Node.SetAttribute("name", "Microsoft-Windows-International-Core")
                $Node.SetAttribute("processorArchitecture", "$CPU_Arch")
                $Node.SetAttribute("publicKeyToken", "31bf3856ad364e35")
                $Node.SetAttribute("language", "neutral")
                $Node.SetAttribute("versionScope", "nonSxS")
                $xmlOobeSystem.AppendChild($node)

                $locale = $unattend.CreateElement("InputLocale", $xmlOobeSystem.NamespaceURI)
                $locale.InnerText = "en-US"
                $Node.AppendChild($locale)
                $locale = $unattend.CreateElement("SystemLocale", $xmlOobeSystem.NamespaceURI)
                $locale.InnerText = "en-US"
                $Node.AppendChild($locale)
                $locale = $unattend.CreateElement("UILanguage", $xmlOobeSystem.NamespaceURI)
                $locale.InnerText = "en-US"
                $Node.AppendChild($locale)
                $locale = $unattend.CreateElement("UserLocale", $xmlOobeSystem.NamespaceURI)
                $locale.InnerText = "en-US"
                $Node.AppendChild($locale)
            }

            # Find OOBE Shell Setup Section
            $xmloobeSetup=$xmlOobeSystem.component | Where-Object {$_.name -eq "Microsoft-Windows-Shell-Setup"} | Where-Object {$_.processorArchitecture -eq "$CPU_Arch"}

            if ($xmloobeSetup -eq $null) {
                $node = $unattend.CreateElement("component", $xmlOobeSystem.NamespaceURI)
                $Node.SetAttribute("name", "Microsoft-Windows-Shell-Setup")
                $Node.SetAttribute("processorArchitecture", "$CPU_Arch")
                $Node.SetAttribute("publicKeyToken", "31bf3856ad364e35")
                $Node.SetAttribute("language", "neutral")
                $Node.SetAttribute("versionScope", "nonSxS")
                $xmlOobeSystem.AppendChild($node)
                $xmloobeSetup=$xmlOobeSystem.component | Where-Object {$_.name -eq "Microsoft-Windows-Shell-Setup"} | Where-Object {$_.processorArchitecture -eq "$CPU_Arch"}
            }

            # Overwrite OOBE section
            $xmlOOBE=$xmloobeSetup.OOBE
            if ($xmlOOBE -ne $null) {
                $xmloobeSetup.RemoveChild($xmlOOBE)
            }

            # Create OOBE Section
            $node = $unattend.CreateElement("OOBE", $xmlOobeSystem.NamespaceURI)
            $xmloobeSetup.AppendChild($node)

            $xmlElement = $unattend.CreateElement("HideEULAPage", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("HideOEMRegistrationScreen", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("HideOnlineAccountScreens", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("ProtectYourPC", $node.NamespaceURI)
            $xmlElement.InnerText = "3"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("HideWirelessSetupInOOBE", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("NetworkLocation", $node.NamespaceURI)
            $xmlElement.InnerText = "Work"
            $node.AppendChild($xmlElement)
            $xmlElement = $unattend.CreateElement("SkipMachineOOBE", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement) 
            $xmlElement = $unattend.CreateElement("SkipUserOOBE", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)
            # SERVER ONLY - doesn't hurt ;)
            $xmlElement = $unattend.CreateElement("HideLocalAccountScreen", $node.NamespaceURI)
            $xmlElement.InnerText = "true"
            $node.AppendChild($xmlElement)

            # Add TimeZone if missing
            $xmlTimeZone=$xmloobeSetup.TimeZone
            if ($xmlTimeZone -eq $null){
                $xmlTimeZone = $unattend.CreateElement("TimeZone", $node.NamespaceURI)
                $xmlTimeZone.InnerText = "Pacific Standard Time"
                $xmloobeSetup.AppendChild($xmlTimeZone)
            }

            if ($AddLocalAdmin) {

                # Overwrite Users Accounts for Auto-Logon
                $node=$xmloobeSetup.UserAccounts
                if ($node -ne $null){
                    $xmloobeSetup.RemoveChild($node)
                }
                $node=$xmloobeSetup.AutoLogon
                if ($node -ne $null){
                    $xmloobeSetup.RemoveChild($node)
                }

                # Add user accounts
                $xmlUserAccounts = $unattend.CreateElement("UserAccounts", $xmlOobeSystem.NamespaceURI)
                $xmloobeSetup.AppendChild($xmlUserAccounts)
                $xmlLocalAccounts = $unattend.CreateElement("LocalAccounts", $xmlOobeSystem.NamespaceURI)
                $xmlUserAccounts.AppendChild($xmlLocalAccounts)
                $xmlLocalAccount = $unattend.CreateElement("LocalAccount", $xmlOobeSystem.NamespaceURI)
                $xmlLocalAccounts.AppendChild($xmlLocalAccount)

                $xmlPassword= $unattend.CreateElement("Password", $xmlOobeSystem.NamespaceURI)
                $xmlLocalAccount.AppendChild($xmlPassword)

                $xmlElement = $unattend.CreateElement("Value", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "$unattendPW"
                $xmlPassword.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("PlainText", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "true"
                $xmlPassword.AppendChild($xmlElement)

                $xmlElement = $unattend.CreateElement("Description", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "Lab Account"
                $xmlLocalAccount.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("DisplayName", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "Local Admin"
                $xmlLocalAccount.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("Group", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "Administrators"
                $xmlLocalAccount.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("Name", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "$unattendAdmin"
                $xmlLocalAccount.AppendChild($xmlElement)

                # Add Admin Password
                $xmlAdminPassword = $unattend.CreateElement("AdministratorPassword", $xmlOobeSystem.NamespaceURI)
                $xmlUserAccounts.AppendChild($xmlAdminPassword)
                $xmlElement = $unattend.CreateElement("Value", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "$unattendPW"
                $xmlAdminPassword.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("PlainText", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "true"
                $xmlAdminPassword.AppendChild($xmlElement)

                # Add AutoLogon
                $xmlAutoLogon = $unattend.CreateElement("AutoLogon", $xmlOobeSystem.NamespaceURI)
                $xmloobeSetup.AppendChild($xmlAutoLogon)

                $xmlElement = $unattend.CreateElement("Enabled", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "true"
                $xmlAutoLogon.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("UserName", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "$unattendAdmin"
                $xmlAutoLogon.AppendChild($xmlElement)

                $xmlPassword= $unattend.CreateElement("Password", $xmlOobeSystem.NamespaceURI)
                $xmlAutoLogon.AppendChild($xmlPassword)
                $xmlElement = $unattend.CreateElement("Value", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "$unattendPW"
                $xmlPassword.AppendChild($xmlElement)
                $xmlElement = $unattend.CreateElement("PlainText", $xmlOobeSystem.NamespaceURI)
                $xmlElement.InnerText = "true"
                $xmlPassword.AppendChild($xmlElement)

                $xmlElement = $unattend.CreateElement("LogonCount", $xmlLocalAccount.NamespaceURI)
                $xmlElement.InnerText = "9999"
                $xmlAutoLogon.AppendChild($xmlElement)
            }

            # Customize Windows
            $xmlspecialize=$unattend.unattend.settings | Where-Object {$_.pass -eq "specialize"}
            if ($xmlspecialize -eq $null) {
                $node = $unattend.CreateElement("settings", $unattend.unattend.NamespaceURI)
                $Node.SetAttribute("pass", "specialize")
                $unattend.unattend.AppendChild($node)
                $xmlspecialize=$node

                $node = $unattend.CreateElement("component", $xmlspecialize.NamespaceURI)
                $Node.SetAttribute("name", "Microsoft-Windows-Shell-Setup")
                $Node.SetAttribute("processorArchitecture", "$CPU_Arch")
                $Node.SetAttribute("publicKeyToken", "31bf3856ad364e35")
                $Node.SetAttribute("language", "neutral")
                $Node.SetAttribute("versionScope", "nonSxS")
                $xmlspecialize.AppendChild($node)

                $xmlShellSpecialize = $node

            } else {
                $xmlShellSpecialize = $xmlspecialize.component | Where-Object {$_.name -eq "Microsoft-Windows-Shell-Setup"} | Where-Object {$_.processorArchitecture -eq "$CPU_Arch"}
                if ($xmlShellSpecialize -eq $null) {
                    $node = $unattend.CreateElement("component", $xmlspecialize.NamespaceURI)
                    $Node.SetAttribute("name", "Microsoft-Windows-Shell-Setup")
                    $Node.SetAttribute("processorArchitecture", "$CPU_Arch")
                    $Node.SetAttribute("publicKeyToken", "31bf3856ad364e35")
                    $Node.SetAttribute("language", "neutral")
                    $Node.SetAttribute("versionScope", "nonSxS")
                    $xmlspecialize.AppendChild($node)

                    $xmlShellSpecialize = $node
                }
            }

            # Set Computer Name
            #$xmlShellSpecialize = $xmlspecialize.component | where {$_.name -eq "Microsoft-Windows-Shell-Setup"}
            if ($xmlShellSpecialize.ComputerName -ne $null){
                $xmlShellSpecialize.ComputerName = "$PCName"

            } else {
                $node = $unattend.CreateElement("ComputerName", $xmlShellSpecialize.NamespaceURI)
                $node.InnerText = "$PCName"
                $xmlShellSpecialize.AppendChild($node)
            }

            #setup PostOS
            $xmlFirstLogon=$xmloobeSetup.FirstLogonCommands
            if ($xmlFirstLogon -eq $null){
                $xmlFirstLogon = $unattend.CreateElement("FirstLogonCommands", $xmlOobeSystem.NamespaceURI)
                $xmloobeSetup.AppendChild($xmlFirstLogon)
            }
            $xmlSynchronousCommand = $unattend.CreateElement("SynchronousCommand", $xmlOobeSystem.NamespaceURI)
            $xmlFirstLogon.AppendChild($xmlSynchronousCommand)
            $xmlElement= $unattend.CreateElement("Description", $xmlOobeSystem.NamespaceURI)
            $xmlElement.InnerText = "PostOS"
            $xmlSynchronousCommand.AppendChild($xmlElement)
            $xmlElement= $unattend.CreateElement("Order", $xmlOobeSystem.NamespaceURI)
            $Count = $xmlFirstLogon.ChildNodes.count
            $Count++
            $xmlElement.InnerText = "$count"
            $xmlSynchronousCommand.AppendChild($xmlElement)
            $xmlElement= $unattend.CreateElement("CommandLine", $xmlOobeSystem.NamespaceURI)
            $xmlElement.InnerText = "C:\DC_PostOS\Postos.cmd"
            $xmlSynchronousCommand.AppendChild($xmlElement)

            $unattend.Save($unattendFile)

        } else {
            "Unattend.xml not found!" | Write-Log
            "Not Found" | out-file -FilePath W:\Logs\Install\Unattend.xml
        }


        break
    } # while $true

    # Copy logs to Windows drive
    if (test-path $Global:LogDir){
        robocopy $Global:LogDir w:\Logs\Install /s
        robocopy "W:\Windows\Panther" W:\Logs\Install "unattend.xml"
    }


    if ($KernelDebug -ne "false"){
        # Setup Debugging
        $WIMGUID = "{4344F6A7-CD1E-48B8-9AD8-0ACE5B6AF332}"
        $SDIGUID = "{00267535-3EDB-43EC-91CE-392EC2B66CC3}"
        $BOOTGUID = "{bootmgr}"
        $DEFAULTGUID = "{default}"
        $dbgsetings = "{dbgsettings}"

        $output = & bcdedit /dbgsettings USB TARGETNAME:$PCName
        Write-Host $output

        if ( ($KernelDebug -eq "true") -or ($KernelDebug -match "Kernel") ) {
            $output = & bcdedit /set $DEFAULTGUID debug on
            Write-Host $output
        }
        if ($KernelDebug -match "Boot"){
            $output = & bcdedit /set $BOOTGUID bootdebug on
            Write-Host $output
        }
        if ($KernelDebug -match "win"){
            $output = & bcdedit /set $DEFAULTGUID bootdebug on
            Write-Host $output
        }
    }

    # PostOS Patch file - PLE images use this to install Drivers and Firmware.
    if (test-path("Z:\ImagePostInstallPatch\runme.ps1")){
        "Found PostInstall Patch, running runme.ps1"
        Z:\ImagePostInstallPatch\runme.ps1
    }


    write-host "Complete..."
    Write-Host "- Restart"
    wpeutil reboot
    exit 0
    
