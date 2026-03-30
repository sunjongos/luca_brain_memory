$WshShell = New-Object -ComObject WScript.Shell
$StartupPath = [Environment]::GetFolderPath('Startup')
$Shortcut = $WshShell.CreateShortcut("$StartupPath\Luca_Unified_Startup.lnk")
$Shortcut.TargetPath = "C:\WINDOWS\system32\wscript.exe"
$Shortcut.Arguments = "`"C:\Users\sunjo\Desktop\luca 연구자동화에이전트\start_unified_hidden.vbs`""
$Shortcut.WorkingDirectory = "C:\Users\sunjo\Desktop\luca 연구자동화에이전트"
$Shortcut.Description = "Luca Unified Startup"
$Shortcut.Save()
Write-Host "Shortcut created OK"
