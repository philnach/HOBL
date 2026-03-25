
param(
    $pwrStripType = "NONE",
    $pwrStripIP = "0.0.0.0",
    $pwrStripOutlet = "0"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()

$key = $true
$Form0_Shown={
    
    while($True)
    {
        $today = (Get-Date).ToString("yyyy'-'MM'-'dd' 'HH':'mm':'ss")
        $Bstatus = (Get-WmiObject -Class Win32_Battery -ea 0).BatteryStatus

        if($Bstatus) {
            switch ($Bstatus)
            {
            1 { $Form0.BackColor = "Red"     } # Battery is discharging
            2 { $Form0.BackColor = "Lime"    } # The system has access to AC so no battery is being discharged. However, the battery is not necessarily charging."
            3 { $Form0.BackColor = "White"   } # Fully Charged
            4 { $Form0.BackColor = "Red"     } # Low
            5 { $Form0.BackColor = "Red"     } # Critical
            6 { $Form0.BackColor = "Lime"    } # Charging
            7 { $Form0.BackColor = "Lime"    } # Charging and High
            8 { $Form0.BackColor = "Lime"    } # Charging and Low
            9 { $Form0.BackColor = "Lime"    } # Charging and Critical
            10 { $Form0.BackColor = "Orange" } # Unknown State
            11 { $Form0.BackColor = "Red"    } # Partially Charged         
    
            }
        }
        
        $totalSoC= [Math]::round(([System.Windows.Forms.SystemInformation]::PowerStatus.BatteryLifePercent) * 100, 2)
        $lblMessage.Text = "$today  Battery: $totalSoC%`n$pwrStripType, $pwrStripIP, Outlet = $pwrStripOutlet"
        start-sleep 1
    }        
        

    $Form0.Close()    
}

#Form0
#
$Form0 = New-Object System.Windows.Forms.Form
$Form0.Text = "Charge_Status"
$Form0.MaximizeBox = $False
$Form0.MinimizeBox = $False
$Form0.Add_Shown($Form0_Shown)
$Form0.BackColor = "White"

$Form0.ClientSize = New-Object System.Drawing.Size(700, 100)
# Font Type
$font = New-Object System.Drawing.Font("Courier New",20,[System.Drawing.FontStyle]::Bold)
$form0.Font = $font


#
#lblMessage
#
$lblMessage = New-Object System.Windows.Forms.Label
$lblMessage.Text = ""
$lblMessage.Size = New-Object System.Drawing.Size(700, 100)
$lblMessage.Location = New-Object System.Drawing.Point(23, 20)
$Form0.Controls.Add($lblMessage)

return $Form0.ShowDialog()
