$grandParent = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$rule = "python_embed ($grandParent)"
$program = Join-Path $grandParent "downloads\python_embed\python.exe"

netsh advfirewall firewall show rule name="$rule" | Out-Null

if ($LASTEXITCODE -eq 1) {
    $addArgs = "advfirewall firewall add rule name=`"$rule`" program=`"$program`""
    $addArgs += " dir=in action=allow enable=yes localport=any protocol=TCP profile=public,private,domain"

    Start-Process -FilePath "netsh" -ArgumentList "$addArgs" -Verb RunAs
}

exit 0
