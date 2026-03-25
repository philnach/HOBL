#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------
function Install-Image {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("sbct", "wim", "swm", "seedingPartition")]
        [string] $SourceType,
        [Parameter(Mandatory = $true)]
        [string] $SourcePath,

        [Parameter(Mandatory = $true)]
        [ValidateSet("disk", "vhd")]
        [string] $DestinationType,
        [Parameter(Mandatory = $true)]
        [string] $DestinationPath,

        [Parameter(Mandatory = $false)]
        [string] $SbctBinPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet(512, 4096)]
        [uint32] $SectorSize = 4096,

        [Parameter(Mandatory = $false)]
        [string] $PartitionLayout = "deployment",

        [Parameter(Mandatory = $false)]
        [string] $LogPath = $Global:LogDir,

        [switch] $KeepWinPEPartition,
        [switch] $SkipWinRE,
        [switch] $KeylessInstall,
        [switch] $USBKeyInstall,
        [switch] $RemoveCIPolicy
    )

    begin {
    }

    process {

        write-host "DCARV: 70_msb.deployment"
        $KeylessInstall = $true
        $USBKeyInstall = $false
        $SkipWinRE = $true
        $removeWinPE = $false
	$WiFiInstall = $true

        [int]$DiskNumber = -1
        if ($DestinationType -eq "vhd") {
            Write-Host "Getting VHD: $DestinationPath, SectorSize: $SectorSize" -ForegroundColor Green
            $VHDSize = (Get-ImageSetting sbct.CaptureVMSize) ?? 32GB
            $vhdMount = Get-MountedVHD -VHDPath $DestinationPath -VHDSize $VHDSize -SectorSize $SectorSize
            $DiskNumber = [int] $vhdMount.Number
        }
        else {
            $DiskNumber = [int] $DestinationPath
            Write-Host "Getting DISK: $DiskNumber ($DestinationPath) SectorSize: $SectorSize" -ForegroundColor Green
        }

        if ($DiskNumber -lt 0) {
            Write-Error "Install Disk not found"
            return
        }
        Write-Host "> Install to Disk: $DiskNumber ($PartitionLayout)"

        $removeWinPE = $false
        if ($PartitionLayout -eq "deployment") {
            $removeWinPE = !$KeepWinPEPartition
            $PartitionLayout = "factory"
        }

        Write-Host "> Format Disk $DiskNumber with Layout $PartitionLayout ($removeWinPE)"
        $partitionCfg = Get-ImageSetting PartitionConfig.$PartitionLayout.Partition

        if ($PartitionLayout -eq "vm" -and $null -eq $partitionCfg) {
            $partitionCfg = Get-DefaultVMPartitionConfig
        }
        if ($PartitionLayout -eq 'seeding' -and $null -eq $partitionCfg) {
            $partitionCfg = Get-DefaultSeededPartitionConfig
        }

        [bool] $hasWinRE = $null -ne ($partitionCfg | Where-Object Name -eq 'WinRE')
        $configureWinRE = ((-not $SkipWinRE -and $hasWinRE) -and (-not $KeylessInstall))

        if ($USBKeyInstall -or (($SourceType -eq 'seedingPartition') -or (-not (Test-SeedPartitionCreated)) -and (-not $KeylessInstall))) {
            write-host "DCARV: USBKeyInstall"
            $diskPartParams = @{
                DiskNumber = $DiskNumber
                PartitionConfig = $partitionCfg
                DestinationType = $DestinationType
            }

            $DynamicWinRESize = Get-ImageSetting -Name PartitionConfig.DynamicWinRESize
            if ($configureWinRE -and $DynamicWinRESize) {
                $diskPartParams['DynamicWinRESize'] = $DynamicWinRESize
            }

            Invoke-ImagingDiskPartition @diskPartParams
        }

        if($KeylessInstall){
            $OSPartition = Get-Partition -DiskNumber $DiskNumber | Where-Object { $_.GptType -eq "{$GPT_GUID_BASIC_DATA}" } | Select-Object -first 1
            Write-Host "> Format Disk $DiskNumber Partition $OSPartition As OS Partition"
            $OSPartition | Format-Volume -FileSystem NTFS

            $RecoveryPartition = Get-Partition -DiskNumber $DiskNumber | Where-Object {$_.FileSystemLabel -inotmatch 'WinPE'} | Where-Object { ($_.GptType -eq "{$GPT_GUID_RECOVERY_TOOLS}")  -and ($_.size -le 10gb)}
            if ($RecoveryPartition) {
                if ($SourceType -eq 'sbct') {
                    Write-Host "> Format Disk $DiskNumber Partition $RecoveryPartition As Recovery Partition"
                    $RecoveryPartition | Format-Volume -FileSystem NTFS
                }
                else {
                    Write-Host "Skipping WinRE Reformatting. WinRE is not supported for $SourceType installs."
                }
            }
            else {
                Write-Host  'No recovery partition to format'
            }
        }
        Invoke-PwshDriveRefresh -DiskNumber $DiskNumber

        $Compact = (Get-ImageSetting PartitionConfig.bmr.ResetConfig.compact) -eq 'True'

        if ($SourceType -eq "wim") {
            $OSLetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_BASIC_DATA}"
            Write-Host "> Install WIM $SourcePath to $OSLetter`:\ on disk $DiskNumber"
            if ($Compact ) {
                Add-WofToVolume -Volume "$OSLetter`:"
            }
            Expand-WindowsImage -ImagePath $SourcePath -ApplyPath "$OSLetter`:\" -Index 1 -CheckIntegrity -Verify -Compact:$Compact

            $DefragPath = "$($ENV:SYSTEMDRIVE)\Windows\System32\defrag.exe"
            if (Test-Path -Path $DefragPath) {
                "> Defragmenting the drive" | Write-Log
                "    - $DefragPath $OSLetter`: /X /O /V" | Write-Log
                & $DefragPath "$OSLetter`:" /X /O /V | Write-Log
            }
            else {
                Write-Host "Image does not support defragging. $DefragPath does not exist."
            }
        }

        if ($SourceType -eq "swm") {
            $OSLetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_BASIC_DATA}"
            Write-Host "> Install SWM $SourcePath to $OSLetter`:\ on disk $DiskNumber"
            $splitImageFilePattern = Join-Path -Path $([System.IO.Path]::GetDirectoryName($SourcePath)) -ChildPath  $([System.IO.Path]::GetFileNameWithoutExtension($SourcePath) + '*.swm')
            if ($Compact ) {
                Add-WofToVolume -Volume "$OSLetter`:"
            }
            Expand-WindowsImage -ImagePath $SourcePath -SplitImageFilePattern $splitImageFilePattern -ApplyPath "$OSLetter`:\" -Index 1 -CheckIntegrity -Verify -Compact:$Compact
        }

        if ($SourceType -eq "sbct") {
            Write-Host "> Install SBCT $SourcePath"
            $sbctfiles = @(Get-ChildItem $SourcePath\*.sbct.vol.p* | ForEach-Object { if ($_ -match ".*(\.sbct.vol.p\d\d).*") { $matches[1] } } | Sort-Object -uniq)
            $sbctparts = $sbctfiles | ForEach-Object { if ($_ -match ".*\.p(\d\d).*") { [int]$matches[1] } } | Sort-Object -uniq

            foreach ($sbctpartnum in $sbctparts) {
                $sbctHeader = Get-ChildItem -Path $SourcePath -Filter ("*.p{0:d2}.header" -f $sbctpartnum)
                $sbctpartnum = [int]$sbctpartnum + 1
                #If keyless, then ensure that the partition it's going to write to is not the keyless partition
                if($KeylessInstall)
                {
                    # check for SSD and ensure we don't conflict.
                    $SSDVolume = Get-Volume | Where-Object { $_.FileSystemLabel -eq 'Ruacana' }
                    if($SSDVolume)
                    {
                        $SSDPartition = Get-Partition | Where-Object { $_.AccessPaths -contains $volume.Path }
                        if($SSDPartition.PartitionNumber -eq $sbctpartnum)
                        {
                            Write-Host "ShinkansenSSD Install detected, incrementing partition for Recovery partition to not conflict"
                            $sbctpartnum = [int]$sbctpartnum + 1
                        }
                    }

                    # Check the keyless partition and ensure we don't conflict
                    $volume = Get-Volume | Where-Object { $_.FileSystemLabel -eq 'Winpe' }
                    $keylessPartition = Get-Partition | Where-Object { $_.AccessPaths -contains $volume.Path }
                    if($keylessPartition.PartitionNumber -eq $sbctpartnum)
                    {
                        #This is the recovery partition, and is conflicting with the keyless partition which is in the way.
                        Write-Host "Shinkansen Keyless partition detected, incrementing partition number for Recovery partition to not conflict"
                        $sbctpartnum = [int]$sbctpartnum + 1
                    }
                    Write-Host "Partition to be written is now: $sbctpartnum"
                }
                $sbctLogPath = Join-Path -Path $LogPath -ChildPath "sbctLog_${sbctpartnum}"
                mkdir -Path $sbctLogPath -Force | Out-Null
                & $SbctBinPath\SurfaceBlockCaptureTool.exe restore $DiskNumber $sbctHeader /dnv /arsd /l:$sbctLogPath /lh:$sbctLogPath /spr:$sbctpartnum /tpr:$sbctpartnum
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "SBCT Failed: $LASTEXITCODE"
                }
                Invoke-PwshDriveRefresh -DiskNumber $DiskNumber
            }
        }

        if ($SourceType -eq "seedingPartition") {
            # All we want to do is partition the disk, so currently this
            # selection doesn't copy anything like the others do and instead
            # returns directly to skip further processing.
            Write-Host "> Disk partitioned for seeding."

            # Set drive letters for WinPE and OS partitions (WinPE:P; OS:W) based on the canned config
            $winPEDriveLetter = Get-DefaultSeededPartitionConfig | Where-Object -Property 'name' -EQ 'WinPE' | Select-Object -ExpandProperty letter
            Get-Partition -DiskNumber $DiskNumber -PartitionNumber 4 | Set-Partition -NewDriveLetter $winPEDriveLetter

            $osDriveLetter = Get-DefaultSeededPartitionConfig | Where-Object -Property 'name' -EQ 'OS' | Select-Object -ExpandProperty letter
            Get-Partition -DiskNumber $DiskNumber -PartitionNumber 3 | Set-Partition -NewDriveLetter $osDriveLetter
            return
        }

        $OSLetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_BASIC_DATA}"
        $EFILetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_EFI}"

        $currentBuild = Get-OSBuildFromRegistry -ImagePath "${OSLetter}:\"
        if ($currentBuild -ge 26100) {
            Write-Host "Using /bootex Build is >= 26100 ($currentBuild)"
            & bcdboot "$OSLetter`:\Windows" /s "$EFILetter`:" /f UEFI /bootex
        }
        else {
            Write-Host "Skipping /bootex. Build is < 26100 ($currentBuild)"
            & bcdboot "$OSLetter`:\Windows" /s "$EFILetter`:" /f UEFI
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Error "bcdboot Failed: $LASTEXITCODE"
        }

        if ($RemoveCIPolicy) {
            Write-Host "> Remove CI Policy"
            if (Test-Path -Path "${EFILetter}:\efi\microsoft\boot\CIPolicies\active\*.cip" -PathType Leaf) {
                foreach ($policyFile in Get-ChildItem -Path "${EFILetter}:\efi\microsoft\boot\CIPolicies\active\*.cip") {
                    Write-Host " - Removing $($policyFile.Name)"
                    $policyFile | Remove-Item -Force
                }
            }
        }

        if ( (Get-ImageSetting deployment.os.testsigning) -eq $true) {
            Write-Host "    - Enable OS testsigning"
            $EFILetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_EFI}"
            Write-Host "    - bcdedit /store $EFILetter`:\EFI\Microsoft\Boot\BCD /set `{default`} testsigning on"
            bcdedit /store $EFILetter`:\EFI\Microsoft\Boot\BCD /set `{default`} testsigning on
            if ($LASTEXITCODE -ne 0) {
                Write-Error "   - Failed to set BCD"
            }
        }

        if ($configureWinRE) {
            Write-Host "> Configure WinRE"
            $WinRESource = "$OSLetter`:\Windows\System32\Recovery\Winre.wim"
            $WinRESourceAlt = "$(Split-Path -Parent $SourcePath)\Winre.wim"
            if (Test-Path $WinRESourceAlt) {
                $WinRESource = $WinRESourceAlt
            }

            $RELetter = Set-PartitionToDriveLetter -DiskNumber $DiskNumber -PartitionGuid "{$GPT_GUID_RECOVERY_TOOLS}"

            $WinREDestination = "$RELetter`:\Recovery\WindowsRE\Winre.wim"
            if (-not (Test-Path $WinREDestination)) {
                Write-Host "    - Copy WinRE to Recovery $WinRESource -> $WinREDestination"
                mkdir -force -p $(Split-Path -Parent $WinREDestination) | Out-Null
                Copy-Item $WinRESource $WinREDestination
            }

            $windowsFolder = "$OSLetter`:\windows"
            $reagentc = "$windowsFolder\system32\reagentc.exe"
            $TargetArchitecture = Get-ImageSetting TargetArchitecture
            if ($env:PROCESSOR_ARCHITECTURE -eq $TargetArchitecture) {
                Write-Host "    - reagentc /setreimage"
                & $reagentc /setreimage /path "$WinREDestination" /target "$windowsFolder"
                if ($LASTEXITCODE -ne 0) {
                    throw New-Object System.ApplicationException("reagentc /setreimage returned error $LASTEXITCODE")
                }

                #WinPE Check
                if (Test-Path -Path "${Env:windir}\System32\winpeshl.exe") {
                    Write-Host "    - reagentc /enable"
                    $entry = Get-BcdDefaultEntry -Store "${EFILetter}:\EFI\Microsoft\Boot\BCD"
                    & $reagentc /enable /osguid "$($entry.identifier)"
                    if ($LASTEXITCODE -ne 0) {
                        throw New-Object System.ApplicationException("reagentc /enable returned error $LASTEXITCODE")
                    }
                }
            }
            else {
                Write-Host "    - SKIP: TargetArchitecture $TargetArchitecture and Deployment Architecture $($env:PROCESSOR_ARCHITECTURE) mismatch, probably a VM install"
            }
        }

        #if ($removeWinPE) {
        if ($false) {
            Write-Host "Removing WinPE Partition for non-Factory Deployment"
            $partNum = 1
            foreach ($part in $partitionCfg) {
                if ($part.Name -eq "WinPE") {
                    break
                }
                $partNum++
            }

            Get-Partition -DiskNumber $DiskNumber -PartitionNumber $partNum | Remove-Partition -Confirm:$false
            $partNum--
            $newSize = Get-PartitionSupportedSize -DiskNumber $DiskNumber -PartitionNumber $partNum
            Resize-Partition -DiskNumber $DiskNumber -PartitionNumber $partNum -Size $newSize.SizeMax
        }

        if ($WiFiInstall){
            # Copy Install Scripts to Windows Partiton
            Write-Host "- Copying PostOS Scripts"
            robocopy /mir "D:\DC_PostOS" "$osletter`:\DC_PostOS"

            # Add PostOS registry
            if (test-path -path "$OSLetter`:\DC_PostOS") {
                $OSDrive = "$OSLetter`:"
                Update-OfflineRegistry -registryRoot $OSDrive\windows\system32\config -registryFilePath $OSDrive\DC_PostOS\RegFiles_OS
            }
        }

    }

    end {
    }
}

function Update-OfflineRegistry{
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

}

function Test-SeedPartitionCreated {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingEmptyCatchBlock', '', Justification='Force default path')]
    [OutputType('System.Boolean')]
    [CmdletBinding()]
    param (
    )
    # return true if WinPE partition > 5GB
    try {
        $winPEVolume = Get-Volume | Where-Object -Property FileSystemLabel -eq 'WinPE'
        if ($winPEVolume.Size -gt 5GB) {
            return $true
        }
    }
    catch {
        # no-op - only want to go into the "return $true" path if we find the needed
    }
    return $false
}

function Get-DefaultVMPartitionConfig {
    Write-Warning   "    - Using Default VM Partition Layout"
    return @(
        [PSCustomObject]@{
            name       = "EFI"
            size       = "260"
            type       = "efi"
            filesystem = "fat32"
            label      = "System"
            format     = "quick"
        },
        [PSCustomObject]@{
            name = "MSR"
            size = "16"
            type = "msr"
        },
        [PSCustomObject]@{
            name           = "OS"
            type           = "primary"
            filesystem     = "ntfs"
            label          = "Local Disk"
            format         = "quick"
            partattributes = "0x0000000000000000"
        }
    )
}

function Get-DefaultSeededPartitionConfig {
    Write-Warning   "    - Using Default Seeding Partition Layout"
    return @(
        [PSCustomObject]@{
            name       = "EFI"
            size       = "260"
            type       = "efi"
            filesystem = "fat32"
            label      = "System"
            format     = "quick"
            letter     = "S"
        },
        [PSCustomObject]@{
            name = "MSR"
            size = "16"
            type = "msr"
        },
        [PSCustomObject]@{
            name           = "OS"
            type           = "primary"
            size           = "-27648" # -(REToolsPartition + WinPE Partition)
            bmrSize        = "-1152"
            filesystem     = "ntfs"
            label          = "Local Disk"
            format         = "quick"
            partattributes = "0x0000000000000000"
            letter         = "W"
        },
        [PSCustomObject]@{
            name           = "WinPE"
            type           = "primary"
            size           = "25600" # 25GB - this should work for now, may make a param in future
            filesystem     = "ntfs"
            label          = "WinPE"
            format         = "quick"
            partattributes = "0x0000000000000000"
            letter         = "P"
        },
        [PSCustomObject]@{
            name           = "WinRE"
            size           = "2048"
            type           = "primary"
            filesystem     = "ntfs"
            label          = "Windows RE tools"
            format         = "quick"
            id             = "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC"
            partattributes = "0x8000000000000001"
            letter         = "T"
        }
    )
}

function Invoke-BcdEditExe {
    Write-Host "${env:SYSTEMROOT}\System32\bcdedit.exe ${args}"
    & "${env:SYSTEMROOT}\System32\bcdedit.exe" @args

    if ($LASTEXITCODE) {
        throw "BCDEDIT failed with exit code ${LASTEXITCODE}"
    }
}

function Get-BcdDefaultEntry {
    [CmdletBinding()]
    param (
        [Alias('Path')]
        [string] $Store
    )

    $bcdArgs = @(
        "/enum", '{default}', "/v"
    )
    if (-not [string]::IsNullOrEmpty($Store)) {
        if (-not (Test-Path -Path $Store -PathType Leaf)) {
            throw [System.IO.FileNotFoundException]::new("BCD store not found: '${Store}'")
        }
        $bcdArgs += @(
            "/store", $Store
        )
    }

    $spew = @(Invoke-BcdEditExe @bcdArgs)
    #Write-Host $spew
    foreach ($line in $spew) {
        #Write-Host $line
        switch -regex ($line) {
            '^\s*Windows Boot' { continue }

            '^\s*----+' {
                $ht = @{}
                continue
            }

            '^\s*(?<key>\w+)\s+(?<v>.+)\s*$' {
                $key = $Matches.key
                if ($key) {
                    $ht.Add($key, $Matches.v);
                }
                continue
            }

            '^\s*$' {
                if ($ht -is [hashtable] -and ($ht.Keys.Count -gt 0)) {
                    [pscustomobject] $ht
                    $ht = @{}
                }
            }
        }
    }
    $ht
}

function Invoke-FltmcExe {
    Write-Host "${env:SYSTEMROOT}\System32\fltmc.exe ${args}"
    & "${env:SYSTEMROOT}\System32\fltmc.exe" @args

    if ($LASTEXITCODE) {
        throw "FLTMC failed with exit code ${LASTEXITCODE}"
    }
}

function Add-WofToVolume {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [ValidatePattern("^[a-zA-z]:$")]
        [string] $Volume
    )

    $fltArgs = @(
        'instances', '-f', 'Wof'
    )

    if($null -eq (Invoke-FltmcExe @fltArgs | Select-String -Pattern $Volume )){
        $fltArgs = @(
            'attach', 'Wof', $Volume
        )

        Invoke-FltmcExe @fltArgs
    }
    else {
        Write-Host "Wof already attached to volume $Volume"
    }
}



