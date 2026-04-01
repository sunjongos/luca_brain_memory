---
name: auto_website_builder
version: 2.0.0
description: 완벽한 자동화 파이프라인. 주제(또는 NotebookLM 링크)만 주어지면 리서치, 디자인, 개발, 결제 연동, 배포까지 한 번에 끝냅니다. (2026 최신 트렌드 반영)
tags: [web, automation, firebase, paypal, notebooklm, deploy]
---

# Auto Website Builder Skill 🚀 v2.0

이 스킬은 **"주제를 던져주면 AI가 알아서 기획하고 만들어 수익화 세팅 후 배포까지 완료하는"** 궁극의 자동화 워크플로우입니다.
**병렬 처리 원칙**: 서로 의존성 없는 작업은 반드시 동시에 실행합니다.

## [NEW 2026] Pre-Flight: 컨텍스트 파악
- 대표님의 최근 프로젝트 패턴(병원/클리닉 마케팅, SEO 등)을 선제적으로 파악
- 기존 완성된 랜딩 페이지들을 레퍼런스로 활용 (혈관클리닉, NDB스트레스클리닉 등)

## Workflow

### 1단계: Research (NotebookLM 심층 분석)
1. 사용자로부터 제공받은 주제나 NotebookLM 공유 URL을 파악합니다.
2. `notebooklm` MCP 도구(`mcp_notebooklm_list_notebooks`, `mcp_notebooklm_ask_question`)로 노트북에 질의합니다.
3. **추출 필수 요소**:
   - 서비스/제품의 핵심 가치 (Value Proposition)
   - 타겟 고객 (Target Audience) + 페인 포인트
   - SEO 최적화 키워드 (네이버/구글 검색어 포함)
   - 헤드라인, 서브 헤드라인, 특장점(Features) 3가지, CTA 문구
   - **[NEW]** 경쟁사 차별화 포인트 (Competitive Edge)

### 2단계: Design & Architecture 설계
1. **2026 필수 디자인 원칙**:
   - 반응형 디자인 (모바일 우선 - Mobile-First)
   - Glassmorphism + Neomorphism 조합
   - Micro-animations (GSAP 또는 CSS 기반 스크롤 애니메이션)
   - 모던 타이포그래피 (Google Fonts: Pretendard, Noto Sans KR for 한국어)
   - **[NEW]** Dark/Light 모드 자동 전환 (`prefers-color-scheme`)
   - **[NEW]** Core Web Vitals 최적화 (LCP, FID, CLS 고려)
2. `generate_image` 도구로 히어로 섹션 배경/아이콘 이미지 즉시 생성
3. 파일 구조: `index.html` (All-in-One 또는 분리된 `style.css`, `script.js`)

### 3단계: Website Development (웹사이트 완성)
1. 1단계 카피 + 2단계 디자인 시스템을 결합하여 코드 작성
2. `write_to_file`로 프로젝트 폴더 내 코드 일괄 생성
3. **[NEW] SEO 자동 최적화**:
   - `<title>`, `<meta description>`, Open Graph 태그 삽입
   - 구조화된 데이터 (Schema.org JSON-LD) 삽입
   - `<h1>` 계층 구조 최적화
4. **[NEW] 성능 최적화**:
   - 이미지 lazy loading 적용 (`loading="lazy"`)
   - Critical CSS 인라인화
   - Google Analytics 4 트래킹 코드 삽입 준비

### 4단계: Payment Integration (PayPal 결제 연동)
1. HTML/JS 파일에 PayPal Smart Payment Buttons 코드 삽입
2. 대표님 전용 PayPal Production(Live) 자격 증명:
   - **Client ID**: `ATMx3Y4oJldZfNhlYuFmrXW9jrQZIExZ6Zi1DJ9NOYe4GfmXS2BgX5J5J6OYkcq2N1aEr1nEs95qBWGP`
   - **Secret(API KEY)**: `EI9T8X4k-YcRbs5fulEVcoaEqthKcanftiFG9ME8PGc83EFpyH_5MpiTD5oi58y_cNh3RHBuWu4ez83Q`
3. **[NEW]** 카카오페이/토스페이 연동 가이드 주석 삽입 (한국 시장 대응)

### 5단계: Firebase Hosting Deployment (배포)
1. `mcp_firebase_firebase_init`으로 Firebase Hosting 초기화
2. `firebase deploy --only hosting` 명령을 백그라운드 실행
3. **[NEW]** 배포 후 자동 헬스체크: 라이브 URL에 Playwright로 스크린샷 캡처
4. 배포된 최종 라이브 URL 추출 및 보고

## 최종 보고 (Reporting)
모든 프로세스 완료 후 **Luca 본부장 페르소나**로 브리핑:
- 배포된 Firebase URL
- SEO 점수 예측 및 네이버 최적화 팁
- PayPal 결제 테스트 안내
- Playwright 스크린샷 첨부
- **[NEW]** 네이버 서치어드바이저 등록 가이드

> ⚡ 이 스킬을 실행할 때는 더 이상의 질문 없이 즉각적으로 각 단계에 요원들을 투입하여 병렬로 밀어붙이십시오!
