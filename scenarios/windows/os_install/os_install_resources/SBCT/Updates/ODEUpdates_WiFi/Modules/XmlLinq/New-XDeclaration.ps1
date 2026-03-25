#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

function New-XDeclaration {
<#
.SYNOPSIS
    Creates a new XDeclaration Node

.PARAMETER Encoding
    The encoding for the XML file

.PARAMETER Standalone
    Set when "standalone" document

.EXAMPLE
    $declaration = New-XDeclaration -Encoding utf-8
#>
    param(
        [ValidateSet('utf-8', 'iso-8859-1')]
        [string] $Encoding,
        [switch] $Standalone
    )

    New-Object System.Xml.Linq.XDeclaration('1.0', $Encoding, $(if ($Standalone) {'yes'} else {'no'}))
}