---
name: 웹 모니터링 스킬
description: 키워드 기반 뉴스 모니터링 및 웹사이트 변경 감지 스킬입니다.
---

# 🌐 웹 모니터링 스킬

키워드 뉴스 트래킹과 웹사이트 변경 감지를 자동화합니다.

## 언제 사용하나
- "AI 관련 뉴스 모니터링해줘"
- 경쟁사 사이트 변경 감지
- 특정 키워드 일일 뉴스 수집

## 실행 방법

```powershell
# 키워드 뉴스 검색
python ".agent/skills/web_monitor/web_monitor.py" --keywords "AI 에이전트,Claude,GPT-5" --save

# 웹사이트 변경 감지
python ".agent/skills/web_monitor/web_monitor.py" --url "https://example.com"
```

## 출력 예시
```
🔍 검색 중: AI 에이전트
📰 [AI 에이전트]
   2026년 AI 에이전트 시장이 급성장...
   🔗 https://source1.com
```

결과는 `.agent/skills/web_monitor/monitor_data/` 폴더에 자동 저장됩니다.
