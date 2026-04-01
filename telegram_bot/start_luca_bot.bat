@echo off
title Luca Telegram Bot v2.0
color 0A
echo.
echo ======================================
echo   Luca Bot v2.0 - OpenClaw Level
echo   Powered by Gemini 2.5 Pro
echo ======================================
echo.
cd /d "c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\telegram_bot"
:RESTART
echo [%date% %time%] Luca Bot 시작 중...
node index.js
echo.
echo [WARN] 봇이 종료됐습니다. 5초 후 자동 재시작...
timeout /t 5
goto RESTART
