# $test_plan = "c:\hoblexe\testplans\toast_automation.ps1 -PhaseLocalPlayback -Scenario LVP -Loops 5"
write-host "Argument Count: $($Args.Length)"
write-host "Argument 0: " + $Args[0]
$task_name = $Args[0]
write-host "Argument 1: " + $Args[1]
$test_plan = $Args[1]
For ($x=2; $x -le $args.Length; $x++){
        $test_plan = $test_plan + " " + $Args[$x]
} 

write-host "task_name" $task_name
write-host "test_plan" $test_plan

# Specify the trigger settings
$Trigger= New-ScheduledTaskTrigger -AtLogOn
# Create Settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries
# Create action
$test_plan = "/C " + '"Powershell.exe "' + " " + $test_plan
write-host "Test_Plan: " $test_plan
$Action = New-ScheduledTaskAction -Execute cmd.exe -Argument $test_plan
# Test if scheduled task exists - if so delete it
if (Get-ScheduledTask -TaskName $task_name -EA 0){
    Unregister-ScheduledTask -TaskName $task_name -Confirm:$false
}
# Register the task
Register-ScheduledTask -TaskName $task_name -Trigger $Trigger -Action $Action -RunLevel Highest -Settings $settings -Force

