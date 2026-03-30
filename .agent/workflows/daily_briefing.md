---
description: 매일 아침 Luca가 캘린더 일정 + 중요 메일 + 오늘의 AI 뉴스를 병렬로 수집하여 대표님께 통합 브리핑하는 워크플로우
---

# 📅 Daily Morning Briefing — Luca 일일 브리핑

대표님이 "오늘 브리핑 해줘" 또는 "굿모닝 루카" 라고 하면 즉시 실행합니다.

## Workflow Steps

### Step 1: 병렬 데이터 수집 (Multi-Agent Parallel Execution)

아래 3가지를 **동시에** 실행합니다 (`browser_subagent` + `run_command` 병렬):

// turbo
1. **캘린더 조회** (자동 처리)
```powershell
python ".agent/skills/google_workspace/get_calendar_events.py"
```

// turbo
2. **메일 조회** (자동 처리)
```powershell
python ".agent/skills/google_workspace/get_emails.py" --count 5 --unread
```

// turbo
3. **오늘의 AI/비즈니스 뉴스** (Perplexity 자동 검색)
```powershell
python ".agent/skills/perplexity/perplexity_search.py" "오늘 AI 비즈니스 주요 뉴스 2026년 2월" --model sonar
```

// turbo
4. **Luca 메모리 컨텍스트 로드** (자동 처리)
```powershell
python ".agent/skills/memory/memory_manager.py" summary
```

---

### Step 2: 통합 브리핑 작성

수집된 데이터를 종합하여 아래 형식으로 대표님께 브리핑합니다:

```
🌅 Good Morning, 대표님! Luca 일일 브리핑입니다 ✨

📅 오늘의 일정 (N개)
  [시간] — [일정명]
  ...

📬 읽지 않은 중요 메일 (N개)
  [발신자] — [제목]
  ...

📰 오늘의 AI/비즈니스 뉴스
  [핵심 뉴스 3줄 요약]

🧠 Luca 메모 (진행 중 프로젝트)
  [관련 기억 컨텍스트]

💡 오늘 Luca 추천 액션
  1. [추천 1]
  2. [추천 2]
```

---

### Step 3: Human-in-the-Loop 확인

브리핑 후 대표님께 확인:
> "대표님, 오늘 브리핑 완료입니다! 🫡 바로 특정 항목을 더 깊이 파볼까요?"
