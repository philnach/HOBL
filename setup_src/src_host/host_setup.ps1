param(
    [string]$logFile = "c:\temp\host_setup.log",
    [switch]$framework,
    [switch]$ui
)

# HOBL UI and Dut Setup versions
$hobl_ui_version = "0.92"
$dut_setup_version = "2.0"

function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match "ERROR:") {
            Write-Host $msg -ForegroundColor Red
        } else {
            Write-Host $msg
        }
        Add-Content -Path $logFile -encoding utf8 "$msg"
    }
}

function check {
    param($code)
    if ($code -ne 0) {
        "ERROR: Last command failed." | log
        Exit $code
    }
}

function checkCmd {
    param($code)
    if ($code -ne "True") {
        "ERROR: Last command failed." | log
        Exit 1
    }
}

New-Item -ItemType Directory -Force -Path c:\temp > $null
New-Item -ItemType Directory -Force -Path c:\hobl_results > $null

Set-Content -Path $logFile -encoding utf8 "-- HOBL Install started"
"Install framework: $framework" | log
"Install ui: $ui" | log

if ($framework -eq $false -and $ui -eq $false) {
    "No components specifed. Aborting." | log
    "`nYou must specify at least one of: " | log
    "  -framework" | log
    "  -ui" | log
    exit 1
}

##
## HOBL
##

if ($framework) {

    $runtimeVersion = "8.0.23"
    $runtimeX64DownloadUrl = "https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/$runtimeVersion/windowsdesktop-runtime-$runtimeVersion-win-x86.exe"
    $vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x86.exe"

    # Download .NET Windows Desktop Runtime installers
    $runtimeFilePath = "$PSScriptRoot\..\..\downloads\setup\assets\windowsdesktop-runtime-$runtimeVersion-win-x86.exe"
    if (-not (Test-Path $runtimeFilePath)) {
        "-- Downloading .NET Windows Desktop Runtime $runtimeVersion" | log
        Invoke-WebRequest -Uri $runtimeX64DownloadUrl -OutFile $runtimeFilePath 2>&1 | log
        checkCmd($?)
        "-- Installing .NET Windows Desktop Runtime $runtimeVersion" | log
        & "$runtimeFilePath" /quiet 2>&1 | log
        # check($lastexitcode)
    } else {
        "   $runtimeFilePath already exists, skipping download" | log
    }

    # Download Visual C++ Redistributable
    $vcRedistPath = "$PSScriptRoot\..\..\downloads\setup\assets\vc_redist.x86.exe"
    if (-not (Test-Path $vcRedistPath)) {
        "-- Downloading Visual C++ Redistributable" | log
        Invoke-WebRequest -Uri $vcRedistUrl -OutFile $vcRedistPath 2>&1 | log
        checkCmd($?)
        "-- Installing Visual C++ Redistributable" | log
        & "$vcRedistPath" /install /quiet /norestart 2>&1 | log
        # check($lastexitcode)
    } else {
        "   $vcRedistPath already exists, skipping download" | log
    }

    # Download dut_setup
    "-- Downloading DUT setup" | log
    $dut_setupUrl = "https://github.com/microsoft/HOBL/releases/download/dut_setup/dut_setup_$dut_setup_version.exe"
    $dut_setupZip = "$PSScriptRoot\..\..\downloads\setup\dut_setup_$dut_setup_version.exe"
    Invoke-WebRequest -Uri $dut_setupUrl -OutFile $dut_setupZip 2>&1 | log
    checkCmd($?)
    $dut_setupUrl = "https://github.com/microsoft/HOBL/releases/download/dut_setup/dut_setup_$dut_setup_version.sh"
    $dut_setupZip = "$PSScriptRoot\..\..\downloads\setup\dut_setup_$dut_setup_version.sh"
    Invoke-WebRequest -Uri $dut_setupUrl -OutFile $dut_setupZip 2>&1 | log
    checkCmd($?)

    # Install embedded python
    "-- Installing embedded Python" | log
    & "$PSScriptRoot\python_embed_install.cmd" 2>&1 | log
    check($lastexitcode)

    # Download ffmpeg
    "-- Downloading ffmpeg win64" | log
    $ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-02-28-12-59/ffmpeg-N-123073-g743df5ded9-win64-gpl.zip"
    $ffmpegZip = "$PSScriptRoot\..\..\downloads\ffmpeg_win64.zip"
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip 2>&1 | log
    checkCmd($?)
    Expand-Archive -Path $ffmpegZip -DestinationPath "$PSScriptRoot\..\..\downloads" -Force 2>&1 | log
    checkCmd($?)
    Move-Item "$PSScriptRoot\..\..\downloads\ffmpeg-N-123073-g743df5ded9-win64-gpl" "$PSScriptRoot\..\..\downloads\ffmpeg_win64" -Force 2>&1 | log
    Remove-Item $ffmpegZip 2>&1 | log        
    # "-- Downloading ffmpeg arm64" | log
    # $ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-02-28-12-59/ffmpeg-N-123073-g743df5ded9-winarm64-gpl.zip"
    # $ffmpegZip = "$PSScriptRoot\..\..\downloads\ffmpeg_arm64.zip"
    # Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip 2>&1 | log
    # check($lastexitcode)
    # Expand-Archive -Path $ffmpegZip -DestinationPath "$PSScriptRoot\..\..\downloads" -Force 2>&1 | log
    # check($lastexitcode)
    # Move-Item "$PSScriptRoot\..\..\downloads\ffmpeg-N-123073-g743df5ded9-winarm64-gpl" "$PSScriptRoot\..\..\downloads\ffmpeg_arm64" -Force 2>&1 | log
    # Remove-Item $ffmpegZip 2>&1 | log

    # Set git hooks if git exists
    if (Get-Command git.exe -ErrorAction SilentlyContinue) {
        "-- Setting git hooks path" | log
        git.exe config core.hooksPath git_hooks 2>&1 | log
        check($lastexitcode)
    }

    # Disable error reporting UI
    "-- Disabling Windows Error Reporting UI" | log
    reg add "HKLM\Software\Microsoft\Windows\Windows Error Reporting" /f /v DontShowUI /t REG_DWORD /d 1 2>&1 | log
    check($lastexitcode)
}

##
## UI 
##

if ($ui) {

    # Backup existing appsettings.json and delete existing hoblweb folder
    if (test-path c:\hoblweb) {
        "-- Backing up HOBLweb appsettings.json" | log
        copy c:\HOBLweb\appsettings.json c:\temp\appsettings.json 2>&1 | log
        "-- Deleting existing HOBLweb" | log
        Stop-Process -Name hoblweb -Force -ErrorAction SilentlyContinue
        remove-item c:\hoblweb -recurse -force 2>&1 | log
    }

    # Download hobl ui zip file
    "-- Downloading HOBLweb" | log
    $uiUrl = "https://github.com/microsoft/HOBL/releases/download/dut_setup/dut_setup_$dut_setup_version.exe"
    $uiZip = "c:\hoblweb.zip"
    Invoke-WebRequest -Uri $uiUrl -OutFile $uiZip 2>&1 | log
    checkCmd($?)
    Expand-Archive -Path $uiZip -DestinationPath "c:\hoblweb" -Force 2>&1 | log
    checkCmd($?)
    Remove-Item $uiZip 2>&1 | log
    checkCmd($?)

    "-- Installing vc_redist" | log
    c:\hoblweb\vc_redist.x64.exe /install /quiet /norestart 2>&1 | log
    c:\hoblweb\vc_redist.x86.exe /install /quiet /norestart 2>&1 | log

    "-- Installing dotnet hosting" | log
    # This will throw error if IIS not installed, so don't check
    c:\hoblweb\dotnet-hosting-6.0.7-win.exe /install /quiet /norestart 2>&1 | log

    "-- Installing local DB" | log
    msiexec /i c:\hoblweb\SqlLocalDB.msi /qb IACCEPTSQLLOCALDBLICENSETERMS=YES 2>&1 | log
    check($lastexitcode)
    &"c:\Program Files\microsoft sql server\150\tools\binn\sqllocaldb.exe" create HOBL 2>&1 | log
    check($lastexitcode)
    &"c:\Program Files\microsoft sql server\150\tools\binn\sqllocaldb.exe" start HOBL 2>&1 | log
    check($lastexitcode)

    # Restore appsettings.json
    if (test-path c:\temp\appsettings.json) {
        "-- Restoring backed up appsettings.json" | log
        copy c:\temp\appsettings.json c:\HOBLweb\appsettings.json 2>&1 | log
    } else {
        "-- Copying default appsettings.json" | log
        copy c:\HOBLweb\appsettings.default.json c:\HOBLweb\appsettings.json 2>&1 | log
    }

    # Open firewall
    "-- Opening firewall for hoblweb.exe" | log
    netsh advfirewall firewall delete rule name="HOBLweb" 2>&1 > $null
    netsh advfirewall firewall add rule name="HOBLweb" program="C:\hoblweb\hoblweb.exe" dir=in action=allow enable=yes localport=any protocol=TCP profile=public,private,domain 2>&1 | log
    check($lastexitcode)

    # Add desktop shortcut
    "-- Copying launch shortcut to desktop" | log
    copy c:\HOBLweb\HOBLweb.lnk ~\Desktop\HOBLweb.lnk 2>&1 | log

    # Launch HOBL UI
    "-- Launching HOBLweb" | log
    start-process -FilePath "c:\hoblweb\hoblweb.cmd" -ArgumentList "install" -WorkingDirectory "c:\hoblweb" -WindowStyle hidden
    checkCmd($?)

    "-- Install complete" | log
    "-- Waiting ~15 seconds for app to launch" | log
    Start-Sleep -seconds 15
}

Exit 0