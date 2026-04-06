import os
import re
import asyncio
import glob
import sys
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip

OUTPUT_DIR = os.path.dirname(__file__)

# Read caption script
with open(os.path.join(OUTPUT_DIR, "caption.txt"), "r", encoding="utf-8") as f:
    text = f.read()

# Extract TTS
match = re.search(r"\[TTS 스크립트\](.*?)\[인스타그램", text, re.DOTALL)
if match:
    raw_script = match.group(1)
    tts_text = re.sub(r'#\S+', '', raw_script).strip()
else:
    print("Cannot find TTS script")
    sys.exit(1)

OUTPUT_TTS = os.path.join(OUTPUT_DIR, "auto_tts_voice.mp3")

async def generate_tts():
    print("▶ Microsoft TTS (InJoonNeural) 음성 렌더링 중...")
    communicate = edge_tts.Communicate(tts_text, 'ko-KR-InJoonNeural')
    await communicate.save(OUTPUT_TTS)

asyncio.run(generate_tts())

# find newest fal generation
vids = glob.glob(os.path.join(OUTPUT_DIR, "*_fal_minimax_generated.mp4"))
if not vids:
    print("No generated video found!")
    sys.exit(1)

newest_video = max(vids, key=os.path.getctime)
print(f"▶ 비디오 채택 (Fal.ai): {os.path.basename(newest_video)}")

# if there is an existing BGM
songs = glob.glob(os.path.join(OUTPUT_DIR, "*.mp3"))
# filter out tts
bgm_songs = [s for s in songs if "tts_" not in os.path.basename(s).lower()]
newest_bgm = max(bgm_songs, key=os.path.getctime) if bgm_songs else None

# Combine
try:
    video = VideoFileClip(newest_video)
    voice = AudioFileClip(OUTPUT_TTS)
    target_dur = voice.duration

    if video.duration < target_dur:
        # fal minimax produces 5 seconds usually, but edge TTS can be longer.
        # loop video to match audio length
        # Using loop filter requires moviepy config, simpler to subclip module.
        # But `.loop` is standard in moviepy v1
        video = video.loop(duration=target_dur)
    else:
        video = video.subclip(0, target_dur)

    if newest_bgm:
        print(f"▶ BGM 발견 및 오토 믹싱 (15% 볼륨): {os.path.basename(newest_bgm)}")
        bgm = AudioFileClip(newest_bgm)
        repeats = int(target_dur / bgm.duration) + 1
        bgm_audio = concatenate_audioclips([bgm]*repeats).subclip(0, target_dur).volumex(0.15)
        final_audio = CompositeAudioClip([bgm_audio, voice])
    else:
        print("▶ BGM이 없어 목소리만 합성합니다.")
        final_audio = voice
        
    video = video.set_audio(final_audio)

    out_folder = r"C:\Users\USER\OneDrive\바탕 화면\동영상제작"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    final_out = os.path.join(out_folder, "FINAL_자동완성_2026_NDB_Together.mp4")
    print("▶ 최종 인코딩 시작 (약 1분 소요)...")
    video.write_videofile(final_out, fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"🎉 모든 자동 병합 완료! 결과물: {final_out}")
except Exception as e:
    print(f"❌ 병합 중 오류 발생: {e}")
