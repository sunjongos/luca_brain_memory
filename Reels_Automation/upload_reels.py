import time
import sys
import os
from playwright.sync_api import sync_playwright

FB_ID = "01062095699"
FB_PW = "761122love@"

# 대표님께서 이동하신 영상 경로
# 렌더링 된 최종 영상 경로
VIDEO_PATH = r"C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\Reels_Automation\final_reels.mp4"

TEXT_PATH = r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타\이순태교수_부친상_추모글.txt"
with open(TEXT_PATH, 'r', encoding='utf-8') as f:
    CAPTION = f.read().strip()

def run():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file not found at {VIDEO_PATH}")
        sys.exit(1)

    print("=== 인스타그램 업로드 자동화 봇 실행 시작 ===")
    with sync_playwright() as p:
        # 눈으로 동작을 확인할 수 있도록 headless=False 로 실행
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("1. 인스타그램 접속 중...")
        page.goto("https://www.instagram.com/")
        page.wait_for_timeout(3000)

        # Facebook으로 로그인
        print("2. 페이스북 연동 로그인 진행 중...")
        if page.locator("button:has-text('Facebook으로 로그인')").is_visible():
            page.click("button:has-text('Facebook으로 로그인')")
            page.wait_for_timeout(3000)
            
            page.fill("input[name='email']", FB_ID)
            page.fill("input[name='pass']", FB_PW)
            page.click("button[name='login']")
            page.wait_for_timeout(8000)  # 로그인 대기
        else:
            print("Facebook 로그인 버튼을 찾을 수 없거나 이미 로그인되어 있습니다.")

        # 정보 저장 파업창 패스
        if page.locator("button:has-text('나중에 하기')").is_visible():
            page.click("button:has-text('나중에 하기')")
            page.wait_for_timeout(2000)
        
        # 알림 설정 팝업창 패스
        if page.locator("button:has-text('나중에 하기')").is_visible():
            page.click("button:has-text('나중에 하기')")
            page.wait_for_timeout(2000)

        print("3. 새 게시물 작성 모달 열기...")
        create_btn = page.locator('span:has-text("만들기")')
        if create_btn.count() > 0:
            create_btn.first.click()
        else:
            page.locator('svg[aria-label="새로운 게시물"]').first.click()
        page.wait_for_timeout(2000)

        print(f"4. 릴스 영상 파일 주입 중: {VIDEO_PATH}")
        # 파일 업로드 다이얼로그 우회
        page.locator('input[type="file"]').set_input_files(VIDEO_PATH)
        page.wait_for_timeout(6000) # 영상 인코딩/화면 로딩 대기

        print("5. 화면 비율 및 필터 '다음' 단계 통과 중...")
        page.locator('div[role="button"]:has-text("다음")').first.click()
        page.wait_for_timeout(3000)
        
        page.locator('div[role="button"]:has-text("다음")').first.click()
        page.wait_for_timeout(3000)

        print("6. 캡션 본문 타이핑 중...")
        caption_box = page.locator('div[aria-label*="문구 입력"]')
        if caption_box.count() > 0:
            caption_box.fill(CAPTION)
        page.wait_for_timeout(2000)

        print("7. 공유하기 버튼 클릭!")
        share_btn = page.locator('div[role="button"]:has-text("공유하기")')
        if share_btn.count() > 0:
            share_btn.first.click()
            
            print("8. 인스타그램 서버 업로드 대기 중 (최대 30초)...")
            try:
                page.wait_for_selector('text="게시물이 공유되었습니다."', timeout=30000)
                print("====================================")
                print("성공! 릴스 게시물이 업로드 되었습니다 🎉")
                print("====================================")
            except:
                print("업로드 결과 알림을 찾지 못했지만 업로드가 백그라운드에서 진행되었을 수 있습니다.")
        else:
            print("공유하기 버튼을 찾을 수 없습니다.")

        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    run()
