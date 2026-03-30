import sqlite3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from telegram import Bot

# 환경 변수 로드
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def send_briefing():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found.")
        return

    # 가장 최근 대화한 chat_id 찾기
    db_path = Path(__file__).parent / "luca_brain.db"
    chat_id = None
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM interactions ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()
        if row:
            chat_id = row[0]
        conn.close()
    except Exception as e:
        print(f"Failed to read db: {e}")
        return

    if not chat_id:
        print("Error: No chat_id found in database.")
        return

    # walkthrough 내용 읽기
    walkthrough_path = Path(r"C:\Users\sunjo\.gemini\antigravity\brain\fd3a1eea-e16f-4bd4-a0fe-dfd0dad00709\walkthrough.md")
    if not walkthrough_path.exists():
        print("Error: walkthrough.md not found.")
        return
    
    content = walkthrough_path.read_text(encoding="utf-8")
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        # 메시지가 길 수 있으므로 분할 전송 고려 (텔레그램 제한 4096자)
        if len(content) > 4000:
            content = content[:4000] + "\n... (중략)"
        
        await bot.send_message(chat_id=chat_id, text=content)
        print(f"Successfully sent briefing to chat_id: {chat_id}")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__ == "__main__":
    asyncio.run(send_briefing())
