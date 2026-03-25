#-------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
#-------------------------------------------------------------------------------

filter ConvertTo-XObject {
<#
.SYNOPSIS
    Converts input object to XObject

.EXAMPLE
    "Some Text" | ConvertTo-XObject
#>

    foreach ($Private:inputObject in $_) {
        if ($inputObject -is [string]) {
            XText $inputObject
        }
        elseif ($inputObject -is [scriptblock]) {
            &$inputObject
        }
        elseif (($inputObject -is [System.Xml.Linq.XObject]) -or 
                ($inputObject -is [System.Xml.Linq.XDeclaration])) {
            $inputObject
        }
        else {
            throw New-Object System.ArgumentException('Unsupported type of child object in content model')
        }
    }
}