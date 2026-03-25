param (
    [string]$Theme,
    [string]$Version,
    [string]$Archive,
    [string]$Excludes,
    [string]$RandPorts = 1, # If set to 1, the script will find available ports in the range.
    [string]$HttpPort,
    [string]$HttpsPort,
    [int]$StartPort = 6100, # Define the port range.  This range needs to have port-forwarding set up in the router.
    [int]$EndPort = 6199
)

$WorkingDir = "C:\web_replay\$Version"
$AppPath = "C:\web_replay\$Version\bin\web_replay.exe"

# Function to find an available port
function Get-AvailablePort {
    param (
        [int]$StartPort,
        [int]$EndPort
    )
    for ($Port = $StartPort; $Port -le $EndPort; $Port++) {
        if (-not (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue)) {
            return @{ Port = $Port; Listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $Port) }
        }
    }
    throw "No available ports found in the range $StartPort-$EndPort."
}

# Get available ports and reserve them for HTTP and HTTPS
if ($RandPorts -eq "1") {
    $Result = Get-AvailablePort -StartPort $StartPort -EndPort $EndPort
    $HttpPort = $Result.Port
    $HttpListener = $Result.Listener
    $HttpListener.Start()
    $Result = Get-AvailablePort -StartPort $StartPort -EndPort $EndPort
    $HttpsPort = $Result.Port
    $HttpsListener = $Result.Listener
    $HttpsListener.Start()
}

# Launch application with the reserved port
Start-Process -FilePath "$AppPath" -WorkingDirectory "$WorkingDir" -ArgumentList "replay --host=0.0.0.0 --http_port=$HttpPort --https_port=$HttpsPort --theme=$Theme --excludes_list=`"$Excludes`" --timeout_min=60 $Archive"

# Stop the listener to release the port for use by application
if ($RandPorts -eq "1") {
    $HttpListener.Stop()
    $HttpsListener.Stop()
}

# Return port number to caller
Write-Host "$HttpPort,$HttpsPort"
