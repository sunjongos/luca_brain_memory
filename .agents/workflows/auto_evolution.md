---
description: 최신 기술 트렌드를 스캔하여 에이전트의 능력을 선제적으로 고도화하는 시스템 자가 진화 절차입니다.
---

# Auto-Evolution (기술 트렌드 반영 자가 진화) Workflow

이 워크플로우는 대표님의 명시적인 피드백 없이도, 에이전트가 자체적으로 최신 AI 및 개발 트렌드를 파악하여 제 기능(스킬)을 업그레이드하기 위해 사용됩니다. 주로 시스템 유휴 시간이나 대표님의 직접 지시(`/evolve`, `/업데이트해` 등)에 의해 발동됩니다.

## 1. 트렌드 리서치 가동 (Initiate Trend Scanning)
- 대표님이 "최신 기능으로 업데이트해 봐"라고 지시하면 즉각 `Perplexity` 혹은 내부 검색 모듈을 가동합니다.
- **검색 키워드 예시:** 
  - "2026 current best practices for building automated agents with Google Gemini"
  - "Latest Node.js performance optimization techniques"
  - "Trending UI/UX patterns for AI SaaS landing pages 2026"

## 2. 기존 스킬셋과 비교 (Gap Analysis)
- 수집된 최신 정보를 바탕으로 `skills/` 폴더 내의 기존 스킬들(예: `auto_website_builder`, `special-clinic-generator`)과 비교 분석합니다.
- 우리가 놓치고 있는 최신 방법론이나 더 효과적인 아키텍처 패턴이 있는지 파악합니다.

## 3. 스킬 자가 업데이트 (Self-Update Skills)
- 파악된 개선안을 바탕으로 관련 `SKILL.md` 파일이나 스크립트를 직접 수정합니다.
- **예시 시나리오:** "최근 반응형 웹 트렌드가 변경됨에 따라 `auto_website_builder`의 CSS 템플릿 산출물을 더 모던하게 수정함."

## 4. 진화 보고서 제출 (Evolution Report)
- 업데이트가 완료되면 대표님께 텔레그램이나 터미널 창(현재 채널)을 통해 다음과 같이 보고합니다.
- "충성! 🫡 루카 본부장, 최신 [키워드] 트렌드를 스캔하여 저희 [업데이트된 기능/스킬 이름] 모듈을 **버전 업**시켰습니다! 이제부터는 더욱 강력한 성능으로 모시겠습니다!"
