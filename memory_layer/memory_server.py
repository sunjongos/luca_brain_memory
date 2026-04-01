from flask import Flask, request, jsonify
import asyncio
import os
import threading
import sys
import subprocess

# Add luca_brain_memory to path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
luca_brain_path = os.path.join(base_dir, "luca_brain_memory")
if luca_brain_path not in sys.path:
    sys.path.insert(0, luca_brain_path)

import luca_brain

# Supabase Client
from supabase import create_client, Client
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ejibkgzcvfkefcpvezqi.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_kYEGWnFVMX2rQPD4swA5kA_aoSMUz1T")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[Supabase Init Error] {e}")
    supabase = None

# Inject API key globally for ADK if missing in env
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
elif "GEMINI_API_KEY" not in os.environ:
    # Fallback to the discovered API key for testing
    os.environ["GEMINI_API_KEY"] = "AIzaSyDipeFnZQS06vdO3Tt4JFhATWljJDXL-Go"

from core import build_memory_agents
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = Flask(__name__)

# Initialize Memory Agent Runner
class MemoryAgent:
    def __init__(self):
        self.agent = build_memory_agents()
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="luca_memory_layer",
            session_service=self.session_service,
        )

    async def run(self, message: str) -> str:
        session = await self.session_service.create_session(
            app_name="luca_memory_layer", user_id="luca_bot",
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=message)])
        response = ""
        async for event in self.runner.run_async(
            user_id="luca_bot", session_id=session.id, new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response += part.text
        return response

memory_agent = MemoryAgent()

# Helper function to run async methods from Flask sync context
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


import traceback
import json

def parse_json_body():
    """UTF-8로 명시적 디코딩하여 한글 등 멀티바이트 문자 지원"""
    raw = request.get_data(as_text=False)
    return json.loads(raw.decode('utf-8'))

def fire_and_forget(msg):
    def _run():
        try:
            run_async(memory_agent.run(msg))
        except Exception as e:
            print(f"[ADK Fire & Forget Error] {e}")
    threading.Thread(target=_run).start()

@app.route('/ingest', methods=['POST'])
def ingest():
    try:
        data = parse_json_body()
        text = data.get('text')
        if not text:
            return jsonify({"error": "text is required"}), 400

        msg = f"Remember this information:\n\n{text}"
        result = run_async(memory_agent.run(msg))
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/system_prompt', methods=['GET'])
def system_prompt():
    """Tier 4 동기화 요소: 현재 활성 시스템 프롬프트 반환"""
    prompt = luca_brain.get_current_system_prompt()
    return jsonify({"prompt": prompt})

@app.route('/log_interaction', methods=['POST'])
def log_interaction():
    """Tier 1~3 메인 메모리 라우터"""
    try:
        data = parse_json_body()
        chat_id = data.get('chat_id', 'unknown')
        user_msg = data.get('user_msg', '')
        ai_reply = data.get('ai_reply', '')
        model = data.get('model', 'unknown')
        has_error = data.get('has_error', False)
        error_msg = data.get('error_msg', '')
        
        # 1. Tier 1 (SQLite) 무조건 로컬 로깅
        interaction_id = luca_brain.log_interaction(chat_id, user_msg, ai_reply, model, has_error, error_msg)
        
        # 2. 중요도 판단 알고리즘
        important_keywords = ["요약", "정리", "중요", "기억", "알려줘", "환자", "예약", "광고", "설정", "이름"]
        is_important = any(kw in user_msg for kw in important_keywords) or len(user_msg) > 30

        if is_important:
            # Tier 2 (Port 5050 ADK) 장기 기억망 전송 (백그라운드)
            msg_for_adk = f"Remember this:\n[User {chat_id}]: {user_msg}\n[Luca]: {ai_reply}"
            fire_and_forget(msg_for_adk)
            
            # Tier 3 (Supabase) 클라우드 로깅
            if supabase:
                try:
                    summary = ai_reply[:100] + "..." if len(ai_reply) > 100 else ai_reply
                    supabase.table("crm_logs").insert({
                        "patient_name": f"Telegram_User_{chat_id}",
                        "stt_original": f"User: {user_msg}\nAI: {ai_reply}",
                        "ai_summary": summary,
                        "call_status": "telegram_chat"
                    }).execute()
                except Exception as e:
                    print("[Supabase Error]", e)

        return jsonify({"status": "success", "interaction_id": interaction_id})
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/github_sync', methods=['POST'])
def github_sync():
    """Tier 4: GitHub 동기화 (Pull & Push)"""
    try:
        subprocess.run(["git", "pull", "origin", "main"], cwd=luca_brain_path, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=luca_brain_path, capture_output=True, text=True)
        message = "Up to date (Pulled)"
        if status.stdout.strip():
            subprocess.run(["git", "add", "."], cwd=luca_brain_path, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-sync brain state"], cwd=luca_brain_path, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=luca_brain_path, check=True)
            message = "Synced with GitHub (Pull + Push)"
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """CALL BACK 처리를 위한 범용 웹훅 엔드포인트"""
    try:
        data = parse_json_body() if request.method == 'POST' else request.args.to_dict()
        fire_and_forget(f"Webhook Callback Received:\n{json.dumps(data, ensure_ascii=False)}")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/query', methods=['POST'])
def query():
    data = parse_json_body()
    question = data.get('question')
    if not question:
        return jsonify({"error": "question is required"}), 400

    msg = f"Query memory: {question}"
    result = run_async(memory_agent.run(msg))
    return jsonify({"status": "success", "result": result})

@app.route('/consolidate', methods=['POST'])
def consolidate():
    msg = "Consolidate all recent unconsolidated memories now."
    result = run_async(memory_agent.run(msg))
    return jsonify({"status": "success", "result": result})

def background_consolidation_loop():
    """Periodically triggers consolidation in the background"""
    import time
    while True:
        try:
            time.sleep(3600) # Once an hour
            print("[Auto-Consolidation] Triggering hourly background consolidation...")
            run_async(memory_agent.run("Consolidate all recent unconsolidated memories now."))
        except Exception as e:
            print(f"[Auto-Consolidation Error] {e}")

if __name__ == '__main__':
    # Start auto-consolidation background thread
    t = threading.Thread(target=background_consolidation_loop, daemon=True)
    t.start()
    
    print("🚀 Luca Persistent Memory Server running on port 5050")
    app.run(host='0.0.0.0', port=5050)
