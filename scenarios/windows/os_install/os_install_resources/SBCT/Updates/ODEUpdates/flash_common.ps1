param(
    [Parameter(Mandatory = $true)]
    [string] $SourceOSPath,
    [Parameter(Mandatory = $false)]
    [int] $DestDiskNumber = 0,
    [Parameter(Mandatory = $false)]
    [uint] $BatteryLevel = 0,
    [Parameter(Mandatory = $false)]
    [string] $SbctBinPath,
    [Parameter(Mandatory = $false)]
    [string] $PwshmodPath,
    [Parameter(Mandatory = $false)]
    [string] $PostDeployRoot,
    [Parameter(Mandatory = $false)]
    [string] $PartitionLayout = "deployment",
    [hashtable] $RuntimeConfig,
    [Parameter()]
    [switch] $SkipRestart,
    [switch] $KeylessInstall,
    [switch] $USBKeyInstall,
    [string] $LogFolder = 'x:\logs'
)
$Global:ErrorActionPreference = 'Stop'

if (-not (Test-Path $SourceOSPath)) {
    Write-Error "Source OS Path not found"
}

Write-Host "------------------------------"
Write-Host "Init pwsh"
Write-Host "------------------------------"
# Load modules
# $PwshmodPath when set will point to the modules packaged with the OS image
# If not set, we will fall back to the modules at X:\pwshmod
if (-not (Test-Path $PwshmodPath)) {
    $PwshmodPath = "$PSScriptRoot\pwshmod"
    if (-not (Test-Path $PwshmodPath)) {
        Write-Error "Powershell modules not found at $PwshmodPath"
        return
    }
}
Get-ChildItem "$PwshmodPath\*\init.ps1" |
Sort-Object |
ForEach-Object {
    Write-Host "> Import: $_"
    . $_.FullName
}

Write-Host "------------------------------"
Write-Host "Create logs folder: $LogFolder"
Write-Host "------------------------------"
$Global:LogDir = mkdir -Path $LogFolder -Force
$Global:LogPath = New-LogPath "log.txt"

if ($BatteryLevel -gt 0) {
    Write-Host "------------------------------"
    Write-Host "Check Battery Charge Level"
    Write-Host "------------------------------"
    Request-BatteryLevel $BatteryLevel
}

Write-Host "------------------------------"
Write-Host "Check for Image Settings"
Write-Host "------------------------------"
# For MTE WinPE IPN, image_settings.json will be at the OS root
$OSImageSettings = "$SourceOSPath\image_settings.json"
if (-not (Test-Path $OSImageSettings)) {
    Write-Error "Image not found - missing image_settings.json at $OSImageSettings"
    return
}

Write-Host "------------------------------"
Write-Host "Adjusting Device Date and Time if needed"
Write-Host "------------------------------"
$now = Get-Date
$Date = (Get-Item $OSImageSettings).LastWriteTime
Write-Host "  - Device Date:   $now"
Write-Host "  - OS Image Date: $Date"

if ($now -lt $Date) {
    Write-Host -ForegroundColor Yellow " Clock looks like it is old ($now) --Setting date to $Date"
    Set-Date $Date
    Start-Sleep 5
}

if (($now - $Date).TotalDays -gt 365) {
    Write-Host -ForegroundColor Yellow "Significant Date Shift Warning"
    Write-Host "You are either using a really old image or there has been an anomaly in time."
    Write-Host "Is it really $now ?"
    Write-Host -ForegroundColor Yellow " --Setting date to $Date"
    Set-Date $Date
    Start-Sleep 5
}

Write-Host "------------------------------"
Write-Host "Check for SBCT"
Write-Host "------------------------------"
# $SbctBinPath when set will point to the tool packaged with the OS image
# If not set, we will fall back to the tool at X:\bin\sbct
if (-not (Test-Path $SbctBinPath)) {
    $SbctBinPath = "$PSScriptRoot\bin\sbct"
    if (-not (Test-Path $SbctBinPath)) {
        Write-Error "SBCT not found - missing SBCT tool at $SbctBinPath"
        return
    }
}

Write-Host "------------------------------"
Write-Host "Install Image"
Write-Host "------------------------------"
Import-ImageSettings $OSImageSettings
$installSplat = @{
    SourceType = 'sbct'
    SourcePath = $SourceOSPath
    DestinationType = 'disk'
    DestinationPath = $DestDiskNumber
    SbctBinPath = $SbctBinPath
    PartitionLayout = $PartitionLayout
    KeepWinPEPartition = $RuntimeConfig.requireWinPEPartition -as [bool]
    KeylessInstall = $KeylessInstall -as [bool]
    USBKeyInstall = $USBKeyInstall -as [bool]
}
Install-Image @installSplat

# handle common part for post deployment
if ($PostDeployRoot) {
    <#
        Install drivers from       "${PostDeployRoot}\drivers"
        Copy CI Policy files from  "${PostDeployRoot}\benchmarkcipolicy"
        Copy other files from      "${PostDeployRoot}\copyfiles"
        Run post deployment script "${PostDeployRoot}\ImageConfigurationPostDeploy.ps1"
    #>
    Invoke-PwshDriveRefresh -DiskNumber $DestDiskNumber
    $OSPartition = Get-Partition -DiskNumber $DestDiskNumber | Where-Object { $_.GptType -eq "{ebd0a0a2-b9e5-4433-87c0-68b6b72699c7}" } | Select-Object -first 1
    $OSLetter = $OSPartition.DriveLetter
    Write-Host "OSLetter = $OSLetter"

    $driversPath = Join-Path -Path $PostDeployRoot -ChildPath 'drivers'
    if (Test-Path -Path $driversPath -PathType Container) {
        Write-Host "------------------------------"
        Write-Host "Post Deploy Drivers"
        Write-Host "------------------------------"
        Write-Host "> Find Drivers"
        $drivers = Get-ChildItem $driversPath\*.inf -Recurse | ForEach-Object FullName
        $drivers | ForEach-Object {
            Write-Host "    - $_"
        }
        Install-Driver -Path "${OSLetter}:\" -Driver $drivers
    }

    $copyFilesPath = Join-Path -Path $PostDeployRoot -ChildPath 'copyfiles'
    if (Test-Path -Path $copyFilesPath -PathType Container) {
        Write-Host "------------------------------"
        Write-Host "Post Deploy Copy Files"
        Write-Host "------------------------------"
        Write-Host "> Copy ${copyFilesPath} to $OSLetter`:\"
        robocopy /e "${copyFilesPath}" "$OSLetter`:\"
    }

    $postDeployScript = Join-Path -Path $PostDeployRoot -ChildPath 'ImageConfigurationPostDeploy.ps1'
    if (Test-Path -Path $postDeployScript -PathType Leaf) {
        $ScriptOOBEDir = "$OSLetter`:\Users\Default\AppData\Local\Microsoft\Surface\OOBE"
        Write-Host "------------------------------"
        Write-Host "Post Deploy Actions"
        Write-Host "------------------------------"
        Write-Host "> Copy $ScriptOOBEDir\ImageConfiguration.ps1 $ScriptOOBEDir\ImageConfigurationOOBE.ps1"
        Copy-Item -Force $ScriptOOBEDir\ImageConfiguration.ps1 $ScriptOOBEDir\ImageConfigurationOOBE.ps1

        Write-Host "> Copy ${postDeployScript} to $ScriptOOBEDir\ImageConfiguration.ps1"
        Copy-Item -Force -Path ${postDeployScript} -Destination $ScriptOOBEDir\ImageConfiguration.ps1
    }

    $ciSource = Join-Path -Path $PostDeployRoot -ChildPath 'benchmarkcipolicy'
    if (Test-Path -Path $ciSource -PathType Container) {
        Write-Host "------------------------------"
        Write-Host "Post Deploy Benchmark CIPolicy"
        Write-Host "------------------------------"
        $ciDestination = "${OSLetter}:\Windows\System32\CodeIntegrity\CiPolicies\Active"
        Write-Host "> Copy benchmark CI policy .cip from ${ciSource} into Windows CodeIntegrity folder(${ciDestination})"
        Copy-Item -Path "${ciSource}\*" -Destination "${ciDestination}\" -PassThru -Recurse -Force
    }
}

if (Test-Path Function:\Invoke-WPEPostInstall) {
    Write-Host "------------------------------"
    Write-Host " Invoke-WPEPostInstall"
    Write-Host "------------------------------"
    $Global:DestDiskNumber = 0
    Invoke-WPEPostInstall
}

if (-not $SkipRestart) {
    Write-Host "------------------------------"
    Write-Host "REBOOT"
    Write-Host "------------------------------"
    Restart-Computer -Force
    #Sleep here to avoid a prompt being shown
    Start-Sleep -Seconds 9999
}
else {
    Write-Host "Skipped restart of computer"
}
