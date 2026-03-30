---
description: 웹페이지 기획부터 배포·결제까지 원스톱 자동화 파이프라인
---

# 🌐 웹페이지 기획 및 자동 배포 워크플로우 (Web Creation Pipeline)

대표님의 아이디어를 클릭 몇 번으로 실제 결제가 가능한 라이브 웹 서비스로 만들어내는 Super Agent 전용 워크플로우입니다.

## 🎯 전체 파이프라인 흐름
`기획(NotebookLM)` → `디자인(Stich/UI)` → `개발(Antigravity)` → `결제(PayPal MCP)` → `배포(Firebase)`

---

## 🛠️ 단계별 실행 절차

### 단계 1: 🧠 기획 및 연구 (NotebookLM MCP)
아이디어를 비즈니스 모델과 구체적인 웹사이트 기획안으로 발전시킵니다.
1. `notebooklm` 서브 에이전트를 호출하여 시장 조사 및 핵심 타겟을 분석합니다.
2. 랜딩 페이지에 들어갈 주요 카피라이팅, 기능 정의서, 섹션 구분 리포트를 생성합니다.
3. 생성된 기획안은 `google_workspace`를 통해 Google Docs로 자동 저장하여 대표님(CEO)의 컨펌을 받습니다. (**Human-in-the-Loop**)

### 단계 2: 🎨 UI/UX 디자인 코드 완성 (Stitch MCP)
1. 추출된 기획안을 바탕으로 프론트엔드 UI 디자인 구조를 잡습니다.
2. 환경 변수에 저장된 `STITCH_API_KEY`를 활용해 Stitch AI 엔진과 연동합니다.
3. Stitch를 통해 모던하고 트렌디한(Premium Aesthetics) 실제 UI/UX 코드를 단 몇 초 만에 생성 및 추출합니다.
4. 필요시 `generate_image` 도구로 추가적인 배너/리소스를 생성합니다.

### 단계 3: 💻 프론트엔드/백엔드 개발 (Antigravity Agent)
Antigravity 시스템(바로 저, Luca 본체)의 탁월한 코딩 능력을 활용해 실제 코드를 작성합니다.
1. `run_command`로 Vite, React, 또는 Next.js 프로젝트를 자동 셋업 (`npx -y create-vite@latest ...`) 합니다.
2. 단계 2의 디자인 시스템을 적용하여 `index.css`, 컴포넌트를 코딩합니다.
3. 프리미엄하고 모던한 UI(애니메이션, 글래스모피즘 등)를 완벽하게 구현합니다.

### 단계 4: 💳 결제 시스템 연동 (PayPal MCP)
수익 창출을 위한 결제 모듈을 자동으로 붙입니다.
1. PayPal MCP 서버를 셋업하거나 API를 통해 상품 결제 링크 및 버튼 컴포넌트를 생성합니다.
2. Antigravity가 프론트엔드에 결제 버튼을 통합하고, 샌드박스 테스트 환경을 자동 구성합니다.
3. 결제 시나리오 테스트 후 결과를 대표님께 보고합니다.

### 단계 5: 🚀 서버리스 배포 (Firebase 연동)
완성된 코드를 전 세계에 라이브로 띄웁니다.
1. `firebase-tools`를 활용해 Firebase 프로젝트를 초기화합니다. (`firebase init hosting`)
2. 자동 빌드 스크립트(`npm run build`)를 실행합니다.
3. `firebase deploy` 명령으로 호스팅 서버에 배포하여 최종 라이브 URL을 추출합니다.
4. 텔레그램 봇이나 메시지로 최종 URL을 대표님께 브리핑합니다!

---

## ⚡ 텔레그램 봇 단축 커맨드 (추가 제안)
이 워크플로우 전체를 텔레그램 명령 한 줄로 시작할 수 있습니다.
- **사용 예시:** `/build "AI 기반 영어 회화 트레이닝 구독 서비스 랜딩페이지"`
- Luca가 위 5단계를 병렬+직렬 조합으로 자동 진행!
