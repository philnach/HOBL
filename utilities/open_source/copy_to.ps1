param(
	[string]$Address = '127.0.0.1',
	[string]$source = "",
	[string]$dest = ""
)

#Push-Location -Path (Split-Path $MyInvocation.MyCommand.Path -Parent)
open-device $address

cmdd mkdir $dest
putd $source $dest

Close-Device
#Pop-Location
