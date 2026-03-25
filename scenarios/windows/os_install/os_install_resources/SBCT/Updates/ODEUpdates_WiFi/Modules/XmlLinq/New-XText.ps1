#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XText {
<#
.SYNOPSIS
    Creates a new XText node

.PARAMETER Content
    Value to assign to the Text node

.EXAMPLE
    New-XElement "Data" {
        New-XText {
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

    $Content -join "`r`n" -as [System.Xml.Linq.XText]
}