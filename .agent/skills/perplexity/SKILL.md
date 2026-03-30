---
name: Perplexity 딥서치 스킬
description: Perplexity AI를 활용하여 AI 기반 심층 검색을 수행하는 스킬입니다. browser_subagent를 통한 방식과 Perplexity API 방식 모두 지원합니다.
---

# 🔍 Perplexity 딥서치 스킬

Luca가 Perplexity AI를 통해 AI 기반 심층 검색을 수행하는 스킬입니다.
일반 웹 검색(`search_web`)보다 훨씬 풍부한 맥락과 출처 기반 답변을 제공합니다.

## 📌 언제 이 스킬을 사용하나

- 대표님이 "perplexity로 검색해줘", "딥서치해줘" 라고 명시할 때
- 일반 검색으로는 부족한 심층 리서치가 필요할 때
- 최신 뉴스 + 깊은 분석 조합이 필요할 때
- 여러 소스를 종합한 신뢰도 높은 인사이트가 필요할 때

## 🛠️ 실행 방식 (2가지)

### 방식 A — Browser Subagent (기본, API 키 불필요)

`browser_subagent`를 사용해 perplexity.ai에 직접 접속하여 검색합니다.

**사용 시나리오:** API 키가 없거나, 빠른 임시 검색이 필요한 경우.

```
browser_subagent 태스크 예시:
- URL: https://www.perplexity.ai
- 검색창에 쿼리 입력 후 결과 캡처
- 출처 URL과 요약 내용을 반환
```

### 방식 B — Perplexity API (권장, 자동화 최적)

`perplexity_search.py` 스크립트를 사용하여 API로 직접 쿼리합니다.

**사전 조건:**
1. Perplexity API 키 발급: https://www.perplexity.ai/settings/api
2. `.env` 파일에 `PERPLEXITY_API_KEY=pplx-xxxx` 설정

**실행 방법:**
```powershell
python .agent/skills/perplexity/perplexity_search.py "검색할 내용"
```

## 🔑 설정 방법

1. https://www.perplexity.ai/settings/api 에서 API 키 발급
2. 프로젝트 루트에 `.env` 파일 생성:
   ```
   PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxx
   ```
3. 의존성 설치:
   ```powershell
   pip install -r .agent/skills/perplexity/requirements.txt
   ```

## 📋 지원 모델

| 모델 | 특징 | 용도 |
|------|------|------|
| `sonar` | 빠른 일반 검색 (기본값) | 빠른 사실 확인 |
| `sonar-pro` | 심층 분석 + 출처 강화 | 딥 리서치 |
| `sonar-reasoning` | 추론 + 분석 | 복잡한 전략 분석 |

## 📤 Luca 출력 형식

검색 완료 후 아래 형식으로 대표님께 브리핑합니다:

```
🔍 [검색 키워드] — Perplexity 딥서치 결과

📌 핵심 요약:
[3~5줄 핵심 내용]

🔗 주요 출처:
1. [출처명] — [URL]
2. [출처명] — [URL]

💡 Luca 인사이트:
[비즈니스 관점에서의 추가 해석]
```
