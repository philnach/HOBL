Param(
    [int] $Delay       = 0,
    [int] $ScreenIndex = 0
)

$exePath = Join-Path $PSScriptRoot "InputInject.exe"
$json    = "[{'cmd':'windowmove','delay':['$Delay'],'direction':'$ScreenIndex'}]"

if (-not (Test-Path $exePath)) {
    Write-Error "Cannot find executable at '$exePath'"
    exit 1
}

# Launch as hidden
Start-Process -FilePath $exePath  `
              -ArgumentList $json `
              -WindowStyle Hidden `
              -WorkingDirectory $PSScriptRoot
