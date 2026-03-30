import os
import asyncio
import json
import websockets
import base64
from pathlib import Path

# Setup paths and environment
BASE_DIR = Path(__file__).parent.parent.parent.parent
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        _line = _line.replace('\x00', '').strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def start_voice_chat():
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        print("🎙️ Luca Real-time Voice 연결됨! 말씀해 주세요...")
        
        # Initial Session Setup
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "당신은 AI 최고의 Super Agent '루카 부장'입니다. 사용자와 실시간 음성으로 대화합니다. 충성스러운 부장님 말투를 쓰세요.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {"type": "server_vad"}
            }
        }
        await ws.send(json.dumps(config))

        async def receive_events():
            async for message in ws:
                event = json.loads(message)
                if event["type"] == "response.audio.delta":
                    # In a real app, send this to speakers via sounddevice
                    print("🎵 [Audio Received]", end="", flush=True)
                elif event["type"] == "response.audio_transcript.delta":
                    print(f"🗨️ Luca: {event['delta']}", end="", flush=True)
                elif event["type"] == "input_audio_buffer.speech_started":
                    print("\n👂 듣고 있습니다...")
                elif event["type"] == "error":
                    print(f"\n❌ Error: {event['error']}")

        await receive_events()

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY가 없습니다.")
    else:
        try:
            asyncio.run(start_voice_chat())
        except KeyboardInterrupt:
            print("\n👋 음성 대화 종료")
