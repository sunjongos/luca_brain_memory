@echo off
chcp 65001 >nul 2>&1
title Install MCP Dependencies

echo ============================================
echo   Luca Computer & Chrome MCP 의존성 설치
echo ============================================
echo.

SET PYTHON=C:\Users\sunjo\AppData\Local\Programs\Python\Python313\python.exe

echo [1/2] 필수 파이썬 패키지 설치... (pyautogui, mss, playwright, mcp)
"%PYTHON%" -m pip install -U pyautogui mss playwright mcp

echo [2/2] Playwright 브라우저 바이너리(Chromium) 설치...
"%PYTHON%" -m playwright install chromium

echo.
echo ============================================
echo   설치가 완료되었습니다!
echo   이제 클로드 코드(Claude Code) 또는 루카에서
echo   화면 캡처, 마우스 클릭, 크롬 제어가 가능합니다.
echo ============================================
pause
