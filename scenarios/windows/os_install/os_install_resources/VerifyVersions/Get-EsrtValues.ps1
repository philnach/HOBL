<#
.Synopsis
   Get-EsrtValues.ps1

.DESCRIPTION
   Reads the ESRT registry keys and returns results of 
    the latest Firmware installation attempts.

.EXAMPLE
   $fwGUID = '{0603709b-92e8-4e49-8ed2-f065e2ad826b}'
   $esrt = Get-EsrtValues -useHashTable
   $esrt.$fwGUID.LowestSupportedVersion_VerStr
   118.1890.0
   $esrt.$fwGUID.LastAttemptedVersion_VerStr
   117.1000.770

   if ($esrt.$fwGUID.LastAttemptedVersion_Binary -LT $esrt.$fwGUID.LowestSupportedVersion_Binary)
   {
      "Cannot install FW with version lower than Lowest Supported Version!"
   }

.INPUTS
   None
   Run without the -useHashTable switch to get human-readable output.

.OUTPUTS
   An array of objects representing each of the registry keys under the ESRT key ('HKLM:\HARDWARE\UEFI\ESRT').

.NOTES
   Some of the following code was leveraged from: 
   $/Imaging/Main/Scripts/modules/UtilityFunctions/BuildVersionUtil.ps1

#>
function Convert-Int32HexToVersionString
{
    <#
    .SYNOPSIS
        Convert a 32-bit integer to www.xxx.yyy formatted version string.
    #>

    param (
      [Parameter(Mandatory=$true)]
      # Hex value to convert to www.xxx.yyy formatted version string
      [uint32] $HexNumber
    )
    $number = $HexNumber
    $bitmask = (1 -shl $NumBits_yyy) - 1
    $yyy = $number -band $bitmask

    $number = $number -shr $NumBits_yyy
    $bitmask = (1 -shl $NumBits_xxx) - 1
    $xxx = $number -band $bitmask

    $www = $number -shr $NumBits_xxx

    return "$www.$xxx.$yyy"
}


function Get-FirmwareName
{
    param
    (
        [GUID] $fwGUID
    )

    $fwName = ''

    $fwGuidLookup = `
    @{
        # ZaP - (Zariah & Pyxis)
        '7a8be0e8-239e-452c-8281-ca184427982c' = 'ZaP ISH'
        '2b1811d7-7e5c-49e9-b04e-e4e048605158' = 'ZaP ME'
        '37da9c3d-6b50-4dbf-82b8-46ca912d98f2' = 'ZaP SAM'
        '5773662e-2343-48b5-b018-db09eae2ea41' = 'Pyxis Touch'
        '5917bcbe-626f-4b76-89d1-b0a8b7a6707a' = 'Zariah Touch'
        'eb60d6cc-00fc-4c65-b5ed-d4005a5807bc' = 'ZaP UEFI'

        # Jupiter
        'A9C020DF-114D-420E-8890-A1436DF3199C' = 'Jupiter UEFI (Production)'
        '1D00B735-0164-48D9-B92B-3DBE716DD147' = 'Jupiter UEFI (Unfused)'
        'D854652B-15EB-4250-B9F8-F05DF501023E' = 'Jupiter Touch'
        '75A2C3E5-B343-4024-8046-3CA6B9FFDF35' = 'Jupiter SAM'
        '3624CD98-BDB6-461B-84A3-4F4853EFC7E3' = 'Jupiter SAMUSP'
        '56BE3499-EE0D-45FC-BB90-CE54AACF3C4A' = 'Jupiter Integrated Sensor Hub (ISH)'
        'c44ae56e-e274-4ce4-86c5-0eac96b831f3' = 'Jupiter Surface Management Engine (ME)'

        # Lynx
        'D3196CA8-D8DC-476B-A4DE-CAA642FEA0EC' = 'Lynx UEFI (Production)'
        'A1575CB8-5184-49AB-A932-9C2146B68DED' = 'Lynx UEFI (Unfused)'
        'E359E1E1-F6CE-457A-A8C7-B296F2A8E061' = 'Lynx Touch ??? SAM'
        '3378D499-69AF-4862-A001-5189F68C617E' = 'Lynx ME'

        #Cardinal
        '0603709B-92E8-4E49-8ED2-F065E2AD826B' = 'Cardinal UEFI (Production) [KBL]'
        '43D602C2-5B9C-447C-A5AB-BFCAEBFC33A6' = 'Cardinal UEFI (Unfused) [KBL]'
        'AAD0CDD3-D9BA-4A50-A4B6-EEB62BD2AF69' = 'Cardinal Touch & TAM'
        'B652EEC4-A36B-4AAD-BA73-DDFBA8A9D234' = 'Cardinal EC'
        '2B35D785-B7EC-49CC-9353-1919F5C1EC7B' = 'Cardinal ME (Pre-KBL)'
        '8BAC16B8-E8CF-41D3-A17D-AD1D18FE984F' = 'Cardinal ME'
        '88444650-38D0-4532-8B1B-609DD7184F8E' = 'Cardinal TPM (Fallback)'
        'E6D6E367-209F-42CF-9739-7F76C7660A89' = 'Cardinal TPM (x.x.x.0)'
        'DE944F55-25BB-4AF5-AC46-2C9F1BF59D97' = 'Cardinal TPM (x.x.x.2)'

        # Hera/Vela
        '0FC24D6E-E5A4-4297-8C6C-57D9873BBCFB' = 'Hera/Vela UEFI (Production) [KBL]'
        '6AB7AF37-D13A-4823-AEF9-A35E9F25D01A' = 'Hera/Vela UEFI (Unfused) [KBL]'
        '40DFC8A4-4CE6-4D30-A3AA-7B51B297E21C' = 'UEFI - Hera'
        '1948245C-CE4C-414C-9830-20C366A45628' = 'Touch - Hera/Vela'
        'F47FD839-8282-E21C-AB1C-ADF971F1B07C' = 'Touch - Hera'
        '22774A20-E21C-466B-905C-3583D74E873F' = 'EC - Hera'
        'ECD2803A-3501-4CBA-E21C-F6BB1B34AA20' = 'SAM - Hera'
        '5D5FDE19-96EF-4C58-B19F-9DEFBDE7DA75' = 'Hera/Vela ME [Old]'
        '9725E8BF-3DAA-4661-8AA7-B1C4A80573A4' = 'Hera/Vela ME [Pre-KBL]'
        '5E4A8510-E949-4789-A1BB-61712A3C2AF0' = 'Hera/Vela ME [KBL]'
        '10DEDADC-31C4-497A-858A-9B74FFEDE705' = 'Hera/Vela TPM (Fallback)'
        'A7A9832A-E3F2-43B6-ACFC-CA08C38583B8' = 'Hera/Vela TPM (x.x.x.0)'
        'BB5D5498-5BC2-4DB7-BE46-2241083EB8AE' = 'Hera/Vela TPM (x.x.x.2)'

        # Peregrine 
        '137F5D0A-B53B-45B3-AA77-8E6671ACE16B' = 'Peregrine UEFI (Production) [KBL]'
        '3F5EB8EC-127E-4460-B3C4-9ED310CC84DE' = 'Peregrine UEFI (Unfused) [KBL]'
        '28D00F7A-9D01-4C63-8AE3-E435BA6C34CD' = 'Peregrine Touch (Original)'
        '2ACC0EF7-426F-435F-8AD4-7B17D303295B' = 'Peregrine Touch (Pulsar)'
        '1122D5A7-4988-446B-85A8-25B66186A260' = 'Peregrine EC'
        'B0EA81E9-3290-4E17-A25C-64FA19EA2D19' = 'Peregrine EC'
        '0774D3E4-984D-41AE-BEB5-443FA7281511' = 'Peregrine SAM'
        '17A432A7-3E01-44BC-93F1-C229A795E969' = 'Peregrine ME [Old]'
        'E18F18D7-4991-482E-BBF0-B1DA8555BA0B' = 'Peregrine ME [Pre-KBL]'
        '118E0D76-770B-4AF6-A25F-9AC26AC6BACA' = 'Peregrine ME [KBL]'
        'EDAA0B41-158B-447C-BF96-AF9837A49AD6' = 'Peregrine TPM (Fallback)'
        '3DE2BFBD-4A47-4567-87B6-5926D1F73C02' = 'Peregrine TPM (x.x.x.0)'
        'C1FCB873-B084-4400-8C5B-B59B05B6D3AB' = 'Peregrine TPM (x.x.x.2)'

        # Nyx (RTM/WU)
        '5A2D987B-CB39-42FE-A4CF-D5D0ABAE3A08' = 'UEFI - Nyx'
        '512B1F42-CCD2-403B-8118-2F54353A1226' = 'SAM - Nyx'
        '52D9DA80-3D55-47E4-A9ED-D538A9B88146' = 'EC - Nyx (pre-BPM)'
        '1004B6B0-10AA-40B7-B155-C92A60BB0E71' = 'EC - Nyx (with Battery Protection Mode)'
        '8F3778C9-DFA1-4BA7-8113-BB481FB972B1' = 'Touch (23B and later) - Nyx'

        # Nyx (Pre-RTM)
        '742cc1d9-9ed1-4e6a-b10f-0f93306a3def' = 'UEFI - Nyx (Pre-RTM)'
        '44e2ee21-fd9b-4252-9655-3f3bb635a111' = 'SAM - Nyx (Pre-RTM)'
        'e83ab77c-8445-43b8-9fb8-e96b1f1b6b51' = 'EC - Nyx (Pre-RTM)'
        'E5FFF56F-D160-4365-9E21-22B06F6746DD' = 'Touch (19B and earlier) - Nyx'

        # Nyx (Accessories)
        '7769da36-18b7-4e06-825c-068380dac6b9' = 'Accessories - Nyx'
        '3a9c934b-d52f-4029-ae50-60e155d04b87' = 'SL Dock - Nyx'

        # Themis
        'C2CA803D-1693-4A05-8511-B8DD3EAF369D' = 'UEFI - Themis'
        '8EBE2064-9D13-41B3-A6C4-FB07465BA73D' = 'SAM - Themis'
        'F68B7F80-C568-476B-A823-81A6F9AF1699' = 'Touch - Themis'

        # Common across multiple products (Athena, Nyx)
        'd2e0b9c9-9860-42cf-b360-f906d5e0077a' = 'Surface Firmware Common Settings'

        # Athena
        '182cdca6-6202-4735-88f2-9394e77b901c' = 'UEFI - Athena'
        '9b037dbb-d33a-4727-afe2-eedce68f8653' = 'SAM - Athena'
        '1693d967-151f-443e-afe8-3eb63d5a236a' = 'EC - Athena'
        '2ccf5296-296d-43e1-ba6a-b1ab33500e8c' = 'PEN - Athena'

        # GT v1
        '88f4e422-caa7-4206-86a3-6640dbcbxxxx' = 'OTID Accessory - GT'
        'f1b313d2-5b76-4be6-8c35-5c077fcda117' = 'UEFI - GT'
        '58428b3a-8aa3-46d9-8277-799d4167f7eb' = 'Touch - GT'
        '42b4e95b-df81-4fb7-9bda-e0cd95720000' = 'Touch Config - GT'
        '31a00dc1-64d3-490c-b20e-8e365fc54bae' = 'SAM - GT'
        
        # GTX v1
        'cdc18fe8-45c4-4a5a-9660-5bd5fbd5ce1c' = 'UEFI - GTX v1'
        '36a5406e-853a-448d-b3d3-8f8acdf4a691' = 'Touch - GTX v1'
        '7339a57c-8ec8-4cc9-8e45-fc0ed1018e49' = 'Touch Config - GTX v1'
        'eed65e28-d96d-4133-9aaa-e6a513bf04c8' = 'SAM - GTX v1'
        'a70a7f0e-65ee-49cd-ad90-cd3b9ec9fa14' = 'Pen Digitizer - GTX v1'
        '0a3b0009-9ee3-444f-b149-051ad884af91' = 'EC - GTX v1'

        #Iris
        'A3339C74-B129-4611-8C3C-AEF841A49B53' = 'UEFI - Iris'
        '7D0F613D-595C-4161-BAF3-C0609EAF0294' = 'Touch - Iris EV1'
        '53B2803C-1BD6-470E-85A7-765E903ADDA2' = 'Touch - Iris'
        '38298766-e6cd-4136-afac-861ed93de9a2' = 'Sensor Hub - Iris'
    }

    $fwName = $fwGuidLookup."$fwGUID"

    if ([string]::IsNullOrEmpty($fwname))
    {
        $fwName = "Unrecognized FW Type: $fwGUID"        
    }

    return $fwName
}

function Get-EsrtValues 
{

    param(
        # This parameter will output the results as a hash table. This is good for when you need to use the rusults in a script.
        [switch] $useHashTable
    )


    # Global
    <#
    BIT0 – BIT9     MTE 0-255/Customer256-510/Development 512-1023  10 bits
    BIT10 – BIT14   Day 1 – 31  5 bits
    BIT15 – BIT18   Month 1 – 12    4 bits
    BIT19 – BIT21   Year offset 0 – 7 (takes us to 2021)    3 bits
    BIT22 – BIT25   Milestone/POC/EV1/EV2/EV3/DV/PV 4 bits
    BIT26 – BIT31   Product specific  6 bits
    #>

    $NumBits_Product      = 6
    $NumBits_MileStone    = 4
    $NumBits_Year         = 3
    $NumBits_Month        = 4
    $NumBits_Day          = 5
    $NumBits_Type         = 10

    $NumBits_www          = $NumBits_Product + $NumBits_MileStone
    $NumBits_xxx          = $NumBits_Year + $NumBits_Month + $NumBits_Day
    $NumBits_yyy          = $NumBits_Type

    $fwTypeLookup = @{
    0 = 'Unknown'
    1 = 'System firmware'
    2 = 'Device firmware'
    3 = 'UEFI driver'
}

    $fwAttemptStatusLookup = @{
    0 = 'Success'
    1 = 'Unsuccessful'
    2 = 'Insufficient resources'
    3 = 'Incorrect version'
    4 = 'Invalid image format'
    5 = 'Authentication error'
    6 = 'Power event - AC not connected'
    7 = 'Power event - Insufficient battery'
}


    # =====================================
    # Start Here
    #

    $resultArray = @()
    $resultHash = [ordered] @{}

    $esrtPath = 'HKLM:\HARDWARE\UEFI\ESRT'
    $esrtKeys = Get-ChildItem -Path $esrtPath

    ForEach ($key in $esrtKeys)
    {
        $keyPath = Split-Path -Parent $key.Name
        $keyName = Split-Path -Leaf $key.Name

        $props = Get-ItemProperty -LiteralPath $(Join-Path -Path $esrtPath -ChildPath $keyName)

        $lowestSupportedVersion_Bin = $props.LowestSupportedVersion
        $lastAttemptVersion_Bin     = $props.LastAttemptVersion
        $currVersion_Bin            = $props.Version

        $currVersion_Str            = Convert-Int32HexToVersionString -HexNumber $( $currVersion_Bin )
        $lastAttemptVersion_Str     = Convert-Int32HexToVersionString -HexNumber $( $lastAttemptVersion_Bin )
        $lowestSupportedVersion_Str = Convert-Int32HexToVersionString -HexNumber $( $lowestSupportedVersion_Bin )

        $lowestSupportedVersion_Bin = "0x{0}" -f $lowestSupportedVersion_Bin
        $lastAttemptVersion_Bin     = "0x{0}" -f $lastAttemptVersion_Bin
        $currVersion_Bin            = "0x{0}" -f $currVersion_Bin

        $type_Int = $props.Type
        $type_Str = $fwTypeLookup.$type_Int

        $lastAttemptStatus_Int = $props.LastAttemptStatus
        $lastAttemptStatus_Str = $fwAttemptStatusLookup.$lastAttemptStatus_Int

   
        $fwName_Guid = $keyName
        $fwName_Str = $( Get-FirmwareName -fwGUID $keyName )


        $returnProperties = [ordered] @{
            'FirmwareName_GUID' = $fwName_Guid
            'FirmwareName_String' = $fwName_Str

            "FirmwareType_Int" = $type_Int
            "FirmwareType_String" = $type_Str

            "LastInstallResult_Int" = $lastAttemptStatus_Int
            "LastInstallResult_String" = $lastAttemptStatus_Str

            "InstalledVersion_Binary" = $currVersion_Bin
            "InstalledVersion_VerStr" = $currVersion_Str

            "LastAttemptedVersion_Binary" = $lastAttemptVersion_Bin
            "LastAttemptedVersion_VerStr" = $lastAttemptVersion_Str

            "LowestSupportedVersion_Binary" = $lowestSupportedVersion_Bin
            "LowestSupportedVersion_VerStr" = $lowestSupportedVersion_Str
        }
    
        $objProperties = New-Object -TypeName psobject -Property $returnProperties
        $resultArray += $objProperties
        $resultHash.Add($fwName_Guid, $objProperties)
    }

    if ($useHashTable) {
        return $resultHash    # Easier to read for scripts.
    }
    else {
        return $resultArray    # Easier to read for humans.
    }
}
