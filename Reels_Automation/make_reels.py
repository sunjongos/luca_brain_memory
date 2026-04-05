import os
import asyncio
import edge_tts
from moviepy.editor import ImageSequenceClip, AudioFileClip
from datetime import datetime

# 오늘 날짜로 폴더명 생성
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = os.path.join(r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타", today_str)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

SCRIPT_FILE = r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타\이순태교수_부친상_추모글.txt"
OUTPUT_AUDIO = os.path.join(OUTPUT_DIR, "tts_audio.mp3")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "final_reels.mp4")
IMAGE_FILES = [r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타\이순태교수_이름추가.png"]

async def generate_tts(text, output_file):
    # 'ko-KR-InJoonNeural' is a professional Korean male voice
    communicate = edge_tts.Communicate(text, 'ko-KR-InJoonNeural')
    await communicate.save(output_file)

def make_video():
    if not os.path.exists(SCRIPT_FILE):
        print(f"Error: {SCRIPT_FILE} not found.")
        return
        
    with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
        text = f.read().strip()
        
    print("Generating TTS audio...")
    asyncio.run(generate_tts(text, OUTPUT_AUDIO))
    
    print("Loading audio...")
    audio = AudioFileClip(OUTPUT_AUDIO)
    audio_duration = audio.duration
    
    valid_images = [img for img in IMAGE_FILES if os.path.exists(img)]
    if not valid_images:
        print("No valid images found in current directory:", os.getcwd())
        return

    duration_per_image = audio_duration / len(valid_images)
    print(f"Creating video with {len(valid_images)} images, total length: {audio_duration:.2f}s")
    
    durations = [duration_per_image] * len(valid_images)
    try:
        video = ImageSequenceClip(valid_images, durations=durations)
        video = video.set_audio(audio)
        
        print("Writing final video...")
        video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
        print("Video generation complete:", OUTPUT_VIDEO)
    except Exception as e:
        print("Error during video synthesis:", e)

if __name__ == "__main__":
    make_video()
