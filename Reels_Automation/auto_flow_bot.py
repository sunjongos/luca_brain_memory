import asyncio
import time
from playwright.async_api import async_playwright

async def auto_flow():
    print("=== 🚀 [릴스 2 완전 자동화] Google Labs Flow + Gemini RPA 봇 가동 ===")
    IMAGE_PATH = r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\orthopedic_healing_webtoon_1774260664587.png"
    
    async with async_playwright() as p:
        try:
            print("▶ 크롬 브라우저 심장부(CDP 포트 9222) 침투 중...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            print("▶ 1. Google Labs Flow (VEO 3) 강제 접속 중...")
            await page.goto("https://labs.google/fx/ko/tools/flow", timeout=60000)
            print("Flow 인터페이스 로딩 대기(10초)...")
            await page.wait_for_timeout(10000)
            
            # 1. 파일 업로드 폼 스캔 및 앞서 만든 이미지 인젝션
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                print("✅ 숨겨진 이미지 업로드 폼 포착! 아까 만든 할머니 웹툰 키 이미지를 Flow 플랫폼에 강제로 꽂아 넣습니다.")
                await file_input.set_input_files(IMAGE_PATH)
                await page.wait_for_timeout(4000)
            else:
                print("⚠️ [수동 협업 요청] Flow 화면 구조 보안으로 인해 자동 파일 스캔 실패. 화면의 버튼을 눌러 이미지를 직접 한 번만 업로드해 주십시오!")
                await page.wait_for_timeout(10000) # 수동 업로드 시간 부여
                
            # 2. 프롬프트 창 타이핑
            print("▶ 2. VEO 3 영상 렌더링 프롬프트 타이핑 및 [Enter] 조작...")
            text_boxes = await page.query_selector_all('textarea, [contenteditable="true"]')
            if text_boxes:
                prompt = "첨부된 이미지를 바탕으로, 진료실에서 다정하고 잘생긴 남성 의사가 환하게 웃으며 할머니 환자의 두 손을 꼭 잡고 벅찬 감동으로 눈물 짓는 장면을 매끄러운 세로형 무빙 비디오(VEO 3) 1개로 연결해서 만들어줘."
                # 가장 마지막(보통 입력영역)의 것을 선택
                await text_boxes[-1].fill(prompt)
                await page.wait_for_timeout(1000)
                await page.keyboard.press("Enter")
            else:
                print("⚠️ 프롬프트 창을 찾지 못했습니다.")
            
            print("⏳ Flow VEO 3 렌더링이 시작되었습니다. (약 3초마다 체크하며 최대 4분 대기)")
            
            # Flow의 다운로드 버튼 스캔 영역
            download_btn = await page.wait_for_selector('button[aria-label*="다운로드"], button[aria-label*="Download"], a[download], button:has-text("다운로드")', timeout=240000)
            
            if download_btn:
                print("✅ Flow 영상 렌더링 완료! 다운로드 버튼을 해킹하여 강제 클릭 및 저장합니다.")
                await download_btn.click()
                await page.wait_for_timeout(5000)
                
            # 3. 제미나이 Lyria 음악 탭으로 동시 가동
            print("\n▶ 3. 제미나이(Lyria BGM) 탭 동시 접속 중...")
            gemini_page = await context.new_page()
            await gemini_page.goto("https://gemini.google.com/app", timeout=60000)
            
            input_box = await gemini_page.wait_for_selector('div[role="textbox"], rich-textarea', timeout=30000)
            prompt_bgm = "방금 만든 감동적인 의사와 환자의 최선종 병원장님 서사에 완벽하게 어울리는 '가슴이 벅차오르는 따뜻하고 웅장한 오케스트라 배경음악(BGM)'을 Lyria 모델을 통해 한 곡(15초 내외) 생성해줘."
            
            print("▶ Lyria 배경음악 프롬프트 전송...")
            await input_box.fill(prompt_bgm)
            await gemini_page.wait_for_timeout(1000)
            await gemini_page.keyboard.press("Enter")
            
            print("⏳ Lyria 음악 렌더링 1분 대기 중...")
            await gemini_page.wait_for_timeout(60000)
            
            music_dl_btns = await gemini_page.query_selector_all('button[aria-label*="다운로드"], button[aria-label*="Download"]')
            if music_dl_btns:
                print("✅ Lyria 음악 렌더링 완료! 다운로드 버튼 클릭!")
                await music_dl_btns[-1].click()
                await gemini_page.wait_for_timeout(4000)
            else:
                print("⚠️ 음악 다운로드 버튼 1차 스캔 실패. 20초 후 재시도...")
                await gemini_page.wait_for_timeout(20000)
                music_dl_btns = await gemini_page.query_selector_all('button[aria-label*="다운로드"], button[aria-label*="Download"]')
                if music_dl_btns:
                    await music_dl_btns[-1].click()
                    
            print("\n🎉 모든 에셋(Flow 영상 + Lyria 음악) 다운로드 RPA 액션 완료! (이제 감시요원이 받아서 조립합니다)")
            
        except Exception as e:
            print(f"❌ 봇 작동 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(auto_flow())
