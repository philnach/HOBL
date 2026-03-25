#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XAttribute {
<#
.SYNOPSIS
    Creates a new XAttribute node

.PARAMETER Name
    The name of the attribute

.PARAMETER Content
    The value of the attribute

.EXAMPLE
    New-XElement "SomeElement" {
        New-XAttribute "someSwitch" "false"
    }
#>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [System.Xml.Linq.XName] $Name,

        [Parameter(Mandatory=$false, Position=1)]
        [string] $Content
    )

    New-Object System.Xml.Linq.XAttribute($Name, $Content)
}