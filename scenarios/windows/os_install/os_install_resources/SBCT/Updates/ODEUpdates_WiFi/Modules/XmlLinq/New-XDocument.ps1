#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XDocument {
<#
.SYNOPSIS
    Creates a new XDocument

.PARAMETER Content
    Content for XDocument

.EXAMPLE
    $doc = New-XDocument {
        New-XElement "SomeElement" {
            New-XAttribute "someFlag" "false"
        }
    }
#>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [object[]] $Content
    )

    [object[]] $xobjects = $Content | ConvertTo-XObject
    $declaration = $xobjects | Where-Object {$_ -is [System.Xml.Linq.XDeclaration]}

    if ($declaration) {
        [System.Xml.Linq.XObject[]] $xobjects = $xobjects | Where-Object {$_ -isnot [System.Xml.Linq.XDeclaration]}
        $xdoc = New-Object System.Xml.Linq.XDocument($declaration, $xobjects)
    }
    else {
        $xdoc = New-Object System.Xml.Linq.XDocument($xobjects)
    }

    $xdoc
}