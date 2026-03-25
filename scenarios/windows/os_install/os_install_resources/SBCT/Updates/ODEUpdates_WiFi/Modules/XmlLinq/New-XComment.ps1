#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XComment {
<#
.SYNOPSIS
    Creates a new XComment node

.PARAMETER Content
    Value to assign to the Comment node

.EXAMPLE
    New-XElement "Data" {
        New-XComment {
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

    $Content -join "`r`n" -as [System.Xml.Linq.XComment]
}