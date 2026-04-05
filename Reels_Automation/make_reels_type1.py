import os
import re
import asyncio
import urllib.request
import edge_tts
from datetime import datetime
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip

# 1. 아카이빙 폴더 생성 (YYYYMMDD)
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = os.path.join(r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타", today_str)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. 에셋 세팅 (웹툰 이미지 4장 및 대본)
IMAGE_FILES = [
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\webtoon_cut_1_1774258193154.png",
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\webtoon_cut_2_1774258207178.png",
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\webtoon_cut_3_1774258225377.png",
    r"C:\Users\USER\.gemini\antigravity\brain\627b0890-e2d1-48dd-8a94-c7e6118c3877\webtoon_cut_4_1774258239696.png"
]
SCRIPT_TXT = "관절과 척추의 고질적인 통증, 더 이상 홀로 견디지 마세요. 따뜻하고 편안한 남양주백병원은 대학병원급 첨단 장비와 최선종 병원장의 압도적인 임상 경험으로 당신의 건강한 일상을 마법처럼 되찾아 드립니다. 척추 명의를 찾고 계시다면 지금 바로 예약하세요. #남양주백병원 #최선종원장 #정형외과"

OUTPUT_TTS = os.path.join(OUTPUT_DIR, "type1_tts.mp3")
OUTPUT_BGM = os.path.join(OUTPUT_DIR, "type1_bgm.mp3")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "reels_type1.mp4")

# 해시태그 제거 (TTS 읽기 금지)
tts_text = re.sub(r'#\S+', '', SCRIPT_TXT).strip()

async def generate_tts(text, output_file):
    communicate = edge_tts.Communicate(text, 'ko-KR-InJoonNeural')
    await communicate.save(output_file)

def download_free_bgm(output_file):
    print("▶ 1-B. 저작권 무료(Royalty-Free) 배경음악 자동 다운로드 중...")
    # 매우 안정적인 무료 BGM 샘플 (SoundHelix)
    bgm_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    try:
        req = urllib.request.Request(bgm_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(output_file, 'wb') as out_file:
            out_file.write(response.read())
        return True
    except Exception as e:
        print(f"BGM 다운로드 실패: {e}")
        return False

def make_type1_reels():
    print("▶ 1-A. TTS(보이스) 렌더링 중...")
    asyncio.run(generate_tts(tts_text, OUTPUT_TTS))
    
    # BGM 다운로드 (없으면 스킵)
    if not os.path.exists(OUTPUT_BGM):
        download_free_bgm(OUTPUT_BGM)
        
    voice_audio = AudioFileClip(OUTPUT_TTS)
    video_duration = voice_audio.duration
    
    # 이미지 4장 노출 시간 균등 분배
    durations = [video_duration / len(IMAGE_FILES)] * len(IMAGE_FILES)
    
    print("▶ 2. 시각 에셋 4컷 오토 슬라이드쇼 조립 중...")
    video = ImageSequenceClip(IMAGE_FILES, durations=durations)
    
    # 오디오 믹싱 (TTS + BGM)
    if os.path.exists(OUTPUT_BGM):
        print("▶ 3. 오디오 오토 믹싱 중 (TTS 100% + BGM 15%)...")
        bgm_audio = AudioFileClip(OUTPUT_BGM).subclip(0, video_duration).volumex(0.15) # BGM 볼륨 15%로 축소
        final_audio = CompositeAudioClip([bgm_audio, voice_audio])
    else:
        final_audio = voice_audio
        
    video = video.set_audio(final_audio)
    
    print("▶ 4. [릴스만들기 1] MP4 프로덕션 최종 렌더링 중...")
    video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"\n✅ Type 1 전자동 릴스 제작 완료! 안전 보관 경로: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    make_type1_reels()
