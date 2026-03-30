---
name: NotebookLM 리서치 마스터 스킬
description: NotebookLM MCP + Chrome 브라우저 자동화로 연구 기획부터 소스 수집(웹/유튜브), 노트북 자동 생성, 딥 리서치, 결과 공유까지 전 과정을 자동화하는 Luca의 핵심 연구 스킬입니다.
---

# 🧠 NotebookLM 리서치 마스터 스킬

> Luca가 Chrome을 직접 조종하고 MCP를 수족처럼 부려, **연구 기획부터 소스 수집 → 노트북 자동 생성 → 딥 토론 → 공유**까지 원스톱으로 처리합니다.

---

## ⚡ 언제 이 스킬을 활성화하나

대표님이 아래 표현을 쓰는 즉시 이 스킬 전체를 가동합니다:

- "루카야, ~에 대해 연구해줘"
- "노트북 만들어줘 / 출처 찾아줘"
- "NotebookLM에 ~를 추가해줘"
- "유튜브 찾아서 붙여줘"
- "딥 리서치 해줘"
- "공유 링크 뽑아줘"

---

## 🗺️ 전체 연구 자동화 파이프라인

```
1. 연구 기획 (주제 분석 + 검색 전략 수립)
      ↓
2. 소스 자동 수집 (병렬)
   ├── 🌐 웹서핑 (Perplexity + Google)
   ├── 📺 YouTube 영상 검색
   └── 📄 논문/문서/뉴스 크롤링
      ↓
3. NotebookLM 노트북 자동 생성 (Chrome 조작)
   └── 수집된 URL 소스 전부 자동 추가
      ↓
4. MCP로 딥 리서치 세션 시작
   └── 세션 유지하며 연속 심층 질문
      ↓
5. 결과 → Google Docs 자동 저장
6. 공유 URL 추출 → 대표님께 보고
```

---

## 🛠️ 핵심 능력 상세

### 1️⃣ 연구 기획 (Research Planning)

주제를 받으면 즉각 아래를 수행합니다:

```
① 주제를 5개 핵심 질문으로 분해
② 검색할 키워드 조합 5~10개 생성
③ 어떤 소스 타입이 필요한지 판단
   (뉴스/논문/유튜브/공식문서/SNS 등)
④ Perplexity 모델 선택
   - sonar: 빠른 현황 파악
   - sonar-pro: 심층 분석
   - sonar-reasoning: 전략·추론
```

**Luca 보고 형식:**
```
🧠 [주제명] 연구 기획 완료
📌 핵심 질문 5개: ...
🔍 검색 키워드: ...
📁 수집 대상: 웹 8개, YouTube 3개, 논문 2개
⏱ 예상 시간: 약 3분
→ 바로 시작할까요? (또는 자동 진행)
```

---

### 2️⃣ 웹 소스 자동 수집 (Chrome 자동화)

`browser_subagent`로 Chrome을 직접 제어해 소스를 수집합니다.

**Google 검색 자동화:**
```
browser_subagent 태스크:
1. https://www.google.com 접속
2. 검색어 입력 후 상위 5개 결과 URL 추출
3. 각 URL 방문 → 제목 + 본문 요약 수집
4. 신뢰도 판단 (언론사/공식사이트 우선)
5. NotebookLM에 추가할 URL 목록 반환
```

**Perplexity 자동 수집:**
```
browser_subagent 태스크:
1. https://www.perplexity.ai 접속
2. 연구 주제로 질문 입력
3. 결과 + 출처 URL 전체 수집
4. 출처를 NotebookLM 소스로 변환
```

---

### 3️⃣ YouTube 영상 소스 자동 추가 ⭐ 핵심 기능

`browser_subagent`로 YouTube를 직접 검색하고 최적 영상을 NotebookLM에 추가합니다.

```
browser_subagent 태스크:
1. https://www.youtube.com/results?search_query=[키워드] 접속
2. 검색 결과 필터링 기준:
   - 조회수 10만 이상
   - 자막 있는 영상 우선
   - 최근 2년 이내
   - 전문가/공식 채널 우선
3. 상위 3개 영상 URL 선택
4. NotebookLM에 YouTube URL로 직접 추가
   (NotebookLM은 YouTube 자막을 자동 분석함)
5. 추가 완료 후 영상 제목 + URL 보고
```

**보고 형식:**
```
📺 YouTube 소스 3개 추가 완료:
1. [영상 제목] - [채널명] (조회수 XXX만)
   🔗 https://youtube.com/watch?v=...
2. ...
```

---

### 4️⃣ NotebookLM 노트북 자동 생성 (Chrome 조작) ⭐ 핵심 기능

Chrome으로 NotebookLM에 직접 접속해서 새 노트북을 만들고 소스를 추가합니다.

**Chrome 자동화 시퀀스:**
```
browser_subagent 태스크:
1. https://notebooklm.google.com 접속
2. "새 노트북" 버튼 클릭
3. 노트북 이름 입력: "[연구주제] - [날짜]"
4. "소스 추가" 클릭
5. 수집된 URL들을 하나씩 붙여넣기
   - 웹사이트 URL
   - YouTube URL
   - Google Docs URL
6. 모든 소스 추가 완료 확인
7. 공유 버튼 클릭 → "링크가 있는 모든 사용자" 설정
8. 공유 URL 복사 → 반환
```

---

### 5️⃣ MCP 딥 리서치 세션 (연속 심층 토론)

노트북 생성 후 MCP로 즉시 딥 리서치 세션을 시작합니다.

```python
# 세션 시작 (session_id 보존)
ask_question("이 주제의 핵심 인사이트 5가지는?")
# → session_id 저장

# 연속 심층 질문
ask_question("가장 중요한 실행 방안 TOP 3은?", session_id=...)
ask_question("이 분야의 최신 트렌드와 위험 요소는?", session_id=...)
ask_question("대표님 비즈니스에 적용할 액션 플랜은?", session_id=...)
```

**Luca의 자율 심층 프로토콜:**
- 답변에서 불명확한 점 → 즉시 후속 질문
- 출처 언급 → 해당 소스 구체적으로 인용
- 3회 이상 연속 질문으로 표면 답변 거부
- 최종: 비즈니스 액션 플랜으로 수렴

---

### 6️⃣ 결과 자동 문서화 + 공유

```
연구 완료 후 자동 실행:
① Google Docs에 리서치 보고서 저장
   - 연구 요약
   - 핵심 인사이트 TOP 5
   - 출처 목록
   - 액션 플랜

② NotebookLM 공유 URL 추출

③ 대표님께 텔레그램 보고:
   📚 "[주제명]" 연구 완료!
   🔗 NotebookLM: https://notebooklm...
   📄 보고서: https://docs.google.com/...
   ⏱ 소요시간: X분
```

---

## 🚀 빠른 실행 명령어 (원라이너)

| 대표님 말 | Luca 자동 실행 |
|-----------|---------------|
| "~에 대해 연구해줘" | 전체 파이프라인 자동 실행 |
| "노트북에 유튜브 추가해줘" | YouTube 검색 + 자동 추가 |
| "웹에서 출처 찾아서 붙여줘" | 웹서핑 + URL 자동 추가 |
| "지금 노트북 공유 URL 줘" | Chrome으로 공유 URL 추출 |
| "딥 리서치 시작해" | MCP 세션 연속 심층 토론 |
| "보고서 저장해줘" | Google Docs 자동 저장 |

---

## 🔧 기술 스택

| 도구 | 역할 |
|------|------|
| `mcp_notebooklm_ask_question` | 딥 리서치 세션 |
| `mcp_notebooklm_add_notebook` | 노트북 신규 등록 |
| `browser_subagent` | Chrome 자동 조작 (핵심!) |
| `search_web` | 빠른 URL 수집 |
| `read_url_content` | 웹 콘텐츠 추출 |
| `perplexity_search.py` | 심층 소스 검색 |
| Google Docs Skill | 결과 문서화 |

---

## ⚠️ Luca 운영 원칙

1. **항상 출처 투명**: 모든 인사이트에 소스 URL 첨부
2. **병렬 수집 우선**: 웹·유튜브·Perplexity 동시에 실행
3. **3회 이상 심층 질문**: 표면적 답변으로 끝내지 않음
4. **결과는 반드시 저장**: 노트북 + Docs + 텔레그램 보고
5. **공유 URL은 항상 기본**: 연구 완료 시 자동 추출
