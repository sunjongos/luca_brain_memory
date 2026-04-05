"""
Luca Watchdog - 텔레그램 봇 및 메모리 서버 자동 재시작 감시자
컴퓨터 부팅 후 자동으로 실행되며, 프로세스가 죽으면 즉시 되살립니다.
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
PYTHON_EXE = r"C:\Users\sunjo\AppData\Local\Programs\Python\Python313\pythonw.exe"  # process without window

SERVICES_CONFIG = [
    {
        "id": "telegram_bot",
        "name": "Telegram Bot",
        "script": str(BASE_DIR / "telegram_bot.py")
    },
    {
        "id": "memory_server",
        "name": "Memory Server",
        "script": str(BASE_DIR / "memory_layer" / "memory_server.py")
    }
]

LOG_FILE = BASE_DIR / "luca_watchdog.log"

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
RESTART_DELAY_SEC = 5       # 프로세스 죽은 후 재시작까지 대기 시간 (초)
BOOT_DELAY_SEC = 15         # 부팅 직후 초기 대기 시간 (네트워크 안정 대기)
MAX_RESTART_COUNT = 999     # 최대 재시작 횟수
CHECK_INTERVAL_SEC = 10     # 프로세스 생존 확인 주기 (초)

class ServiceProcess:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.restart_count = 0

    def start(self):
        logger.info(f"🚀 {self.config['name']} 시작: {self.config['script']}")
        self.process = subprocess.Popen(
            [PYTHON_EXE, self.config["script"]],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        logger.info(f"✅ {self.config['name']} PID: {self.process.pid}")

    def check_and_restart(self):
        if self.process is None:
            return

        if self.process.poll() is not None:
            exit_code = self.process.returncode
            self.restart_count += 1
            if self.restart_count > MAX_RESTART_COUNT:
                logger.error(f"❌ {self.config['name']} 최대 재시작 횟수 초과.")
                return

            logger.warning(
                f"⚠️  {self.config['name']} 종료 감지! "
                f"(종료 코드: {exit_code}, 재시작 횟수: {self.restart_count})"
            )
            logger.info(f"⏳ {RESTART_DELAY_SEC}초 후 {self.config['name']} 재시작...")
            time.sleep(RESTART_DELAY_SEC)
            self.start()
        else:
            if int(time.time()) % 60 < CHECK_INTERVAL_SEC:
                logger.info(f"💚 {self.config['name']} 정상 실행 중 (PID: {self.process.pid})")

def main():
    logger.info("=" * 50)
    logger.info("🛡️  Luca Watchdog 시작됨!")
    logger.info(f"⏳ 부팅 안정화 대기: {BOOT_DELAY_SEC}초")
    logger.info("=" * 50)

    time.sleep(BOOT_DELAY_SEC)

    services = [ServiceProcess(cfg) for cfg in SERVICES_CONFIG]
    
    for srv in services:
        srv.start()

    while True:
        time.sleep(CHECK_INTERVAL_SEC)
        for srv in services:
            srv.check_and_restart()

if __name__ == "__main__":
    main()
