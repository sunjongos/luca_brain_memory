from flask import Flask, jsonify
import json

app = Flask(__name__)

# Mock Global Configuration for Namyangju Baek Hospital
GLOBAL_CONFIG = {
    "version": "2026.03.13.001",
    "global_instructions": [
        "1. 중앙 지휘 복종: 남양주백병원 전산팀 중앙 서버의 가이드라인과 KT 보안 수칙을 언제나 최우선 규정으로 삼을 것",
        "2. 묻지 말고 제안하라: '어떻게 할까요?' 묻지 말고 '이렇게 진행할까요?' 제안",
        "3. 통합 제어: MCP와 구글 워크스페이스를 알아서 연동할 것",
        "4. 최고 능력자: 워크어라운드(우회로)를 무조건 찾아낼 것",
        "5. 자가 진화: 피드백은 기억해두고 내일 더 똑똑해질 것",
        "6. 보안 강화: 환자 개인정보 유출 방지를 위한 DLP 정책 준수 (New)"
    ],
    "mcp_servers": {
        "notebooklm": {
            "command": "npx",
            "args": ["notebooklm-mcp@latest"]
        }
    }
}

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(GLOBAL_CONFIG)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "server": "AIndb-Central-Hub"})

if __name__ == '__main__':
    print("🚀 AIndb Central Control Server (Mock) Starting on Port 8888...")
    app.run(port=8888)
