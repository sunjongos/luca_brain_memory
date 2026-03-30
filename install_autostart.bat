@echo off
:: Luca Super Agent Bot — Windows Task Scheduler 자동 시작 등록
:: 관리자 권한으로 실행하세요!

SET SCRIPT_DIR=%~dp0
SET PYTHON=pythonw
SET BOT_SCRIPT=%SCRIPT_DIR%luca_watchdog.py
SET TASK_NAME=LucaSuperAgentBot

echo.
echo ============================================
echo  Luca Super Agent Bot 자동 시작 등록
echo ============================================
echo.

REM 기존 태스크 삭제 (있을 경우)
schtasks /delete /tn "%TASK_NAME%" /f 2>nul
echo [1] 기존 태스크 초기화 완료

REM Task Scheduler에 등록 (로그온 시)
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%PYTHON%\" \"%BOT_SCRIPT%\"" ^
  /sc onlogon ^
  /ru "%USERNAME%" ^
  /f ^
  /rl LIMITED

IF %ERRORLEVEL% EQU 0 (
    echo [2] Task Scheduler 등록 성공!
    echo     태스크명: %TASK_NAME%
    echo     조건: 로그온 시 자동 실행 (30초 지연)
) ELSE (
    echo [!] Task Scheduler 등록 실패. 관리자 권한으로 다시 실행하세요.
)

echo.
echo [3] 지금 바로 봇 시작...
start "Luca Bot" /min %PYTHON% "%BOT_SCRIPT%"
echo     봇이 백그라운드에서 실행 중입니다!
echo.
echo ============================================
echo  설치 완료! 컴퓨터 재시작 후에도 자동 실행됩니다.
echo ============================================
pause
