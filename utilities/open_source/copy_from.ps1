param(
	[string]$Address = '127.0.0.1',
	[string]$source = "",
	[string]$dest = ""
)

#Push-Location -Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent
open-device $address
	
getd $source $dest

Close-Device
#Pop-Location
