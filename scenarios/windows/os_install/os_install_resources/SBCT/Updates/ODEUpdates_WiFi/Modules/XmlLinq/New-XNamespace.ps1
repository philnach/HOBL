#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XNamespace {
<#
.SYNOPSIS
    Creates a new XNamespace node

.PARAMETER NamespaceUri
    Namespace URI

.EXAMPLE
    $Script:NS = New-XNamespace "http://www.w3.org/2001/XMLSchema"
    $doc = New-XDocument {
        New-XElement (NS + "SomeElement") {
            New-XAttribute "someFlag" "false"
        }
    }
#>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string] $NamespaceUri
    )

    $NamespaceUri -as [System.Xml.Linq.XNamespace]
}