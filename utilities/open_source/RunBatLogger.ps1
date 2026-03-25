param(
	[string]$o 
)

"Date/Time, SAM FCC, SAM BatVoltage, SAM BatAvgCurrent, SAM RSoC, OS RSoC, State#, State Explanation`n"| Out-File -FilePath $o -Encoding Ascii -NoNewline


while (1){
	$TimeNow = Get-Date -Format "MM/dd/yyyy HH:mm:ss"
	# $SmonFCC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryfcc
	# $SmonBatVoltage = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryvoltage
	# $SmonBatAvgCurrent = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryavgcurrent
	# $SmonRSOC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryrsoc
	$OSRSOC = (Get-WmiObject win32_battery).estimatedChargeRemaining
	$Bstatus = (Get-WmiObject -Class Win32_Battery).BatteryStatus

	if (Test-Path "C:\Tools\SMonitor\SMonitorUAP.exe") 
	{
		$SmonFCC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryfcc
		$SmonBatVoltage = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryvoltage
		$SmonBatAvgCurrent = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryavgcurrent
		$SmonRSOC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitorUAP.exe /batteryrsoc
	} 
	else 
	{
		$SmonFCC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitor.exe /batteryfcc
		$SmonBatVoltage = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitor.exe /batteryvoltage
		$SmonBatAvgCurrent = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitor.exe /batteryavgcurrent
		$SmonRSOC = C:\Users\sfudally\Desktop\Tools\SMonitor\SMonitor.exe /batteryrsoc
	}

	$SmonFCC = [System.Convert]::ToString($SmonFCC.split("  ")[2], 10) 
	$SmonBatVoltage = [System.Convert]::ToString($SmonBatVoltage.split("  ")[2], 10) 
	$SmonBatAvgCurrent = [int32]$SmonBatAvgCurrent.split("  ")[2] 
	$SmonRSOC = [System.Convert]::ToString($SmonRSOC.split("  ")[2], 10) 

	"$TimeNow," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$SmonFCC," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$SmonBatVoltage," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$SmonBatAvgCurrent," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$SmonRSOC," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$OSRSOC," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline
	"$Bstatus," | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline

	if($Bstatus) {
		switch ($Bstatus)
		{
			1 { "Battery is discharging`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			2 { "PSU is connected`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			3 { "Fully Charged`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			4 { "Low`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			5 { "Critical`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			6 { "Charging`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			7 { "Charging and High`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			8 { "Charging and Low`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			9 { "Charging and Critical`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			10 { "Unknown State`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
			11 { "Partially Charged`n"  | Out-File -FilePath $o -Append -Encoding Ascii -NoNewline}
		}
	}

	Start-Sleep -Seconds 60
}