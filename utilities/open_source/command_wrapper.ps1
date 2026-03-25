$timeout = 3600  # 1 hr timeout in case test is terminated or killed and can't gracefully shut down.
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Args[0]
$psi.Arguments = $Args[1]
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true

$p = [System.Diagnostics.Process]::Start($psi)

$time_count = 0
$file = $Args[2]
Remove-Item $file -Force -ErrorAction SilentlyContinue
while(!(Test-Path $file)) {    
    Start-Sleep -s 1
    $time_count += 1
    if ($time_count -gt $timeout) {
        break
    }   
}  

# Inject key to quit (usually 'q')
$stop_key = $Args[3]
if ($stop_key -eq "kill") {
    $p.kill()
}
else {
    $p.StandardInput.WriteLine($stop_key)
}

# Kill in 30s just in case graceful close didn't work
Start-Sleep -s 30
if (!$p.HasExited) {
    $p.kill()
}