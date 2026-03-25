#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

. $PSScriptRoot\ConvertTo-XObject.ps1
. $PSScriptRoot\New-XAttribute.ps1
. $PSScriptRoot\New-XCData.ps1
. $PSScriptRoot\New-XComment.ps1
. $PSScriptRoot\New-XDeclaration.ps1
. $PSScriptRoot\New-XDocument.ps1
. $PSScriptRoot\New-XElement.ps1
. $PSScriptRoot\New-XNamespace.ps1
. $PSScriptRoot\New-XText.ps1

New-Alias -Name 'XAttribute' -Value 'New-XAttribute'
New-Alias -Name 'XCData' -Value 'New-XCData'
New-Alias -Name 'XComment' -Value 'New-XComment'
New-Alias -Name 'XDeclaration' -Value 'New-XDeclaration'
New-Alias -Name 'XDocument' -Value 'New-XDocument'
New-Alias -Name 'XElement' -Value 'New-XElement'
New-Alias -Name 'XNamespace' -Value 'New-XNamespace'
New-Alias -Name 'XText' -Value 'New-XText'

Export-ModuleMember -Function @(
    'ConvertTo-XObject'
    'New-XAttribute', 
    'New-XCData', 
    'New-XComment', 
    'New-XDeclaration', 
    'New-XDocument', 
    'New-XElement', 
    'New-XNamespace',
    'New-XText'
) -Alias @(
    'XAttribute',
    'XCData',
    'XComment',
    'XDeclaration',
    'XDocument',
    'XElement',
    'XNamespace',
    'XText'
)