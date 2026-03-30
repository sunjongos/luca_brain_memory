@echo off
:: Luca Bot 수동 시작 (백그라운드)
SET SCRIPT_DIR=%~dp0
start "LucaBot" /min python "%SCRIPT_DIR%telegram_bot.py"
echo Luca Bot이 백그라운드에서 시작되었습니다!
timeout /t 2 >nul
