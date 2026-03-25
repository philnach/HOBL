#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XElement {
<#
.SYNOPSIS
    Creates a new XElement node

.PARAMETER Name
    The name of the element

.PARAMETER Content
    The content for the element

.EXAMPLE
    $doc = New-XDocument {
        New-XElement "SomeElement" {
            New-XAttribute "someSwitch" "false"
            New-XComment "Define Settings Here"        
            New-XElement "Setting" {
                New-XElement "KeepOn" "Keepin' On"
            }
        }
    }
#>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [System.Xml.Linq.XName] $Name,

        [Parameter(Mandatory=$false, Position=1)]
        [object[]] $Content
    )

    [System.Xml.Linq.XObject[]] $xobjects = $Content | ConvertTo-XObject
    New-Object System.Xml.Linq.XElement($Name, $xobjects)
}