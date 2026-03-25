

# Installs the OS image from the USB Key
function Install-USBKey {
    param(
        [Parameter(Mandatory)]
        [string] $LogFolder
    )
    trap {
        $_
        Write-Host 'Stack Trace'
        Write-Host $_.ScriptStackTrace
    }

    Write-Host "------------------------------"
    Write-Host "Find USB Drive"
    Write-Host "------------------------------"
    $UsbVolume = Get-Volume -FileSystemLabel "BOOTME" | Select-Object -first 1
    $UsbDriveLetter = $UsbVolume.DriveLetter

    Write-Host "------------------------------"
    Write-Host "USB Drive"
    Write-Host "------------------------------"
    $UsbDrivePath = "$UsbDriveLetter`:"
    if (-not (Test-Path $UsbDrivePath)) {
        Write-Error "$UsbDrivePath does not exist"
    }

    Write-Host "------------------------------"
    Write-Host "Check for Source OS Path"
    Write-Host "------------------------------"
    $SourcePath = "$UsbDrivePath\osimage"
    if (-not (Test-Path $SourcePath)) {
        Write-Error "Source OS path not found"
        return
    }

    Write-Host "------------------------------"
    Write-Host "Check for SBCT"
    Write-Host "------------------------------"
    $SbctBinPath = "$UsbDrivePath\bin\sbct"
    if (-not (Test-Path $SbctBinPath)) {
        Write-Error "SBCT not found - missing SBCT tool at $SbctBinPath"
        return
    }

    Write-Host "------------------------------"
    Write-Host " Assign pwshmod path"
    Write-Host "------------------------------"
    $PwshmodPath = "$UsbDrivePath\pwshmod"

    Write-Host "------------------------------"
    Write-Host " Assign postdeploy path"
    Write-Host "------------------------------"
    $PostDeployRoot = "$UsbDrivePath\bin\postdeploy"

    Write-Host "------------------------------"
    Write-Host " Load WinPE Extensions"
    Write-Host "------------------------------"
    $WPEExtensions = "$PostDeployRoot\WPEExtensions.ps1"
    if (Test-Path $WPEExtensions) {
        . $WPEExtensions
    }

    if (Test-Path Function:\Invoke-WPEPreInstall) {
        Write-Host "------------------------------"
        Write-Host " Invoke-WPEPreInstall"
        Write-Host "------------------------------"
        Invoke-WPEPreInstall
    }

    Write-Host "------------------------------"
    Write-Host "Install OS Image"
    Write-Host "------------------------------"
    #. $PSScriptRoot\flash_common.ps1 -SourceOSPath $SourcePath -BatteryLevel 45 -SbctBinPath $SbctBinPath -PwshmodPath $PwshmodPath -PostDeployRoot $PostDeployRoot

    $NonUsbDisks = Get-NonUsbDisk
    Write-Host "> Using Disk: $($NonUsbDisks[0].Number), $($NonUsbDisks[0].Model), $($NonUsbDisks[0].Size)"
    $diskNumber = $NonUsbDisks[0].Number
    $flashSplat = @{
        SourceOSPath = $SourcePath
        DestDiskNumber = $diskNumber
        BatteryLevel = 45
        SbctBinPath = $SbctBinPath
        PwshmodPath = $PwshmodPath
        PostDeployRoot = $PostDeployRoot
        RuntimeConfig = $script:runtimeConfig
        LogFolder = $LogFolder
    }
    . $PSScriptRoot\flash_common.ps1 @flashSplat -skiprestart

}

function Install-Net {
    param(
        [Parameter(Mandatory)]
        [string] $LogFolder
    )
    trap {
        $_
        Write-Host 'Stack Trace'
        Write-Host $_.ScriptStackTrace
    }

    # Connect to Network share (\\plewusrv1\plegolden) and use a USB Network dongle to install image over Network
    # To setup, see \tools\ple\NetImaging\ - SetupODE.ps1 or ToastImgr.exe
    # email DCarv for issues (wiki -> )

    Write-Host "------------------------------"
    Write-Host "USB NET - Setting path to X:"
    Write-Host "------------------------------"
    $UsbDrivePath = "X:"
 
    Write-Host "------------------------------"
    Write-Host "Check for SBCT"
    Write-Host "------------------------------"
    $SbctBinPath = "$UsbDrivePath\bin\sbct"
    if (-not (Test-Path $SbctBinPath)) {
        Write-Error "SBCT not found - missing SBCT tool at $SbctBinPath"
        return
    }

    Write-Host "------------------------------"
    Write-Host " DCarv's Net Install Setup !!!"
    Write-Host "------------------------------"
     # For recovery use X: in case S:\ (EFI) has been wiped. X: is in RAM and will always be available
     Write-Host "- Getting WTT or HLK Data from ODE WIM"
     $BuildLink = gc "x:\buildlink.txt"
     Write-Host "    * Build Path: $BuildLink"
     $Username = gc "x:\username.txt"
     Write-Host "    * Username:   $Username"
     $Password = gc "x:\password.txt"
     Write-Host "    * Password:   [located but withheld]"
 
      # Still need S: for HLK/WTT Files on the first pass to eliminate orphaned machines.  After that use X:
     $output = & mountvol s: /s
     if ($LASTEXITCODE -ne 0) {
        Write-Host "Last exit code: $LASTEXITCODE`r`nMounting EFI Partition failed`r`n$output"
     }
     if( -not (Test-Path "s:\") ) {
        New-PSDrive "S" -PSProvider FileSystem -Root "S:\" -Scope Global
     }
     Write-Host "- Checking for s:\HLK Folder"
     if (Test-Path "s:\HLK") {
        Write-Host "    * Copy s:\HLK x:\HLK"
        robocopy /mir /r:0 s:\HLK x:\HLK
     }
     Write-Host  "- Checking for s:\WTT Folder"
     if (Test-Path "s:\WTT") {
        Write-Host "    * Copy s:\WTT x:\WTT"
        robocopy /mir /r:0 s:\WTT x:\WTT
     }
     Write-Host "    * Dismount S:"
     $output = & mountvol s: /d
     if ($LASTEXITCODE -ne 0) {
        Write-Host "Last exit code: $LASTEXITCODE`r`nDismounting EFI Partition failed`r`n$output"
        #exit 1
     }
 
     # Network mount with retry logic
     net use z: /delete /yes | Out-Null
     Write-Host "Mounting ODE path to z:"
     $retryAttempts = 20
     net use z: "$BuildLink" "$Password" /user:$Username
     While ( ($LASTEXITCODE -ne 0) -and ($retryAttempts -ne 0) ) {
        $RetryAttempts--
        start-sleep 30 
        Write-Host "Net use failed, Waiting 30 seconds..."
        net use z: "$BuildLink" "$Password" /user:$Username
     }
     if ( $LASTEXITCODE -ne 0) {
        Write-Host "Last exit code: $LASTEXITCODE.`r`nNetwork Mount failed.`r`n$output"
        wpeutil reboot
     }
     if ( ($retryAttempts -eq 0) -and ($LASTEXITCODE -ne 0)){
        Write-Error "Last exit code: $LASTEXITCODE.`r`nRetry attempt reached.`r`n$output"
        wpeutil reboot
     }
      if( -not (Test-Path "z:\") ) {
        New-PSDrive "Z" -PSProvider FileSystem -Root "Z:\" -Scope Global
     }

     Write-Host "`r`n- Start the magic. Calling Flash-Common.ps1 from Network share...."
     Push-Location z:\

    Write-Host "------------------------------"
    Write-Host " Assign pwshmod path"
    $PwshmodPath = "$UsbDrivePath\pwshmod"       ##  Work around until Install-Image is fixed for log write
    Write-Host "PwshmodPath: $PwshmodPath"
    Write-Host "------------------------------"
    
    Write-Host "------------------------------"
    Write-Host "Check for Source OS Path"
    $SourcePath = "Z:\osimage"
    Write-Host "Updated SourcePath: $SourcePath"
    Write-Host "------------------------------"
    if (-not (Test-Path $SourcePath)) {
        Write-Error "Source OS path not found"
        return
    }

    Write-Host "------------------------------"
    Write-Host " Assign postdeploy path"
#    $PostDeployRoot = "$UsbDrivePath\bin\postdeploy"
    $PostDeployRoot = "Z:\bin\postdeploy"
    Write-Host "PostDeployRoot: $PostDeployRoot"
    Write-Host "------------------------------"

    Write-Host "------------------------------"
    Write-Host " Load WinPE Extensions"
    $WPEExtensions = "$PostDeployRoot\WPEExtensions.ps1"
    Write-Host "WPEExtensions: $WPEExtensions"
    Write-Host "------------------------------"
    if (Test-Path $WPEExtensions) {
        . $WPEExtensions
    }

    if (Test-Path Function:\Invoke-WPEPreInstall) {
        Write-Host "------------------------------"
        Write-Host " Invoke-WPEPreInstall"
        Write-Host "------------------------------"
        Invoke-WPEPreInstall
    }

    Write-Host "------------------------------"
    Write-Host "Install OS Image"
    Write-Host "------------------------------"
    #. $PSScriptRoot\flash_common.ps1 -SourceOSPath $SourcePath -BatteryLevel 45 -SbctBinPath $SbctBinPath -PwshmodPath $PwshmodPath -PostDeployRoot $PostDeployRoot -skiprestart
    
    $NonUsbDisks = Get-NonUsbDisk
    $diskNumber = $NonUsbDisks[0].Number
    $flashSplat = @{
        SourceOSPath = $SourcePath
        DestDiskNumber = $diskNumber
        BatteryLevel = 45
        SbctBinPath = $SbctBinPath
        PwshmodPath = $PwshmodPath
        PostDeployRoot = $PostDeployRoot
        RuntimeConfig = $script:runtimeConfig
        LogFolder = $LogFolder
        $USBKeyInstall = $false

    }
    . $PSScriptRoot\flash_common.ps1 @flashSplat -skiprestart
}

function Install-Local {
    param(
        [Parameter(Mandatory)]
        [string] $LogFolder
    )
    trap {
        $_
        Write-Host 'Stack Trace'
        Write-Host $_.ScriptStackTrace
    }

    # WiFi and Toast ReImage will set Volume to 'SHIFU_SCOTT' to identify requested install path.  Reset Vol label to avoid loops.
    # This may cause issue if user wants to boot to USB and volume fails to be renamed.  Run Diskpart -clean from WinPE to reimage from USB.
    # email DCarv for issues  (Wiki -> )
    Write-Host "------------------------------"
    Write-Host "Install-Local image"
    Write-Host "------------------------------"
    $UsbDriveLetter = (get-volume -FriendlyName 'SHIFU_SCOTT' -erroraction ignore).DriveLetter
    $UsbDrivePath = "$UsbDriveLetter`:"
    if (-not (Test-Path $UsbDrivePath)) {
        Write-Host "$UsbDrivePath does not exist"
        Write-Error "Partition 'SHIFU_SCOTT' not found"
        return
    }

    # Label does not work
    Write-Host "------------------------------"
    Write-Host " Setting Drive Label"
    Write-Host "------------------------------"
    $LocalInstallDrive = Get-CimInstance -ClassName Win32_Volume -Filter "DriveLetter = '$UsbDrivePath'"
    $LocalInstallDrive | Set-CimInstance -Property @{Label='BOOTME'}

    Write-Host "------------------------------"
    Write-Host "Check for Source OS Path"
    Write-Host "------------------------------"
    $SourcePath = "$UsbDrivePath\osimage"
    if (-not (Test-Path $SourcePath)) {
        Write-Error "$SourcePath path not found"
        return
    }

    Write-Host "------------------------------"
    Write-Host "Check for SBCT"
    Write-Host "------------------------------"
    $SbctBinPath = "$UsbDrivePath\bin\sbct"
    if (-not (Test-Path $SbctBinPath)) {
        Write-Error "SBCT not found - missing SBCT tool at $SbctBinPath"
        return
    }

    Write-Host "------------------------------"
    Write-Host " Assign pwshmod path"
    Write-Host "------------------------------"
    $PwshmodPath = "$UsbDrivePath\pwshmod"

    Write-Host "------------------------------"
    Write-Host " Assign postdeploy path"
    Write-Host "------------------------------"
    $PostDeployRoot = "$UsbDrivePath\bin\postdeploy"

    Write-Host "------------------------------"
    Write-Host " Load WinPE Extensions"
    Write-Host "------------------------------"
    $WPEExtensions = "$PostDeployRoot\WPEExtensions.ps1"
    if (Test-Path $WPEExtensions) {
        . $WPEExtensions
    }

    if (Test-Path Function:\Invoke-WPEPreInstall) {
        Write-Host "------------------------------"
        Write-Host " Invoke-WPEPreInstall"
        Write-Host "------------------------------"
        Invoke-WPEPreInstall
    }

    Write-Host "------------------------------"
    Write-Host "Install OS Image"
    Write-Host "------------------------------"
    #. $PSScriptRoot\flash_common.ps1 -SourceOSPath $SourcePath -BatteryLevel 45 -SbctBinPath $SbctBinPath -PwshmodPath $PwshmodPath -PostDeployRoot $PostDeployRoot -SkipRestart

    $NonUsbDisks = Get-NonUsbDisk
    $diskNumber = $NonUsbDisks[0].Number
    $flashSplat = @{
        SourceOSPath = $SourcePath
        DestDiskNumber = $diskNumber
        BatteryLevel = 45
        SbctBinPath = $SbctBinPath
        PwshmodPath = $PwshmodPath
        PostDeployRoot = $PostDeployRoot
        RuntimeConfig = $script:runtimeConfig
        LogFolder = $LogFolder
        $KeylessInstall = $true
        $USBKeyInstall = $false
    }
    . $PSScriptRoot\flash_common.ps1 @flashSplat -skiprestart

}

# starts Device Bridge and DBDiscoveryClient and waits
function Start-DeviceBridge {
    param (
        [Parameter(Mandatory, Position = 0)]
        [string] $rootPath
    )
    $DBDiscoveryPath = "$rootPath\DBDiscoveryClient.exe"
    $DeviceBridgePath = "$rootPath\DeviceBridgeProxy.exe"

    Write-Host "- DBDiscoveryClient: $DBDiscoveryPath"
    Write-Host "- DeviceBridgeProxy: $DeviceBridgePath"
    if (-not ($DBDiscoveryPath -and $DeviceBridgePath)) {
        Write-Error "Did not find DeviceBridge Proxy or Client"
    }

    $ShutdownWaitCount = 0
    $ShutdownWait = $false

    # wait for adapter to be present
    $ShutdownWaitCount = $ShutdownWaitCounter
    while (@(netsh interface show interface | Where-Object { $_ -match "Enabled" } | Where-Object { $_ -match "Ethernet" }).Count -eq 0) {
        Write-Host "Waiting for network interface... ctrl-c to stop ($ShutdownWaitCount)"
        Start-Sleep -Seconds 5

        if ($ShutdownWait) {
            if ($ShutdownWaitCount -le 0) {
                Write-Host "Timed out - shut down"
                Stop-Computer -force
                pause
            }
            $ShutdownWaitCount--
        }
    }

    Write-Host "- DeviceImaging: got interface"
    # wait for adapter to be connected
    $ShutdownWaitCount = $ShutdownWaitCounter
    while (@(netsh interface show interface | Where-Object { $_ -match " Connected" } | Where-Object { $_ -match "Ethernet" }).Count -eq 0) {
        Write-Host "Waiting for network connection... ctrl-c to stop ($ShutdownWaitCount)"
        Start-Sleep -Seconds 5

        if ($ShutdownWait) {
            if ($ShutdownWaitCount -le 0) {
                Write-Host "Timed out - shut down"
                Stop-Computer -force
                pause
            }
            $ShutdownWaitCount--
        }
    }

    Write-Host "- DeviceImaging: got network connection"
    Start-Sleep -Seconds 3
    while (-not ((ipconfig) -match "192.") ) {
        if ( (ipconfig) -match "169.254." ) {
            Write-Host "Renewing IP"
            ipconfig /release
            ipconfig /renew
        }
        else {
            Write-Host "IP address not correct, waiting"
        }
        Start-Sleep -Seconds 3
    }
    Write-Host "- DeviceImaging: got network IP address"
    $IPAddress = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPAddress } | Select-Object -Expand IPAddress
    Write-Host $IPAddress

    if ($DBDiscoveryPath -and $DeviceBridgePath) {
        Write-Host "- DBDiscoveryClient: starting $DBDiscoveryPath"
        Start-Process -FilePath $DBDiscoveryPath

        Write-Host "- DeviceBridgeProxy: starting $DeviceBridgePath"
        Start-Process -FilePath $DeviceBridgePath
    }
}
function Get-NonUsbDisk {
    $disk = @(Get-Disk | Where-Object BusType -ne "USB" | Where-Object Size -gt 20GB)
    Write-Host "Found $($disk.Count) non-USB disk(s) with size greater than 20GB"
    return $disk
}

function Get-ConfigFilePath {
    Write-Host "---------------------------------------"
    Write-Host "Find internal storage disk"
    Write-Host "---------------------------------------"
    $NonUsbDisks = Get-NonUsbDisk
    Write-Host "> Using Disk: $($NonUsbDisks[0].Number), $($NonUsbDisks[0].Model), $($NonUsbDisks[0].Size)"
    $diskNumber = $NonUsbDisks[0].Number

    Write-Host "---------------------------------------"
    Write-Host "Mount partitions"
    Write-Host "---------------------------------------"
    Write-Host "> Set-PartitionsToDriveLetters"
    # Recovery/Recovery Tools partitions
    Set-PartitionsToDriveLetters -DiskNumber $NonUsbDisks[0].Number -PartitionGuid "{de94bba4-06d1-4d40-a16a-bfd50179d6ac}"
    # WINPE partition for Provisioning
    Set-PartitionsToDriveLetters -DiskNumber $NonUsbDisks[0].Number -PartitionGuid "{ebd0a0a2-b9e5-4433-87c0-68b6b72699c7}"
    Write-Host "> Set-PartitionsToDriveLetters Done"

    # Check in Recovery Image or BOOTME partition first, return with first found
    $volumeLabel = @("Recovery image", "BOOTME")
    $improvWinpeConfigPath = "`:\winpe\config.json"
    $usbConfigPath = "`:\config.json"
    foreach ($label in $volumeLabel) {
        Write-Host "---------------------------------"
        Write-Host "Find runtime config in $label"
        Write-Host "---------------------------------"
        $DriveLetter = (Get-Volume | Where-Object FileSystemLabel -eq $label | Select-Object -first 1 | Get-Partition).DriveLetter
        if ( $null -ne $DriveLetter ) {
            $RecoveryDrivePath = $DriveLetter + $improvWinpeConfigPath
            $UsbDrivePath = $DriveLetter + $usbConfigPath
            if ( Test-Path -Path $RecoveryDrivePath ) {
                return $RecoveryDrivePath
            }
            if ( Test-Path -Path $UsbDrivePath ) {
                return $UsbDrivePath
            }
        }
    }
    # we check for Customer WinPE partition here. This scenario is for when provisioning copies the
    # ImprovWinPE into partition 4 as part of the factory layout
    Write-Host "---------------------------------------"
    Write-Host "Find runtime config in Disk $diskNumber"
    Write-Host "---------------------------------------"
    if ( (Get-Partition -DiskNumber $diskNumber -ErrorAction SilentlyContinue).Count -gt 4 ) {
        $WPELetter = (Get-Volume | Where-Object FileSystemLabel -eq "WINPE" | Select-Object -first 1 | Get-Partition).DriveLetter
        if ($WPELetter) {
            $WPEDrivePath = $WPELetter + $improvWinpeConfigPath
            if ($WPEDrivePath -eq $improvWinpeConfigPath) {
                Write-Error "Drive Letter not assigned to the WinPE partition"
            }
            return $WPEDrivePath
        }
    }
    Write-Host "------------------------------"
    Write-Host "No runtime config found"
    Write-Host "------------------------------"
    return $null
}

function Get-RuntimeConfig {
    $configFilePath = Get-ConfigFilePath
    Write-Host "configFile: $configFilePath"
    $defaultConfig = @{commands = ,@{mode = 'installOS'}}

    if ($configFilePath -and (Test-Path $configFilePath)) {
        $parsedObj = Get-Content $configFilePath -Raw | ConvertFrom-Json -AsHashtable
        if ($parsedObj.commands.count -eq 0) {
            $parsedObj += $defaultConfig
        }
    }
    else {
        Write-Host "    WARN: $configFilePath not found"
    }

    $parsedObj ?? $defaultConfig
}

function Set-PartitionsToDriveLetters {
    param(
        [int] $DiskNumber,
        [string] $PartitionGuid
    )

    $REPartition = @(Get-Partition -DiskNumber $DiskNumber -ErrorAction Continue | Where-Object { $_.GptType -eq $PartitionGuid })

    $REPartition | ForEach-Object {
        $RELetter = $_.DriveLetter
        if ($RELetter) {
            Remove-PartitionAccessPath -DiskNumber $DiskNumber -PartitionNumber $_.PartitionNumber -AccessPath "$RELetter`:"
        }
    }
    $REPartition = @(Get-Partition -DiskNumber $DiskNumber -ErrorAction Continue | Where-Object { $_.GptType -eq $PartitionGuid })


    $REPartition | ForEach-Object {
        $RELetter = $_.DriveLetter
        Write-Host "$($_.DiskNumber) $($_.PartitionNumber) $($_.GptType) $($_.DriveLetter)"
        if (-not $RELetter) {
            Write-Host "> Mounting Disk:$DiskNumber Partition:$PartitionGuid"
            $addPartPath = $false
            try {
                Add-PartitionAccessPath -DiskNumber $DiskNumber -PartitionNumber $_.PartitionNumber -AssignDriveLetter
                $addPartPath = $true
            }
            catch {
                Write-Host "    - Add-PartitionAccessPath failed"
            }

            if (-not $addPartPath) {
                $ltrs = Get-PSDrive | ForEach-Object { $_.Name }
                $freeLtr = 'A'
                foreach ($ltr in 'C'..'Z') {
                    if (-not ($ltr -in $ltrs)) {
                        $freeLtr = $ltr
                        break
                    }
                }
                $_ | Set-Partition -NewDriveLetter $freeLtr
            }

            $null = Get-PSDrive
            Update-Disk -Number $DiskNumber
            Update-HostStorageCache
        }
    }
}

function GetLogFolder {

    if (test-path x:\log) {remove-item -path "$PSScriptRoot\log" -recurse -force}
    if (test-path x:\logs) {remove-item -path "$PSScriptRoot\logs" -recurse -force}
    $logFolder = mkdir -Path  "$PSScriptRoot\logs"
    return $logFolder.FullName

    $UsbVolume = Get-Volume -FileSystemLabel "BOOTME", "WinPE" -ErrorAction SilentlyContinue | Sort-Object -Property FileSystemLabel | Select-Object -First 1
    if (-not $UsbVolume) {
        if (test-path x:\log) {remove-item -path "$PSScriptRoot\log" -recurse -force}
        if (test-path x:\logs) {remove-item -path "$PSScriptRoot\logs" -recurse -force}
        $logFolder = mkdir -Path  "$PSScriptRoot\logs"
    }
    else {
        $logPathPrefix = "$($UsbVolume.DriveLetter):\logs_"
        $folders = Get-ChildItem -Path "${logPathPrefix}*" | Sort-Object -Property CreationTime
        if ($folders.count -ge 10) {
            Remove-Item -Path $folders[0..$($folders.Count - 10)] -Recurse -Force
        }

        [int] $dailyCount = 0
        $folderPathWithDate = $LogPathPrefix + (Get-Date -Format 'yyyyMMdd')
        $folderWithSameDate = $folders.Where({$_.FullName -like "${folderPathWithDate}*"})
        if ($folderWithSameDate) {
            [int[]] $n = $folderWithSameDate.Name | ForEach-Object { $_ -split '\.' | Select-Object -Last 1 }
            $dailyCount = ($n | Sort-Object | Select-Object -Last 1) + 1
        }

        $logFolder = mkdir -Path "${folderPathWithDate}.${dailyCount}"
    }

    return $logFolder.FullName
}

function PostInstallProcessing {

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

    if (Test-Path "x:\buildlink.txt"){
        $BuildLink = gc "x:\buildlink.txt"
        "    * Build Path: $BuildLink" | Write-Log
    }
    # Post Install Customizations actions
    if (Test-Path "x:\PostActions.txt"){
        $PostActions = gc "x:\PostActions.txt" 
    }
    Write-Host "    * PostActions: $PostActions"
    # Check to enable USB Debug
    if (Test-Path "x:\KernelDebug.txt"){
        $KernelDebug = gc "x:\KernelDebug.txt"
    }
    Write-Host "    * KernelDebug: $KernelDebug"
    # Unattend.xml
    if (Test-Path "x:\pcname.txt"){
        $PCName = gc "x:\pcname.txt"
        Write-Host "    * PC Name:    $PCName"
    }

    if( -not (Test-Path "v:\") ){
        New-PSDrive "v" -PSProvider FileSystem -Root "v:\" -Scope Global
    }

    $OSPartition = Get-Partition -DiskNumber 0 | Where-Object { $_.GptType -eq "{ebd0a0a2-b9e5-4433-87c0-68b6b72699c7}" } | Select-Object -first 1
    $OSLetter = $OSPartition.DriveLetter

    Write-Host "OS Letter: $OSLetter"

    # Verify SBCT installed a new image, if not recover and reboot back to Windows.
    if (Test-Path "$OSLetter`:\SafeBuild"){
        $host.UI.RawUI.BackgroundColor = "RED"
        $current = "{current}"
        $output = & bcdedit /delete $current
        Write-Host $output 
        robocopy $Global:LogDir "$osletter`:\Logs\Install" /s
        Clear-Host
        for($i = 0; $i -lt 50; $i++){ write-host "Install.ps1 failed to apply new image!!" -Foreground Yellow }
        Start-Sleep 10
        Write-Host "Install.ps1 failed to apply image, rebooting back to orginal OS." | 
        Restart-Computer
    }

    # Copy Install Scripts to Windows Partiton
    if(Test-Path "X:\Updates\DC_PostOS"){
        Write-Host "- Copying PostOS Scripts"
        robocopy /mir "X:\Updates\DC_PostOS" "$osletter`:\DC_PostOS"

        # Copy build info for WTT Dimension
        Write-Host "- Copy Buildinfo for WTT"
        $BuildLink | Out-File -Encoding ASCII -FilePath "$OSLetter`:\DC_PostOS\buildlink.txt" -Force
        if (Test-Path "X:\pcname.txt"){
            Copy-Item "x:\pcname.txt" "$osletter`:\DC_PostOS\pcname.txt"
        }
    }

    # Copy WTT or HLK Folders so job continues
    if (Test-Path "x:\WTT"){
        Write-Host "    - Copy WTT Folder"
        Write-Host "    - Copy x:\WTT $osletter`:\WTT"
        robocopy /mir "x:\WTT" "$osletter`:\WTT"

    } elseif (Test-Path "x:\HLK") {        
        Write-Host "    - Copy HLK Folder"
        Write-Host "    - Copy x:\HLK $osletter`:\HLK"
        robocopy /mir /z "x:\HLK" "$osletter`:\HLK"
        # Replace PostOS (WTT Client install) with PostOS.HLK (HLK Client install)
        copy-item "$osletter`:\DC_PostOS\PostOS.HLK.cmd" -destination "$osletter`:\DC_PostOS\postos.cmd" -force
    }

    # Check Unattend actions to skip features
    while ($true){

        if ($PostActions -match "null"){
            Write-Host "Executing Unattend NULL actions and removing dirs."
            if (Test-Path "$osletter`:\DC_PostOS") {Remove-Item ("$osletter`:\DC_PostOS")}
            if (Test-Path "$osletter`:\WTT") {Remove-Item ("$osletter`:\WTT")}
            if (Test-Path "$osletter`:\HLK") {Remove-Item ("$osletter`:\HLK")}
            break
        }

        if ($PostActions -match "disablewu"){
            Write-Host "Disabling WU using Registry."
            X:\Updates\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot $osletter`:\windows\system32\config -registryFilePath "$osletter`:\DC_PostOS\RegFiles_OS\WU"
        }
                
        if ( ($PostActions -match "wttclientonly") -or ($PostActions -match "clientonly") ){
            Write-Host "Executing Client install, adding PostOS RunOnce Registry key."
            X:\Updates\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot $osletter`:\windows\system32\config -registryFilePath "$osletter`:\DC_PostOS\RegFiles_OS\PostOS"
            break
        }

        if ($PostActions -match "none"){
            Write-Host "Executing Unattend NONE actions and exiting."
            if (Test-Path "$osletter`:\DC_PostOS\WTT_Core\WTTClientInstall.lnk"){
                Copy-Item "$osletter`:\DC_PostOS\WTT_Core\WTTClientInstall.lnk" "$osletter`:\Users\default\Desktop\WTTClientInstall.lnk"
            }
            if (Test-Path "X:\pcname.txt"){
                Copy-Item "x:\pcname.txt" "$osletter`:\DC_PostOS\pcname.txt"
            }
            break
        }

                
        if ( ($PostActions -match "nowttclient") -or ($PostActions -match "noclient") ){
            Write-Host "Executing NO WTT CLIENT actions and removing PostOS.reg"
            if (Test-Path "$osletter`:\DC_PostOS\RegFiles_OS\postos.reg"){
                Remove-Item ("$osletter`:\DC_PostOS\RegFiles_OS\postos.reg")
            }
            if (Test-Path "$osletter`:\DC_PostOS\WTT_Core\WTTClientInstall.lnk"){
                Copy-Item "$osletter`:\DC_PostOS\WTT_Core\WTTClientInstall.lnk" "$osletter`:\Users\default\Desktop\WTTClientInstall.lnk"
            }
        }

        if ( ($PostActions -match "norollback") -or ($PostActions -match "nrb") ){
            Write-Host "Executing NO ROLLBACK, removing ROLLBACK registry policy."
            $filepath = "$osletter`:\DC_PostOS\RegFiles_OS"
            if (Test-Path $filepath){
                    foreach ($f in gci $filepath | Where-Object {$_.name -like "rollback*.reg"}) {Remove-Item "$filepath\$($f.name)"}
            }
            if (test-path ("X:\ImagePostInstallPatch\CMD_RollbackFirmware.txt")){
                remove-item ("X:\ImagePostInstallPatch\CMD_RollbackFirmware.txt") -Force -ErrorAction Ignore
            }
        }


        if ( ($PostActions -notmatch "noreg") -and ($PostActions -notmatch "noregistry") ){
            Write-Host "Executing Registry actions."
            # Add ALL custom registry keys - Expecting WTT Install & Rename computer runonce script.
            if (Test-Path "$osletter`:\DC_PostOS\Update-OfflineRegistry.ps1"){
                "Adding registry keys to image"
                X:\Updates\DC_PostOS\Update-OfflineRegistry.ps1 -registryRoot $osletter`:\windows\system32\config -registryFilePath "$osletter`:\DC_PostOS\RegFiles_OS"
            }
        }

        # Remove Dev startup script (from unattend.xml) - This is causing WTT Unexpected reboots because of the HCK Install check.
        if (Test-Path "$osletter`:\Devoobe.cmd"){
            Write-Host "renaming DevOOBE.cmd to DevOOBE2.cmd to remove unexpected reboot when under WTT."
            Rename-Item -Path "$osletter`:\Devoobe.cmd" -NewName devoobe.org.cmd -force
        }

        # Remove Selfhost Startup Scripts and settings.
        if (Test-Path "$osletter`:\Selfhost_tools"){
            Write-Host "Removing Selfhost Tools"
            remove-item -path "$osletter`:\Selfhost_tools" -Force -Recurse
        }


        if ( ($PostActions -notmatch "noprivatefiles") -and ($PostActions -notmatch "nowinupdates") ){
            Write-Host "Executing Private File actions"
            # Update any private files
            Write-Host " - Checking for Windows file replacements"
            if (Test-Path "$osletter`:\DC_PostOS\WinUpdates"){
                Write-Host "Coping $osletter`:\DC_PostOS\WinUpdates\ to $osletter`:\"
                & robocopy "$osletter`:\DC_PostOS\WinUpdates" "$osletter`:\" /s /NFL /NDL
            }
        }

        # Check if we are requested to remove all OEM Drivers, before we add Private Drivers
        if ($PostActions -match "plainimage") {
            $OEM = Get-ChildItem "$osletter`:\Windows\Inf\OEM*.inf"
            Write-Host "Found: $($oem.count)" 
            ForEach ($inf in $OEM) {
                Write-Host "OEM Driver to remove: $inf"| write-Log
                dism /image:W:\ /remove-driver /driver:$inf
            }

            # Cleanup any Firmware
            Remove-Item "$osletter`:\windows\firmware" -force -ErrorAction Ignore
        }

        # Side load install
        if ( ($PostActions -notmatch "noprivatedrivers") -and ($PostActions -notmatch "nodrivers") ) {
            Write-Host "Adding any private drivers."
            # install any Private Drivers
            if (Test-Path "X:\Updates\Drivers_OS"){
                Write-Host "Installing Drivers_OS"
                dism /image:$osletter`:\ /add-driver /driver:X:\Updates\Drivers_OS /recurse /forceunsigned
            }
        }

        if ( ($PostActions -match "nounattend") -or ($PostActions -match "skipunattend") ) {
            Write-Host "Executing NO UNATTEND - Skipping unattend modifications"
            break
        }
        
        #   unattend.xml
        $unattendFile = "$osletter`:\Windows\Panther\unattend.xml"
        if (test-path $unattendFile) {
            copy-Item $unattendFile "$unattendFile.org"
        } else {
            Write-Host "Unattend not found, coping default"
            new-item "$osletter`:\Windows\Panther" -ItemType "directory" -ErrorAction Ignore
            copy-item "$osletter`:\Updates\unattend.xml" -destination "$osletter`:\Windows\Panther" -Container:$True
        }

        # check for ARM images that may do sysprep on the local machine, use the unattend that gets processed after
        # NOT SUPPORTED IN GLISSADE - Scott disabled unattend.xml actions.
            #if (Get-Content $unattendFile | select-string -pattern sysprepToOOBE.ps1) {
            #    $unattendFile = $(Get-ChildItem "$osletter`:\GoldenPath\*.oobe.unattend.xml").FullName
            #    Remove-Item ("W:\DC_PostOS\RegFiles_OS\postos.reg")
            #}
                
        if (test-path $unattendFile) {
            copy-Item $unattendFile "$unattendFile.org"
        } else {
            copy-item "$osletter`:\updates\unattend.xml" $unattendFile
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

            #setup PostOS - Scott disabled Unattend.xml features in DEV images.
                <#
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
                #>

            $unattend.Save($unattendFile)

        } else {
            Write-Host "Unattend.xml not found!"
            "Not Found" | out-file -FilePath "$osletter`:\Logs\Install\Unattend.xml"
        }


        break
    } # while $true

    # Copy logs to Windows drive
    if (test-path $Global:LogDir){
        robocopy $Global:LogDir "$osletter`:\Logs\Install" /s
        robocopy "$osletter`:\Windows\Panther" "$osletter`:\Logs\Install" unattend.xml
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
        Write-Host "Found PostInstall Patch, running runme.ps1"
        Z:\ImagePostInstallPatch\runme.ps1
    }

}

$Global:ErrorActionPreference = 'Stop'

Write-Host "------------------------------"
Write-Host "Configure Console"
Write-Host "------------------------------"
& mode con:lines=9000

$root = $PSScriptRoot
Write-Host "root: $root"

try {
    stop-transcript
} catch {}

    $logFolder = GetLogFolder

    Start-Transcript -Path "$logFolder\transcript.log"
    try {
        if (test-path "X:\buildlink.txt") {
            Install-Net -LogFolder $logFolder
write-host "NET Install - EMAIL DCARV"
pause
        } elseif (get-volume -FriendlyName 'SHIFU_SCOTT' -erroraction ignore) {
            Install-Local -LogFolder $logFolder
        } else {
write-host "USB Install - EMAIL DCARV"
pause
            Install-USBKey -LogFolder "$logFolder\install.txt"
        }

        PostInstallProcessing
    }
    finally {

        Stop-Transcript

        $OSPartition = Get-Partition -DiskNumber 0 | Where-Object { $_.GptType -eq "{ebd0a0a2-b9e5-4433-87c0-68b6b72699c7}" } | Select-Object -first 1
        $OSDrive = $OSPartition.DriveLetter + ":"

        if (test-path "X:\logs"){
            copy-item "x:\logs" "$OSDrive\DC_PostOS" -recurse
        }

    }

Write-Host "- Restart"
wpeutil reboot
exit 0
