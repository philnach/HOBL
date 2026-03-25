
param(
    [string]$form_text = "Default window",
    [string]$label_text = "",
    [string]$retry = "RETRY",
    [string]$ok = "OK"
    
)

[void][Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic')
[void][Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
[void][Reflection.Assembly]::LoadWithPartialName('System.Net.Mail')
[void][Reflection.Assembly]::LoadWithPartialName('Collections.Generic')

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = $form_text
$form.Size = New-Object System.Drawing.Size(550,250) # 550,250 - changes form size
$form.FormBorderStyle = 4
$form.StartPosition = 'CenterScreen'

# Add OK button
$okButton = New-Object System.Windows.Forms.Button
if (($retry -eq "RETRY") -or ($retry -eq "REMOTE")){
    $okButton.Location = New-Object System.Drawing.Point(120,150) #120,150
}
else{
    $okButton.Location = New-Object System.Drawing.Point(230,150) #230,150
}
$okButton.Size = New-Object System.Drawing.Size(75,25) # 75,25
$okButton.Font = New-Object System.Drawing.Font("Lucida Console",11,[System.Drawing.FontStyle]::Regular)
$okButton.Text = $ok
$okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
$form.AcceptButton = $okButton
$form.Controls.Add($okButton)

if (($retry -eq "RETRY") -or ($retry -eq "REMOTE")){
    # Add RETRY button
    $Button2 = New-Object System.Windows.Forms.Button
    $Button2.Location = New-Object System.Drawing.Point(350,150) # 350,150
    $Button2.Size = New-Object System.Drawing.Size(90,25) #90,25
    $Button2.Font = New-Object System.Drawing.Font("Lucida Console",11,[System.Drawing.FontStyle]::Regular)
    $Button2.Text = $retry
    $Button2.DialogResult = [System.Windows.Forms.DialogResult]::RETRY
    $form.AcceptButton = $Button2
    $form.Controls.Add($Button2)
}

# Add label
$label = New-Object System.Windows.Forms.Label
$label.Location = New-Object System.Drawing.Point(10,10) # 10,10
$label.Size = New-Object System.Drawing.Size(450,60) # 450,60
$label.Font = New-Object System.Drawing.Font("Lucida Console",11,[System.Drawing.FontStyle]::Regular)
$label.Text = $label_text
$form.Controls.Add($label)
$form.Topmost = $true

if ($retry -ne "RETRY" -and $retry -ne "End" -and $retry -ne "REMOTE" -and $ok -eq "OK")
{
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(45,110) #45,110
    $textBox.Size = New-Object System.Drawing.Size(450,60) #450,60
    $textBox.Font = New-Object System.Drawing.Font("Lucida Console",11,[System.Drawing.FontStyle]::Regular)
    $form.Controls.Add($textBox)
    $form.Add_Shown({$textBox.Select()})
}

$result = $form.ShowDialog()

if (($result -eq [System.Windows.Forms.DialogResult]::OK) -and ($ok -eq "OK"))
{
    $x = $textBox.Text
    #$x = "OK"
}
elseif ($result -eq [System.Windows.Forms.DialogResult]::OK){
    $x = $ok
}
else{
    $x = $retry
}

write-host($x)

