@echo off
cd /d "%~dp0"
:: 봇 프로세스가 이미 실행 중인지 확인
tasklist /fi "imagename eq python.exe" /v | find /i "telegram_bot.py" > nul
if errorlevel 1 (
    echo 시작: 텔레그램 봇 - Luca Super Agent - 을 백그라운드에서 가동합니다...
    start /min pythonw telegram_bot.py
) else (
    echo 이미 텔레그램 봇이 실행 중입니다.
)
exit
