import os
import re
import asyncio
import edge_tts
from datetime import datetime
from moviepy.editor import ImageSequenceClip, VideoFileClip, AudioFileClip, CompositeAudioClip

# 1. 날짜 기반 아카이빙 폴더 생성
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = os.path.join(r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타", today_str)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. 에셋 경로 설정 (V2 표준화)
SCRIPT_FILE = os.path.join(OUTPUT_DIR, "script.txt")
IMAGE_FILES = [os.path.join(OUTPUT_DIR, "scene1.png")] # 추후 비디오 클립(veo3)으로 확장
BGM_FILE = os.path.join(OUTPUT_DIR, "bgm.mp3")

OUTPUT_TTS = os.path.join(OUTPUT_DIR, "tts_voice.mp3")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "final_reels_v2.mp4")

async def generate_tts(text, output_file):
    communicate = edge_tts.Communicate(text, 'ko-KR-InJoonNeural')
    await communicate.save(output_file)

def make_video_v2():
    print(f"=== V2.0 Cinematic Reels Pipeline Started ===")
    print(f"Target Directory: {OUTPUT_DIR}")
    
    if not os.path.exists(SCRIPT_FILE):
        print(f"⚠️ [대기] 대본 파일이 존재하지 않습니다: {SCRIPT_FILE}")
        return
        
    with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
        raw_text = f.read().strip()
        
    # [핵심] 해시태그 제거 로직 (기호 포함 단어 제거)
    tts_text = re.sub(r'#\S+', '', raw_text).strip()
        
    # 1단계: TTS 생성 (메인 보이스)
    print("1. Generating Premium TTS Voice...")
    asyncio.run(generate_tts(tts_text, OUTPUT_TTS))
    
    voice_audio = AudioFileClip(OUTPUT_TTS)
    audio_duration = voice_audio.duration
    
    # 2단계: 오디오 믹싱 (BGM + Voice)
    final_audio = voice_audio
    print("2. Audio Auto Switching/Mixing...")
    if os.path.exists(BGM_FILE):
        bgm_audio = AudioFileClip(BGM_FILE)
        # BGM 길이를 보이스 길이에 맞추거나 루프 처리, 볼륨을 0.3으로 낮춰 잔잔하게
        bgm_audio = bgm_audio.volumex(0.3).set_duration(audio_duration)
        final_audio = CompositeAudioClip([bgm_audio, voice_audio])
    else:
        print("  - BGM 파일이 없어 보이스만 사용합니다.")

    # 3단계: 시각 에셋 연결
    valid_images = [img for img in IMAGE_FILES if os.path.exists(img)]
    if not valid_images:
        print("⚠️ [대기] 시각 에셋(이미지/비디오)이 폴더에 없습니다.")
        return

    print("3. Visual Asset Rendering & Syncing...")
    duration_per_asset = audio_duration / len(valid_images)
    durations = [duration_per_asset] * len(valid_images)
    
    try:
        video = ImageSequenceClip(valid_images, durations=durations)
        video = video.set_audio(final_audio)
        
        print("4. Mastering final_reels_v2.mp4...")
        video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
        print(f"\n✅ V2.0 영상 제작 완료! 경로: {OUTPUT_VIDEO}")
    except Exception as e:
        print("❌ 렌더링 치명적 오류:", e)

if __name__ == "__main__":
    make_video_v2()
