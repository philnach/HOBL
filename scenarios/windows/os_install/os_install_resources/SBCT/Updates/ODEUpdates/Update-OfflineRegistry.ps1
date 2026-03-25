<#
.Synopsis
    Updates an offline registry
.Desciption
    Loads hives for a registry and applies registry files to it
    Registry files are expected to be in 'online' format
        ex: [HKEY_LOCAL_MACHINE\Software\...]
    This script will modify temporary copies so that they can be applied offline
.Parameter registryRoot
    Location where registry hives to be modified lives
.Parameter registryFilePath
    Location of directory containing .reg files to apply
.Example Update-OfflineRegistry -registryRoot u:\windows\system32\config -registryFilePath d:\files\registry
    Will update the registry located at registryRoot with values found in .reg files that live in registryFilePath
#>


param(

    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_ -PathType 'Container'})]
    [string]$registryRoot,

    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_ -PathType 'Container'})]
    [string]$registryFilePath

)

# Define a directory to store temporary registry files
$tempDir = "$env:Temp\Update-OfflineRegistry"
if (Test-Path $tempDir) { Remove-Item $tempDir -Force -Recurse }
New-Item $tempDir -ItemType Directory

# Get the registry files to apply
$registryFiles = Get-ChildItem -Path $registryFilePath\*.reg

# Modify reg file, load hive, apply reg file, unload hive, unleash the Kraken
foreach ($registryFile in $registryFiles)
{

    # Identify the hive.  There is only one hive per file in all the regfiles we are processing in our SOC projects
    $hive = ((Get-Content $registryFile | Select-String 'HKEY_LOCAL_MACHINE' | Select-Object -First 1) -split ("\\"))[1]

	$modifiedRegistryFileName = "$tempDir\$($registryFile.Name)"

    # Modify the reg file
    $newContent = (Get-Content $registryFile) -replace "\[HKEY_LOCAL_MACHINE\\$hive","[HKEY_LOCAL_MACHINE\Temp$hive"
	$newContent | Out-File $modifiedRegistryFileName

    # Load hive
    Invoke-Expression -Command "reg load HKLM\Temp$hive $registryRoot\$hive"

    # Apply reg files
    Invoke-Expression -Command "reg import `"$modifiedRegistryFileName`""

    # Unload hive
    Invoke-Expression -Command "reg unload HKLM\Temp$hive"

}

# Clean up
Remove-Item $tempDir -Force -Recurse
return $true