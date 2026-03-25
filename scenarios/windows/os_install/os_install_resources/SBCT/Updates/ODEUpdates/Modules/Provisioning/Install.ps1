#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
<#

DCarv's Install.ps1 for installing across network.

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
    Write-Host "  NETWORK IMAGE INSTALLER - email DCarv for more info."
    Write-Host "********************"


    $Global:rootPath = "X:"
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

    # For recovery use X: in case S:\ (EFI) has been wiped. X: is in RAM and will always be available
    "- Getting WTT or HLK Data from ODE WIM" | Write-Log
    if (Test-Path -Path "x:\buildlink.txt") {
        $BuildLink = gc "x:\buildlink.txt"
    }
    "    * Build Path: $BuildLink" | Write-Log
    $Username = gc "x:\username.txt"
    "    * Username:   $Username" | Write-Log
    $Password = gc "x:\password.txt"
    "    * Password:   [located but withheld]" | Write-Log



    # Network mount with retry logic
    net use z: /delete /yes | Out-Null
    "Mounting ODE path to z:" | Write-Log
    $retryAttempts = 20
    net use z: "$BuildLink" "$Password" /user:$Username
    While ( ($LASTEXITCODE -ne 0) -and ($retryAttempts -ne 0) ) {
        $RetryAttempts--
        start-sleep 30 
        "Net use failed, Waiting 30 seconds..."
        net use z: "$BuildLink" "$Password" /user:$Username
    }
    if ( $LASTEXITCODE -ne 0) {
        "Last exit code: $LASTEXITCODE.`r`nNetwork Mount failed.`r`n$output" | Write-Log
        wpeutil reboot
    }
    if ( ($retryAttempts -eq 0) -and ($LASTEXITCODE -ne 0)){
        "Last exit code: $LASTEXITCODE.`r`nRetry attempt reached.`r`n$output" | Write-Log
        wpeutil reboot
    }

    if( -not (Test-Path "z:\") ) {
        New-PSDrive "Z" -PSProvider FileSystem -Root "Z:\" -Scope Global
    }

    Write-Host "`r`n- Calling Install.ps1 from Network share...."
    Push-Location z:\

    # remove TXT file so PostOS causes exception and we get control back to run local PostOS script
    #Remove-Item "S:\password.txt" -Force -ErrorAction Ignore

    try{
        if ($ENV:PROCESSOR_ARCHITECTURE -like "ARM*") {
            & "X:\Program Files\Powershell\pwsh.exe" -ExecutionPolicy bypass -command "& z:\modules\Provisioning\Install.ps1 -ExitAfterInstall -HCKInstall -SkipClear"
        } else {
            & powershell -ExecutionPolicy bypass -command "& z:\modules\Provisioning\Install.ps1 -ExitAfterInstall -HCKInstall -SkipClear"
        }
    } catch {
        Write-Host "Exception caught from Net Install.ps1 as planned."
    }

    #popd
    Write-Host "- [dcarv's] Installing Post Deployment Software"

    # Load our new file
    #x:\modules\Imaging\Install-PostDeviceDeployment.ps1
    #Install-PostDeviceDeployment.ps1 -HCKInstall       

    
    # PostOS
    #---------------------------------------------
    $PostActions = "full"
    $KernelDebug = "false"
    # Determine CPU type
    $CPU_Arch = $Env:Processor_Architecture

    # Post Install Customizations actions
    if (Test-Path "x:\PostActions.txt"){
        $PostActions = gc "x:\PostActions.txt" 
    }
    "    * PostActions: $PostActions" | Write-Log
    # Check to enable USB Debug
    if (Test-Path "x:\KernelDebug.txt"){
        $KernelDebug = gc "x:\KernelDebug.txt"
    }
    "    * KernelDebug: $KernelDebug" | Write-Log
    # Unattend.xml
    if (Test-Path "x:\pcname.txt"){
        $PCName =   gc "x:\pcname.txt"
        "    * PC Name:    $PCName" | Write-Log
    }

    if( -not (Test-Path "v:\") ){
        New-PSDrive "v" -PSProvider FileSystem -Root "v:\" -Scope Global
    }

    #$recoveryPath = Get-PartitionCommands -Format RecoveryImagePath -ForVHD $False -DiskIndex $DiskIndex
    #$osLetter =  Get-PartitionCommands -Format OSLetter -ForVHD $False -DiskIndex $DiskIndex
    #$efiLetter = Get-PartitionCommands -Format EFILetter -ForVHD $False -DiskIndex $DiskIndex
    #$recoveryImageLetter = Get-PartitionCommands -Format RecoveryImageLetter -ForVHD $False -DiskIndex $DiskIndex
    
    $OSPartition = Get-PartitionCommands -format OSPartition -ForVHD $False
    "OSPartition: $OSPartition"

<#
    # Assign a letter to the new Windows Partition for Post-processing
    "- Mounting Windows Partition" | Write-Log
    $emmcDisk = Get-WmiObject Win32_DiskDrive -Filter "MediaType='Fixed hard disk media'"
    if ($emmcDisk -eq $null){
        "Unable to find fix hard disk media drive" | Log-Output
        exit 1
    }
    $diskIndex = $emmcDisk.Index
#>

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
    Write-Host "- Copying PostOS Scripts"
    robocopy /mir "X:\Updates\DC_PostOS" "W:\DC_PostOS"

    # Copy build info for WTT Dimension
    "- Copy Buildinfo for WTT" | write-Log
    if ($BuildLink.length -gt 0){ 
        $BuildLink | Out-File -Encoding ASCII -FilePath "W:\DC_PostOS\buildlink.txt" -Force
    }
    if (Test-Path "X:\pcname.txt"){
        Copy-Item "x:\pcname.txt" "W:\DC_PostOS\pcname.txt"
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
                
        if ( ($PostActions -match"wttclientonly") -or ($PostActions -match "clientonly") ){
            "Executing Client install, adding PostOS RunOnce Registry key." | Write-Log
            W:\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot W:\windows\system32\config -registryFilePath W:\DC_PostOS\RegFiles_OS\PostOS
            break
        }

        if ($PostActions -match "none"){
            "Executing Unattend NONE actions and exiting." | Write-Log
            if (Test-Path "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk"){
                Copy-Item "W:\DC_PostOS\WTT_Core\WTTClientInstall.lnk" "W:\Users\default\Desktop\WTTClientInstall.lnk"
            }
            if (Test-Path "X:\pcname.txt"){
                Copy-Item "x:\pcname.txt" "W:\DC_PostOS\pcname.txt"
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

        if ( ($PostActions -match "norollback") -or ($PostActions -match "nrb") ){
            "Executing NO ROLLBACK, removing ROLLBACK registry policy." | Write-Log
            $filepath = "W:\DC_PostOS\RegFiles_OS"
            if (Test-Path $filepath){
                foreach ($f in gci $filepath | Where-Object {$_.name -like "rollback*.reg"}) {Remove-Item "$filepath\$($f.name)"}
            }
            if (test-path ("X:\ImagePostInstallPatch\CMD_RollbackFirmware.txt")){
                remove-item ("X:\ImagePostInstallPatch\CMD_RollbackFirmware.txt") -Force -ErrorAction Ignore
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
            copy-item "W:\DC_PostOS\unattend.xml" -destination "W:\Windows\Panther" -Container:$True
        }

        # check for ARM images that may do sysprep on the local machine, use the unattend that gets processed after
        if (Get-Content $unattendFile | select-string -pattern sysprepToOOBE.ps1) {
            $GoldenUnattend = $TRUE
            $unattendFile = $(Get-ChildItem "W:\GoldenPath\*.oobe.unattend.xml").FullName
            Remove-Item ("W:\DC_PostOS\RegFiles_OS\postos.reg")
        }
                
        if (test-path $unattendFile) {
            copy-Item $unattendFile "$unattendFile.org"
        } else {
            copy-item "W:\DC_PostOS\unattend.xml" $unattendFile
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

            if (($PostActions -match "LocalAdmin")) {

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


    $WIMGUID = "{4344F6A7-CD1E-48B8-9AD8-0ACE5B6AF332}"
    $SDIGUID = "{00267535-3EDB-43EC-91CE-392EC2B66CC3}"
    $BOOTGUID = "{bootmgr}"
    $DEFAULTGUID = "{default}"
    $dbgsetings = "{dbgsettings}"

<#  Leaving, may need for dev devices
    $output = & bcdedit /set $DEFAULTGUID debug off
    Write-Host $output
    $output = & bcdedit /set $BOOTGUID bootdebug off
    Write-Host $output
    $output = & bcdedit /set $DEFAULTGUID bootdebug off
    Write-Host $output
#>

    if ($KernelDebug -ne "false"){
        # Setup Debugging
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


    if (test-path("Z:\ImagePostInstallPatch\runme.ps1")){
        "Found PostInstall Patch, running runme.ps1"
        Z:\ImagePostInstallPatch\runme.ps1
    }

    copy-item x:\logs W:\DC_PostOS -recurse

    write-host "Complete..."
    Write-Host "- Restart"
    wpeutil reboot
    exit 0
