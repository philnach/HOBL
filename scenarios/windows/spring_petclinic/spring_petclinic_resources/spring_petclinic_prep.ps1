param(
    [string]$logFile = ""
)

$scriptDrive = Split-Path -Qualifier $PSScriptRoot
if (-not (Test-Path "$scriptDrive\hobl_data")) {
    Write-Host " ERROR - Required directory not found: $scriptDrive\hobl_data" -ForegroundColor Red
    Exit 1
}
if (-not (Test-Path "$scriptDrive\hobl_bin")) {
    Write-Host " ERROR - Required directory not found: $scriptDrive\hobl_bin" -ForegroundColor Red
    Exit 1
}
if (-not $logFile) { $logFile = "$scriptDrive\hobl_data\spring_petclinic_prep.log" }

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match " ERROR - ") {
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
        " ERROR - Last command failed." | log
        Exit $code
    }
}

function checkCmd {
    param($code)
    if ($code -ne "True") {
        " ERROR - Last command failed." | log
        Exit 1
    }
}

Set-Content -Path $logFile -encoding utf8 "-- spring_petclinic prep started"

"-- Installing OpenJDK 25" | log
winget install --id Microsoft.OpenJDK.25 --version 25.0.0.36 --accept-source-agreements --accept-package-agreements

"-- Installing git" | log
winget install --id git.git --accept-source-agreements --accept-package-agreements
$Env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

"-- Setting up Java 25 environment" | log
# Find the Microsoft JDK installation dynamically
$microsoftJdkBase = "${env:ProgramFiles}\Microsoft"
$javaHome = $null

if (Test-Path $microsoftJdkBase) {
    # Look for any jdk-25.* directory
    $jdkDirs = Get-ChildItem -Path $microsoftJdkBase -Directory -Filter "jdk-25.*" | Sort-Object Name -Descending
    if ($jdkDirs.Count -gt 0) {
        $javaHome = $jdkDirs[0].FullName
        "Found Java 25 installation at: $javaHome" | log
    }
}

if ($javaHome -and (Test-Path $javaHome)) {
    $Env:JAVA_HOME = $javaHome
    "Set JAVA_HOME to: $javaHome" | log
} else {
    " ERROR - Could not find Java 25 installation in $microsoftJdkBase" | log
    Exit 1
}

# Refresh PATH to include new Java
$Env:Path = "$Env:JAVA_HOME\bin;" + $Env:Path
"Updated PATH to prioritize Java 25" | log

# Verify Java version
"-- Verifying Java version" | log
java -version 2>&1 | log

"-- Configuring Windows Firewall for Java" | log
$javaExe = "$Env:JAVA_HOME\bin\java.exe"
if (Test-Path $javaExe) {
    try {
        # Remove existing Java firewall rules to avoid conflicts
        Get-NetFirewallRule -DisplayName "*OpenJDK Platform binary*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
        
        # Add firewall rules for Java on both private and public networks
        New-NetFirewallRule -DisplayName "OpenJDK Platform binary (Inbound TCP)" -Direction Inbound -Program $javaExe -Action Allow -Profile Private,Public -Protocol TCP
        New-NetFirewallRule -DisplayName "OpenJDK Platform binary (Inbound UDP)" -Direction Inbound -Program $javaExe -Action Allow -Profile Private,Public -Protocol UDP

        "Added Windows Firewall rules for Java (TCP and UDP inbound) on private and public networks" | log
    } catch {
        "Warning: Failed to configure firewall rules for Java: $($_.Exception.Message)" | log
    }
} else {
    "Warning: Java executable not found at $javaExe" | log
}

"-- Cloning git repo" | log
Set-Location "$scriptDrive\"
git clone https://github.com/spring-projects/spring-petclinic.git
"-- Checking out a specific version of spring pet clinic to ensure consistent version" | log
git checkout 6feeae0f13e0e258eedc99832416b42bb13779b1

"-- Setting up Maven local repository" | log
if (Test-Path "$scriptDrive\temp\m2-spring-petclinic") {
    Remove-Item -Path "$scriptDrive\temp\m2-spring-petclinic" -Recurse -Force
    "Removed existing Maven repository" | log
}
mkdir "$scriptDrive\temp\m2-spring-petclinic"
"Created fresh Maven repository directory" | log

"-- Verify repo" | log
Set-Location "$scriptDrive\spring-petclinic"
"-- Warming Maven cache online" | log
.\mvnw.cmd "-Dmaven.repo.local=$scriptDrive\temp\m2-spring-petclinic" "-DskipTests" dependency:go-offline
check($LASTEXITCODE)

"-- Verifying repo online" | log
.\mvnw.cmd "-Dmaven.repo.local=$scriptDrive\temp\m2-spring-petclinic" clean verify
check($LASTEXITCODE)

"-- spring_petclinic prep completed" | log
Exit 0