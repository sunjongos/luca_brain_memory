import asyncio
import time
from playwright.async_api import async_playwright

async def auto_gemini():
    print("=== 🚀 [릴스 2 완전 자동화] True RPA 제미나이 해킹 봇 가동 ===")
    async with async_playwright() as p:
        try:
            print("▶ 크롬 브라우저 심장부(CDP 포트 9222) 침투 중...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            
            page = None
            for p_obj in context.pages:
                if p_obj.url != "about:blank":
                    page = p_obj
                    break
            if not page:
                page = await context.new_page()
                
            print("▶ 제미나이(Gemini Ultra) 접속...")
            await page.goto("https://gemini.google.com/app", timeout=60000)
            
            print("▶ 입력창 스캔 중...")
            # 제미나이의 텍스트 입력 다이얼로그
            input_box = await page.wait_for_selector('div[role="textbox"], rich-textarea', timeout=30000)
            
            prompt_video = "인스타그램 릴스용 9:16 비율, 네이버 웹툰 스타일. 다정하고 잘생긴 남성 한국인 정형외과 의사가 지팡이를 내려놓고 환하게 웃으며 걷는 할머니 환자의 두 손을 잡고 눈물 짓는 장면을 VEO 3 영상으로 1개만 만들어줘."
            
            print("▶ VEO 3 영상 렌더링 지시어 타이핑 중...")
            await input_box.fill(prompt_video)
            time.sleep(1)
            await page.keyboard.press("Enter")
            
            print("⏳ 제미나이가 영상을 렌더링 중입니다. 구글 서버 응답을 기다립니다 (최대 3분 소요)...")
            
            # 응답 카드 내 다운로드 버튼 생성 대기
            download_btn = await page.wait_for_selector('button[aria-label*="다운로드"], button[aria-label*="Download"], a[download]', timeout=240000)
            
            print("✅ VEO 3 영상 다운로드 버튼 스크린 포착! 강제 탈취(클릭) 합니다!")
            await download_btn.click()
            time.sleep(4) # 다운로드 디스크 기록 여유
            
            print("\n🎵 쉴 틈 없이 Lyria 배경음악(BGM) 렌더링을 지시합니다...")
            prompt_bgm = "방금 만든 감동적인 의사와 환자의 서사에 완벽하게 어울리는 '가슴이 벅차오르는 따뜻하고 희망찬 오케스트라 배경음악(BGM)'을 Lyria 모델을 통해 한 곡(15초 내외) 생성해줘."
            
            await input_box.fill(prompt_bgm)
            time.sleep(1)
            await page.keyboard.press("Enter")
            
            print("⏳ Lyria 음악 렌더링 대기 중 (약 1.5분)...")
            time.sleep(60) # 음악 생성은 보통 40~60초 안팎
            
            # 페이지에 있는 모든 다운로드 버튼 스캔 후 가장 마지막(최신 응답) 것을 클릭
            download_btns = await page.query_selector_all('button[aria-label*="다운로드"], button[aria-label*="Download"]')
            if download_btns:
                print("✅ Lyria 음악 다운로드 버튼 포착! (강제 탈취)")
                await download_btns[-1].click()
                time.sleep(3)
            else:
                print("⚠️ 음악 다운로드 버튼을 1차에서 못찾았습니다. 20초 더 대기합니다...")
                time.sleep(20)
                download_btns = await page.query_selector_all('button[aria-label*="다운로드"], button[aria-label*="Download"]')
                if download_btns:
                    await download_btns[-1].click()
            
            print("🎉 제미나이 렌더링 및 다운로드 100% 자동 해킹 조작 완료!")
            
        except Exception as e:
            print(f"❌ 봇 작동 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(auto_gemini())
