$timeout = 3600  # 1 hr timeout in case test is terminated or killed and can't gracefully shut down.
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "C:\Program Files\wireshark\dumpcap.exe"
$psi.Arguments = "-i 8 -p -w c:\temp\google_images.pcap"
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true

$p = [System.Diagnostics.Process]::Start($psi)

# $time_count = 0
# $file = $Args[2]
# Remove-Item $file -Force -ErrorAction SilentlyContinue
# while(!(Test-Path $file)) {    
#     Start-Sleep -s 1
#     $time_count += 1
#     if ($time_count -gt $timeout) {
#         break
#     }   
# }  

Start-Sleep -s 5

# Inject key to quit (usually 'q')
$key = $Args[3]
write-host "Sending $key"
$p.StandardInput.WriteLine($Args[3])
$p.kill()

# Kill in 30s just in case graceful close didn't work
# Start-Sleep -s 30
# if (!$p.HasExited) {
#     $p.kill()
# }