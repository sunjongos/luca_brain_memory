---
name: Web Creator (웹페이지 자동화 스킬)
description: 기획(NotebookLM)부터 디자인, 코딩(Antigravity), 결제(PayPal), 배포(Firebase)까지 웹페이지 제작의 전 과정을 자동화하는 파이프라인 스킬입니다.
---

# 🌐 Web Creator 스킬

대표님의 지시 한 번으로 **수익 창출이 가능한 라이브 웹사이트**를 즉시 만들어내는 궁극의 초자동화 스킬입니다.

## 📌 언제 이 스킬을 사용하는가?
- 대표님이 새로운 비즈니스 아이디어나 랜딩페이지 제작을 지시했을 때
- "OOO을 파는 웹사이트 만들어줘", "구독형 랜딩페이지 짜봐" 등의 요청 시

## ⚙️ 실행 파이프라인 (총 5단계)

이 스킬이 트리거되면, 반드시 `.agent/workflows/web_creation.md` 워크플로우를 참조하여 다음 단계를 순차/병렬로 실행합니다.

1. **🧠 기획 (NotebookLM + Docs):**
   - 아이디어 구체화, 타겟 분석, 카피라이팅 도출 (NotebookLM)
   - 기획안을 Google Docs로 생성 후 **CEO 컨펌 (필수)**
2. **🎨 디자인 및 UI 코드 생성 (Stitch MCP):**
   - 발급받은 `STITCH_API_KEY` 환경 변수를 사용하여 Stitch AI와 연동합니다.
   - 대표님의 기획안을 바탕으로 Stitch AI에게 트렌디하고 화려한 프리미엄 UI 디자인 코드를 생성시킵니다.
   - 메인 배너 이미지/무드보드 생성이 필요한 경우 추가로 `generate_image`를 활용합니다.
3. **💻 개발 세팅 (Antigravity):**
   - `run_command`로 Vite/Next.js 프로젝트 자동 셋업 (`npx -y create-vite@latest ...`)
   - Stitch가 뱉어낸 코드를 프로젝트에 이식하고, Glassmorphism, 애니메이션 등 모던한 효과를 다듬습니다.
4. **💳 결제 연동 (PayPal):**
   - `.env`에서 키를 읽어 연동합니다:
     - `PAYPAL_CLIENT_ID` : Antigravity 전용 PayPal Client ID
     - `PAYPAL_SECRET`    : Antigravity 전용 PayPal Secret
     - `PAYPAL_ENV`       : `sandbox` (테스트) / `production` (라이브)
   - **구현 방식**: 웹페이지 `<head>`에 PayPal JS SDK를 삽입하고 버튼 컴포넌트를 렌더링
     ```html
     <script src="https://www.paypal.com/sdk/js?client-id=ATMx3Y4oJldZfNhlYuFmrXW9jrQZIExZ6Zi1DJ9NOYe4GfmXS2BgX5J5J6OYkcq2N1aEr1nEs95qBWGP&currency=USD"></script>
     ```
   - **백엔드 API 검증**: `PAYPAL_SECRET`으로 서버사이드 주문 검증 (Node.js / Python)
   - 샌드박스 테스트 후 `PAYPAL_ENV=production`으로 전환하면 라이브 결제 자동 전환
5. **🚀 배포 (Firebase):**
   - `firebase-tools`를 이용해 빌드 및 호스팅 배포
   - 생성된 최종 라이브 URL을 대표님께 브리핑

## 🚨 주의사항
- **[컨펌 필수]** 1단계 기획안이 나오면 코딩에 들어가기 전 반드시 대표님(CEO)의 컨펌을 받습니다.
- **[프리미엄 퀄리티]** 디자인과 UI는 단순한 템플릿 수준이 아닌, 트렌디하고 압도적인 퀄리티(Premium Aesthetics)를 유지해야 합니다.
- **[키 보안]** PayPal 키는 절대 클라이언트 코드에 하드코딩하지 않습니다. Client ID만 프론트엔드에 노출하고, Secret은 서버사이드에서만 사용합니다.

