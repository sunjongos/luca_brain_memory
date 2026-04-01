import os
import re
import asyncio
import edge_tts
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips

import sys
import glob

# 1. 아카이빙 폴더 기본 접속 (YYYYMMDD) - 인자값으로 덮어씌워질 수 있음
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_DIR = os.path.join(r"C:\Users\USER\OneDrive\바탕 화면\SNS\인스타", today_str)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. VEO 3 비디오 에셋 및 Lyria 음악 수동 경로 설정
VEO_VIDEOS = []
LYRIA_BGM = r""

# Watcher(감시 요원)가 넘겨준 폴더 경로가 있다면 동적으로 색인
if len(sys.argv) > 1:
    target_dir = sys.argv[1]
    OUTPUT_DIR = target_dir
    all_mp4 = sorted(glob.glob(os.path.join(target_dir, "*.mp4")))
    VEO_VIDEOS = [f for f in all_mp4 if "reels_type2" not in f]
    all_audio = glob.glob(os.path.join(target_dir, "*.mp3")) + glob.glob(os.path.join(target_dir, "*.wav")) + glob.glob(os.path.join(target_dir, "*.m4a"))
    if all_audio:
        LYRIA_BGM = all_audio[0]

SCRIPT_TXT = '마음속 무거운 짐들, 이제는 잠시 내려놓을 시간입니다. 스트레스와 걱정으로 마음을 가득 채우면 긍정이 들어올 자리가 없습니다. 오늘 하루는 복잡한 생각을 비워내고 긍정의 기운으로 채워보세요. 남양주백병원 최선종 원장입니다. #남양주백병원 #최선종원장 #긍정의힘'

OUTPUT_TTS = os.path.join(OUTPUT_DIR, "type2_tts.mp3")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "reels_type2_veo.mp4")

# 해시태그 제거 (TTS 읽기 금지)
tts_text = re.sub(r'#\S+', '', SCRIPT_TXT).strip()

async def generate_tts(text, output_file):
    communicate = edge_tts.Communicate(text, 'ko-KR-InJoonNeural')
    await communicate.save(output_file)

def make_type2_reels():
    if not VEO_VIDEOS:
        print("❌ VEO 3로 렌더링된 비디오 클립 경로를 배열에 입력해주십시오.")
        return

    print("▶ 1. TTS(보이스) 렌더링 중...")
    asyncio.run(generate_tts(tts_text, OUTPUT_TTS))
    voice_audio = AudioFileClip(OUTPUT_TTS)
    
    print("▶ 2. VEO 3 고화질 무빙 비디오 클립(I2V) 연결 중...")
    clips = []
    for vp in VEO_VIDEOS:
        if os.path.exists(vp):
            clips.append(VideoFileClip(vp))
        else:
            print(f"⚠️ 경고: {vp} 비디오를 찾을 수 없습니다.")
            
    if not clips:
        print("❌ 유효한 비디오 클립이 없어 병합을 중단합니다.")
        return
        
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = voice_audio.duration
    
    # 멘트 길이에 맞춰 영상 길이 자동 조절 (반복 처리)
    if final_video.duration < video_duration:
        final_video = final_video.loop(duration=video_duration)
    else:
        final_video = final_video.subclip(0, video_duration)
    
    print("▶ 3. 오디오 오토 믹싱 중 (TTS 100% + Lyria BGM 15%)...")
    if LYRIA_BGM and os.path.exists(LYRIA_BGM):
        base_bgm = AudioFileClip(LYRIA_BGM)
        from moviepy.editor import concatenate_audioclips
        repeats = int(video_duration / base_bgm.duration) + 1
        bgm_audio = concatenate_audioclips([base_bgm] * repeats).subclip(0, video_duration).volumex(0.15)
        final_audio = CompositeAudioClip([bgm_audio, voice_audio])
    else:
        print("⚠️ Lyria BGM 경로가 비어있거나 파일을 찾을 수 없어 TTS 보이스만 삽입됩니다.")
        final_audio = voice_audio
        
    final_video = final_video.set_audio(final_audio)
    
    print("▶ 4. [릴스만들기 2] VEO 3 하이엔드 릴스 최종 MP4 프로덕션 렌더링 중...")
    final_video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"\n✅ Type 2 VEO 최고급 릴스 병합 완료! 안전 보관 경로: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    make_type2_reels()
