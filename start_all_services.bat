@echo off
chcp 65001 >nul 2>&1
title Luca All Services Launcher

echo ============================================
echo  Luca All Services Launcher
echo  Memory Server (5050) + Telegram Bot + Watchdog
echo ============================================
echo.

SET BASE_DIR=%~dp0
SET PYTHON=C:\Users\sunjo\AppData\Local\Programs\Python\Python313\python.exe
SET PYTHONW=C:\Users\sunjo\AppData\Local\Programs\Python\Python313\pythonw.exe
SET MEMORY_DIR=%BASE_DIR%memory_layer
SET MEMORY_SCRIPT=%MEMORY_DIR%\memory_server.py
SET WATCHDOG_SCRIPT=%BASE_DIR%luca_watchdog.py
SET LOG_FILE=%BASE_DIR%service_launcher.log

echo [%date% %time%] === Service Launcher Started === >> "%LOG_FILE%"

:: ── Step 0: Boot stabilization (wait for network)
echo [1/4] Waiting 20s for network stabilization...
echo [%date% %time%] Waiting 20s for boot stabilization >> "%LOG_FILE%"
timeout /t 20 /nobreak >nul

:: ── Step 1: Start Memory Server (port 5050)
echo [2/4] Starting Memory Server (port 5050)...

:: Check if already running
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:5050/query 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo       Memory Server already running. Skipping.
    echo [%date% %time%] Memory Server already running >> "%LOG_FILE%"
    goto :start_watchdog
)

:: Launch memory server in background
start /min "Luca Memory Server" "%PYTHON%" "%MEMORY_SCRIPT%"
echo [%date% %time%] Memory Server process started >> "%LOG_FILE%"

:: Wait for port 5050 to become available (max 60s)
echo       Waiting for port 5050...
set /a WAIT_COUNT=0
:wait_loop
timeout /t 3 /nobreak >nul
set /a WAIT_COUNT+=1

curl -s -X POST http://127.0.0.1:5050/query -H "Content-Type: application/json" -d "{\"question\":\"ping\",\"agent_id\":\"launcher\"}" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Memory Server is UP on port 5050!
    echo [%date% %time%] Memory Server confirmed UP >> "%LOG_FILE%"
    goto :start_watchdog
)

if %WAIT_COUNT% geq 20 (
    echo       WARNING: Memory Server failed to start within 60s!
    echo [%date% %time%] WARNING: Memory Server timeout >> "%LOG_FILE%"
    goto :start_watchdog
)
goto :wait_loop

:: ── Step 2: Start Watchdog (which manages the Telegram Bot)
:start_watchdog
echo [3/4] Starting Watchdog (manages Telegram Bot)...

:: Check if watchdog/bot already running
tasklist /fi "imagename eq pythonw.exe" /v 2>nul | find /i "telegram_bot" >nul
if %errorlevel% equ 0 (
    echo       Telegram Bot already running. Skipping watchdog.
    echo [%date% %time%] Telegram Bot already running >> "%LOG_FILE%"
    goto :done
)

start /min "Luca Watchdog" "%PYTHONW%" "%WATCHDOG_SCRIPT%"
echo [%date% %time%] Watchdog started >> "%LOG_FILE%"

:: ── Done
:done
echo [4/4] All services launched!
echo.
echo   - Memory Server : http://127.0.0.1:5050
echo   - Telegram Bot   : managed by Watchdog
echo   - Watchdog       : auto-restart on bot crash
echo.
echo [%date% %time%] === All services launched === >> "%LOG_FILE%"
echo ============================================
exit
