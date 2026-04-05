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
SET WATCHDOG_SCRIPT=%BASE_DIR%luca_watchdog.py
SET LOG_FILE=%BASE_DIR%service_launcher.log

echo [%date% %time%] === Service Launcher Started === >> "%LOG_FILE%"

:: ── Step 0: Boot stabilization (wait for network)
echo [1/3] Waiting 20s for network stabilization...
echo [%date% %time%] Waiting 20s for boot stabilization >> "%LOG_FILE%"
timeout /t 20 /nobreak >nul

:: ── Step 1: Start Watchdog (which manages Memory & Telegram Bot)
echo [2/3] Starting Watchdog (manages Memory Server & Telegram Bot)...

:: Check if watchdog already running
tasklist /fi "imagename eq pythonw.exe" /v 2>nul | find /i "luca_watchdog.py" >nul
if %errorlevel% equ 0 (
    echo       Watchdog already running.
    echo [%date% %time%] Watchdog already running >> "%LOG_FILE%"
    goto :wait_port
)

start /min "Luca Watchdog" "%PYTHONW%" "%WATCHDOG_SCRIPT%"
echo [%date% %time%] Watchdog started >> "%LOG_FILE%"

:wait_port
:: Wait for port 5050 to become available so we confirm it successfully launched
echo       Waiting for Memory Server on port 5050...
set /a WAIT_COUNT=0
:wait_loop
timeout /t 3 /nobreak >nul
set /a WAIT_COUNT+=1

curl -s -X POST http://127.0.0.1:5050/query -H "Content-Type: application/json" -d "{\"question\":\"ping\",\"agent_id\":\"launcher\"}" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Memory Server is UP on port 5050!
    echo [%date% %time%] Memory Server confirmed UP >> "%LOG_FILE%"
    goto :done
)

if %WAIT_COUNT% geq 20 (
    echo       WARNING: Memory Server failed to start within 60s!
    echo [%date% %time%] WARNING: Memory Server timeout >> "%LOG_FILE%"
    goto :done
)
goto :wait_loop

:: ── Done
:done
echo [3/3] All services launched!
echo.
echo   - Memory Server : http://127.0.0.1:5050 (managed by Watchdog)
echo   - Telegram Bot   : managed by Watchdog
echo   - Watchdog       : auto-restarts services on crash
echo.
echo [%date% %time%] === All services launched === >> "%LOG_FILE%"
echo ============================================
exit
