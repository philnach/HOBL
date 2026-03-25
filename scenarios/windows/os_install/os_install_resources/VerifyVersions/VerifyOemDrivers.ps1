
## DCARV's version script
## Used to verify driver and firmware versions on the system match INF in supplied $Drivers path (image\support folder).
## Requires SUPPORT Folder - Use PLE's QuickImges, or Choose 'Y' to include Support folder using CreateUSB.ps1

## Version 1.2

Param(
    [string] $drivers = "C:\Support" ,
    [string] $Exclude_HWID = "PID_07C6;example",

    [string] $Exclude_File = "C:\Tools\PLE\TOAST\Misc\Setup\TrainInformation.xml",
    #[string] $Exclude_File = ".\ExcludeList.xml",

    [string] $testDeviceStatus = "true",
    [string] $testDeviceVersions = "true",
    [string] $testDriverSigning = "false",
    [string] $testFirmwareInf = "true",
    [string] $testFirmwareRollback = "true",
    [string] $testExtensionDrivers = "true",

    [string] $driversFullPath ,         # Used for translatinig paths to Sever using network automation
    [string] $xmlIteration = "1",       # Results file number or version
    [string] $xmlEnabled = "true"       # Create XML Results file
)

$scriptPath = Split-Path -parent $MyInvocation.MyCommand.Definition
$global:LocalExitCode = 0
$global:ResultsXmlWriter = $null
$script:ExcludeList = New-Object System.Collections.Generic.List[System.Object]

if (test-path "C:\Tools\PLE\TOAST\Messenger\ToastClientMessenger.exe") {
        c:\Tools\PLE\TOAST\Messenger\ToastClientMessenger.exe -s 0 -d "Running the Verfiy Versions Tool"
}


function TestDeviceStatus {
    $testName = "Checking that all devices are in good status."
    if (IsWttLogger) {Start-WTTTest $testName}

    # Get list of interesting devices
    "Getting devices that have Status codes greater the 0...." | OutputStatusMessage
    $BangedDevices = Get-WmiObject Win32_PNPEntity | Where-Object {$_.ConfigManagerErrorCode -gt 0 }

    # Get ESRT Info
    $esrt = Get-EsrtValues -useHashTable
    
    $NumberofBadDeviceStates = 0
    $NumberofLowestSupportedVersion = 0
    foreach ($Device in $BangedDevices)
    {

        $BangDeviceName = $Device.name
        $BangDeviceCode = $Device.ConfigManagerErrorCode
        $BangDeviceID = $Device.deviceID
        $BangHardwareID = $Device.HardwareID

        # Skip excluded devices
        if (CheckForExlcude -deviceHWID $BangHardwareID) {continue}

        # Check firmware version is lower then ESRT Lowest_Supported_Version.  Unable to rollback.
        if ( ($BangDeviceCode -eq 10) -and ($BangDeviceID -like ("*{*}*") ))
        {

            "Firmware: '$BangDeviceName' has status code: $BangDeviceCode" | OutputStatusMessage
            "Checking Lowest Supported Version...." | OutputStatusMessage
            $fwGUID = "{" + $BangDeviceID.Split("{}")[1] + "}"
            
            $fwAttemptVer = $esrt.$fwGUID.LastAttemptedVersion_verstr
            $fwLowestSupportedVer = $esrt.$fwGUID.LowestSupportedVersion_verstr
            $fwInstallVersion = $esrt.$fwGUID.InstalledVersion_VerStr
            $fwName = Get-FirmwareName -fwGUID $fwGUID

            # Intel has different versioning
            if ($Device.name -like "ME")
            {
                $fwAttemptVer = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name LastAttemptVersion
                $fwLowestSupportedVer = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name LowestSupportedVersion
                $fwInstallVersion = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name Version
            }

            $logExpectedDriverInfo = "Frimware Info:" +
            "`n  Firmware name:`t`t$fwName" +
            "`n  Installed Version:`t`t$fwInstallVersion" +
            "`n  Last Attempted Version:`t$fwAttemptVer" +
            "`n  Lowest Supported Version:`t$fwLowestSupportedVer"
            $logExpectedDriverInfo | OutputStatusMessage

            if ($esrt.$fwGUID.LastAttemptedVersion_Binary -LT $esrt.$fwGUID.LowestSupportedVersion_Binary)
            {
                $NumberofLowestSupportedVersion =+ 1
                "ESRT shows attempted installed Firmware driver is lower than supported rollback version, skipping failure!" | OutputWarningMessage
                # Skip this device
                continue
            }
            

        }

        # Log banged devices to XML
        $DriverType = "Driver"
        if ( ($BangDeviceID -like ("*{*}*") )){
            $DriverType = "Firmware"
        }
        if ($BangDeviceName -eq $null){
            $global:ResultsXmlWriter.WriteStartElement('Result')
            $global:ResultsXmlWriter.WriteElementString('InfFilePath', "Unknown Device - This device is missing a driver!")
            $global:ResultsXmlWriter.WriteElementString('DeviceName', $BangDeviceID)
            $global:ResultsXmlWriter.WriteElementString('StatusCode', $BangDeviceCode)
            $global:ResultsXmlWriter.WriteElementString('DriverType', $DriverType)
            $global:ResultsXmlWriter.WriteEndElement()
        } else {
            $global:ResultsXmlWriter.WriteStartElement('Result')
            $global:ResultsXmlWriter.WriteElementString('InfFilePath', "NA")
            $global:ResultsXmlWriter.WriteElementString('DeviceName', $BangDeviceName)
            $global:ResultsXmlWriter.WriteElementString('StatusCode', $BangDeviceCode)
            $global:ResultsXmlWriter.WriteElementString('DriverType', $DriverType)
            $global:ResultsXmlWriter.WriteEndElement()
        }

        $NumberofBadDeviceStates += 1
        if (IsWttLogger)
        {
            "Device: '$($Device.name)' has status code: $($device.ConfigManagerErrorCode)" | OutputStatusMessage
            Stop-WTTTest -result "fail" -name $testName
            $Global:LocalExitCode = 1
        }
    }

    if ($NumberofBadDeviceStates -eq 0)
    {
        # Need at least one Pass/Fail result.
        "All devices are in good state!" | OutputStatusMessage
        if (IsWttLogger) {Stop-WTTTest -result "pass" -name $testName}

    }else{
        "$NumberofBadDeviceStates device(s) are in a bad state!" | OutputStatusMessage
        if (IsWttLogger) {Stop-WTTTest -result "fail" -name $testName}

$DeviceCodes = @"

0 = "This device is working properly.",
1 = "This device is not configured correctly.",
2 = "Windows cannot load the driver for this device.",
3 = "The driver for this device might be corrupted, or your system may be running low on memory or other resources.",
4 = "This device is not working properly. One of its drivers or your registry might be corrupted.",
5 = "The driver for this device needs a resource that Windows cannot manage.",
6 = "The boot configuration for this device conflicts with other devices.",
7 = "Cannot filter.",
8 = "The driver loader for the device is missing.",
9 = "This device is not working properly because the controlling firmware is reporting the resources for the device incorrectly.",
10 = "This device cannot start.",
11 = "This device failed.",
12 = "This device cannot find enough free resources that it can use.",
13 = "Windows cannot verify this device's resources.",
14 = "This device cannot work properly until you restart your computer.",
15 = "This device is not working properly because there is probably a re-enumeration problem.",
16 = "Windows cannot identify all the resources this device uses.",
17 = "This device is asking for an unknown resource type.",
18 = "Reinstall the drivers for this device.",
19 = "Failure using the VxD loader.",
20 = "Your registry might be corrupted.",
21 = "System failure: Try changing the driver for this device. If that does not work, see your hardware documentation. Windows is removing this device.",
22 = "This device is disabled.",
23 = "System failure: Try changing the driver for this device. If that doesn't work, see your hardware documentation.",
24 = "This device is not present, is not working properly, or does not have all its drivers installed.",
25 = "Windows is still setting up this device.",
26 = "Windows is still setting up this device.",
27 = "This device does not have valid log configuration.",
28 = "The drivers for this device are not installed.",
29 = "This device is disabled because the firmware of the device did not give it the required resources.",
30 = "This device is using an Interrupt Request (IRQ) resource that another device is using.",
31 = "This device is not working properly because Windows cannot load the drivers required for this device.
"@    
    $DeviceCodes | OutputStatusMessage

    }
}

function GetDriverVersions {

    # Gather exclude list
    $exclude_HWID_List = $Exclude_HWID -split ';'
    foreach ($path in $exclude_HWID_List) 
    {
        "Excluded Hardware ID's: $path" | OutputStatusMessage
    }

    # Gather installed drivers, based on OEM*.INF
    $installedDrivers = Get-WMIObject WIN32_PnPSignedDriver | Where-Object { ($_.DeviceName -ne $null) -and ($_.InfName -like "oem*.inf") } | Sort-Object -Property DeviceName

    # Loop through installed drivers
    $driverNumber = 0
    $driverNamePrevious = $null
    foreach ($driver in $installedDrivers)
    {

        $driverName = $($driver.DeviceName)
        $driverVersion = $($driver.DriverVersion)
        $driverDate = "NotFound"
        $infInstalled = "NotFound"
        $infupdatedPath = "NA"
        $infUpdatedPath = "NA"
        $infDriverDate = "NA"
        $infDriverVersion = "NA"
        $xmlResult = "NA"
        $driverType = "Driver"

        if ($driverName -eq $driverNamePrevious) {
            $driverNumber++
            $driverNameNumber = "_$driverNumber"
        } else {
            $driverNumber=0
            $driverNameNumber = $null
        }
        $driverNamePrevious = $driverName

        # SKIP EXCLUDED
        if (CheckForExlcude -deviceHWID $($driver.HardwareID)) { continue }

        # Driver info
        $d = $($driver.DriverDate)
        # Convert DATE: 20160621000000, to: 06/21/2016
        $driverDate = $d.Substring(4,2) + "/" + $d.Substring(6,2) + "/" + $d.Substring(0,4)
        $driverHWID = $($Driver.HardWareID)
        "Currently installed Date and Version: $driverDate, $driverVersion" | OutputStatusMessage

        $infInstalled = "$ENV:windir\inf\$($driver.InfName)"
        "INF of driver that is installed: $infInstalled" | OutputStatusMessage
        "Hardware ID: $driverHWID"  | OutputStatusMessage

        if ($Driver.HardWareID -match "uefi") {
            "Capsule HWID: $driverHWID" | OutputStatusMessage
        }

        if ( ($driverHWID -match "uefi") -and ($driver.deviceID -like ("*{*}*") )) {
            $driverType = "Firmware"
        }

        try {
            # .CAT will be OEM*.cat, no need to get cat name from INF info.
            $catFilePath = $env:windir + "\System32\CatRoot\{F750E6C3-38EE-11D1-85E5-00C04FC295EE}\" + ((split-path ($infInstalled) -leaf).replace(".inf", ".cat"))
            if (Test-Path -Path $catFilePath) {
                $catFile = Get-Item -Path $catFilePath
                if ($catFile.GetType().Name -match "file") {
                    # Get Catalog details
                    $certInfo = GetCertificateWithInfo -CatalogFile $catFilePath
                    # Check for OEM UEFI
                    if ( ($certInfo.Cert -like "OEM*Leaf" -or $certInfo.AttestationSigned) -and $($inf.name) -like "OEM*UEFI*"){
                        "Found OEM UEFI, skipping cert check" | OutputStatusMessage
                        $installedSigning = "OEMUEFI"
                        $testPassed = $true
                    } elseif ($certInfo.AttestationSigned) {
                        "$driverName is Attestation signed" | OutputStatusMessage
                        $installedSigning = "AtTestation"
                    } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                        "$driverName is PreProduction signed" | OutputStatusMessage
                        $installedSigning = "PreProduction"
                    } elseif (-not $certInfo.WHQLStyleCert) {
                        "$driverName is Not WHQL signed" | OutputStatusMessage
                        $installedSigning = "Not-WHQL"
                    } else {
                        $installedSigning = "WHQL"
                        $testPassed = $true
                    }
                } else {
                    "$catFilePath is not a file" | OutputStatusMessage
                    $installedSigning = "Catalog Not a file"
                }
            } else {
                "$catFilePath not found." | OutputStatusMessage
                $installedSigning = "$catFile - Not Found"
            }
        } catch {
            "$expectedDescription threw an exception`n$($_.Exception.Message)`n$($_.ScriptStackTrace)" | OutputErrorMessage
        }
          
                    # Log to XML
        # Friendly name, hwid, status, version, result
        $statusCode = (Get-WmiObject Win32_PNPEntity | Where-Object {$_.DeviceID -eq $($driver.DeviceID)} | Select-Object ConfigManagerErrorCode).ConfigManagerErrorCode
        $global:ResultsXmlWriter.WriteStartElement('Result')
        $global:ResultsXmlWriter.WriteElementString('InfFilePath', $infUpdatedPath)
        $global:ResultsXmlWriter.WriteElementString('DriverDate', $driverDate)
        $global:ResultsXmlWriter.WriteElementString('DeviceName', $driverName + $driverNameNumber)
        $global:ResultsXmlWriter.WriteElementString('StatusCode', $statusCode)
        $global:ResultsXmlWriter.WriteElementString('DriverVersionInInfFile', $infDriverDate.trim() + ", " + $infDriverVersion.trim())
        $global:ResultsXmlWriter.WriteElementString('DriverVersionInSystem', $driverDate.trim() + ", " + $driverVersion.trim())        
        $global:ResultsXmlWriter.WriteElementString('DriverMatchStatus', "ignore")
        $global:ResultsXmlWriter.WriteElementString('Rollback', "ignore")
        $global:ResultsXmlWriter.WriteElementString('ExpectedSigning', "ignore")
        $global:ResultsXmlWriter.WriteElementString('InstalledSigning', "$installedSigning")
        $global:ResultsXmlWriter.WriteElementString('DriverType', "$driverType")
        $global:ResultsXmlWriter.WriteEndElement()

    }
}

function VerifyVersions {

    # Get ESRT Info
    $esrt = Get-EsrtValues -useHashTable

    # Track INFs to log all INFS not used
    $InfsUsed =@{}

    # Track Excluded Devices
    $ExcludedDevices = @{}

    $driversFullPath = $driversFullPath.Trim()
    $driversFullPath = $driversFullPath.TrimEnd('\')
    "Drivers Full Path: $driversFullPath" | OutputStatusMessage
    if ([string]::IsNullOrWhitespace($driversFullPath))
    {
        "Drivers Full Path is empty." | OutputErrorMessage
    }
    
    # Gather INF files
    $infs = Get-ChildItem $drivers\*.inf -Recurse | Where-Object {!$_.PsIsContainer}
    
    # Gather installed drivers, based on OEM*.INF
    $installedDrivers = Get-WMIObject WIN32_PnPSignedDriver | Where-Object { ($_.DeviceName -ne $null) -and ($_.InfName -like "oem*.inf") } | Sort-Object -Property DeviceName

    # Loop through installed drivers
    $driverNumber = 0
    $driverNamePrevious = $null
    foreach ($driver in $installedDrivers) {
    
        $driverName = $($driver.DeviceName)
        $driverVersion = $($driver.DriverVersion)
        $driverDate = "NotFound"
        $infDriverDate = "NotFound"
        $infDriverVersion = "NotFound"
        $infInstalled = "NotFound"
        $MatchingDeviceID = "NotFound"
        $inf = $null
        $infUpdatedPath = "NotFound"
#        $driverDeviceID = "NotFound"
        $driverService = "NotFound"
        $driverFile = "NotFound"
        $rollbackPolicy = "False"
        $driverType = "Driver"

        # SKIP EXCLUDED
        if (CheckForExlcude -deviceHWID $($driver.HardwareID)) {
            # Add to list, will store in XML. Check for Duplicates
            if (-not $ExcludedDevices.ContainsKey($driverName)){
                $ExcludedDevices.add($driverName,$true)
            }
            continue
        }

        # Don't allow Duplicate Driver Names'
        if ($driverName -eq $driverNamePrevious) {
            $driverNumber++
            $driverNameNumber = "_$driverNumber"
        } else {
            $driverNumber=0
            $driverNameNumber = $null
        }
        $driverNamePrevious = $driverName


        # Test for OEM* strings
        $testName = "Verify device '$driverName' INF Manufacturer is not using OEM* string."
        if (IsWttLogger) {Start-WTTTest -name $testName}
        if (($driver.Manufacturer -like "OEM*") -and (-not $driver.DriverProviderName -like "OEM*UEFI*") ) {
            "FAIL $($driver.DeviceName) has manufacturer name: $($Driver.Manufacturer)" | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
        } else {
            if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
        }

        $testName = "Verify device '$driverName' INF Porvider is not using OEM* string."
        if (IsWttLogger) {Start-WTTTest -name $testName}
        if ( ($driver.DriverProviderName -match "OEM") -and (-not $driver.DriverProviderName -like "OEM*UEFI*") ) {
            "FAIL $($driver.DeviceName) has DriverProviderName name: $($Driver.DriverProviderName)" | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
        } else {
            if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
        }

        # Start device testing...
        " --- Looking for matching INF For device: $driverName ---" | OutputStatusMessage
        $testName = "'$driverName' using INF from expected driver share."
        if (IsWttLogger) {Start-WTTTest $testName}

        # Each OEM driver is expected to match.
        $infHash = $(Get-FileHash $ENV:windir\inf\$($driver.InfName)).Hash

        # Loop through the INFs and log if we found a match.
        foreach ($inf in $infs) {

            $fileHash = $(Get-FileHash $inf).Hash
            $HashCheckSuccess = $false
            if ($fileHash -ne $infHash) {
                continue
            }

            $HashCheckSuccess = $true
            $xmlResult = "Verified"

            # Mark INF As being used - for logging at the end of test
            if (-not ($InfsUsed.ContainsKey($inf))) {
                $InfsUsed.add($inf, $true)
            }

            #"Matching INF: $inf"  | OutputStatusMessage
            "Success: $driverName"  | OutputStatusMessage
            break

        }

        # Get Hardware ID that the PNP Manager matched on.
        #$escapedDeviceName = $driver.DeviceName -Replace "\(","\(" -replace "\)", "\)"
        $MatchingDeviceID = $(Get-ChildItem -Path HKLM:\SYSTEM\CurrentControlSet\Control\Class\$($driver.ClassGUID) -exclude Properties | 
            Get-ItemProperty | 
            Where-Object {$_.DriverDesc -eq $driverName} |
            Select-Object -Property MatchingDeviceID).MatchingDeviceId

        if ($HashCheckSuccess -eq $false) {
            "FAILURE: $driverName"  | OutputStatusMessage
            $xmlResult = "INF Hash Mismatch"

            # find INF that has the FriendlyName and matching DeviceID string
            $infMatchingFiles=$(Get-ChildItem -Path $drivers -file -Recurse -include *.inf | 
                                Where-Object { $_ | Select-String -pattern $MatchingDeviceID -SimpleMatch} | 
                                Where-Object { $_ | Select-String -pattern $driverName -SimpleMatch} |
                                Get-Unique | Sort-Object LastWriteTime).fullname

            if ($infMatchingFiles.count -eq 1)
            {
                $inf = Get-ChildItem $infMatchingFiles

            } elseif ($infMatchingFiles -gt 1) {
                "WARNING: Multiple INF files found matching this device!  Selecting newest file by write time." | OutputStatusMessage
                $inf = Get-ChildItem $infMatchingFiles[0]

            } else {
                $inf = "NotFound"
                $xmlResult = "INF match Not Found"
            }
        } 
        
        # Gather and Log INF INFO
        $infCatName = "NotFound"
        $infCatFullPath = "NotFound"
        if ($inf -ne "NotFound") {
            $Content = Get-Content -Path $inf
            $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $infDriverDate = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
            $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $infDriverVersion = ($_.Split(","))[1].split(';')[0] -replace '([^;]*);.*',"`$1" } }
            $Content | ForEach-Object { if ($_ -like "*CatalogFile.NT*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
            $Content | ForEach-Object { if ($_ -like "*CatalogFile*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1"} }
            $infUpdatedPath = $inf.fullname.Replace("C:\ExpectedDrivers",$driversFullPath)
            $infUpdatedPath = $infUpdatedPath.Replace("'","")
            $infCatFullPath = (split-path ($inf.fullname) -parent) + "\" + $infCatName.trim()
            $infCatFullPath = $infCatFullPath.Replace("\\","\")
        }
        "Expected INF Driver Date and Version: $infDriverDate, $infDriverVersion" | OutputStatusMessage

        # Driver info
        $d = $($driver.DriverDate)
        # Convert DATE: 20160621000000, to: 06/21/2016
        $driverDate = $d.Substring(4,2) + "/" + $d.Substring(6,2) + "/" + $d.Substring(0,4)
        $driverHWID = $($Driver.HardWareID)
        "Currently installed Date and Version: $driverDate, $driverVersion" | OutputStatusMessage

        # Get the Service Binary (.sys)
        $driverDeviceID = $($Driver.serviceName)
        $driverService = (Get-WMIObject Win32_PnPEntity | Where-Object { ($_.DeviceID -ne $null) -and ($_.DeviceID -eq $($driver.DeviceID)) } | Sort-Object -Property DeviceID -Unique | Select-Object Service).Service
        if ($driverService -ne $null) {
            $driverFile = Split-path((Get-ItemProperty HKLM:\System\CurrentControlSet\Services\$driverService -name ImagePath).ImagePath) -leaf
        }

        # Print Info
        $infInstalled = "$ENV:windir\inf\$($driver.InfName)"
        "INF of driver that is installed: $infInstalled" | OutputStatusMessage
        "INF of driver that is expected: $infUpdatedPath" | OutputStatusMessage
        "Hardware ID: $driverHWID"  | OutputStatusMessage
        "PNP Matching HWID: $MatchingDeviceID" | OutputStatusMessage

        # Log result
        if ($HashCheckSuccess -eq $false) {
            "FAIL: Device NOT using INF from the expected Drivers Path. DeviceName: $driverName." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
        } else {
            "PASS: Device IS using INF from the expected Drivers. DeviceName: $driverName." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
        }

        # Firmware Checks
        if ( ($driverHWID -match "uefi") -and ($driver.deviceID -like ("*{*}*") )) {
            $XmlResultInf = $xmlResult
            $driverType = "Firmware"
            $testname = "'$driverName' firmware installed matches expected INF."
            if (IsWttLogger) {Start-WTTTest $testName}
            "Checking Firmware versions for $($driver.description)" | OutputStatusMessage

            # Get Machines Firmware info
            $fwGUID = "{" + $($driver.deviceID).Split("{}")[1] + "}"
            $fwAttemptVer = $esrt.$fwGUID.LastAttemptedVersion_verstr
            $fwLowestSupportedVer = $esrt.$fwGUID.LowestSupportedVersion_verstr
            $fwInstallVersion = $esrt.$fwGUID.InstalledVersion_VerStr
            $fwName = Get-FirmwareName -fwGUID $fwGUID

            # Intel has different versioning
            if ($Device.name -like "ME") {
                $fwAttemptVer = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name LastAttemptVersion
                $fwLowestSupportedVer = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name LowestSupportedVersion
                $fwInstallVersion = Get-ItemPropertyValue "HKLM:\Hardware\UEFI\ESRT\$fwGUID" -Name Version
            }

            # Log info
            $logExpectedDriverInfo = "Firmware Info:" +
            "`n  Firmware name:`t`t$fwName" +
            "`n  Installed Version:`t`t$fwInstallVersion" +
            "`n  Last Attempted Version:`t$fwAttemptVer" +
            "`n  Lowest Supported Version:`t$fwLowestSupportedVer"
            $logExpectedDriverInfo | OutputStatusMessage

            # XML Updates
            # $driverDate = ""
            # $infDriverDate = ""
            #$xmlResult = "Verified"

            # Check for Lowest Supported Version
            if ($infDriverVersion -like ("1.0.0*")) {
                $xmlResult = "NULL capsule, unable to get version"
                "INF Capsule does not contain Firmware (NULL CAPSULE), failing version check." | OutputStatusMessage
                # Null capsule skip
                if ( ($fwName -eq "Jupiter Touch" -and $fwInstallVersion -eq "660.0.256") -or ($fwName -eq "Cardinal EC" -and $fwInstallVersion -eq "117.1288.257") ){
                    "$fwName firmware matches factory released version, changing failure to WARNING to null capsule." | OutputWarningMessage
                    if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
                } else {
                    if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
                }

            } elseif ($driverHWID -notlike ("*}&*")){
                $xmlResult = "INF match Not Found"
                "Unable to find hardware ID version, failing version check." | OutputStatusMessage
                if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}

            } elseif ($inf -eq "NotFound"){
                $xmlResult = "INF match Not Found"
                "INF Capsule not found, failing version check." | OutputStatusMessage
                if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}

            } else {

                $infContent = Get-Content -Path $inf
                $firmwareVerID = $driverHWID.substring($driverHWID.IndexOf("&REV_") + ("&REV_").Length)
                if ($infContent -like ("*firmwareversion*$firmwareVerID")) {
                    "Found HWID Version in INF" | OutputStatusMessage
                    if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
                    #$xmlResult = "Verified"
                    $XmlResult = $XmlResultInf

                } elseif ($esrt.$fwGUID.LastAttemptedVersion_Binary -LT $esrt.$fwGUID.LowestSupportedVersion_Binary){
                    $xmlResult = "Driver Mismatch"
                    "WARNING: Firmware driver attempted install will not rollback without Manufacturing Mode !!!!!!!!!!" | OutputStatusMessage
                    if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}

                } else {
                    "Installed Firmware Revision: $firmwareVerID" | OutputStatusMessage
                    $driverVersion = $driverVersion + ", 0x$firmwareVerID"

                    $xmlResult = "Hardware (HWID Rev) Version Mismatch"
                    "ERROR: Did Not Find the installed firmware HWID in expected INF" | OutputStatusMessage

                    $infFirmwareVersionLine = $infContent -like ("*DriverVer*")
                    "Expected Version: $infFirmwareVersionLine" | OutputStatusMessage

                    $infFirmwareVersionLine = $infContent -like ("*firmwareversion*")
                    $infRev = $infFirmwareVersionLine.substring($infFirmwareVersionLine[0].IndexOf(",0x") + (",0x").Length)
                    "INF Frimware Revision: $infFirmwareVersionLine" | OutputStatusMessage
                    $infDriverVersion = $infDriverVersion + ", 0x$infRev"

                    if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
                }
            }

            # Firmware Rollback Policy Check
            if (test-path $inf ) {
                $rollbackPolicy = "False"
                $infLine = Get-Content -path $Inf | Select-String -pattern ",Policy,%REG_DWORD%,1"
                if ( ($infLine -ne $null) -and ($inf -notlike "*OEM*UEFI.inf") ) {
                    $rollbackPolicy = "True"
                }

                if ($testFirmwareRollback -eq "true") {
                    $testName = "Verify INF '$($inf)' is not setting a Policy Rollback registry key."
                    if (IsWttLogger) {Start-WTTTest -name $testName}
                    if ($rollbackPolicy -eq "True") {
                        "FAIL '$($inf)' has Policy Rollback registry key. Found: '$infLine'" | OutputStatusMessage
                        if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
                    } else {
                        "PASS '$($inf)' Policy string not found." | OutputStatusMessage
                        if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
                    }
                }else {
                    "testFirmwareRollback:$testFirmwareRollback - Skipping Firmware Rollback Policy check." | OutputStatusMessage
                }
            } 

        } # Capsule check

        #region DriverSigningTest
        "Getting Signing info..." | OutputStatusMessage
        $testName = "Verify Expected device '$driverName' driver is signed correctly."
        $testPassed = $false
        $expectedSigning = "NotFound"  
        $catFile = "NotFound"
        # Verify Signing on Expected drivers
        try {
            if (Test-Path -Path $infCatFullPath) {
                $catFile = Get-Item -Path $infCatFullPath
                if ($catFile.GetType().Name -match "file") {
                    # Get Catalog details
                    $certInfo = GetCertificateWithInfo -CatalogFile $infCatFullPath
                    if ( ($certInfo.Cert -like "OEM*Leaf" -or $certInfo.AttestationSigned) -and $($inf.name) -like "OEM*UEFI*"){
                        "Found OEM UEFI, skipping cert check" | OutputStatusMessage
                        $expectedSigning = "OEMUEFI"
                        $testPassed = $true
                    } elseif ($certInfo.AttestationSigned) {
                        "$driverName is Attestation signed" | OutputStatusMessage
                        $expectedSigning = "AtTestation"
                    } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                        "$driverName is PreProduction signed" | OutputStatusMessage
                        $expectedSigning = "PreProduction"
                    } elseif (-not $certInfo.WHQLStyleCert) {
                        "$driverName is Not WHQL signed" | OutputStatusMessage
                        $expectedSigning = "Not-WHQL"
                    } else {
                        $expectedSigning = "WHQL"
                        $testPassed = $true
                    }
                } else {
                    "$catFilePath is not a file" | OutputStatusMessage
                    $expectedSigning = "Catalog Not a file"
                }
            } else {
                "$infCatFullPath not found." | OutputStatusMessage
                if ($inf -ne "NotFound") {
                    $expectedSigning = "$infCatFullPath - Not Found"
                } else {
                    $expectedSigning = "N/A"
                }
            }
        } catch {
            "$expectedDescription threw an exception`n$($_.Exception.Message)`n$($_.ScriptStackTrace)" | OutputErrorMessage
        }

        # Log Pass Fail as requested
        if ($testDriverSigning -eq "true"){
            if (IsWttLogger) {Start-WTTTest -name $testName}
            if ($testPassed) {
                if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
            } else {
                "  Inf File Path: $infUpdatedPath" | OutputStatusMessage
                "  Inf Catalog Path: $catFilePath" | OutputStatusMessage
                "  Inf Catalog FULL Path: $infCatFullPath" | OutputStatusMessage
                if (IsWttLogger) { Stop-WTTTest -result "Fail" -name $testName}

                # Update Return code if Signing issue Found
                if ( ($expectedSigning -ne "WHQL") -and ($expectedSigning -ne "OEMUEFI") ) {
                    "Signing Check Failed, Setting Exit to 1" | OutputStatusMessage
                    $Global:LocalExitCode = 1
                }
            }
        } else {
            " - Skipping Signing Check" | OutputStatusMessage
        }

        # Verify Signing on the Installed Drivers
        $testName = "Verify Installed device '$driverName' driver is signed correctly."
        $testPassed = $false
        $installedSigning = "NotFound"
        $catFile = "NotFound"
        try {
            # .CAT will be OEM*.cat, no need to get cat name from INF info.
            $catFilePath = $env:windir + "\System32\CatRoot\{F750E6C3-38EE-11D1-85E5-00C04FC295EE}\" + ((split-path ($infInstalled) -leaf).replace(".inf", ".cat"))
            if (Test-Path -Path $catFilePath) {
                $catFile = Get-Item -Path $catFilePath
                if ($catFile.GetType().Name -match "file") {
                    # Get Catalog details
                    $certInfo = GetCertificateWithInfo -CatalogFile $catFilePath
                    # Check for OEM UEFI
                    if ( ($certInfo.Cert -like "OEM*Leaf" -or $certInfo.AttestationSigned) -and $($inf.name) -like "OEM*UEFI*"){
                        "Found OEM UEFI, skipping cert check" | OutputStatusMessage
                        $installedSigning = "OEMUEFI"
                        $testPassed = $true
                    } elseif ($certInfo.AttestationSigned) {
                        "$driverName is Attestation signed" | OutputStatusMessage
                        $installedSigning = "AtTestation"
                    } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                        "$driverName is PreProduction signed" | OutputStatusMessage
                        $installedSigning = "PreProduction"
                    } elseif (-not $certInfo.WHQLStyleCert) {
                        "$driverName is Not WHQL signed" | OutputStatusMessage
                        $installedSigning = "Not-WHQL"
                    } else {
                        $installedSigning = "WHQL"
                        $testPassed = $true
                    }
                } else {
                    "$catFilePath is not a file" | OutputStatusMessage
                    $installedSigning = "Catalog Not a file"
                }
            } else {
                "$catFilePath not found." | OutputStatusMessage
                $installedSigning = "$catFile - Not Found"
            }
        } catch {
            "$expectedDescription threw an exception`n$($_.Exception.Message)`n$($_.ScriptStackTrace)" | OutputErrorMessage
        }

        # Log Pass Fail as requested
        if ($testDriverSigning -eq "true"){
            if (IsWttLogger) {Start-WTTTest -name $testName}
            if ($testPassed) {
                if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
            } else {
                "  Inf File Path: $infUpdatedPath" | OutputStatusMessage
                "  Inf Catalog Path: $catFilePath" | OutputStatusMessage
                if (IsWttLogger) { Stop-WTTTest -result "Fail" -name $testName}

                # Update Return code if Signing issue Found
                if ( ($installedSigning -ne "WHQL") -and ($installedSigning -ne "OEMUEFI") ) {
                    "Signing Check Failed, Setting Exit to 1" | OutputStatusMessage
                    $Global:LocalExitCode = 1
                }
            }
        } else {
            " - Skipping Signing Check" | OutputStatusMessage
        }

        "Getting Signing info... Complete." | OutputStatusMessage
        #endregion DriverSigningTest

        # Update Return code if FAILURE Found
        #if ( ($xmlResult -ne "Verified") -or ($($rollbackPolicy) -ne "False") -and ($inf -notlike "*\autorun.inf") ) {
        #     "Version or Rollback failed, Setting Exit to 1" | OutputStatusMessage
        #     $Global:LocalExitCode = 1
        # }

        # Log to XML as requested
        if ($xmlEnabled -eq "true") { 
            $statusCode = (Get-WmiObject Win32_PNPEntity | Where-Object {$_.DeviceID -eq $($driver.DeviceID)} | Select-Object ConfigManagerErrorCode).ConfigManagerErrorCode
            $global:ResultsXmlWriter.WriteStartElement('Result')
            $global:ResultsXmlWriter.WriteElementString('InfFilePath', $infUpdatedPath)
            $global:ResultsXmlWriter.WriteElementString('DriverDate', $driverDate)
            $global:ResultsXmlWriter.WriteElementString('DeviceName', $driverName + $driverNameNumber)
            $global:ResultsXmlWriter.WriteElementString('DriverFile', $driverFile)
            $global:ResultsXmlWriter.WriteElementString('DriverVersionInInfFile', $infDriverDate.trim() + ", " + $infDriverVersion.trim())
            $global:ResultsXmlWriter.WriteElementString('DriverVersionInSystem', $driverDate.trim() + ", " + $driverVersion.trim())
            $global:ResultsXmlWriter.WriteElementString('DriverMatchStatus', $xmlResult)
            $global:ResultsXmlWriter.WriteElementString('StatusCode', $statusCode)
            $global:ResultsXmlWriter.WriteElementString('Rollback', $($rollbackPolicy))
            $global:ResultsXmlWriter.WriteElementString('ExpectedSigning', $expectedSigning)
            $global:ResultsXmlWriter.WriteElementString('InstalledSigning', $installedSigning)
            $global:ResultsXmlWriter.WriteElementString('DriverType', $driverType)
            $global:ResultsXmlWriter.WriteElementString('HwIDMatch', $MatchingDeviceID)
            $global:ResultsXmlWriter.WriteEndElement()
        }
    }

    # INF Tests
    foreach ($inf in $infs) {

        # Log INFS not installed, and signing
        if ( ($xmlEnabled -eq "true") -and (-not ($InfsUSed.ContainsKey($inf))) -and ($inf -notlike "*\autorun.inf") ) {

            # Skip if extension driver
             if (gc $inf | select-string -pattern "e2f84ce7-8efa-411c-aa69-97454ca4cb57") {
                continue
             }

            # Get Sigining Info
            $Content = Get-Content -Path $inf
            $Content | ForEach-Object { if ($_ -like "*CatalogFile.NT*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
            $Content | ForEach-Object { if ($_ -like "*CatalogFile*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1"} }
            $infCatFullPath = (split-path ($inf.fullname) -parent) + "\" + $infCatName.trim()
            $infCatFullPath = $infCatFullPath.Replace("\\","\")
            
            "inf: $inf" | OutputStatusMessage
            "infCatFullPath: $infCatFullPath" | OutputStatusMessage

            $certInfo = GetCertificateWithInfo -CatalogFile $infCatFullPath
            $signed = "WHQL"
            if ($certInfo.AttestationSigned) {
                $signed = "AtTestation"
            } elseif ($certInfo.Cert -like "OEM*Leaf" -and $($inf.name) -like "OEM*UEFI*"){
                $signed = "OEMUEFI"
            } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                $signed = "PreProduction"
            } elseif (-not $certInfo.WHQLStyleCert) {
                $signed = "TestSigned"
            }

            # Firmware Rollback Policy Check
            if (test-path $inf ) {
                $rollbackPolicy = "False"
                $infLine = Get-Content -path $Inf | Select-String -pattern ",Policy,%REG_DWORD%,1"
                if ( ($infLine -ne $null) -and ($inf -notlike "*OEM*UEFI.inf") ) {
                    $rollbackPolicy = "True"
                }

                if ($testFirmwareRollback -eq "true") {
                    $testName = "Verify INF '$($inf)' is not setting a Policy Rollback registry key."
                    if (IsWttLogger) {Start-WTTTest -name $testName}
                    if ($rollbackPolicy -eq "True") {
                        "FAIL '$($inf)' has Policy Rollback registry key. Found: '$infLine'" | OutputStatusMessage
                        if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
                    } else {
                        "PASS '$($inf)' Policy string not found." | OutputStatusMessage
                        if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
                    }
                }else {
                    "testFirmwareRollback:$testFirmwareRollback - Skipping Firmware Rollback Policy check." | OutputStatusMessage
                }
            } 
 
            "Not installed: $($inf)" | OutputStatusMessage
            $global:ResultsXmlWriter.WriteStartElement('NotFound')
            $global:ResultsXmlWriter.WriteElementString('NotInstalled', $($inf))
            $global:ResultsXmlWriter.WriteElementString('Rollback', $($rollbackPolicy))
            $global:ResultsXmlWriter.WriteElementString('Signed', $($signed))
            $global:ResultsXmlWriter.WriteEndElement()
       }
    }


    # Loop Excluded Devices
    if ($ExcludedDevices -ne $null) {
        foreach ($excludedDevice in $ExcludedDevices.GetEnumerator())
        {
            # Log if requested
            if ($xmlEnabled -eq "true")
            {
                "Excluded Device $($excludedDevice.name)" | OutputStatusMessage
                $global:ResultsXmlWriter.WriteStartElement('Excluded')
                $global:ResultsXmlWriter.WriteElementString('ExcludedDevice', $($excludedDevice.name))
                $global:ResultsXmlWriter.WriteEndElement()
            }
        }
    }
}

function VerifyExtensionDrivers {

    # Track INFs to log all INFS not used
    $InfsUsed =@{}

    # Gather INSTALLED Extension INF's
    $ExtensionDrivers = ((GCI -Recurse -Path $env:SystemRoot\System32\DriverStore\FileRepository -Filter *.inf | ? {!$_.PsIsContainer -and $_.name -ne "c_extension.inf"}) | ? {gc $_.pspath | select-string -pattern "e2f84ce7-8efa-411c-aa69-97454ca4cb57"}).FullName

    # Gather EXPECTED INF Extension INF's
    $infs = (Get-ChildItem $drivers\*.inf -Recurse | Where-Object {!$_.PsIsContainer} | ? {gc $_.pspath | select-string -pattern "e2f84ce7-8efa-411c-aa69-97454ca4cb57"}).fullname

    # Loop through all Expected Extension INF's
    foreach ($inf in $infs) {

        $driverDate = "NotFound"
        $driverVersion = "NotFound"
        $DriverFullName = "NotFound"
        $DriverCatName = "NotFound"
        $catFilePath = "NotFound"
        $installedSigning = "NotFound"

        $infDriverDate = "NotFound"
        $infDriverVersion = "NotFound"
        $infCatName = "NotFound"
        $infCatFullPath = "NotFound"
        $infUpdatedPath = "NotFound"

        $DriverInBox = $false
        $xmlResult = "NotMatched"

        # Loop through the INSTALLED INFs and look for a match.
        foreach ($driver in $ExtensionDrivers) {

            $infHash = $(Get-FileHash $inf).Hash
            write-host "Looking at: $inf with HASH: $infhash"
            $fileHash = $(Get-FileHash $driver).Hash
            $HashCheckSuccess = $false
            if ($fileHash -ne $infHash) {
                continue
            }

            # Mark DRIVER As being used - for logging at the end of test
            if (-not ($InfsUsed.ContainsKey($driver))) {
                $InfsUsed.add($driver, $true)
            }

            $HashCheckSuccess = $true
            $xmlResult = "Verified"

            #"Matching INF: $inf"  | OutputStatusMessage
            "SUCCESS!! - Found Matching INF: $driver"  | OutputStatusMessage
            break
        }

        if ($xmlResult -ne "Verified") { 
            "FAIL!! - Did not find matching INF" | OutputStatusMessage
            $driver = "NotFound"
        } 

        # Get info from Expected INF
        $Content = Get-Content -Path $inf
        $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $infDriverDate = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
        $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $infDriverVersion = ($_.Split(","))[1].split(';')[0] -replace '([^;]*);.*',"`$1" } }
        $Content | ForEach-Object { if ($_ -like "*CatalogFile.NT*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
        $Content | ForEach-Object { if ($_ -like "*CatalogFile*=*") { $infCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1"} }
        $infUpdatedPath = $inf.Replace("C:\ExpectedDrivers",$driversFullPath)
        $infUpdatedPath = $infUpdatedPath.Replace("'","")
        $infCatFullPath = (split-path $inf -parent) + "\" + $infCatName.trim()
        $infCatFullPath = $infCatFullPath.Replace("\\","\")

        # Check the Expected Driver INF, or log NotFound.  This is from C:\Support folder
        "Getting Signing info..." | OutputStatusMessage
        $testName = "Expected INF driver is signed correctly."
        $testPassed = $false
        $expectedSigning = "NotFound"  
        $catFile = "NotFound"
        try {
            if (Test-Path -Path $infCatFullPath) {
                $catFile = Get-Item -Path $infCatFullPath
                if ($catFile.GetType().Name -match "file") {
                    # Get Catalog details
                    $certInfo = GetCertificateWithInfo -CatalogFile $infCatFullPath
                    if ($certInfo.AttestationSigned) {
                        "$driverName is Attestation signed" | OutputStatusMessage
                        $expectedSigning = "AtTestation"
                    } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                        "$driverName is PreProduction signed" | OutputStatusMessage
                        $expectedSigning = "PreProduction"
                    } elseif (-not $certInfo.WHQLStyleCert) {
                        "$driverName is Not WHQL signed" | OutputStatusMessage
                        $expectedSigning = "Not-WHQL"
                    } else {
                        $expectedSigning = "WHQL"
                        $testPassed = $true
                    }
                } else {
                    "$catFilePath is not a file" | OutputStatusMessage
                    $expectedSigning = "Catalog Not a file"
                }
            } else {
                "$infCatFullPath not found." | OutputStatusMessage
                if ($inf -ne "NotFound") {
                    $expectedSigning = "Not Found"
                } else {
                    $expectedSigning = "N/A"
                }
            }
        } catch {
            "$expectedDescription threw an exception`n$($_.Exception.Message)`n$($_.ScriptStackTrace)" | OutputErrorMessage  
        }

        if ($Driver -ne "NotFound") {

            # Verify Signing on the Installed Driver -
            $testName = "Verify Installed device '$driverName' driver is signed correctly."
            $testPassed = $false
            try {
        
                $Content = Get-Content -Path $Driver
                $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $DriverDate = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
                $Content | ForEach-Object { if ($_ -like "*DriverVer*=*,*") { $DriverVersion = ($_.Split(","))[1].split(';')[0] -replace '([^;]*);.*',"`$1" } }
                $Content | ForEach-Object { if ($_ -like "*CatalogFile.NT*=*") { $DriverCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1" } }
                $Content | ForEach-Object { if ($_ -like "*CatalogFile*=*") { $DriverCatName = ($_.Split(","))[0].Split('=')[1] -replace '([^;]*);.*',"`$1"} }
                $infCatFullPath = (split-path ($driver) -parent) + "\" + $DriverCatName.trim()
                $infCatFullPath = $infCatFullPath.Replace("\\","\")
                $DriverFullName = (split-path $driver -Parent).Split('\')[-1]

                "Cat File Path: $infCatFullPath"
                if (Test-Path -Path $infCatFullPath) {
                    $catFile = Get-Item -Path $infCatFullPath
                    if ($catFile.GetType().Name -match "file") {
                        # Get Catalog details
                        $certInfo = GetCertificateWithInfo -CatalogFile $infCatFullPath
                        if ($certInfo.AttestationSigned) {
                            "$DriverInfName is Attestation signed" | OutputStatusMessage
                            $installedSigning = "AtTestation"
                        } elseif ($certInfo.WHQLStyleCert -and $certInfo.PreProductionCert) {
                            "$DriverInfName is PreProduction signed" | OutputStatusMessage
                            $installedSigning = "PreProduction"
                        } elseif (-not $certInfo.WHQLStyleCert) {
                            "$DriverInfName is Not WHQL signed" | OutputStatusMessage
                            $installedSigning = "Not-WHQL"
                        } else {
                            "$DriverInfName is WHQL signed" | OutputStatusMessage
                            $installedSigning = "WHQL"
                            $testPassed = $true
                        }
                    } else {
                        "$infCatFullPath is not a file" | OutputStatusMessage
                        $installedSigning = "Catalog Not a file"
                    }
                } else {
                    "$infCatFullPath not found." | OutputStatusMessage
                    $installedSigning = "Not Found"
                }
            } catch {
                "$expectedDescription threw an exception`n$($_.Exception.Message)`n$($_.ScriptStackTrace)" | OutputErrorMessage
            }
        }

        # Log to XML as requested
        if ($xmlEnabled -eq "true") { 
            $global:ResultsXmlWriter.WriteStartElement('ExtensionDriver')
            $global:ResultsXmlWriter.WriteElementString('ExtensionFolder', $DriverFullName)
            $global:ResultsXmlWriter.WriteElementString('ExtensionExpectedPath', $infUpdatedPath)
            $global:ResultsXmlWriter.WriteElementString('DriverVersionExpected', $infDriverDate.trim() + ", " + $infDriverVersion.trim())
            $global:ResultsXmlWriter.WriteElementString('DriverVersionInInfSystem', $DriverDate.trim() + ", " + $DriverVersion.trim())
            $global:ResultsXmlWriter.WriteElementString('ExpectedSigning', $expectedSigning)
            $global:ResultsXmlWriter.WriteElementString('InstalledSigning', $installedSigning)
            $global:ResultsXmlWriter.WriteElementString('DriverMatchStatus', $xmlResult)
            $global:ResultsXmlWriter.WriteEndElement()
        }


    } # for each extension driver

}

function VerifyNoGenericFirmwareInstalled {

    # Get all Fimware devices
    $installedDrivers = Get-WMIObject WIN32_PnPSignedDriver | Where-Object {($_.Deviceclass -eq "firmware")}

    "Verifing a Firmware capsule is installed, not generic driver." | OutputStatusMessage
    foreach ($device in $installedDrivers)
    {
        $deviceName = $device.DeviceName
        $deviceHardwareID = $device.HardwareID

        # SKIP EXCLUDED
        if (CheckForExlcude -deviceHWID $deviceHardwareID) { continue }

        # Verify device name is not 'Device Firmware'
        $testName = "'$deviceName' (HardwareID:'$deviceHardwareID') Should not have name: 'Device Firmware'. If this fails the Firmware Capsule is missing."
        if (IsWttLogger) {Start-WTTTest $testName}
        if ($deviceName -eq "Device Firmware" -or $deviceName -eq "System Firmware")
        {
            "  FAIL HardwareID:'$deviceHardwareID' Should not have generic INF name of 'Device Firmware' driver." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
        } else {
            "  PASS HardwareID:'$deviceHardwareID is not installed with 'Device Firmware' generic driver." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}
        }

        # Verify INF is OEM*.inf
        "Verifing Firmware clase devices are using OEM inf..." | OutputStatusMessage
        $deviceName = $($device.DeviceName)
        $deviceHardwareID = $device.HardwareID
        $inf = $($device.InfName)
        $testName = "'$deviceName' (HardwareID:'$deviceHardwareID') should not be using Windows Generic firmware INF. If this fails the Firmware Capsule is missing."
        if (IsWttLogger) {Start-WTTTest $testName}
        if ($inf -notlike "oem*.inf")
        {
            "  FAIL HardwareID:'$deviceHardwareID' expected to be using an OEM driver, not OS Generic firmware INF." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Fail" -name $testName}
            "Setting Exit to 1" | OutputStatusMessage
            $Global:LocalExitCode = 1

            # Log failure to XML
            $global:ResultsXmlWriter.WriteStartElement('Result')
            $global:ResultsXmlWriter.WriteElementString('InfFilePath', "System Firmware - This device is missing a driver!")
            $global:ResultsXmlWriter.WriteElementString('DeviceName', $deviceHardwareID)
            $global:ResultsXmlWriter.WriteElementString('DriverType', "Firmware")
            $global:ResultsXmlWriter.WriteEndElement()

        } else {
            "  PASS '$deviceName' using OEM INF driver." | OutputStatusMessage
            if (IsWttLogger) {Stop-WTTTest -result "Pass" -name $testName}

        }
    }


}

#****************************************************************************************
function GetCertificateWithInfo {
    param(
        [Parameter(Mandatory=$true, Position = 0)]
        $CatalogFile
    )
    $CatalogFile = $CatalogFile -replace '"', ''
    $SignerCertificate = $(Get-AuthenticodeSignature -FilePath $CatalogFile).SignerCertificate
    $Cert = $SignerCertificate.DnsNameList.Unicode
    $Issuer = $SignerCertificate.GetIssuerName()
    $EnhancedKeyUsageList = $SignerCertificate.EnhancedKeyUsageList.FriendlyName

    $isWHQLStyleCert = ($Cert -in @("Microsoft Windows Hardware Compatibility Publisher","Microsoft Windows Hardware Abstraction Layer Publisher"))
    $isPreProdCert   = $Issuer -eq "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows PCA 2010"
    $isAttestionSigned = (("Windows Hardware Driver Attested Verification" -in $EnhancedKeyUsageList) -or ($null -in $EnhancedKeyUsageList))

    $certInfo = [pscustomobject] @{
        PreProductionCert = $isPreProdCert
        WHQLStyleCert = $isWHQLStyleCert
        AttestationSigned = $isAttestionSigned
        Cert = $Cert
        Issuer = $Issuer
    }

    return $certInfo
}

#****************************************************************************************
function PerformResultsXmlProcessing {

    if ($xmlEnabled -ne "true")
    { 
        "Skipping XML($xmlEnabled)" | OutputStatusMessage
        return
    }
    
    if ($global:ResultsXmlWriter -ne $null) {return}

    $global:ResultsXmlWriter = New-Object System.Xml.XmlTextWriter(".\results_drivers$xmlIteration.xml", $Null) -Verbose
    $global:ResultsXmlWriter.Formatting = 'Indented'
    $global:ResultsXmlWriter.Indentation = '4'
    $global:ResultsXmlWriter.WriteStartDocument()
    $XsltPropertyText = 'type="text/xsl" href="results_driverVer12.xsl" '
    $global:ResultsXmlWriter.WriteProcessingInstruction('xml-stylesheet', $XsltPropertyText)
    $global:ResultsXmlWriter.WriteStartElement('Results')

    write-host "Created Results XML"

}

#****************************************************************************************
function AddDeviceInfoNodeXML {

    if ($xmlEnabled -ne "true") { 
        return
    }

    $imageName = 'Not Found'
    $systemSKU = 'Not Found'
    $hotFixes = 'Not Found'

    $registry_Key = $null
    if (test-path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage") {
        $registry_Key= Get-ItemProperty -path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage" -name "ImageVersion" -ErrorAction Continue
        if($registry_Key) {
            $OSimageName =  $registry_Key.ImageVersion
        }
    } else {
        if (test-path "C:\Windows\SysNative\Reg.exe"){
                $regOutput = C:\Windows\sysnative\reg.exe query "HKLM\SOFTWARE\Microsoft\Surface\OSImage" /v "ImageVersion"
            try { 
                $OSimageName = $regOutput.split(" ")[14]
            } catch {}
        }
    }

    $registry_Key = $null
    if (test-path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage") {
        $registry_Key= Get-ItemProperty -path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage" -name "ImageProductName" -ErrorAction Continue
        if($registry_Key) {
            $ImageProductName =  $registry_Key.ImageProductName
        }
    } else {
        if (test-path "C:\Windows\SysNative\Reg.exe"){
                $regOutput = C:\Windows\sysnative\reg.exe query "HKLM\SOFTWARE\Microsoft\Surface\OSImage" /v "ImageProductName"
            try { 
                $ImageProductName = $regOutput.split(" ")[14]
            } catch {}
        }
    }

    $registry_Key = $null
    if (test-path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage") {
        $registry_Key= Get-ItemProperty -path "HKLM:\SOFTWARE\Microsoft\Surface\OSImage" -name "ImageName" -ErrorAction Continue
        if($registry_Key) {
            $ImageName =  $registry_Key.ImageName
        }
    } else {
        if (test-path "C:\Windows\SysNative\Reg.exe"){
                $regOutput = C:\Windows\sysnative\reg.exe query "HKLM\SOFTWARE\Microsoft\Surface\OSImage" /v "ImageName"
            try { 
                $ImageName = $regOutput.split(" ")[14]
            } catch {}
        }
    }
    
    $registry_Key = $null
    if (test-path "HKLM:\HARDWARE\DESCRIPTION\System\BIOS") {
        $registry_Key = Get-ItemProperty -path "HKLM:\HARDWARE\DESCRIPTION\System\BIOS" -name "SystemSKU" -ErrorAction Continue
        if($registry_Key) {
            $SystemSKU = $registry_Key.SystemSKU
        }
    } else {
        if (test-path "C:\Windows\SysNative\Reg.exe"){
                $regOutput = C:\Windows\sysnative\reg.exe query "HKLM\HARDWARE\DESCRIPTION\System\BIOS" /v "SystemSKU"
            try { 
                $SystemSKU = $regOutput.split(" ")[14]
            } catch {}
        }
    }

    # get OS info
    $os_version = (cmd /c ver).split(" ")[4].trim("][")
    $os_ID = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").ReleaseId
    
    # Get KB articles
    [string]$hotfix = systeminfo /fo csv | ConvertFrom-Csv | select hotfix*
    $hotfix = ($hotfix.split(",",2).trim("}"))[1]


    $CPU = $env:PROCESSOR_ARCHITECTURE
    $ComputerName = $env:COMPUTERNAME

    $global:ResultsXmlWriter.WriteStartElement('DeviceInfo')
    $global:ResultsXmlWriter.WriteElementString('OS', $os_id + "_$os_version")
    $global:ResultsXmlWriter.WriteElementString('HotFixes', $hotfix)
    $global:ResultsXmlWriter.WriteElementString('ComputerName', $ComputerName)
    $global:ResultsXmlWriter.WriteElementString('BuildImage', $OSimagename)
    $global:ResultsXmlWriter.WriteElementString('ImageProductName', $ImageProductName)
    $global:ResultsXmlWriter.WriteElementString('ImageName', $ImageName)
    $global:ResultsXmlWriter.WriteElementString('SystemSKU', $SystemSKU)
    $global:ResultsXmlWriter.WriteElementString('CPU', $CPU)
    $global:ResultsXmlWriter.WriteElementString('Iteration', $xmlIteration)
    $global:ResultsXmlWriter.WriteEndElement()
    
    XMLClose

    GenHTML
}

Function GenHTML {
     # Transform results to HTML  
        [void] [System.Reflection.Assembly]::LoadWithPartialName("'System.IO.File")
        [void] [System.Reflection.Assembly]::LoadWithPartialName("'System.Xml.XmlReader")
        [void] [System.Reflection.Assembly]::LoadWithPartialName("'System.Xml.XmlTextWriter")
        $outputFIleName = ".\results_drivers$xmlIteration.html"  
        $transformFilePath = ".\results_driverVer12.xsl"  
        if(-not (test-path $transformFilePath)) {
            Write-Host "You must run this report from the directory containing results_driverVer12.xsl"
        }
        else
        {
            if(test-path $outputFIleName)
            {
                #if exists remove and replace with new
                Remove-Item -Path $outputFIleName -Force
            }    
            $tempReportPath = ".\results_drivers$xmlIteration.xml"
            $XSLInputElement = New-Object System.Xml.Xsl.XslCompiledTransform;
            $XSLInputElement.Load($transformFilePath)
            $reader = [System.Xml.XmlReader]::Create($tempReportPath)
            $writer = [System.Xml.XmlTextWriter]::Create($outputFIleName)

            try {
                $XSLInputElement.Transform($reader, $writer)
                write-host "Created Results HTML"
            }
            catch {    
                Write-Host 'Crash hit while attempting to transform the XML file'
            }

            try {
                [System.Xml.XmlTextWriter]::Close()
            }
            catch {
                Write-Host 'Crash hit while attempting to close the writer'
            } 
        }
    }

function XMLClose {

    if ($xmlEnabled -ne "true" -or $global:ResultsXmlWriter -eq $null ) { return }

    $global:ResultsXmlWriter.WriteEndElement()
    $global:ResultsXmlWriter.WriteEndDocument()
    $global:ResultsXmlWriter.Flush()
    $global:ResultsXmlWriter.Close()

    $global:ResultsXmlWriter = $null
    
}

function CheckForExlcude {
    Param(
        [string] $DeviceHWID
    )

    # Skip if excluded
    $exclude = $false
    foreach ($excludeDevice in $script:ExcludeList) 
    {
        if ($DeviceHWID -like "*$excludeDevice*")
        {
            $exclude = $true
            "--------------- Excluding Device: $DeviceHWID" | OutputStatusMessage
            break
        }
    }

    return $exclude
}

function CreateExcludeList {

    # Show Exclude List param   
    "Excluded List Param: $exclude_HWID" | OutputStatusMessage

    # Update using paramater
    $exclude_HWID_List = $Exclude_HWID -split ';'
    foreach ($excluded_HWID in $exclude_HWID_List)
    {
        $script:excludeList.add($excluded_HWID)
        "Excluded Hardware ID: $excluded_HWID" | OutputStatusMessage
    }
   
    # Check for XML containing excluded HWID's
    if ( ($Exclude_File -ne $null) -and (test-path($Exclude_File)) )
    {
        [xml]$xmlExclude = get-content $Exclude_File
        $xmlExcludes = $xmlExclude.DataStore.Whitelist.exclude.DeviceHWID
        foreach ($excluded_HWID in $xmlExcludes)
        {
            $script:excludeList.add($excluded_HWID)
            "Excluded Hardware ID: $excluded_HWID" | OutputStatusMessage
        }
    }
}

#region main
############################
# MAIN
############################

$global:ErrorActionPreference = 'stop'
$IsWTTLogger = $false
$Global:LocalExitCode = 0

# Tools
Invoke-Expression ". '$PSScriptRoot\Get-EsrtValues.ps1'" -ErrorAction Stop

# WTT LOGGING
$WttLogFileName = "VerifyOemDriverVersions.wtl"
Invoke-Expression ". '$PSScriptRoot\PSWttLogger.ps1'" -ErrorAction Stop


# Initialize WTT Logging
try
{
    # Will throw exception if unable to load WTT Logging
    [void] (Start-WTTLog $WttLogFileName);
    'WTT Log started, beginning test!' | OutputStatusMessage
    $IsWTTLogger = $true

} catch {
    Write-Host "Failed to connect to WTT Logger.  Make sure WTTLog is available, or WTT Client is installed."
}

# Execute
try
{

    # Generate an exclude list from XML, and paramter
    CreateExcludeList

    # Check if we have a DIR with INF's
    $driverFolderExists = $true
    if ([string]::IsNullOrWhitespace($drivers)) { 
        $driverFolderExists = $false
    } else {
        $infs = $null
        # try current folder
        if (test-path ($drivers)) {
            $infs = Get-ChildItem $drivers\*.inf -Recurse | Where-Object {!$_.PsIsContainer}
        }
        if ($infs.Length -lt 1) {
            # Try 2nd default folder
            if (test-path ("C:\GoldenPath\Support")) {
                $drivers = "C:\GoldenPath\Support"
                $infs = Get-ChildItem $drivers\*.inf -Recurse | Where-Object {!$_.PsIsContainer}
            }
        }
        if ($infs.Length -lt 1) {$driverFolderExists = $false}
    }

    # no driver path, then just log info to XML
    if ($driverFolderExists -eq $False) {
        if ($IsWTTLogger) {Start-WTTTest "Record Versions"}
        PerformResultsXmlProcessing
        GetDriverVersions
        AddDeviceInfoNodeXML
        if ($IsWTTLogger) {Stop-WTTTest -result "Pass" -name "Record Versions"}
        exit $Global:LocalExitCode
    }
    # Duplicate an Exit for Saftey
    if ($driverFolderExists -eq $False) {exit $Global:LocalExitCode}

    # We found a valid Driver Folder (C:\Support)
    "Drivers Folder: $drivers" | OutputStatusMessage
    $infs = Get-ChildItem $drivers\*.inf -Recurse | Where-Object {!$_.PsIsContainer}
  
    # Check for banged out devices
    if ($testDeviceStatus -eq "true") {
        PerformResultsXmlProcessing
        TestDeviceStatus
    }

    # Verify Firmware drivers are not generic (in-build)
    if ($testFirmwareInf -eq "true") {
        VerifyNoGenericFirmwareInstalled
    }

    # Verify all OEM Infs match inf in expected directory
    if ($testDeviceVersions -eq "true") {
        PerformResultsXmlProcessing
        VerifyVersions
        if ($testExtensionDrivers -eq "true") {
            VerifyExtensionDrivers
        }
        AddDeviceInfoNodeXML

    } elseif ($testExtensionDrivers -eq "true") {
        PerformResultsXmlProcessing
        VerifyExtensionDrivers
        AddDeviceInfoNodeXML
    }


} catch {

    if ( $IsWTTLogger -eq $false) {
        Write-Host "----- TRAP ----"
        Write-Host "Unhandled Exception: $_"
        $_ | Format-List -Force
        #pause

    } else {
        GetErrorInfo | OutputStatusMessage
        Start-WTTTest "Catch Exception"
        Stop-WTTTest -result "Fail" -name "Catch Exception"

    }
    $Global:LocalExitCode = 1

    if ( $ResultsXmlWriter -ne $null){
        $ResultsXmlWriter.Close()
    }

}

if ($IsWTTLogger) {Stop-WTTLog}

if ( $ResultsXmlWriter -ne $null){
    XMLClose
}

if (test-path "C:\Tools\PLE\TOAST\Messenger\ToastClientMessenger.exe") {
        c:\Tools\PLE\TOAST\Messenger\ToastClientMessenger.exe -s 1 -d "Marking machine READY."
}


exit $Global:LocalExitCode
#endregion main

