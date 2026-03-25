# InstallPython.ps1
# PRO Python Installer (ASCII SAFE)

# ---------------- CONTEXT CHECK ----------------
$IsAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($IsAdmin) {
    Write-Host "Installer context: Administrator" -ForegroundColor Green
}
else {
    Write-Host "Installer context: Standard user (non-interactive mode)" -ForegroundColor Yellow
}

# ---------------- FUNCTIONS ----------------
function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Test-RealPython {

    $commands = @("python", "py")

    foreach ($cmd in $commands) {
        try {
            $output = & $cmd --version 2>&1
            if ($output -match "^Python\s+\d+") {
                return $cmd
            }
        }
        catch {}
    }

    return $null
}

function Install-PythonDirect {
    param(
        [Parameter(Mandatory=$true)][bool]$AdminContext
    )

    $pythonVersion = "3.12.1"
    $installerPath = "$env:TEMP\python-installer.exe"
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"

    Write-Host "Downloading Python installer from $pythonUrl ..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing -TimeoutSec 300
    }
    catch {
        Write-Host " ERROR - Failed to download Python installer: $_" -ForegroundColor Red
        return $false
    }

    if (-not (Test-Path $installerPath)) {
        Write-Host " ERROR - Python installer was not downloaded." -ForegroundColor Red
        return $false
    }

    Write-Host "Installing Python (silent) ..." -ForegroundColor Cyan
    try {
        $allUsersArg = if ($AdminContext) { "1" } else { "0" }
        $installArgs = "/quiet InstallAllUsers=$allUsersArg PrependPath=1 Include_pip=1"
        $proc = Start-Process -FilePath $installerPath -ArgumentList $installArgs -PassThru
        Wait-Process -Id $proc.Id -Timeout 900 -ErrorAction Stop
        $proc.Refresh()
        if ($proc.ExitCode -ne 0) {
            Write-Host " ERROR - Python installer exited with code $($proc.ExitCode)." -ForegroundColor Red
            return $false
        }
    }
    catch {
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
        Write-Host " ERROR - Python installer timed out or failed: $_" -ForegroundColor Red
        return $false
    }
    finally {
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    }

    Refresh-Path
    Start-Sleep -Seconds 2
    return $true
}

function Install-PythonWinget {
    param(
        [Parameter(Mandatory=$true)][bool]$AdminContext
    )

    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "winget not available on DUT." -ForegroundColor Yellow
        return $false
    }

    $wingetScope = if ($AdminContext) { "machine" } else { "user" }
    $wingetArgs = "install --id Python.Python.3.12 --silent --disable-interactivity --scope $wingetScope --accept-package-agreements --accept-source-agreements"

    Write-Host "Installing Python via winget ($wingetScope scope) ..." -ForegroundColor Cyan
    try {
        $proc = Start-Process -FilePath "winget.exe" -ArgumentList $wingetArgs -NoNewWindow -PassThru
        Wait-Process -Id $proc.Id -Timeout 900 -ErrorAction Stop
        $proc.Refresh()
        if ($proc.ExitCode -ne 0) {
            Write-Host "winget exited with code $($proc.ExitCode). Falling back to direct installer..." -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
        Write-Host "winget timed out or failed. Falling back to direct installer..." -ForegroundColor Yellow
        return $false
    }

    Refresh-Path
    Start-Sleep -Seconds 2
    return $true
}

Write-Host "`n==== PRO Python Setup ====" -ForegroundColor Cyan
$ProgressPreference = "SilentlyContinue"
$markerPath = "C:\hobl_bin\.python_ready"

# ---------------- CHECK PYTHON ----------------
$pythonCommand = Test-RealPython

if ($pythonCommand) {
    Write-Host "Python detected: $(& $pythonCommand --version)" -ForegroundColor Green

    # Fast path for reruns: if runtime and required modules are already present, skip install/update work.
    try {
        & $pythonCommand -c "import psutil, numpy" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python runtime already ready on DUT. Skipping install/update path." -ForegroundColor Green
            New-Item -Path $markerPath -ItemType File -Force | Out-Null
            exit 0
        }
    }
    catch {}
}
else {

    Write-Host "Python not found." -ForegroundColor Yellow

    if (-not (Install-PythonWinget -AdminContext $IsAdmin)) {
        if (-not (Install-PythonDirect -AdminContext $IsAdmin)) {
            exit 1
        }
    }

    $pythonCommand = Test-RealPython

    if ($pythonCommand) {
        Write-Host "Python installed successfully." -ForegroundColor Green
    }
    else {
        Write-Host " ERROR - Python installed but not detected. Restart PowerShell." -ForegroundColor Red
        exit 1
    }
}

# ---------------- UPDATE PIP ----------------
Write-Host "`nUpdating pip..." -ForegroundColor Cyan

try {
    & $pythonCommand -m ensurepip --upgrade 2>$null
}
catch {}

& $pythonCommand -m pip install --upgrade pip

# ---------------- INSTALL PACKAGES ----------------
$packages = @("psutil", "numpy")

Write-Host "`nInstalling packages..." -ForegroundColor Cyan

foreach ($pkg in $packages) {

    Write-Host "Installing $pkg..."

    try {
        & $pythonCommand -m pip install $pkg --upgrade
    }
    catch {
        Write-Host " ERROR - Failed installing $pkg : $_" -ForegroundColor Red
    }
}

# ---------------- VERIFICATION ----------------
Write-Host "`nVerification..." -ForegroundColor Cyan

try {
    & $pythonCommand -c "import sys; print('Python OK')"
    & $pythonCommand -c "import psutil; print('psutil OK')"
    & $pythonCommand -c "import numpy; print('numpy OK')"

    New-Item -Path $markerPath -ItemType File -Force | Out-Null

    Write-Host "`nENVIRONMENT READY" -ForegroundColor Green
}
catch {
    Write-Host " ERROR - Verification failed: $_" -ForegroundColor Red
    exit 1
}