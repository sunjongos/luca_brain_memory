import asyncio
import os
import sys

# 프로젝트 환경 설정 (.env 등 로드를 위해)
from dotenv import load_dotenv
load_dotenv()

from telegram_bot import run_agent_loop
from unittest.mock import AsyncMock, MagicMock

async def test_agent():
    print("🔄 [Test Start] Verifying Trinity Agent Loop...")
    
    # Mock Telegram Update & Context
    update = MagicMock()
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock(return_value=MagicMock(message_id=1))
    
    ctx = MagicMock()
    ctx.bot = AsyncMock()
    
    # 1. Test Perplexity Search Execution
    user_text_1 = "Perplexity로 2026년 백병원 마케팅 전략 트렌드를 한 문장으로 심층 검색해봐."
    messages_1 = [{"role": "system", "content": "You are Luca. Always use tools when asked."}, {"role": "user", "content": user_text_1}]
    
    print(f"\n[Test 1] User: {user_text_1}")
    try:
        reply_1 = await run_agent_loop(
            update=update,
            ctx=ctx,
            user_text=user_text_1,
            messages=messages_1,
            system_prompt="You are Luca.",
            model_used="gpt-4o"
        )
        print(f"✅ [Test 1 Result]\n{reply_1}")
    except Exception as e:
        print(f"❌ [Test 1 Failed] {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())
