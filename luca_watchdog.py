"""
Luca Watchdog - 텔레그램 봇 자동 재시작 감시자
컴퓨터 부팅 후 자동으로 실행되며, 봇이 죽으면 즉시 되살립니다.
"""

import subprocess
import sys
import time
import os
import logging
from datetime import datetime
from pathlib import Path

# ── 경로 설정
BASE_DIR = Path(__file__).parent
BOT_SCRIPT = BASE_DIR / "telegram_bot.py"
LOG_FILE = BASE_DIR / "luca_watchdog.log"
PYTHON_EXE = r"C:\Users\sunjo\AppData\Local\Programs\Python\Python313\pythonw.exe"  # 봇 실행용 (창 없음)

# ── 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("LucaWatchdog")

# ── 설정
RESTART_DELAY_SEC = 5       # 봇 죽은 후 재시작까지 대기 시간 (초)
BOOT_DELAY_SEC = 15         # 부팅 직후 초기 대기 시간 (네트워크 안정 대기)
MAX_RESTART_COUNT = 999     # 최대 재시작 횟수 (사실상 무제한)
CHECK_INTERVAL_SEC = 10     # 봇 생존 확인 주기 (초)


def start_bot() -> subprocess.Popen:
    """봇 프로세스를 시작하고 Popen 객체 반환"""
    logger.info(f"🚀 봇 시작: {BOT_SCRIPT}")
    process = subprocess.Popen(
        [PYTHON_EXE, str(BOT_SCRIPT)],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    logger.info(f"✅ 봇 PID: {process.pid}")
    return process


def main():
    logger.info("=" * 50)
    logger.info("🛡️  Luca Watchdog 시작됨!")
    logger.info(f"📁 봇 경로: {BOT_SCRIPT}")
    logger.info(f"⏳ 부팅 안정화 대기: {BOOT_DELAY_SEC}초")
    logger.info("=" * 50)

    # 부팅 직후 네트워크 안정화 대기
    time.sleep(BOOT_DELAY_SEC)

    restart_count = 0
    bot_process = start_bot()

    while restart_count < MAX_RESTART_COUNT:
        time.sleep(CHECK_INTERVAL_SEC)

        # 봇 프로세스 생존 확인
        if bot_process.poll() is not None:
            exit_code = bot_process.returncode
            restart_count += 1
            logger.warning(
                f"⚠️  봇 프로세스 종료 감지! "
                f"(종료 코드: {exit_code}, 재시작 횟수: {restart_count})"
            )
            logger.info(f"⏳ {RESTART_DELAY_SEC}초 후 재시작...")
            time.sleep(RESTART_DELAY_SEC)
            bot_process = start_bot()
        else:
            # 봇 정상 실행 중 — 매 60초마다 상태 로깅
            if int(time.time()) % 60 < CHECK_INTERVAL_SEC:
                logger.info(f"💚 봇 정상 실행 중 (PID: {bot_process.pid})")

    logger.error("❌ 최대 재시작 횟수 초과. 워치독 종료.")


if __name__ == "__main__":
    main()
