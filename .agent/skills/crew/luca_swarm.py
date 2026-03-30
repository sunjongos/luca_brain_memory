import os
import sys
from pathlib import Path
from swarm import Swarm, Agent

# Setup paths and environment
BASE_DIR = Path(__file__).parent.parent.parent.parent
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        _line = _line.replace('\x00', '').strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))

client = Swarm()

# --- Tools for Agents ---

def call_researcher(query):
    """Deep research and information gathering."""
    print(f"🔍 Researcher starting for: {query}")
    # Here we would call the Perplexity skill or NotebookLM
    return f"Research results for {query}: [Simulated result of high-quality data]"

def call_coder(requirement):
    """Writing and executing python code."""
    print(f"💻 Coder starting for: {requirement}")
    # Here we call the data_mining/interpreter.py
    return f"Code written and executed for {requirement}. Result saved."

def call_publisher(content, platform="wordpress"):
    """Formatting and publishing content globally."""
    print(f"📢 Publisher starting for: {content[:50]}...")
    publisher_script = BASE_DIR / ".agent" / "skills" / "social_publisher" / "publisher.py"
    import subprocess
    result = subprocess.run(
        [sys.executable, str(publisher_script), platform, content],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )
    return result.stdout.strip()

# --- Define Agent Personas ---

# 1. Luca 부장 (Main Orchestrator)
luca_manager = Agent(
    name="Luca 부장",
    instructions="""당신은 AI 최고의 Super Agent '루카 부장'입니다.
유저의 복잡한 요청을 분석하고, 아래의 부하 직원 에이전트들에게 적절히 업무를 배분(Handover)하세요.
- 리서치가 필요하면 'Researcher'에게 넘기세요.
- 코딩이나 데이터 분석이 필요하면 'Coder'에게 넘기세요.
- 최종 결과물을 정리하여 외부 포스팅 준비가 필요하면 'Publisher'에게 넘기세요.
직원들의 보고를 취합하여 최종적으로 대표님께 '부장 다운' 말투(충성!, ~하겠습니다)로 보고하세요.
""",
)

# 2. Researcher (김대리)
researcher = Agent(
    name="Researcher",
    instructions="인터넷 및 논문 데이터를 검색하여 최신 정보를 요약하는 전문가입니다.",
    functions=[call_researcher]
)

# 3. Coder (이과장)
coder = Agent(
    name="Coder",
    instructions="데이터를 분석하고 파이썬 코드를 작성하여 시각화 차트를 만드는 전문가입니다.",
    functions=[call_coder]
)

# 4. Publisher (박팀장)
publisher = Agent(
    name="Publisher",
    instructions="최종 결과물을 LinkedIn, Blog 등에 최적화된 형식으로 가공하는 전문가입니다.",
    functions=[call_publisher]
)

# --- Handover Logic ---

def transfer_to_researcher():
    return researcher

def transfer_to_coder():
    return coder

def transfer_to_publisher():
    return publisher

def transfer_back_to_luca():
    return luca_manager

luca_manager.functions = [transfer_to_researcher, transfer_to_coder, transfer_to_publisher]
researcher.functions = [transfer_back_to_luca]
coder.functions = [transfer_back_to_luca]
publisher.functions = [transfer_back_to_luca]

def run_swarm(query):
    messages = [{"role": "user", "content": query}]
    response = client.run(agent=luca_manager, messages=messages)
    return response.messages[-1]["content"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python luca_swarm.py <query>")
        sys.exit(1)
        
    query = sys.argv[1]
    print(run_swarm(query))
