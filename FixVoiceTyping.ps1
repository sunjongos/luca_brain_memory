Stop-Process -Name "TextInputHost" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ctfmon" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Packages\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\LocalState\*" -Recurse -Force -ErrorAction SilentlyContinue
Get-Service TabletInputService -ErrorAction SilentlyContinue | Restart-Service -Force
Start-Process "ctfmon.exe"
