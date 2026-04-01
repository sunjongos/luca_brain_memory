---
description: 인스타그램 자동 업로드 우회 워크플로우 (Playwright)
---

이 워크플로우는 Zapier 등 공식 API의 개인 계정 제한이나 CAPTCHA 등으로 인해 인스타그램 자동 업로드가 불가능할 때, Playwright 브라우저 자동화 기술을 통해 대표님의 페이스북 계정 연동으로 인스타그램에 로그인하고 우회 업로드를 진행하는 표준 절차입니다.

**실행 조건:**
- 대표님의 지시: "인스타그램에 게시해줘" 등
- 사전 준비물: 업로드할 이미지(1:1 또는 4:5 비율 권장) 파일과 텍스트 캡션
- 로그인 계정 정보: 페이스북 연동 로그인 (ID: `01062095699`, PW: `761122love@`)

**단계별 실행 지침:**

1. **자동화 스크립트 준비 및 로그인 (Playwright)**
   - `mcp_playwright_browser_run_code` 도구를 사용하여 인스타그램(https://www.instagram.com/)에 접속하고, 페이스북 계정 로그인 버튼을 눌러 연동 로그인을 수행합니다.
   
2. **OS 파일 선택 창 우회 (핵심 기술)**
   - 인스타그램의 UI에서 파일 선택 창을 클릭하면 시스템 OS 다이얼로그가 열려 에이전트의 제어 범위를 벗어나게 됩니다.
   - 이를 해결하기 위해 HTML DOM 내부의 숨겨진 `input[type="file"]` 속성에 직접 이미지 파일 경로를 주입(Inject)합니다.
   - *주의사항: Playwright는 워크스페이스 외부 경로(예: .gemini 아티팩트 폴더 등)의 파일에는 접근할 수 없습니다. 따라서 업로드 전에 이미지를 반드시 워크스페이스 내부(`C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\`)로 먼저 복사(`run_command` 활용)해야 합니다.*

   **참고 템플릿 코드:**
   ```javascript
   async (page) => {
     // 새 게시물 만들기 모달 띄우기
     const createButton = page.locator('svg[aria-label="새로운 게시물"]').locator('xpath=..').locator('xpath=..');
     if (await createButton.count() > 0) {
       await createButton.first().click();
     } else {
       await page.locator('span:has-text("만들기")').first().click();
     }
     await page.waitForTimeout(2000);
     
     // 워크스페이스 내에 저장된 이미지 경로 주입
     const filePath = 'C:\\Users\\USER\\OneDrive\\바탕 화면\\luca연구에이전트\\young_doctor_example.png';
     await page.locator('input[type="file"]').setInputFiles(filePath);
   }
   ```

3. **캡션 입력 및 공유하기**
   - 이미지 업로드 후 나타나는 '다음(Next)' 버튼을 두 번 클릭하여 텍스트 입력 창으로 이동합니다.
   - 캡션 텍스트 박스(예: `div[aria-label*="문구 입력"]` 또는 `div[data-lexical-editor="true"]`)에 대표님이 작성한 문구와 해시태그를 `fill` 메서드로 입력합니다.
   - '공유하기(Share)' 버튼을 클릭하고 포스팅이 서버로 전송될 때까지 충분히 대기합니다. (보통 5~10초 소요)

4. **결과 검증 및 스크린샷 캡처**
   - `mcp_playwright_browser_wait_for` 도구를 활용해 "게시물이 공유되었습니다." 모달 또는 텍스트가 렌더링되는지 확인합니다.
   - `mcp_playwright_browser_take_screenshot` 도구로 최종 확인 화면을 캡처한 뒤, 대표님께 업로드 완료 보고를 진행합니다.
