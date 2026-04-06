import os
import sys
import time
import requests
import urllib.request
from datetime import datetime
from dotenv import load_dotenv

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")
load_dotenv(env_path)

FAL_KEY = os.getenv("FAL_KEY")

if not FAL_KEY:
    print("❌ ERROR: FAL_KEY가 설정되지 않았습니다. .env 파일에 FAL_KEY를 입력해주세요.")
    sys.exit(1)

# Fal.ai Minimax API 엔드포인트 세팅 (Kling 또는 Luma로 변경 가능)
API_URL = "https://queue.fal.run/fal-ai/minimax/video-01"

def generate_video(prompt):
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt
    }

    print("🎬 [Luna's Fal.ai Video Gen] API 호출 중... (과금 됨)")
    print(f"✒️ 프롬프트: {prompt}")

    # 1단계: 큐(Queue)에 작업 등록
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ API 요청 실패: {response.text}")
        sys.exit(1)

    data = response.json()
    status_url = data.get("status_url")
    response_url = data.get("response_url")
    request_id = data.get("request_id")

    if not status_url or not response_url:
        print("❌ 응답 데이터에 상태 URL이 없습니다.")
        sys.exit(1)

    print(f"✅ 작업이 대기열에 등록되었습니다. Request ID: {request_id}")
    print("⏳ 비디오 렌더링 중입니다. 약 2~4분 소요됩니다...")

    # 2단계: 폴링(Polling) - 완료될 때까지 기다림
    while True:
        status_res = requests.get(status_url, headers=headers)
        if status_res.status_code == 200:
            status_data = status_res.json()
            status = status_data.get("status")

            if status == "COMPLETED":
                break
            elif status == "IN_PROGRESS":
                print("🏃‍♂️ 렌더링 진행 중...", end="\r")
            elif status == "IN_QUEUE":
                print("🚶‍♂️ 대기열에서 기다리는 중...", end="\r")
            else:
                print(f"⚠️ 예상치 못한 상태: {status_data}")
        time.sleep(5)

    print("\n✅ 렌더링이 완료되었습니다! 결과 데이터를 가져옵니다.")

    # 3단계: 결과 가져오기
    result_res = requests.get(response_url, headers=headers)
    if result_res.status_code != 200:
        print(f"❌ 결과 다운로드 실패: {result_res.text}")
        sys.exit(1)

    result_data = result_res.json()
    video_url = result_data.get("video", {}).get("url")

    if not video_url:
        print("❌ 결과 데이터에서 비디오 URL을 찾을 수 없습니다.")
        # 만약 dict 구조가 다르면 전체를 출력
        print(result_data)
        sys.exit(1)

    # 4단계: 비디오 파일 디스크에 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_fal_minimax_generated.mp4"
    save_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Reels_Automation")
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    print(f"📥 비디오 다운로드 중... -> {filepath}")
    urllib.request.urlretrieve(video_url, filepath)
    
    print("🎉 생성 및 다운로드 성공!")
    print(f"📁 절대 경로: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fal_video_gen.py 'YOUR_VIDEO_PROMPT_HERE'")
        sys.exit(1)
    
    prompt_input = sys.argv[1]
    # " 나 ' 제거
    prompt_input = prompt_input.strip('"\'')
    generate_video(prompt_input)
