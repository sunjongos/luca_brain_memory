import os
import time
import shutil
import subprocess
from datetime import datetime

DOWNLOADS_DIR = r"C:\Users\USER\Downloads"
REELS_DEST_BASE = r"C:\Users\USER\OneDrive\바탕 화면\SNS\릴스"
MAKER_SCRIPT = r"C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\Reels_Automation\make_reels_type2.py"

def get_recent_files(exts, max_age_minutes=20):
    now = time.time()
    valid_files = []
    
    for f in os.listdir(DOWNLOADS_DIR):
        if any(f.lower().endswith(ext) for ext in exts):
            if f.endswith('.crdownload') or f.endswith('.tmp'): continue
            path = os.path.join(DOWNLOADS_DIR, f)
            try:
                age = now - os.path.getctime(path)
                if age < max_age_minutes * 60:
                    valid_files.append((path, os.path.getctime(path)))
            except:
                pass
                
    valid_files.sort(key=lambda x: x[1]) # 시간순 정렬 (먼저 받은게 앞쪽 씬)
    return [f[0] for f in valid_files]

def main():
    print("=== 🚀 [릴스 2 자동화] Flow 다운로드 감시 요원(Watcher) 가동 ===")
    print(f"👀 {DOWNLOADS_DIR} 폴더를 0.5초 단위로 예의주시하고 있습니다.")
    print("Google Labs Flow에서 완성된 [영상 1개]와 [Lyria 음악 1개]를 다운로드 해주십시오!\n")
    
    while True:
        videos = get_recent_files(['.mp4'])
        audios = get_recent_files(['.mp3', '.wav', '.m4a'])
        
        if len(videos) >= 1 and len(audios) >= 1:
            print("\n✅ Google Labs Flow 통짜 영상(MP4) & Lyria 브금(MP3) 파일 강제 포착 완료!!!")
            
            # 파일 잠금 해제 대기 (다운로드 완료 후 디스크 기록 보장)
            time.sleep(3)
            
            today = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_dir = os.path.join(REELS_DEST_BASE, f"{today}_Type2")
            os.makedirs(dest_dir, exist_ok=True)
            
            print(f"🚚 릴스 하부 아카이빙 폴더({dest_dir})를 구축하고 에셋을 진열합니다...")
            
            # 제일 오래된 것부터 1~4 씬으로 보장하도록 이동
            selected_videos = videos[:4]
            selected_audio = audios[-1] # 최근 다운된 음악 제일 후순위 배정
            
            for idx, vp in enumerate(selected_videos):
                dest_p = os.path.join(dest_dir, f"veo_scene_{idx+1}.mp4")
                shutil.move(vp, dest_p)
                
            audio_ext = os.path.splitext(selected_audio)[1]
            shutil.move(selected_audio, os.path.join(dest_dir, f"lyria_bgm{audio_ext}"))
            
            print("🔥 제미나이 렌더링 파일 이동 완벽 종료! 파이썬 릴스 조립 엔진으로 경로 권한을 넘깁니다!")
            
            # make_reels_type2.py 백그라운드 호출
            subprocess.run(["python", MAKER_SCRIPT, dest_dir])
            
            print("\n🎉 모든 파이프라인이 자동 완료되었습니다! Watcher 임무를 종료합니다.")
            break
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()
