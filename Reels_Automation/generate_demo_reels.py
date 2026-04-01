import os
import re
import asyncio
import edge_tts
from datetime import datetime
from moviepy.editor import ImageSequenceClip, AudioFileClip

today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = os.path.join(r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타", today_str)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

IMAGE_FILES = [
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\ghibli_scene_1_1774257940414.png",
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\ghibli_scene_2_1774257954498.png"
]
SCRIPT_TXT = "관절과 척추의 고질적인 통증, 더 이상 홀로 견디지 마세요. 따뜻하고 편안한 남양주백병원은 대학병원급 첨단 장비와 최선종 병원장의 압도적인 임상 경험으로 당신의 건강한 일상을 마법처럼 되찾아 드립니다. 척추 명의를 찾고 계시다면 지금 바로 예약하세요. #남양주백병원 #최선종원장 #정형외과"

OUTPUT_TTS = os.path.join(OUTPUT_DIR, "ghibli_tts.mp3")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "ghibli_reels.mp4")

# 해시태그 제거 (TTS 읽기 금지)
tts_text = re.sub(r'#\S+', '', SCRIPT_TXT).strip()

async def generate_tts(text, output_file):
    communicate = edge_tts.Communicate(text, 'ko-KR-InJoonNeural')
    await communicate.save(output_file)

def make_demo_video():
    print("▶ 1. TTS(한국어 프리미엄 남성 보이스) 렌더링 중...")
    asyncio.run(generate_tts(tts_text, OUTPUT_TTS))
    
    voice_audio = AudioFileClip(OUTPUT_TTS)
    duration = voice_audio.duration
    
    # 이미지별 노출 시간 분배
    durations = [duration / len(IMAGE_FILES)] * len(IMAGE_FILES)
    
    print("▶ 2. 시각 에셋(고화질 AI 생성 이미지) 영상 조립 중...")
    video = ImageSequenceClip(IMAGE_FILES, durations=durations)
    video = video.set_audio(voice_audio)
    
    print("▶ 3. MP4 프로덕션 최종 렌더링 중...")
    video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac", logger=None) # logger=None 으로 진행바 숨김 처리
    print(f"\n✅ 릴스 병합 100% 완료! 파일 저장 경로: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    make_demo_video()
