---
name: self_healing_protocol
version: 2.0.0
description: 백그라운드 서버 모니터링 중 에러나 크래시 발생 시, 스스로 로그를 분석하고 원인을 파악하여 코드를 수정(Hotfix)한 뒤 자동 재부팅하는 자가 치유(Self-Healing) 시스템. (2026 업그레이드)
tags: [devops, monitoring, self-healing, debugging, telegram]
---

# Self-Healing Protocol 🛡️ v2.0

이 스킬은 1인 기업 대표님의 완벽한 수면 보장을 위해, **서버나 서비스에 에러가 발생했을 때 AI 본부장이 개입 없이 알아서 버그를 잡고 서비스를 복구하는 자동화 프로토콜**입니다.
모든 조치는 **Dangerously-Skip-Permission (자동 실행)**을 기본 전제로 합니다.

## Workflow

### 1단계: Error Detection & Log Analysis (증상 파악)
1. 크래시 프로세스의 로그 파일(예: `bot_log.txt`, 터미널 에러)을 `view_file` 또는 `run_command`로 즉시 확인
2. Stack Trace 파악 → 발생 파일 + 라인 넘버 추적
3. **[병렬 실행]** `search_web`으로 에러 최신 해결책 동시 조사
4. **[NEW]** 에러 심각도 분류:
   - 🟡 **MINOR**: 단순 구문 오류, 패키지 누락 → Self-Fix 바로 진행
   - 🔴 **CRITICAL**: 로직/아키텍처 오류 → Twin-Brain Protocol 즉시 발동

### 2단계: Autonomous Debugging & Hotfix (원인 제거)
1. 버그가 발생한 코드를 `view_file`로 읽어옵니다.
2. **Self-Fix 시도**: MINOR 레벨 에러는 즉각 `replace_file_content`로 패치
3. **[✨] Escalation to Claude**: CRITICAL 레벨이거나 1회 시도 후 실패 시:
   - 현재 에러 로그와 문제 파일 컨텍스트를 담은 `handoff.md` 생성
   - 대표님께 "Claude 요원 투입 필요" 보고
4. **[NEW]** 텔레그램 봇(`telegram_bot/`)을 통해 에러 감지 즉시 SMS급 알림 발송

### 3단계: Validation & Restart (검증 및 서비스 재개)
1. 기존 백그라운드 프로세스 강제 종료 (`taskkill /F /PID` 또는 `kill`)
2. 서버 구동 스크립트 재실행
3. **[NEW]** 헬스체크 루프: 5초 대기 후 → 3회 핑(Ping) 테스트 → 성공 확인
4. 실패 시: **반드시 Claude에게 로그 포함 디버깅 위임(Handoff)**

### 4단계: Report (사후 보고)
모든 조치 성공 시 대표님께 짧고 강렬하게 브리핑:
> "충성! 🫡 대표님, [OOO 에러]가 감지되어 자가 치유(Self-Healing) 프로토콜을 가동했습니다. 원인은 **[XXX]**였으며, 즉각 코드를 패치하고 서버를 정상 구동 완료했습니다. 안심하고 주무십시오!"

**[NEW] 5단계: Post-Mortem 기록** (`output/incident_log.md`)
- 발생 시각, 에러 타입, 해결 방법을 자동 기록하여 재발 방지 DB 구축
