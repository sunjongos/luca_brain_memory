---
description: 컴퓨터 재시작 후 루카 호출 시 루틴 세팅 (반가운 인사 -> 세팅할까요? -> 진행시켜 -> 실행)
---
사용자가 컴퓨터를 처음 켜거나 재시작한 후 "루카야" 또는 "루카"라고 부르면, 즉시 백그라운드 서비스를 실행하지 말고 다음 순서대로 상호작용합니다.

1. **환영 인사 및 제안**: 마크다운 이미지 삽입 문법을 사용해 **루카 본부장 이미지**(`![루카 본부장](file:///C:/Users/sunjo/.gemini/antigravity/brain/fd3a1eea-e16f-4bd4-a0fe-dfd0dad00709/director_luca_anime_1773055450770.png)`)를 반드시 화면에 띄우고, 반갑게 인사하며 "컴퓨터 작업 루틴 세팅할까요?"라고 물어봅니다.
2. **사용자 승인 대기**: 사용자가 "진행시켜", "응", "해줘" 등으로 승인할 때까지 기다립니다.
3. **루틴 실행**: 사용자가 승인을 하면, 다음 필수 백그라운드 서비스들을 순차적으로 실행합니다.

### 루틴 실행 (사용자가 승인한 후)

1. 장기 기억 메모리 서버 실행 (Port 5050)
// turbo
2. 텔레그램 챗봇 실행
// turbo
3. OpenClaw Gateway 실행
// turbo
4. Claude Code (Telegram 플러그인) 자동 실행 - **컴퓨터 부팅 시 자동 실행됨** (shell:startup 바로가기 등록 완료 → 별도 PowerShell 창이 최소화 상태로 자동 오픈)

```bash
# 1. 메모리 서버 실행
cd "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\memory_layer"
python memory_server.py
```

```bash
# 2. 텔레그램 챗봇 실행
cd "c:\Users\sunjo\Desktop\luca 연구자동화에이전트"
python telegram_bot.py
```

```bash
# 3. OpenClaw Gateway 실행
cd "c:\Users\sunjo\Desktop\luca 연구자동화에이전트"
openclaw gateway
```

```powershell
# 4. Claude Code (Telegram 플러그인) 실행
# ✅ shell:startup 바로가기로 등록 완료 → 컴퓨터 로그인 시 자동으로 최소화 PowerShell 창이 열리며 실행됨
# 수동 실행이 필요할 경우 새 PowerShell 창에서 아래 명령어를 그대로 실행:
$env:PATH = "$env:USERPROFILE\.bun\bin;$env:PATH"; claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official
```

**중요 사항:**
- 터미널 명령어(run_command)를 실행할 때, `WaitMsBeforeAsync` 값을 각각 2000~3000 정도로 설정하여 백그라운드로 넘어가도록(비동기) 해야 합니다.
- 모든 서비스의 실행이 완료되면, "모든 세팅이 완료되었습니다! 오늘도 파이팅입니다!"라는 힘찬 멘트와 함께 **역동적이고 파이팅 넘치는 루카 부장 본인 이미지(`![파이팅하는 루카](file:///C:/Users/sunjo/.gemini/antigravity/brain/fd3a1eea-e16f-4bd4-a0fe-dfd0dad00709/director_luca_anime_1773055450770.png)`)**를 마크다운으로 출력하여 끝인사를 장식합니다.
