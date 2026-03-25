
Param(
[string]$cmd_string = "command_string"
)

$Action = New-ScheduledTaskAction -Execute $cmd_string -Argument "8000 --SuppressUserWarning"
$Trigger = New-ScheduledTaskTrigger -Atlogon
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$Principal = New-ScheduledTaskPrincipal -UserId $env:username -RunLevel Highest
Register-ScheduledTask StartSimpleRemote -Action $Action -Trigger $Trigger -Principal $Principal -Settings $taskSettings -F
