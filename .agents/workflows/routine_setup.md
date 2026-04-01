---
description: 컴퓨터 루틴 세팅 (기본 메모리 및 텔레그램 봇 시작)
---

대표님이 "컴퓨터 루틴 세팅해줘"라고 요청하실 때 구동해야 하는 필수 백그라운드 서버와 텔레그램 봇 모듈을 실행하는 워크플로우입니다.

// turbo-all
1. 작업 환경 최신화 (git pull) 실행
```bash
cd "c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트"
git pull
```

2. luca_brain_memory (4단 메모리) 백그라운드 자동 실행
```bash
cd "c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트"
wscript "start_memory_server.vbs"
```

3. OpenClaw / Luca 텔레그램 봇 실행
```bash
cd "c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\telegram_bot"
Start-Process -FilePath "start_luca_bot.bat"
```
