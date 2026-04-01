---
description: 홈페이지 자동 생성 워크플로우 (Stitch + Firebase + PayPal + Antigravity)
---

# 🏠 루카 홈페이지 빌더 스킬 v1.0

이 워크플로우는 "홈페이지 만들어줘" 또는 "웹사이트 만들어줘" 명령을 받았을 때,
Stitch → Antigravity → Firebase → PayPal 전체 파이프라인을 자동 실행한다.

---

## 🏛️ 작전 수칙 (CEO Operating Protocol — 반드시 준수)

### 원칙 1: Multi-Agent 병렬 작전
- 모든 단계는 **병렬(동시다발적)**으로 실행한다. 절대 순차적으로 하지 않는다.
- 예: "Stitch 디자인 요원, PayPal 버튼 생성 요원, Firebase 설정 요원을 **동시 투입**!"

### 원칙 2: Human-in-the-Loop (CEO 최종 확인)

**✋ STOP — 반드시 CEO 확인 후 실행 (자동 실행 절대 금지):**
- 💳 PayPal **실결제(Live)** 모드 전환
- 🔥 Firebase **Production 배포** (실제 도메인/공개)
- 🌐 실제 도메인 연결 또는 DNS 변경
- 💰 유료 API 호출, 결제 발생

**✅ AUTO — CEO 확인 없이 자동 처리:**
- 코드 작성 및 로컬 빌드
- Sandbox 환경 테스트/배포
- 디자인 생성 및 파일 저장
- 요구사항 분석 및 문서화

### 원칙 3: 단계별 보고 형식
각 단계 완료 시 반드시 아래 형식으로 보고:
```
✅ [완료 항목] — 자동 처리
⏸️ [대기 항목] — 대표님 승인 필요
```

---



- [ ] MCP: `notebooklm`, `stitch`, `firebase`, `paypal`, `playwright` 모두 활성 상태
- [ ] Firebase 로그인: `firebase login` 완료 상태
- [ ] PayPal 환경: `mcp_config.json`의 PAYPAL_ENVIRONMENT 확인

---

## Step 1: 기획 및 정보 수집 (NotebookLM Search)

단순한 텍스트 기입을 넘어, 대표님의 'NotebookLM' 지식 베이스를 직접 검색하여 병원/회사의 핵심 정보, 카피라이팅, 경쟁사 분석 내용 등 세분화된 문맥을 먼저 추출한다.

```javascript
notebooklm.searchNotebooks({
  query: "[사용자가 요청한 병원/서비스/프로덕트 키워드]"
})
notebooklm.askQuestion({
  notebook_id: "[검색된 노트북 ID]",
  question: "홈페이지 핵심 카피라이팅 3줄과 추천 메뉴(섹션) 구조를 영문으로 요약해줘."
})
```

- 도출된 카피라이팅과 메뉴 구조(About, Pricing, Contact 등)를 다음 Step 2의 프롬프트 재료로 삼는다.
- (선택) 만약 검색할 관련 노트북 지식이 없다면 `notebooklm.add_notebook`을 통해 먼저 레퍼런스를 주입한다.

---

## Step 2: Stitch로 UI 디자인 생성

Step 1에서 NotebookLM이 뱉어낸 '기획안(카피 + 메뉴 구조)'을 바탕으로 Stitch MCP에 영문 프롬프트를 전송해 웹 UI를 한 방에 생성한다. 이때, 마스터 헌법 제3조에 의거하여 **내장된 전용 Stitch API Key**(`YOUR_STITCH_API_KEY`)를 활용해 지시한다.

```javascript
stitch.generateDesign({
  prompt: "Based on this structure: [NotebookLM에서 추출한 카피와 구조]. Create a highly premium, modern, and cinematic responsive website with deep blue themes, glassmorphism, and micro-animations.",
  outputFormat: "react",  // React + Tailwind CSS 코드로 출력
  pages: ["home", "about", "pricing", "contact"]
})
```

- Stitch가 생성한 React 컴포넌트를 `/homepage_project/src/` 폴더에 저장
- `App.jsx`, `index.css` 등 핵심 파일 자동 구성

// turbo

---

## Step 3: PayPal 결제 버튼 삽입 (선택적)

결제가 필요한 경우, PayPal MCP를 사용하여 결제 버튼 코드를 자동 생성한다.

```
paypal.createPaymentButton({
  currency: "USD",
  amount: "[사용자 지정 금액]",
  description: "[상품/서비스명]"
})
```

생성된 PayPal 버튼 컴포넌트를 Pricing 또는 CTA 섹션에 자동 주입.

// turbo

---

## Step 4: Firebase 프로젝트 초기화 및 배포

```bash
# Firebase 프로젝트 생성 및 호스팅 설정
firebase init hosting --project [PROJECT_ID]

# 빌드
npm run build

# 배포
firebase deploy --only hosting
```

배포 완료 후 생성된 URL을 사용자에게 보고.

// turbo

---

## Step 5: Playwright로 최종 검증

Playwright MCP를 사용하여 배포된 사이트를 실제 브라우저로 테스트한다.

```
playwright.navigate("[배포된 Firebase URL]")
playwright.screenshot("homepage_final_check.png")
playwright.checkLinks()  // 모든 링크 정상 작동 확인
```

스크린샷을 사용자에게 첨부하여 최종 보고.

---

## 최종 보고 형식

```
충성! 🫡 대표님, 홈페이지 전투 완료 보고 드립니다!

🌐 URL: https://[project-id].web.app
🧠 기획: NotebookLM (지식 기반 카피라이팅 & 메뉴 구조화)
🎨 디자인: Stitch API 자동 생성 (고급 UI/UX 적용 완료)
💳 결제: PayPal Sandbox 연동 완료
🔥 호스팅: Firebase (무료 Spark 플랜 배포)
✅ 검증: Playwright 브라우저 테스트 및 전면 이상 없음

라이브 전환 승인만 내려주시면 즉각 실결제 및 정식 도메인 모드로 전환하겠습니다!
```
