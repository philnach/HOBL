# we first get the computer name from the text file..

if (-not (test-path pcname.txt)) {
    return
}

$NewComputerName = Get-Content pcname.txt -first 1
if (($NewComputerName -eq $env:COMPUTERNAME) -or ($NewComputerName.Length -gt 15) -or ($NewComputerName.Length -lt 3)) {
    return
}

#rename PC
Rename-Computer -NewName $NewComputerName
Write-Host "New Computer name set, reboot required.\n"
Write-Host ""
Write-Host ""
Write-Host "DONE"
Start-Sleep 5
