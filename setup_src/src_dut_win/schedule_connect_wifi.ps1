param(
    [string]$network=""
)
# Scheduled task to connect to wifi on logon.
$Action = New-ScheduledTaskAction -Execute "c:\hobl_bin\connect_wifi_task.cmd" -Argument "$network"
$Trigger = New-ScheduledTaskTrigger -Atlogon
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask ConnectWiFi -Action $Action -Trigger $Trigger -Settings $taskSettings -F