$taskName = "LucaSuperAgentBot"
$taskDescription = "Luca Super Agent Telegram Bot - Auto Start on Login"
$pythonExe = "C:\Users\sunjo\AppData\Local\Programs\Python\Python313\pythonw.exe"
$watchdogScript = "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\luca_watchdog.py"
$workingDir = "c:\Users\sunjo\Desktop\luca 연구자동화에이전트"

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$watchdogScript`"" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit 0

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $taskDescription -User $env:USERNAME -Force

Write-Host "Task registered successfully."
