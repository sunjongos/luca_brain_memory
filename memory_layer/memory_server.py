from flask import Flask, request, jsonify
import asyncio
import os
import sys
import io
import threading

# Fix cp949 encoding on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

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

@app.route('/ingest', methods=['POST'])
def ingest():
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({"error": "text is required"}), 400
        
        msg = f"Remember this information:\n\n{text}"
        result = run_async(memory_agent.run(msg))
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/query', methods=['POST'])
def query():
    data = request.json
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
