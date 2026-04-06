import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
sync_dir = BASE_DIR / ".brain_sync"

# 전송할 파일/디렉토리 리스트 (베이스 디렉토리 기준 상대 경로)
TARGETS = [
    "luca_memory.db",
    "luca_brain.db",
    "memory_layer/luca_memory.db",
    "Luca_Memory_Vault"
]

def run_git(args: list, cwd: Path):
    """지정된 디렉토리에서 git 명령어 실행"""
    print(f"Executing: git {' '.join(args)} in {cwd}")
    subprocess.run(["git"] + args, cwd=str(cwd), check=True)

def push_memory():
    """로컬 두뇌(DB, 봁)를 에어록에 복사 후 깃허브로 업로드"""
    print(f"🔒 [PUSH] 에어록 동기화 (로컬 -> 업로드) 엔진 점화...")
    
    # 1. 원격 최신 변경사항을 먼저 땡겨와 충돌 방지
    try:
        run_git(["pull", "origin", "main"], sync_dir)
    except subprocess.CalledProcessError:
        print("경고: 초기 pull 실패 (원격 저장소가 비어있을 수 있습니다). 무시하고 진행합니다.")

    # 2. 파일 복사
    for target in TARGETS:
        src = BASE_DIR / target
        dst = sync_dir / target
        
        if not src.exists():
            continue
            
        print(f"📂 복사 중: {src.name}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
            
    # 3. 깃허브 커밋 & 푸시
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_git(["add", "."], sync_dir)
        # 내용이 변경되었을 때만 커밋
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(sync_dir), capture_output=True, text=True)
        if status.stdout.strip():
            run_git(["commit", "-m", f"🧠 Memory sync: {now_str}"], sync_dir)
            run_git(["push", "origin", "HEAD:main"], sync_dir)
            print("✅ [성공] 루카의 두뇌가 암호화 지대에 무사히 업로드되었습니다.")
        else:
            print("💤 변경된 기억이 없습니다. 푸시 스킵.")
    except Exception as e:
        print(f"❌ 푸시 실패: {e}")

def pull_memory():
    """깃허브 에어록에서 최신 두뇌 다운로드 후 로컬 덮어쓰기"""
    print(f"🔑 [PULL] 에어록 동기화 (다운로드 -> 로컬) 엔진 점화...")
    
    # 1. 깃허브에서 최신 기억 가져오기
    try:
        run_git(["pull", "origin", "main"], sync_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ 다운로드 실패 (인터넷/저장소 연결 확인): {e}")
        return

    # 2. 로컬로 덮어쓰기 복사
    copied = False
    for target in TARGETS:
        src = sync_dir / target
        dst = BASE_DIR / target
        
        if not src.exists():
            continue
            
        print(f"📂 로컬 두뇌 이식 중: {src.name}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied = True
            
    if copied:
        print("✅ [성공] 타 지역(집/병원)에서 생성된 루카의 두뇌를 무사히 이식 완료했습니다.")
    else:
        print("❓ 가져올 파일이 없습니다. 저장소가 비어있는지 확인하세요.")

if __name__ == "__main__":
    if not sync_dir.exists():
        print(f"❌ 에러: 에어록 폴더({sync_dir.name})가 존재하지 않습니다.")
        sys.exit(1)
        
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    
    if cmd == "push":
        push_memory()
    elif cmd == "pull":
        pull_memory()
    else:
        print("사용법: python sync_brain.py [push|pull]")
