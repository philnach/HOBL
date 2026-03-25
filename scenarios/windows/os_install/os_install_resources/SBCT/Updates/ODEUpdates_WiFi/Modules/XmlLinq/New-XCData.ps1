#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XCData {
<#
.SYNOPSIS
    Creates a new XCData node

.PARAMETER Content
    Value to assign to the CData node

.EXAMPLE
    New-XElement "Data" {
        New-XCData {
            "Line 1"
            "Line 2"
            "Line 3"
        }
    }
#>
    param(
        [Parameter(Mandatory=$false, Position=0)]
        [string[]] $Content
    )

    $Content -join "`r`n" -as [System.Xml.Linq.XCData]
}