"""
Luca Unified Startup — Orchestrates all services on boot
Starts in order: Memory Server (5050) → Telegram Bot → Watchdog

Registered in Windows Startup folder for automatic execution on login.
"""

import subprocess
import sys
import os
import io
import time
import socket
import logging
from pathlib import Path
from datetime import datetime

# Fix cp949 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths
BASE_DIR = Path(__file__).parent
MEMORY_SERVER_DIR = BASE_DIR / "memory_layer"
MEMORY_SERVER_SCRIPT = MEMORY_SERVER_DIR / "memory_server.py"
BOT_SCRIPT = BASE_DIR / "telegram_bot.py"
LOG_FILE = BASE_DIR / "luca_unified_startup.log"
PYTHON_EXE = r"C:\Users\sunjo\AppData\Local\Programs\Python\Python313\python.exe"
PYTHONW_EXE = r"C:\Users\sunjo\AppData\Local\Programs\Python\Python313\pythonw.exe"

# ── Settings
BOOT_DELAY_SEC = 10          # Initial delay for network stability
MEMORY_PORT = 5050
MEMORY_WAIT_TIMEOUT = 60     # Max seconds to wait for memory server
MEMORY_CHECK_INTERVAL = 2    # Check every N seconds
BOT_CHECK_INTERVAL = 30      # Bot health check interval
BOT_RESTART_DELAY = 5        # Delay before restarting dead bot
MAX_BOT_RESTARTS = 999       # Effectively unlimited

# ── Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [UNIFIED] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("LucaUnified")


def is_port_open(port: int) -> bool:
    """Check if a TCP port is listening on localhost."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


def start_memory_server() -> subprocess.Popen | None:
    """Start the memory server if not already running."""
    if is_port_open(MEMORY_PORT):
        log.info(f"Memory server already running on port {MEMORY_PORT}")
        return None

    log.info(f"Starting memory server: {MEMORY_SERVER_SCRIPT}")
    proc = subprocess.Popen(
        [PYTHON_EXE, str(MEMORY_SERVER_SCRIPT)],
        cwd=str(MEMORY_SERVER_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    log.info(f"Memory server started (PID: {proc.pid})")
    return proc


def wait_for_memory_server() -> bool:
    """Wait until the memory server is accepting connections."""
    log.info(f"Waiting for memory server on port {MEMORY_PORT}...")
    elapsed = 0
    while elapsed < MEMORY_WAIT_TIMEOUT:
        if is_port_open(MEMORY_PORT):
            log.info(f"Memory server ready (waited {elapsed}s)")
            return True
        time.sleep(MEMORY_CHECK_INTERVAL)
        elapsed += MEMORY_CHECK_INTERVAL
    log.error(f"Memory server failed to start within {MEMORY_WAIT_TIMEOUT}s!")
    return False


def start_bot() -> subprocess.Popen:
    """Start the telegram bot."""
    log.info(f"Starting telegram bot: {BOT_SCRIPT}")
    proc = subprocess.Popen(
        [PYTHONW_EXE, str(BOT_SCRIPT)],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    log.info(f"Telegram bot started (PID: {proc.pid})")
    return proc


def watchdog_loop(bot_proc: subprocess.Popen):
    """Monitor bot and memory server, restart if they die."""
    restart_count = 0
    memory_proc = None

    while restart_count < MAX_BOT_RESTARTS:
        time.sleep(BOT_CHECK_INTERVAL)

        # Check memory server health
        if not is_port_open(MEMORY_PORT):
            log.warning("Memory server DOWN! Restarting...")
            memory_proc = start_memory_server()
            if not wait_for_memory_server():
                log.error("Memory server restart failed. Continuing watchdog...")

        # Check bot health
        if bot_proc.poll() is not None:
            exit_code = bot_proc.returncode
            restart_count += 1
            log.warning(
                f"Bot died (exit code: {exit_code}, restart #{restart_count})"
            )
            time.sleep(BOT_RESTART_DELAY)
            bot_proc = start_bot()
        else:
            # Periodic health log (every ~5 minutes)
            if int(time.time()) % 300 < BOT_CHECK_INTERVAL:
                log.info(f"All systems OK (bot PID: {bot_proc.pid}, memory: port {MEMORY_PORT})")

    log.error("Max bot restarts exceeded. Exiting watchdog.")


def main():
    log.info("=" * 60)
    log.info("Luca Unified Startup")
    log.info(f"Time: {datetime.now().isoformat()}")
    log.info(f"Boot delay: {BOOT_DELAY_SEC}s")
    log.info("=" * 60)

    # Phase 0: Wait for system stability
    time.sleep(BOOT_DELAY_SEC)

    # Phase 1: Start Memory Server
    log.info("--- Phase 1: Memory Server ---")
    start_memory_server()
    if not wait_for_memory_server():
        log.error("CRITICAL: Memory server unavailable. Continuing anyway...")

    # Phase 2: Start Telegram Bot
    log.info("--- Phase 2: Telegram Bot ---")
    bot_proc = start_bot()

    # Phase 3: Watchdog (monitors both)
    log.info("--- Phase 3: Watchdog Active ---")
    watchdog_loop(bot_proc)


if __name__ == "__main__":
    main()
