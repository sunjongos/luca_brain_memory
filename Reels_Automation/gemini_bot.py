import webbrowser
import time
import pyautogui
import pyperclip

def run_gui_bot():
    print("=== 🚀 Zero-API Cost: Human Emulation Bot (PyAutoGUI) ===")
    
    prompt_text = "인스타그램 릴스용 9:16 세로 비율로, '네이버 로맨스 웹툰(Korean Manhwa)' 특유의 화사하고 훈훈한 애니메이션 작화 스타일을 가진 '움직이는 10초 영상' 4개를 VEO 3 모델로 각각 다른 씬으로 생성해줘. \n\n(1) 다정하고 잘생긴 흑발의 한국인 남성 정형외과 의사가 안심하라는 듯 부드럽게 미소짓는 장면\n(2) 햇살이 쏟아지는 밝고 감성적인 관절 진료실 전경\n(3) 지팡이를 버리고 무릎 통증에서 벗어나 눈물을 글썽이며 활짝 웃으며 걷는 할머니 환자\n(4) 의사와 환자가 두 손을 꼭 잡고 마주보며 행복하게 웃는 벅찬 감동 씬\n\n그리고 이 감동 서사에 완벽하게 어울리는 '따뜻하고 희망찬 오케스트라 배경음악(BGM)'도 Lyria 모델을 통해 한 곡(15초 내외) 생성해줘."
    
    print("0. 프롬프트를 클립보드에 복사 완료.")
    pyperclip.copy(prompt_text)
    
    print("1. 대표님의 기본 브라우저를 통해 제미나이(Gemini) 탭을 엽니다.")
    # 기본 브라우저 새 탭으로 제미나이 강제 호출 (프로필 충돌/보안 오류 0%)
    webbrowser.open("https://gemini.google.com/app")
    
    print("페이지 로딩 및 입력창 렌더링을 위해 안전하게 8초 대기합니다...")
    time.sleep(8)
    
    print("2. 마우스/키보드를 조작하여 프롬프트를 붙여넣습니다 (Ctrl+V)")
    # 제미나이는 열리자마자 텍스트 입력창이 기본 포커스됨을 활용
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    
    print("3. Enter 키를 눌러 렌더링을 지시합니다.")
    pyautogui.press('enter')
    
    print("\n📌 [작업 완료] 제미나이가 웹툰을 그리기 시작했습니다! 마우스를 다시 통제하셔도 됩니다.")

if __name__ == "__main__":
    run_gui_bot()
