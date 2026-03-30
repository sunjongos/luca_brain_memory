---
description: NotebookLM MCP + Chrome 자동화로 연구 기획, 웹/유튜브 소스 자동 수집, 노트북 생성, 딥 리서치, Google Docs 저장까지 원스톱 자동화 파이프라인
---

# 🔬 Deep Research — NotebookLM 완전 자동화 파이프라인

대표님이 아래 중 하나라도 말하면 이 워크플로우를 실행합니다:
- "~에 대해 연구해줘"
- "딥 리서치 해줘"
- "노트북 만들어줘 + 출처 붙여줘"

---

## Step 1: 연구 기획 (Luca 자동 수행)

대표님의 주제를 받아 즉시 아래를 수행합니다:
- 핵심 질문 5개로 분해
- 검색 키워드 10개 생성
- 필요한 소스 타입 판단 (웹/유튜브/뉴스/논문)
- Perplexity 모델 선택 (sonar-pro 기본)

Luca 보고 후 → 자동 진행 (컨펌 생략 가능)

---

// turbo
## Step 2: 웹 소스 자동 수집 (browser_subagent 병렬 실행)

**2-A. Perplexity 딥서치:**
```powershell
python ".agent/skills/perplexity/perplexity_search.py" "[주제]" --model sonar-pro
```

**2-B. Google 웹서핑 (browser_subagent):**
```
browser_subagent 태스크:
- https://www.google.com 에서 [키워드] 검색
- 상위 5개 URL 추출 + 제목 + 요약 수집
- 신뢰도 높은 출처만 필터링 (언론사/공식사이트 우선)
- 수집된 URL 목록 반환
```

---

// turbo
## Step 3: YouTube 소스 자동 검색 + 추출 (browser_subagent) ⭐

```
browser_subagent 태스크:
1. https://www.youtube.com/results?search_query=[키워드] 접속
2. 조회수 10만 이상 + 자막 있음 + 최근 2년 이내 필터
3. 전문가/공식 채널 영상 상위 3개 선택
4. 각 영상의 URL, 제목, 채널명, 조회수 수집
5. 최종 선택된 YouTube URL 목록 반환
```

---

// turbo
## Step 4: NotebookLM 노트북 자동 생성 (browser_subagent) ⭐ 핵심

```
browser_subagent 태스크:
1. https://notebooklm.google.com 접속 (Google 로그인 필요 시 처리)
2. "+ 새 노트북" 버튼 클릭
3. 노트북 제목 입력: "[연구주제] - [YYYY-MM-DD]"
4. "소스 추가" 클릭
5. Step 2에서 수집된 웹 URL들 하나씩 추가
6. Step 3에서 수집된 YouTube URL들 추가
7. 모든 소스 추가 완료 확인
8. "공유" 버튼 → "링크가 있는 모든 사용자" 설정
9. 공유 URL 복사 후 반환
```

---

## Step 5: MCP 딥 리서치 세션 (연속 심층 분석)

노트북 생성 완료 후 MCP로 즉시 세션 시작:

```python
# 1차: 전체 개요
session = ask_question("이 연구의 핵심 인사이트 TOP 5를 출처와 함께 설명해줘")

# 2차: 심층 분석
ask_question("가장 중요한 실행 방안 3가지와 구체적 방법은?", session_id=session.id)

# 3차: 비즈니스 적용
ask_question("대표님의 AI 1인 기업에 지금 당장 적용할 수 있는 액션 플랜은?", session_id=session.id)

# 4차: 리스크·트렌드
ask_question("이 분야의 최신 트렌드와 주의해야 할 위험 요소는?", session_id=session.id)
```

---

// turbo
## Step 6: Google Docs 자동 저장

```powershell
python ".agent/skills/google_workspace/create_doc.py" --title "[연구주제] 딥 리서치 보고서 - [날짜]" --content "[MCP 분석 결과 전체]"
```

---

// turbo
## Step 7: 메모리 저장

```powershell
python ".agent/skills/memory/memory_manager.py" save "research_[날짜]" "[주제] | NotebookLM: [URL] | Docs: [URL]" --category research
```

---

## Step 8: 최종 보고 (대표님께)

```
🎯 "[연구 주제]" 딥 리서치 완료!

📚 NotebookLM 노트북: https://notebooklm.google.com/...
📄 Google Docs 보고서: https://docs.google.com/...
📺 YouTube 소스 3개 / 🌐 웹 소스 5개 추가됨

💡 핵심 인사이트:
[TOP 3 요약]

⏱ 총 소요시간: X분
대표님, 링크로 직접 열어보실 수 있습니다! 💙🚀
```
