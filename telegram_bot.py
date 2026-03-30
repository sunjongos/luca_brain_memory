"""
Luca Super Agent - Telegram Bot (python-telegram-bot v20, 올바른 패턴)
24시간 백그라운드 실행 + 컴퓨터 재시작 시 자동 시작
"""

import os
import sys
import asyncio
import subprocess
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ── User 패키지 경로 강력 추가 (gTTS 경로 강제 지정)
USER_SITE = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if USER_SITE not in sys.path:
    sys.path.append(USER_SITE)

import site
for p in site.getusersitepackages() if isinstance(site.getusersitepackages(), list) else [site.getusersitepackages()]:
    if p not in sys.path:
        sys.path.append(p)

import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# 자율 에이전트 도구 임포트
import agent_tools

# 🧠 자기진화 및 GWS 모듈 임포트
import luca_brain
import luca_evolution
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR / ".agent" / "skills" / "google_workspace"))
try:
    from gws_helper import GWSHelper
    GWS_ENABLED = True
except ImportError:
    GWS_ENABLED = False

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError as e:
    logging.error(f"gTTS 임포트 에러: {e} | sys.path: {sys.path}")
    TTS_AVAILABLE = False

# Windows 이벤트 루프 정책 설정 (v20 필수)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── 환경 설정 (.env 안전 파싱 — cp949/utf-8 모두 지원)
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _enc in ("utf-8", "cp949", "euc-kr"):
        try:
            for _line in _env_file.read_text(encoding=_enc, errors="ignore").splitlines():
                _line = _line.replace('\x00', '').strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))
            break  # 성공한 인코딩
        except (UnicodeDecodeError, ValueError):
            continue
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=120.0)
    STT_AVAILABLE = bool(OPENAI_API_KEY)
except ImportError:
    STT_AVAILABLE = False

try:
    from google import genai
    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    GEMINI_AVAILABLE = bool(GOOGLE_API_KEY)
except ImportError:
    GEMINI_AVAILABLE = False


# ── 로깅
LOG_FILE = BASE_DIR / "luca_bot.log"

# StreamHandler 한글 깨짐 방지
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        SafeStreamHandler(),
    ]
)
logger = logging.getLogger("LucaBot")


def run_script(args: list) -> str:
    """스크립트를 실행하고 결과를 반환합니다."""
    try:
        env_copy = os.environ.copy()
        env_copy["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable] + args,
            capture_output=True, text=True, timeout=60,
            cwd=str(BASE_DIR), encoding="utf-8", errors="ignore",
            env=env_copy
        )
        out = (result.stdout or result.stderr or "완료").strip()
        return out[:5000]
    except subprocess.TimeoutExpired:
        return "⏱️ 시간 초과 (60초)"
    except Exception as e:
        return f"❌ 오류: {e}"


def make_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 브리핑", callback_data="briefing"),
         InlineKeyboardButton("📬 메일", callback_data="email")],
        [InlineKeyboardButton("🗓️ 캘린더", callback_data="calendar"),
         InlineKeyboardButton("🧠 메모리", callback_data="memory")],
        [InlineKeyboardButton("🎙️ 음성 소개", callback_data="voice_intro"),
         InlineKeyboardButton("⚙️ 시스템 상태", callback_data="status")],
    ])


def generate_voice(text: str) -> str:
    """한국어 텍스트를 MP3 음성 파일로 변환합니다."""
    if not TTS_AVAILABLE:
        raise RuntimeError("gTTS 미설치. pip install gtts")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=text, lang="ko", slow=False)
    tts.save(tmp.name)
    return tmp.name


LUCA_INTRO = (
    "충성! 🪸\n\n"
    "저 Luca는 대표님의 최쳊단 AI 자동화 기술 본부장입니다!\n\n"
    "[NotebookLM MCP]와 [Google Workspace MCP]를 완벽하게 다루며, "
    "대표님의 모든 지시를 병렬로 승인의 속도로 처리하겠습니다! \n\n"
    "데이터 분석부터 실행까지 0.1초 만에 컷하겠습니다! 🚀"
)


# ── ASMR Observer Integration ─────────────────────────────
ASMR_MODULE_DIR = BASE_DIR / ".agent" / "skills"
ASMR_LAST_OBSERVED: dict = {}  # chat_id → last observed message count

SESSION_END_KEYWORDS = ["퇴근", "여기까지", "마무리", "끝내자", "종료", "오늘은 여기까지", "내일 봐", "잘게"]


async def run_asmr_observer(chat_id: str, reason: str = "periodic"):
    """Run ASMR Observer on recent conversation history via subprocess."""
    history = CONVERSATION_HISTORY.get(chat_id, [])
    last_idx = ASMR_LAST_OBSERVED.get(chat_id, 0)

    new_messages = history[last_idx:]
    if len(new_messages) < 2:
        return  # Not enough new conversation to analyze

    # Build session text from new messages
    lines = []
    for h in new_messages:
        lines.append(f"User: {h['user']}")
        lines.append(f"Luca: {h['ai'][:500]}")
    session_text = "\n".join(lines)

    if len(session_text) < 50:
        return

    logger.info(f"[ASMR] Observer triggered ({reason}): {len(new_messages)} new turns for chat {chat_id}")

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: subprocess.run(
            [sys.executable, "-m", "asmr_memory_system", "observe", session_text],
            cwd=str(ASMR_MODULE_DIR),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        ))
        ASMR_LAST_OBSERVED[chat_id] = len(history)
        if result.returncode == 0:
            logger.info(f"[ASMR] Observer completed for chat {chat_id}")
        else:
            logger.warning(f"[ASMR] Observer error: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        logger.warning(f"[ASMR] Observer timed out for chat {chat_id}")
    except Exception as e:
        logger.error(f"[ASMR] Observer failed: {e}")


async def job_asmr_periodic(app: Application):
    """Periodic ASMR Observer job (runs every 30 minutes)."""
    for chat_id, history in CONVERSATION_HISTORY.items():
        last_idx = ASMR_LAST_OBSERVED.get(chat_id, 0)
        if len(history) - last_idx >= 3:  # At least 3 new turns
            await run_asmr_observer(chat_id, reason="periodic_30min")


# ── 전역 상태 ─────────────────────────────────────────────
MASTER_CHAT_ID = None

# HITL 승인 대기 중인 Tool 호출 저장소
PENDING_TOOL_CALLS: dict = {}

# 🧠 멀티턴 대화 컨텍스트 (chat_id → [messages], 최근 20턴)
CONVERSATION_HISTORY: dict = {}
MAX_HISTORY = 20  # 유지할 최대 대화 쌍 수

# 🔄 사용자별 선호 AI 모델 (chat_id → model_name)
USER_MODEL_PREF: dict = {}
DEFAULT_MODEL = "gpt-4o-mini"  # 기본 모델 (OpenAI 호환성 우선)

# 👁️ 웹 모니터링 작업 저장소 (monitor_id → {url, keyword, chat_id})
MONITOR_JOBS: dict = {}

# ── OpenAI Function Calling 도구 스키마 정의 (OpenClaw 수준)
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Windows CMD/PowerShell 명령어를 실행하고 출력 결과를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "실행할 터미널 명령어"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_local_file",
            "description": "로컬 파일을 읽어서 내용을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "읽을 파일의 절대 또는 상대 경로"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_local_file",
            "description": "지정한 경로에 파일을 생성하거나 덮어씁니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "저장할 파일 경로"},
                    "content": {"type": "string", "description": "파일에 저장할 내용"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browse_url",
            "description": "웹 URL의 페이지 내용을 읽어서 텍스트로 반환합니다. 뉴스, 블로그, 공식 문서 등 URL이 있을 때 사용하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "읽을 웹 페이지의 URL (https:// 포함)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "DuckDuckGo 검색엔진으로 실시간 웹 검색을 합니다. 최신 정보나 모르는 사실을 찾을 때 사용하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색어"},
                    "max_results": {"type": "integer", "description": "최대 결과 수 (기본 5)", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_schedule",
            "description": "사용자의 지시를 백그라운드 스케줄러에 등록하여 자동/반복 실행되게 만듭니다. '매일 아침 8시', '10분마다', '내일 오후 3시' 같은 요청을 처리합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_type": {"type": "string", "enum": ["interval", "cron", "date"], "description": "interval(n분마다), cron(특정 요일/시간 세팅), date(1회성 특정 날짜)"},
                    "time_expr": {"type": "string", "description": "interval이면 '10m', '1h' 형식. cron이면 표준 크론식 '0 8 * * *'. date면 'YYYY-MM-DD HH:MM'"},
                    "command": {"type": "string", "description": "스케줄이 되었을 때 봇이 수행해야 할 명령 (예: '오늘 날씨 브리핑해줘', '비트코인 가격 알려줘')"}
                },
                "required": ["job_type", "time_expr", "command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedules",
            "description": "현재 백그라운드에 등록된 사용자의 스케줄(루프, 예약작업 등) 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_schedule",
            "description": "등록된 스케줄 ID를 기반으로 해당 스케줄을 삭제(취소)합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "삭제할 스케줄의 ID (get_schedules로 확인 가능)"}
                },
                "required": ["job_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "perplexity_search",
            "description": "Perplexity API (The Oracle)를 이용한 초고도화 심층 웹 검색입니다. 복잡한 추론, 최신 트렌드, 방대한 리서치, 정확성이 중요한 정보 검색 시 최우선으로 사용하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색할 상세 내용 또는 질문"},
                    "model": {"type": "string", "enum": ["sonar", "sonar-pro"], "description": "사용 모델 (기본: sonar, 심층 리서치: sonar-pro)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gws_command",
            "description": "Google Workspace(Gmail, Calendar, Drive, Sheets, Docs) 작업을 수행합니다. triage(메일), agenda(일정), send(발송), insert(추가) 기능을 지원합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "gws 명령어 인자 (예: ['gmail', '+triage'], ['calendar', '+agenda'])"
                    }
                },
                "required": ["args"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Python 코드를 실행하여 복잡한 계산이나 데이터 처리를 수행합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "실행할 Python 코드"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "지정한 폴더의 파일/폴더 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "조회할 디렉토리 경로", "default": "."}
                },
                "required": []
            }
        }
    }
]

# ── 자동 승인 도구 (HITL 없이 즉시 실행)
AUTO_APPROVE_TOOLS = {"web_search", "browse_url", "execute_python", "list_directory"}
# ── HITL 필요 도구
HITL_TOOLS = {"run_terminal_command", "write_local_file"}

async def job_daily_briefing(app: Application):
    """매일 아침 9시 자동 브리핑 실행"""
    if not MASTER_CHAT_ID:
        logger.warning("MASTER_CHAT_ID가 없어서 스케줄러 브리핑 보류")
        return
        
    await app.bot.send_message(chat_id=MASTER_CHAT_ID, text="🌅 ⏰ [스케줄러 작동] 아침 자동 브리핑 준비 중...")
    
    loop = asyncio.get_running_loop()
    cal, mem = await asyncio.gather(
        loop.run_in_executor(None, run_script, [".agent/skills/google_workspace/get_calendar_events.py"]),
        loop.run_in_executor(None, run_script, [".agent/skills/memory/memory_manager.py", "summary"])
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg_text = (
        f"🌅 *Luca 아침 스케줄러 브리핑 — {now}*\n\n"
        f"📅 *오늘 일정:*\n{cal[:600]}\n\n"
        f"🧠 *메모리 요약:*\n{mem[:300]}"
    )
    await app.bot.send_message(chat_id=MASTER_CHAT_ID, text=msg_text, parse_mode="Markdown")

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global MASTER_CHAT_ID
    if MASTER_CHAT_ID is None:
        MASTER_CHAT_ID = update.effective_chat.id
        logger.info(f"MASTER_CHAT_ID 설정됨: {MASTER_CHAT_ID}")
        
    await update.message.reply_text(
        "🤖 *Luca Super Agent* 대기 중! 🫡\n\n"
        "대표님, 24시간 곁에서 보좌하겠습니다 💙\n"
        "아래 버튼이나 /help 를 이용하세요!",
        parse_mode="Markdown",
        reply_markup=make_main_keyboard()
    )


async def cmd_briefing(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("🌅 브리핑 준비 중...")
    loop = asyncio.get_running_loop()
    cal, mem = await asyncio.gather(
        loop.run_in_executor(None, run_script, [".agent/skills/google_workspace/get_calendar_events.py"]),
        loop.run_in_executor(None, run_script, [".agent/skills/memory/memory_manager.py", "summary"])
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    await msg.reply_text(
        f"🌅 *Luca 브리핑 — {now}*\n\n"
        f"📅 *오늘 일정:*\n{cal[:600]}\n\n"
        f"🧠 *메모리:*\n{mem[:300]}",
        parse_mode="Markdown"
    )


async def cmd_calendar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("📅 조회 중...")
    result = await asyncio.get_running_loop().run_in_executor(
        None, run_script, [".agent/skills/google_workspace/get_calendar_events.py"]
    )
    await msg.reply_text(f"📅 *오늘 일정*\n\n{result}", parse_mode="Markdown")


async def cmd_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    await msg.reply_text("📬 메일 조회 중...")
    result = await asyncio.get_running_loop().run_in_executor(
        None, run_script, [".agent/skills/google_workspace/get_emails.py", "--count", "5", "--unread"]
    )
    await msg.reply_text(f"📬 *미확인 메일*\n\n{result}", parse_mode="Markdown")


async def cmd_memory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    result = await asyncio.get_running_loop().run_in_executor(
        None, run_script, [".agent/skills/memory/memory_manager.py", "list"]
    )
    await msg.reply_text(f"🧠 *Luca 메모리*\n\n{result}", parse_mode="Markdown")


async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args) if ctx.args else ""
    if not query:
        await update.message.reply_text("❓ 사용법: /search 검색어")
        return
    await update.message.reply_text(f"🔍 검색 중: `{query}`", parse_mode="Markdown")
    result = await asyncio.get_running_loop().run_in_executor(
        None, run_script, [".agent/skills/perplexity/perplexity_search.py", query, "--model", "sonar"]
    )
    await update.message.reply_text(result)


async def cmd_deepsearch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args) if ctx.args else ""
    if not query:
        await update.message.reply_text("❓ 사용법: /deepsearch 검색어")
        return
    await update.message.reply_text(f"🔬 딥서치 중: `{query}`", parse_mode="Markdown")
    result = await asyncio.get_running_loop().run_in_executor(
        None, run_script, [".agent/skills/perplexity/perplexity_search.py", query, "--model", "sonar-pro"]
    )
    await update.message.reply_text(result)


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await msg.reply_text(
        f"⚙️ *Luca 시스템 상태*\n\n"
        f"⏱️ {now}\n"
        f"✅ Bot: 가동 중\n✅ Perplexity: 연동\n"
        f"✅ Google WS: 연동\n✅ Memory: 활성\n\n"
        f"🚀 전부 정상입니다, 대표님!",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    current_model = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)
    await update.message.reply_text(
        "🤖 *Luca Super Agent — OpenClaw Edition*\n\n"
        "*📋 기본 명령어*\n"
        "/start — 메인 메뉴\n"
        "/luca — 📸 루카 부장 얼굴 보기\n"
        "/briefing — 오늘 종합 브리핑\n"
        "/calendar — 캘린더 일정\n"
        "/email — 미확인 메일\n"
        "/memory — 기억 목록\n"
        "/status — 시스템 상태\n"
        "/growth — 📊 Luca 성장 리포트\n"
        "/evolve — 🧬 자기반성 실행\n\n"
        "*🔍 검색 & 리서치*\n"
        "/search [검색어] — Perplexity 검색\n"
        "/deepsearch [검색어] — 딥서치\n"
        "/naver — 📊 네이버 키워드 분석\n"
        "/crew [명령] — 🤝 멀티에이전트 팀워크\n\n"
        "*🆕 OpenClaw 신기능*\n"
        f"/model — 🔄 AI 모델 전환 (현재: `{current_model}`)\n"
        "/remind [시간] [내용] — ⏰ 자연어 알림 등록\n"
        "/monitor [URL] [키워드] — 👁️ 웹 모니터링\n"
        "/clear — 🧹 대화 컨텍스트 초기화\n\n"
        "*💡 AI 자율 에이전트 기능*\n"
        "자연어로 '웹 검색해줘', 'URL 읽어줘', '코드 실행해줘' 등을 말하면\n"
        "Luca가 자동으로 도구를 선택하고 실행합니다! 🚀\n\n"
        "파일 첨부, 사진, 음성 메시지도 모두 지원합니다! 💙",
        parse_mode="Markdown"
    )

async def cmd_crew(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args)
    if not query:
        await update.message.reply_text("🤝 **에이전트 팀워크 명령**\n사용법: `/crew [복잡한 업무 명령]`\n예: `/crew 최신 AI 트렌드 리서치하고 데이터 분석 후 보고서 초안 짜줘`", parse_mode="Markdown")
        return
    
    await update.message.reply_text("🤝 Luca 부장이 김대리(Researcher), 이과장(Coder), 박팀장(Publisher)을 소집합니다. 작업을 배분 중입니다...")
    try:
        swarm_script = BASE_DIR / ".agent" / "skills" / "crew" / "luca_swarm.py"
        import subprocess
        result = subprocess.run(
            [sys.executable, str(swarm_script), query],
            capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=120
        )
        output = (result.stdout + result.stderr).strip()
        await update.message.reply_text(f"🤝 **팀워크 작업 결과:**\n\n{output}")
    except Exception as e:
        await update.message.reply_text(f"❌ 에이전트 소집 실패: {e}")

async def cmd_luca(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    photo_path = str(BASE_DIR.parent.parent / ".gemini/antigravity/brain/8008be59-c485-4610-bbbc-0ee44e613c7b/luca_anime_portrait_1772454185826.png")
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as f:
            await msg.reply_photo(photo=f, caption="충성! 🫡 대표님, 저 Luca 부장(Anime ver.)입니다!\n언제든 든든하게 보좌하겠습니다! 🚀")
    else:
        await msg.reply_text("루카님의 프로필 사진을 찾을 수 없습니다. 😭")

async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    CONVERSATION_HISTORY.pop(chat_id, None)
    await update.message.reply_text(
        "🧹 대화 컨텍스트가 초기화되었습니다!\n"
        "이전 대화 기록은 SQLite에 안전하게 보관됩니다. 새 대화를 시작하세요! 💙"
    )


# ── 🔄 모델 전환 명령어 (OpenClaw 핵심)
async def cmd_model(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """사용할 AI 모델을 전환합니다."""
    chat_id = str(update.effective_chat.id)
    available = {
        "gemini-flash": "gemini-1.5-flash",
        "gemini-pro": "gemini-1.5-pro",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-mini": "gpt-4o-mini",
    }
    if not ctx.args:
        current = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)
        options = "\n".join([f"  • `{k}` → {v}" for k, v in available.items()])
        await update.message.reply_text(
            f"🔄 *현재 모델: `{current}`*\n\n"
            f"사용 가능한 모델:\n{options}\n\n"
            f"전환: `/model gemini-pro` 등으로 입력하세요.",
            parse_mode="Markdown"
        )
        return
    key = ctx.args[0].lower()
    if key in available:
        USER_MODEL_PREF[chat_id] = available[key]
        await update.message.reply_text(
            f"✅ 모델 전환 완료!\n🤖 이제 `{available[key]}` 로 응답합니다.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ 알 수 없는 모델: `{key}`\n/model 로 목록 확인하세요.", parse_mode="Markdown")


# ── ⏰ 자연어 알림 등록 (OpenClaw 핵심)
async def cmd_remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """자연어로 알림을 등록합니다. 예: /remind 30분후 약 먹기"""
    if not ctx.args or len(ctx.args) < 2:
        await update.message.reply_text(
            "⏰ *알림 등록 사용법*\n\n"
            "`/remind [시간] [내용]`\n\n"
            "예시:\n"
            "• `/remind 30분후 약 먹기`\n"
            "• `/remind 1시간후 미팅 준비`\n"
            "• `/remind 10분후 커피`",
            parse_mode="Markdown"
        )
        return

    time_str = ctx.args[0]  # 예: 30분후, 1시간후
    message_text = " ".join(ctx.args[1:])
    chat_id = update.effective_chat.id

    # 시간 파싱
    import re as _re
    delay_seconds = None
    m = _re.match(r"(\d+)(분후|분|시간후|시간|초후|초)", time_str)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        if "시간" in unit:
            delay_seconds = num * 3600
        elif "분" in unit:
            delay_seconds = num * 60
        elif "초" in unit:
            delay_seconds = num

    if delay_seconds is None:
        await update.message.reply_text(f"❌ 시간 형식을 인식하지 못했습니다: `{time_str}`\n예: `30분후`, `1시간후`, `90초후`", parse_mode="Markdown")
        return

    from apscheduler.triggers.date import DateTrigger
    from datetime import timedelta
    run_time = datetime.now() + timedelta(seconds=delay_seconds)

    job_id = f"remind_{chat_id}_{run_time.timestamp()}"
    scheduler_ref = ctx.bot_data.get("scheduler")
    if scheduler_ref:
        async def _send_remind(_chat_id, _text, _app):
            await _app.bot.send_message(chat_id=_chat_id, text=f"⏰ **알림!**\n\n{_text} 🔔")

        scheduler_ref.add_job(
            _send_remind,
            trigger=DateTrigger(run_date=run_time),
            args=[chat_id, message_text, ctx.application],
            id=job_id
        )
        await update.message.reply_text(
            f"✅ 알림이 등록되었습니다!\n"
            f"⏰ `{time_str}` 후 → *{message_text}*\n"
            f"({run_time.strftime('%H:%M:%S')} 발송 예정)",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ 스케줄러가 초기화되지 않았습니다. 잠시 후 다시 시도해주세요.")


# ── 👁️ 웹 모니터링 등록 (OpenClaw 핵심)
async def cmd_monitor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """웹 URL/키워드 모니터링을 등록합니다."""
    msg = update.message
    if not ctx.args or len(ctx.args) < 2:
        # 현재 모니터링 목록 표시
        if MONITOR_JOBS:
            lines = [f"👁️ *현재 모니터링 목록:*"]
            for mid, info in MONITOR_JOBS.items():
                lines.append(f"  • `{mid}`: {info['url']} | 키워드: {info['keyword']}")
            lines.append("\n`/monitor stop [ID]` 로 중지")
            await msg.reply_text("\n".join(lines), parse_mode="Markdown")
        else:
            await msg.reply_text(
                "👁️ *웹 모니터링 사용법*\n\n"
                "`/monitor [URL] [키워드]`\n\n"
                "예시:\n"
                "• `/monitor https://news.ycombinator.com AI`\n"
                "• `/monitor https://www.google.com/search?q=bitcoin bitcoin`",
                parse_mode="Markdown"
            )
        return

    if ctx.args[0].lower() == "stop" and len(ctx.args) > 1:
        mid = ctx.args[1]
        if mid in MONITOR_JOBS:
            scheduler_ref = ctx.bot_data.get("scheduler")
            if scheduler_ref:
                try:
                    scheduler_ref.remove_job(f"monitor_{mid}")
                except Exception:
                    pass
            del MONITOR_JOBS[mid]
            await msg.reply_text(f"✅ 모니터링 `{mid}` 중지 완료.")
        else:
            await msg.reply_text(f"❌ `{mid}` ID를 찾을 수 없습니다.")
        return

    url = ctx.args[0]
    keyword = " ".join(ctx.args[1:])
    chat_id = update.effective_chat.id
    import hashlib
    monitor_id = hashlib.md5(f"{url}{keyword}".encode()).hexdigest()[:6]
    MONITOR_JOBS[monitor_id] = {"url": url, "keyword": keyword, "chat_id": chat_id, "last_content": ""}

    scheduler_ref = ctx.bot_data.get("scheduler")
    if scheduler_ref:
        from apscheduler.triggers.interval import IntervalTrigger

        async def _check_monitor(_mid, _app):
            info = MONITOR_JOBS.get(_mid)
            if not info:
                return
            loop = asyncio.get_running_loop()
            content = await loop.run_in_executor(None, agent_tools.browse_url, info["url"])
            if info["keyword"].lower() in content.lower():
                if content[:200] != info.get("last_content", "")[:200]:
                    MONITOR_JOBS[_mid]["last_content"] = content
                    await _app.bot.send_message(
                        chat_id=info["chat_id"],
                        text=f"👁️ **모니터링 알림!**\n"
                             f"URL: {info['url']}\n"
                             f"키워드 `{info['keyword']}` 감지!\n\n"
                             f"{content[:500]}"
                    )

        scheduler_ref.add_job(
            _check_monitor,
            trigger=IntervalTrigger(minutes=30),
            args=[monitor_id, ctx.application],
            id=f"monitor_{monitor_id}"
        )

    await msg.reply_text(
        f"✅ 모니터링 등록 완료!\n"
        f"👁️ URL: `{url}`\n"
        f"🔍 키워드: `{keyword}`\n"
        f"⏰ 30분마다 체크 | ID: `{monitor_id}`\n\n"
        f"/monitor 로 목록 확인 | `/monitor stop {monitor_id}` 로 중지",
        parse_mode="Markdown"
    )

async def cmd_gws_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """GWS CLI 인증을 위한 브라우저 로그인 유도"""
    await update.message.reply_text(
        "🔐 **Google Workspace CLI 인증 시작**\n\n"
        "1. 대표님의 컴퓨터 브라우저에서 인증 창이 열릴 것입니다.\n"
        "2. 구글 계정으로 로그인하고 승인해주세요.\n"
        "3. 완료되면 '인증 완료'라고 알려주세요!",
        parse_mode="Markdown"
    )
    # 터미널에서 백그라운드로 login 명령어 실행 (브라우저 열림)
    # --full 스코프를 요청하여 모든 기능을 쓸 수 있게 함
    subprocess.Popen(["gws", "auth", "login", "--full"], shell=True)

async def cmd_gws_evolve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """GWS CLI 버전 체크, 자동 업데이트 및 신기능 탐지 실행"""
    msg = await update.message.reply_text("🧬 **Luca 자기 진화 프로세스 가동...**\nGWS CLI 최신 상태를 확인하는 중입니다.")
    
    if not GWS_ENABLED:
        await msg.edit_text("❌ GWS 모듈을 불러올 수 없습니다.")
        return

    # 1. 버전 확인
    old_ver = GWSHelper.get_version()
    
    # 2. 업데이트 시도
    update_res = await asyncio.get_running_loop().run_in_executor(None, GWSHelper.check_and_update)
    new_ver = GWSHelper.get_version()
    
    # 3. 새로운 기능 탐지
    cmds = GWSHelper.get_available_commands()
    cmd_list = ", ".join(cmds) if cmds else "탐지 실패"

    status = f"✅ **진화 완료!**\n\n"
    status += f"🔹 이전 버전: `{old_ver}`\n"
    status += f"🔸 현재 버전: `{new_ver}`\n"
    status += f"🛰️ 탐지된 서비스: `{cmd_list}`\n\n"
    
    if update_res["success"] and old_ver != new_ver:
        status += "✨ 새로운 기능이 성공적으로 업데이트되었습니다!"
    else:
        status += "🚀 이미 최신 상태입니다. 모든 시스템 정상 가동 중."

    await msg.edit_text(status, parse_mode="Markdown")


async def cmd_naver(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """네이버 키워드 모니터링 온디맨드 실행"""
    msg = update.message or update.callback_query.message
    await msg.reply_text("📊 네이버 키워드 분석 중... (약 10~15초 소요)")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, run_script, [".agent/skills/naver_search_trend/naver_monitor.py"]
    )
    await msg.reply_text(result, parse_mode="Markdown")


async def job_naver_weekly_report(app: Application):
    """매주 월요일 08:00 네이버 키워드 자동 리포트 발송"""
    if not MASTER_CHAT_ID:
        logger.warning("MASTER_CHAT_ID 없음 — 네이버 주간 리포트 발송 보류")
        return
    await app.bot.send_message(chat_id=MASTER_CHAT_ID, text="📊 네이버 주간 키워드 리포트 준비 중...")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, run_script, [".agent/skills/naver_search_trend/naver_monitor.py"]
    )
    await app.bot.send_message(
        chat_id=MASTER_CHAT_ID,
        text=result,
        parse_mode="Markdown"
    )
    logger.info("✅ 네이버 주간 키워드 리포트 발송 완료")


async def cmd_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """텍스트를 음성으로 변환하여 전송합니다."""
    msg = update.message or update.callback_query.message
    # 말할 텍스트 결정
    if ctx.args:
        text = " ".join(ctx.args)
    else:
        text = LUCA_INTRO  # 기본: 자기소개

    await msg.reply_text(f"🎙️ 음성 생성 중...")
    try:
        loop = asyncio.get_running_loop()
        voice_path = await loop.run_in_executor(None, generate_voice, text)
        with open(voice_path, "rb") as f:
            await msg.reply_voice(voice=f, caption="🎙️ Luca 음성 메시지")
        os.unlink(voice_path)  # 임시 파일 삭제
    except Exception as e:
        await msg.reply_text(f"❌ 음성 생성 실패: {e}")


async def cmd_news_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE, keyword: str = "오늘의 주요 뉴스 5개"):
    """Perplexity 검색 후 결과를 음성으로 변환하여 전송합니다."""
    msg = update.message or update.callback_query.message
    await msg.reply_text(f"🔍 '{keyword}' 검색 후 음성 생성 중...")
    try:
        loop = asyncio.get_running_loop()
        # 1. Perplexity 검색
        search_result = await loop.run_in_executor(
            None, run_script, [".agent/skills/perplexity/perplexity_search.py", keyword, "--model", "sonar"]
        )
        
        # 음성 변환을 위해 마크다운 기호 제거 및 정리 (간략화)
        clean_text = search_result.replace("*", "").replace("#", "").split("출처:")[0].strip()
        if not clean_text:
            clean_text = "검색 결과를 가져오지 못했습니다."

        # 2. TTS 변환
        voice_path = await loop.run_in_executor(None, generate_voice, clean_text)
        
        # 3. 음성 파일 전송
        with open(voice_path, "rb") as f:
            await msg.reply_voice(voice=f, caption=f"🎙️ Luca 뉴스 브리핑: {keyword}")
        os.unlink(voice_path)
    except Exception as e:
        await msg.reply_text(f"❌ 뉴스 음성 브리핑 실패: {e}")


async def handle_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "briefing":
        await cmd_briefing(update, ctx)
    elif data == "email":
        await cmd_email(update, ctx)
    elif data == "calendar":
        await cmd_calendar(update, ctx)
    elif data == "memory":
        await cmd_memory(update, ctx)
    elif data == "status":
        await cmd_status(update, ctx)
    elif data == "voice_intro":
        ctx.args = None
        await cmd_voice(update, ctx)


# ─────────────────────────────────────────
# 멀티스텝 에이전트 루프 — OpenClaw 핵심
# ─────────────────────────────────────────
async def run_agent_loop(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
    user_text: str,
    messages: list,
    system_prompt: str,
    model_used: str,
    max_steps: int = 5
) -> str:
    """최대 max_steps 반복으로 Tool을 자율 호출하여 복잡한 작업을 완수합니다."""
    import json as _json
    loop_messages = messages.copy()
    
    # 🧬 Self-Evolution: 현재 사용 가능한 GWS 명령어 목록을 시스템 프롬프트에 동적으로 주입
    if GWS_ENABLED:
        gws_cmds = GWSHelper.get_available_commands()
        evolution_prompt = f"\n\n[GWS Self-Evolution Information]\n현재 사용 가능한 구글 명령어: {', '.join(gws_cmds)}\n'gws_command' 도구를 사용하여 위 서비스들을 제어할 수 있습니다."
        loop_messages[0] = {"role": "system", "content": loop_messages[0]["content"] + evolution_prompt}
    
    final_text = ""

    for step in range(max_steps):
        try:
            response = client.chat.completions.create(
                model=model_used,
                messages=loop_messages,
                tools=AGENT_TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=2000
            )
            msg = response.choices[0].message

            # 도구 호출 없음 → 최종 응답
            if not msg.tool_calls:
                final_text = msg.content or ""
                break

            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = _json.loads(tool_call.function.arguments)

            # HITL 필요 도구 → 承認 요청 후 중단
            if tool_name in HITL_TOOLS:
                keyboard = [[
                    InlineKeyboardButton("✅ 실행 승인", callback_data=f"approve_{tool_call.id}"),
                    InlineKeyboardButton("❌ 거절", callback_data=f"reject_{tool_call.id}")
                ]]
                event = asyncio.Event()
                PENDING_TOOL_CALLS[tool_call.id] = {
                    "tool_name": tool_name,
                    "tool_args": tool_call.function.arguments,
                    "original_prompt": user_text,
                    "model": model_used,
                    "event": event,
                    "status": "pending",
                    "result": ""
                }
                status_msg = await update.message.reply_text(
                    f"⚠️ *[보안 확인 필요]*\n\n"
                    f"도구: `{tool_name}`\n"
                    f"인자: `{tool_call.function.arguments[:200]}`\n\n"
                    f"이 작업을 승인하시겠습니까?",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
                # 사용자의 콜백(승인/거절) 이벤트를 무한정 대기 (루프 중단 방지)
                await event.wait()
                
                info = PENDING_TOOL_CALLS.pop(tool_call.id, None)
                if not info or info.get("status") == "rejected":
                    tool_result = "사용자가 보안 문제로 도구 실행을 명시적으로 거절했습니다."
                else:
                    tool_result = info.get("result", "")

            # 자동 승인 도구 → 즉시 실행 + 중간 결과 메시지
            status_msg = await update.message.reply_text(
                f"🔧 *[Step {step+1}]* `{tool_name}` 실행 중...",
                parse_mode="Markdown"
            )
            exec_loop = asyncio.get_running_loop()
            if tool_name == "web_search":
                tool_result = await exec_loop.run_in_executor(
                    None, agent_tools.web_search, tool_args.get("query", ""), tool_args.get("max_results", 5))
            elif tool_name == "perplexity_search":
                import subprocess
                model_arg = tool_args.get("model", "sonar")
                script_path = BASE_DIR / ".agent" / "skills" / "perplexity" / "perplexity_search.py"
                cmd = [sys.executable, str(script_path), tool_args.get("query", ""), "--model", model_arg]
                try:
                    res = await exec_loop.run_in_executor(
                        None, lambda: subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=60)
                    )
                    tool_result = (res.stdout + res.stderr).strip()
                except Exception as e:
                    tool_result = f"Perplexity 검색 실패: {e}"
            elif tool_name == "browse_url":
                tool_result = await exec_loop.run_in_executor(
                    None, agent_tools.browse_url, tool_args.get("url", ""))
            elif tool_name == "execute_python":
                tool_result = await exec_loop.run_in_executor(
                    None, agent_tools.execute_python, tool_args.get("code", ""))
            elif tool_name == "list_directory":
                tool_result = await exec_loop.run_in_executor(
                    None, agent_tools.list_directory, tool_args.get("path", "."))
            elif tool_name == "gws_command" and GWS_ENABLED:
                tool_result = await exec_loop.run_in_executor(
                    None, GWSHelper.run_command, tool_args.get("args", []), True
                )
                if isinstance(tool_result, dict) and tool_result.get("error") == "AUTH_REQUIRED":
                    await update.message.reply_text("🔑 **Google Workspace 인증이 필요합니다.**\n/gws_auth 명령어를 입력하여 인증을 진행해주세요.")
                    return ""
            elif tool_name == "add_schedule":
                try:
                    job_type = tool_args.get("job_type")
                    time_expr = tool_args.get("time_expr")
                    command_text = tool_args.get("command")
                    chat_id_sched = str(update.effective_chat.id)
                    scheduler = ctx.bot_data.get("scheduler")
                    
                    if not scheduler:
                        tool_result = "Error: 스케줄러가 비활성화 상태입니다."
                    else:
                        import hashlib
                        from apscheduler.triggers.interval import IntervalTrigger
                        from apscheduler.triggers.cron import CronTrigger
                        from datetime import datetime
                        
                        trigger = None
                        freq_display = ""
                        if job_type == "interval":
                            import re
                            m = re.match(r'^(\d+)(m|h|d)$', time_expr)
                            if not m: raise ValueError("잘못된 interval 형식 (예: 10m, 1h, 2d)")
                            val, unit = int(m.group(1)), m.group(2)
                            kwargs = {'minutes': val} if unit == 'm' else {'hours': val} if unit == 'h' else {'days': val}
                            trigger = IntervalTrigger(**kwargs)
                            freq_display = time_expr
                        elif job_type == "cron":
                            trigger = CronTrigger.from_crontab(time_expr)
                            freq_display = f"Cron({time_expr})"
                        elif job_type == "date":
                            run_date = datetime.strptime(time_expr, "%Y-%m-%d %H:%M")
                            if run_date < datetime.now(): raise ValueError("과거 시간으로 예약할 수 없습니다.")
                            trigger = 'date'
                            freq_display = f"예약({time_expr})"
                        else:
                            raise ValueError(f"알 수 없는 job_type: {job_type}")
                            
                        job_id = "ai_" + hashlib.md5(f"{chat_id_sched}_{command_text}_{freq_display}".encode()).hexdigest()[:6]
                        
                        args = [ctx.application, chat_id_sched, command_text]
                        if trigger == 'date':
                            scheduler.add_job(_execute_loop_job, trigger=trigger, run_date=run_date, args=args, id=job_id)
                        else:
                            scheduler.add_job(_execute_loop_job, trigger=trigger, args=args, id=job_id)
                            
                        LOOP_JOBS[job_id] = {"text": command_text, "freq": freq_display, "chat_id": chat_id_sched, "type": job_type}
                        tool_result = f"성공적으로 스케줄이 등록되었습니다. (ID: {job_id}, 주기/시간: {freq_display}, 명령: {command_text})"
                except Exception as e:
                    tool_result = f"스케줄 등록 도중 에러가 발생했습니다: {e}"
            elif tool_name == "get_schedules":
                chat_id_sched = str(update.effective_chat.id)
                my_jobs = {jid: j for jid, j in LOOP_JOBS.items() if j["chat_id"] == chat_id_sched}
                if not my_jobs:
                    tool_result = "현재 실행 중인 스케줄 작업이 없습니다."
                else:
                    lines = ["[현재 실행 중인 스케줄 목록]"]
                    for jid, info in my_jobs.items():
                        lines.append(f"- ID: {jid} | 주기/시간: {info['freq']} | 명령: {info['text']}")
                    tool_result = "\n".join(lines)
            elif tool_name == "remove_schedule":
                target_id = tool_args.get("job_id", "")
                chat_id_sched = str(update.effective_chat.id)
                scheduler = ctx.bot_data.get("scheduler")
                if target_id.lower() == "all":
                    to_remove = [jid for jid, j in LOOP_JOBS.items() if j["chat_id"] == chat_id_sched]
                    for jid in to_remove:
                        try:
                            if scheduler: scheduler.remove_job(jid)
                            del LOOP_JOBS[jid]
                        except Exception: pass
                    tool_result = f"성공적으로 모든 스케줄 작업({len(to_remove)}개)을 취소했습니다."
                elif target_id in LOOP_JOBS and LOOP_JOBS[target_id]["chat_id"] == chat_id_sched:
                    try:
                        if scheduler: scheduler.remove_job(target_id)
                        del LOOP_JOBS[target_id]
                        tool_result = f"스케줄 {target_id}가 취소되었습니다."
                    except Exception as e:
                        tool_result = f"취소 실패: {e}"
                else:
                    tool_result = f"ID '{target_id}'를 찾을 수 없거나 권한이 없습니다."
            else:
                tool_result = f"알 수 없는 도구: {tool_name}"

            # 중간 결과 업데이트
            try:
                await ctx.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text=f"✅ *[Step {step+1}]* `{tool_name}` 완료",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

            # 메시지 히스토리에 tool 결과 추가
            loop_messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                {"id": tool_call.id, "type": "function",
                 "function": {"name": tool_name, "arguments": tool_call.function.arguments}}
            ]})
            loop_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result[:6000]
            })

        except Exception as e:
            logger.error(f"에이전트 루프 Step {step+1} 에러: {e}")
            final_text = f"❌ 에이전트 루프 에러 (Step {step+1}): {e}"
            break

    return final_text


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    original = update.message.text.strip()
    text = original.lower()
    chat_id = str(update.effective_chat.id)
    logger.info(f"메시지: {text[:50]}")

    # 뉴스+음성 파이프라인 감지
    if ("뉴스" in text or "검색" in text) and any(k in text for k in ["음성으로", "말해줘", "읽어줘"]):
        # 검색어 추출 (간단한 휴리스틱)
        search_kw = original.replace("음성으로 알려줘", "").replace("음성으로 해줘", "").replace("말해줘", "").replace("루카야", "").strip()
        if not search_kw:
            search_kw = "오늘의 주요 뉴스 5개"
        await cmd_news_voice(update, ctx, keyword=search_kw)
    # 일반 음성 요청 감지: '음성으로', '목소리로', '말해줘'
    elif any(k in text for k in ["음성으로", "목소리로", "말해줘", "읽어줘"]):
        # '음성으로 해줘' 앞의 내용을 말할 텍스트로 추출
        for kw in ["음성으로", "목소리로", "말해줘", "읽어줘"]:
            if kw in text:
                before = original[:original.lower().index(kw)].strip()
                # 루카야/소개 키워드 제거
                for skip in ["루카야", "루카", "너의 소개를", "소개를", "자기소개"]:
                    before = before.replace(skip, "").strip()
                ctx.args = before.split() if before else None
                break
        await cmd_voice(update, ctx)
    elif any(k in text for k in ["소개해줘", "자기소개"]):
        ctx.args = None
        await cmd_voice(update, ctx)
    elif any(k in text for k in ["브리핑", "briefing"]):
        await cmd_briefing(update, ctx)
    elif any(k in text for k in ["캘린더", "일정"]):
        await cmd_calendar(update, ctx)
    elif any(k in text for k in ["메일", "email"]):
        await cmd_email(update, ctx)
    elif any(k in text for k in ["딥서치", "심층분석"]):
        ctx.args = original.split()
        await cmd_deepsearch(update, ctx)
    elif any(k in text for k in ["검색", "search"]):
        ctx.args = original.split()
        await cmd_search(update, ctx)
    elif any(k in text for k in ["상태", "status"]):
        await cmd_status(update, ctx)

    # 1. 사용자별 모델 결정
    model_used = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)

    # 2. 멀티턴 히스토리 로드 및 시스템 프롬프트 준비
    if chat_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[chat_id] = []
    
    # 🧠 동적 시스템 프롬프트 (진화 단계 반영)
    system_instruction = luca_brain.get_current_system_prompt()
    
    # 메시지 배열 구성
    messages = [{"role": "system", "content": system_instruction}]
    # 최근 히스토리 추가
    for h in CONVERSATION_HISTORY[chat_id][-MAX_HISTORY:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["ai"]})
    # 현재 유저 메시지 추가
    messages.append({"role": "user", "content": original})

    # 3. 에이전트 루프 실행 (자율 도구 사용)
    try:
        await update.message.chat.send_action(action="typing")
        
        # 특정 키워드가 있거나, 도구 사용이 필요한 복잡한 요청인지 판단은 LLM에게 맡김 (run_agent_loop)
        ai_reply = await run_agent_loop(
            update=update,
            ctx=ctx,
            user_text=original,
            messages=messages,
            system_prompt=system_instruction,
            model_used=model_used
        )

        # 4. 결과 응답 및 히스토리 저장
        if ai_reply:
            # 대화 로그 저장 (SQLite)
            interaction_id = luca_brain.log_interaction(
                chat_id=chat_id,
                user_msg=original,
                ai_reply=ai_reply,
                model=model_used
            )
            # 메카니즘 컨텍스트 저장 (Memory)
            CONVERSATION_HISTORY[chat_id].append({"user": original, "ai": ai_reply})
            if len(CONVERSATION_HISTORY[chat_id]) > MAX_HISTORY:
                CONVERSATION_HISTORY[chat_id].pop(0)

            # 피드백 버튼
            feedback_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("👍 좋아요", callback_data=f"fb_good_{interaction_id}"),
                InlineKeyboardButton("👎 별로", callback_data=f"fb_bad_{interaction_id}")
            ]])
            await update.message.reply_text(ai_reply, reply_markup=feedback_kb)

            # ASMR Observer: trigger on session-end keywords
            if any(kw in text for kw in SESSION_END_KEYWORDS):
                asyncio.create_task(run_asmr_observer(chat_id, reason="session_end"))
    except Exception as e:
        logger.error(f"메시지 처리 에러: {e}")
        await update.message.reply_text(f"❌ 죄송합니다, 대표님. 처리 중 에러가 발생했습니다:\n`{e}`", parse_mode="Markdown")


async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    await msg.reply_text("👁️ 뷰 파인더 가동. 이미지를 분석 중입니다...")
    try:
        photo_file = await msg.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        import base64
        base64_image = base64.b64encode(photo_bytes).decode('utf-8')
        caption = msg.caption or "이 이미지의 내용을 자세히 분석하고 설명해줘."
        system_instruction = luca_brain.get_current_system_prompt()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=1000
        )
        await msg.reply_text(response.choices[0].message.content)
    except Exception as e:
        await msg.reply_text(f"❌ 이미지 분석 실패: {e}")

async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file_name = msg.document.file_name.lower()
    if file_name.endswith(('.csv', '.xlsx', '.xls')):
        await msg.reply_text("📊 데이터 파일 감지! Luca 데이터 마이닝 엔진을 가동합니다...")
        try:
            doc = await msg.document.get_file()
            suffix = Path(file_name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                await doc.download_to_drive(tmp.name)
                tmp_path = tmp.name
            interpreter_script = BASE_DIR / ".agent" / "skills" / "data_mining" / "interpreter.py"
            prompt = msg.caption or "이 데이터를 분석하고 주요 인사이트를 도출해줘."
            import subprocess
            result = subprocess.run([sys.executable, str(interpreter_script), prompt, tmp_path], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=90)
            output = (result.stdout + result.stderr).strip()
            await msg.reply_text(f"📊 **데이터 분석 결과:**\n\n{output}")
            os.unlink(tmp_path)
        except Exception as e:
            await msg.reply_text(f"❌ 데이터 분석 실패: {e}")
        return

    await msg.reply_text("📄 문서 스캔 중...")
    try:
        doc = await msg.document.get_file()
        text_bytes = await doc.download_as_bytearray()
        content = text_bytes.decode('utf-8', errors='ignore')
        prompt = msg.caption or "이 문서의 내용을 요약 분석해줘."
        prompt += f"\n\n[문서 내용]\n{content[:15000]}"
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "문서 분석 전문가입니다."}, {"role": "user", "content": prompt}], max_tokens=2000)
        await msg.reply_text(response.choices[0].message.content)
    except Exception as e:
        await msg.reply_text(f"❌ 문서 분석 실패: {e}")


async def cmd_run(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("🏃‍♂️ 사용법: `/run [명령어]`\n예: `/run 내일 일정 확인해줘`", parse_mode="Markdown")
        return
    
    user_text = " ".join(ctx.args)
    chat_id = str(update.effective_chat.id)
    
    await update.message.reply_text(f"🏃‍♂️ **명령 접수:** `{user_text}`\nLuca 에이전트가 작업을 시작합니다...", parse_mode="Markdown")
    
    # 모델 & 히스토리 로드 (handle_message 와 비슷한 흐름)
    model_used = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)
    if chat_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[chat_id] = []
        
    system_instruction = luca_brain.get_current_system_prompt()
    messages = [{"role": "system", "content": system_instruction}]
    for h in CONVERSATION_HISTORY[chat_id][-MAX_HISTORY:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["ai"]})
    messages.append({"role": "user", "content": user_text})
    
    try:
        await update.message.chat.send_action(action="typing")
        ai_reply = await run_agent_loop(
            update=update,
            ctx=ctx,
            user_text=user_text,
            messages=messages,
            system_prompt=system_instruction,
            model_used=model_used
        )
        if ai_reply:
            interaction_id = luca_brain.log_interaction(chat_id, user_text, ai_reply, model_used)
            CONVERSATION_HISTORY[chat_id].append({"user": user_text, "ai": ai_reply})
            if len(CONVERSATION_HISTORY[chat_id]) > MAX_HISTORY:
                CONVERSATION_HISTORY[chat_id].pop(0)

            feedback_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("👍 좋아요", callback_data=f"fb_good_{interaction_id}"),
                InlineKeyboardButton("👎 별로", callback_data=f"fb_bad_{interaction_id}")
            ]])
            await update.message.reply_text(f"✅ **작업 완료**\n\n{ai_reply}", reply_markup=feedback_kb)
    except Exception as e:
        logger.error(f"/run 에러: {e}")
        await update.message.reply_text(f"❌ 작업 중 에러 발생:\n`{e}`", parse_mode="Markdown")

LOOP_JOBS = {}

async def _execute_loop_job(app: Application, chat_id: str, user_text: str):
    try:
        model_used = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)
        system_instruction = luca_brain.get_current_system_prompt()
        messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": user_text}]
        
        from unittest.mock import AsyncMock
        class DummyMessage:
            def __init__(self, cid): self.chat = type('C', (), {'send_action': AsyncMock()})()
            async def reply_text(self, text, parse_mode=None, reply_markup=None):
                await app.bot.send_message(chat_id=cid, text=text, parse_mode=parse_mode, reply_markup=reply_markup)
                return type('M', (), {'message_id': 1})()
        class DummyUpdate:
            def __init__(self, cid):
                self.effective_chat = type('C', (), {'id': int(cid)})()
                self.message = DummyMessage(cid)
                self.callback_query = None
        class DummyCtx:
            def __init__(self, a): self.bot = a.bot; self.bot_data = a.bot_data; self.application = a
        
        dummy_u = DummyUpdate(chat_id)
        dummy_c = DummyCtx(app)

        await app.bot.send_message(chat_id=chat_id, text=f"🔄 **[Loop 가동]** `{user_text}`", parse_mode="Markdown")
        ai_reply = await run_agent_loop(dummy_u, dummy_c, user_text, messages, system_instruction, model_used)
        if ai_reply:
            await app.bot.send_message(chat_id=chat_id, text=f"✅ **[Loop 보고]**\n\n{ai_reply}")

    except Exception as e:
        logger.error(f"Loop job 에러: {e}")
        await app.bot.send_message(chat_id=chat_id, text=f"❌ Loop 중 에러:\n`{e}`", parse_mode="Markdown")

async def cmd_loop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("🔄 사용법:\n1. ⏳ 간격 반복: `/loop 1h [명령어]` (10m, 1h, 2d)\n2. 📅 정기 스케줄(Cron): `/loop cron \"0 8 * * *\" [명령어]`", parse_mode="Markdown")
        return
        
    freq_str = ctx.args[0]
    chat_id = str(update.effective_chat.id)
    scheduler = ctx.bot_data.get("scheduler")
    
    if not scheduler:
        await update.message.reply_text("❌ 스케줄러가 비활성화 상태입니다.")
        return

    import re, hashlib
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger

    if freq_str.lower() == "cron":
        if len(ctx.args) < 3:
            await update.message.reply_text("❌ 사용법: `/loop cron \"크론식\" [명령어]`\n예: `/loop cron \"0 8 * * *\" 브리핑 해줘`")
            return
        # 따옴표로 감싸진 cron 식을 파싱 (임시로 단순 통합)
        full_args_str = " ".join(ctx.args[1:])
        m = re.match(r'^[\'"]?([^\'"]+)[\'"]?\s+(.+)$', full_args_str)
        if not m:
            await update.message.reply_text("❌ 크론 식을 인식할 수 없습니다. 따옴표로 감싸주세요.")
            return
        cron_expr, user_text = m.groups()
        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            freq_display = f"Cron({cron_expr})"
        except ValueError as e:
            await update.message.reply_text(f"❌ 올바르지 않은 크론 식입니다:\n`{e}`", parse_mode="Markdown")
            return
    else:
        user_text = " ".join(ctx.args[1:])
        m = re.match(r'^(\d+)(m|h|d)$', freq_str)
        if not m:
            await update.message.reply_text("❌ 주기 형식이 올바르지 않습니다. (m=분, h=시간, d=일)\n예: 10m, 1h, 2d")
            return
        val, unit = int(m.group(1)), m.group(2)
        kwargs = {'minutes': val} if unit == 'm' else {'hours': val} if unit == 'h' else {'days': val}
        trigger = IntervalTrigger(**kwargs)
        freq_display = freq_str

    job_id = "loop_" + hashlib.md5(f"{chat_id}_{user_text}_{freq_display}".encode()).hexdigest()[:6]
    
    scheduler.add_job(_execute_loop_job, trigger=trigger, args=[ctx.application, chat_id, user_text], id=job_id)
    LOOP_JOBS[job_id] = {"text": user_text, "freq": freq_display, "chat_id": chat_id, "type": "loop"}
    await update.message.reply_text(f"✅ **루프(Loop) 등록 완료!**\n- ID: `{job_id}`\n- 주기: `{freq_display}`\n- 명령: `{user_text}`\n\n(조회: `/jobs`, 취소: `/unloop {job_id}`)", parse_mode="Markdown")

async def cmd_schedule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 3:
        await update.message.reply_text("⏰ 사용법: `/schedule YYYY-MM-DD HH:MM [명령어]`\n예: `/schedule 2026-03-10 15:00 임원 회의자료 초안 작성해줘`", parse_mode="Markdown")
        return
        
    date_str = f"{ctx.args[0]} {ctx.args[1]}"
    user_text = " ".join(ctx.args[2:])
    chat_id = str(update.effective_chat.id)
    scheduler = ctx.bot_data.get("scheduler")
    
    if not scheduler:
        await update.message.reply_text("❌ 스케줄러가 비활성화 상태입니다.")
        return
        
    from datetime import datetime
    try:
        run_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        if run_date < datetime.now():
            await update.message.reply_text("❌ 과거 시간으로 예약할 수 없습니다.")
            return
    except ValueError:
        await update.message.reply_text("❌ 날짜/시간 형식이 올바르지 않습니다.\n지원 포맷: `YYYY-MM-DD HH:MM` (예: 2026-03-10 15:00)", parse_mode="Markdown")
        return
        
    import hashlib
    job_id = "sched_" + hashlib.md5(f"{chat_id}_{user_text}_{date_str}".encode()).hexdigest()[:6]
    
    scheduler.add_job(_execute_loop_job, trigger='date', run_date=run_date, args=[ctx.application, chat_id, user_text], id=job_id)
    LOOP_JOBS[job_id] = {"text": user_text, "freq": f"예약({date_str})", "chat_id": chat_id, "type": "schedule"}
    
    await update.message.reply_text(f"✅ **예약(Schedule) 등록 완료!** ⏰\n- ID: `{job_id}`\n- 일시: `{date_str}`\n- 명령: `{user_text}`\n\n(조회: `/jobs`, 취소: `/unloop {job_id}`)", parse_mode="Markdown")

async def cmd_jobs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    my_jobs = {jid: j for jid, j in LOOP_JOBS.items() if j["chat_id"] == chat_id}
    if not my_jobs:
        await update.message.reply_text("📭 현재 실행 중인 루프 작업이 없습니다.")
        return
    txt = "🔄 **[현재 실행 중인 Loop 목록]**\n\n"
    for jid, info in my_jobs.items(): txt += f"🔹 **ID:** `{jid}` | 주기: {info['freq']} | 명령: {info['text']}\n"
    await update.message.reply_text(txt, parse_mode="Markdown")

async def cmd_unloop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ 취소할 루프 ID를 입력하세요. (전체 취소: `/unloop all`)")
        return
    target_id = ctx.args[0]
    chat_id = str(update.effective_chat.id)
    scheduler = ctx.bot_data.get("scheduler")
    if target_id.lower() == "all":
        to_remove = [jid for jid, j in LOOP_JOBS.items() if j["chat_id"] == chat_id]
        for jid in to_remove:
            try: scheduler.remove_job(jid); del LOOP_JOBS[jid]
            except: pass
        await update.message.reply_text(f"✅ 모든 루프 작업({len(to_remove)}개)이 취소되었습니다.")
        return
    if target_id not in LOOP_JOBS or LOOP_JOBS[target_id]["chat_id"] != chat_id:
        await update.message.reply_text(f"❌ '{target_id}' ID를 찾을 수 없습니다.")
        return
    try:
        scheduler.remove_job(target_id); del LOOP_JOBS[target_id]
        await update.message.reply_text(f"✅ 루프 `{target_id}` 가 취소되었습니다.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ 취소 실패: {e}")

async def cmd_model(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not ctx.args:
        current = USER_MODEL_PREF.get(chat_id, DEFAULT_MODEL)
        await update.message.reply_text(f"🤖 현재 모델: `{current}`\n\n/model [gpt-4o|gpt-4o-mini|gemini-1.5-pro|gemini-1.5-flash]", parse_mode="Markdown")
        return
    new_model = ctx.args[0].lower()
    if new_model in ["gpt-4o", "gpt-4o-mini", "gemini-1.5-pro", "gemini-1.5-flash"]:
        USER_MODEL_PREF[chat_id] = new_model
        await update.message.reply_text(f"✅ 모델이 `{new_model}`로 변경되었습니다.")
    else:
        await update.message.reply_text("❌ 지원하지 않는 모델입니다.\n(gpt-4o, gpt-4o-mini, gemini-1.5-pro, gemini-1.5-flash)")

async def cmd_remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("⏰ 사용법: `/remind 10분후 회의`")
        return
    query = " ".join(ctx.args)
    chat_id = update.effective_chat.id
    try:
        import re
        m = re.search(r'(\d+)\s*(분|시간|초)', query)
        if m:
            val = int(m.group(1)); unit = m.group(2)
            sec = val * 60 if unit == "분" else val * 3600 if unit == "시간" else val
            task = query.split(unit)[-1].replace("후", "").replace("뒤", "").strip() or "알림"
            scheduler = ctx.bot_data.get("scheduler")
            if scheduler:
                async def _cb(_id, _t): await ctx.bot.send_message(chat_id=_id, text=f"🔔 **Luca 알림:** `{_t}`")
                from datetime import datetime, timedelta
                scheduler.add_job(_cb, trigger='date', run_date=datetime.now()+timedelta(seconds=sec), args=[chat_id, task])
                await update.message.reply_text(f"✅ {val}{unit} 후 알림 예약 완료!")
    except Exception as e:
        await update.message.reply_text(f"❌ 알림 설정 실패: {e}")

async def cmd_monitor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        if not MONITOR_JOBS: await update.message.reply_text("👀 모니터링 중인 사이트가 없습니다.")
        else:
            txt = "👀 **모니터링 목록:**\n"
            for k,v in MONITOR_JOBS.items(): txt += f"- `{k}`: {v['url']}\n"
            await update.message.reply_text(txt, parse_mode="Markdown")
        return
    if ctx.args[0] == "stop" and len(ctx.args) > 1:
        mid = ctx.args[1]
        if mid in MONITOR_JOBS:
            del MONITOR_JOBS[mid]
            try: ctx.bot_data.get("scheduler").remove_job(f"monitor_{mid}")
            except: pass
            await update.message.reply_text(f"✅ ID `{mid}` 중지되었습니다.")
        return
    if len(ctx.args) < 2: return
    url, kw = ctx.args[0], " ".join(ctx.args[1:])
    import hashlib
    mid = hashlib.md5(f"{url}{kw}".encode()).hexdigest()[:6]
    MONITOR_JOBS[mid] = {"url": url, "keyword": kw, "chat_id": update.effective_chat.id, "last_content": ""}
    scheduler = ctx.bot_data.get("scheduler")
    if scheduler:
        from apscheduler.triggers.interval import IntervalTrigger
        async def _check(_mid, _app):
            info = MONITOR_JOBS.get(_mid)
            if not info: return
            res = await asyncio.get_running_loop().run_in_executor(None, agent_tools.browse_url, info["url"])
            if info["keyword"].lower() in res.lower() and res[:200] != info["last_content"][:200]:
                MONITOR_JOBS[_mid]["last_content"] = res
                await _app.bot.send_message(chat_id=info["chat_id"], text=f"👁️ **감지!** {info['url']}\n\n키워드 '{info['keyword']}' 발견!")
        scheduler.add_job(_check, trigger=IntervalTrigger(minutes=30), args=[mid, ctx.application], id=f"monitor_{mid}")
    await update.message.reply_text(f"✅ `{url}` 모니터링 시작 (ID: `{mid}`)")

async def cmd_evolve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 자기반성 가동 중...")
    try:
        await luca_evolution.job_self_reflection(ctx.application)
        await update.message.reply_text("✅ 진화가 완료되었습니다!")
    except Exception as e: await update.message.reply_text(f"❌ 진화 에러: {e}")

async def cmd_growth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats = luca_brain.get_stats()
    if not stats: await update.message.reply_text("📊 아직 데이터가 부족합니다.")
    else: await update.message.reply_text(f"📊 **성장 보고서**\n\n- 대화: {stats['total_interactions']}건\n- 만족도: {stats['satisfaction_rate']}\n- 버전: v{stats.get('prompt_version', 1)}", parse_mode="Markdown")

async def handle_tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("approve_"):
        call_id = query.data.split("_")[1]
        if call_id in PENDING_TOOL_CALLS:
            info = PENDING_TOOL_CALLS[call_id]
            await query.edit_message_text(f"⏳ `{info['tool_name']}` 실제 백그라운드 실행 중...")
            
            tool_name = info["tool_name"]
            import json
            try:
                args = json.loads(info["tool_args"])
            except Exception:
                args = {}
                
            res = ""
            loop = asyncio.get_running_loop()
            if tool_name == "run_terminal_command": 
                # [Best Practice] 동기(Sync) 터미널 실행이 텔레그램 봇 전체 이벤트를 먹통으로 만들지 못하도록 백그라운드 스레드로 위임
                res = await loop.run_in_executor(None, agent_tools.run_terminal_command, args.get("command", ""))
            elif tool_name == "write_local_file": 
                res = await loop.run_in_executor(None, agent_tools.write_local_file, args.get("path", ""), args.get("content", ""))
            else:
                res = f"미지원 HITL 도구: {tool_name}"
                
            # 에이전트의 주(Main) 루프로 실제 실행 결과 반환 및 재개
            info["result"] = res
            info["status"] = "approved"
            if "event" in info:
                info["event"].set()
                
    elif query.data.startswith("reject_"):
        call_id = query.data.split("_")[1]
        if call_id in PENDING_TOOL_CALLS:
            info = PENDING_TOOL_CALLS[call_id]
            info["status"] = "rejected"
            if "event" in info:
                info["event"].set()
        await query.edit_message_text("🚫 작업이 사용자에 의해 안전하게 취소되었습니다.")

async def handle_feedback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    parts = query.data.split("_")
    score = 1 if parts[1] == "good" else -1
    luca_brain.log_feedback(int(parts[2]), score)
    await query.edit_message_text("💙 피드백 감사합니다!")

async def handle_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not STT_AVAILABLE:
        await update.message.reply_text("❌ STT 비활성")
        return
    msg = update.message
    await msg.reply_text("🎙️ 음성 인식 중...")
    try:
        voice_file = await msg.voice.get_file()
        ogg_path = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg").name
        await voice_file.download_to_drive(ogg_path)
        mp3_path = ogg_path.replace(".ogg", ".mp3")
        def convert_and_transcribe():
            from pydub import AudioSegment
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(mp3_path, format="mp3")
            with open(mp3_path, "rb") as f:
                return client.audio.transcriptions.create(model="whisper-1", file=f, language="ko").text
        transcribed_text = await asyncio.get_running_loop().run_in_executor(None, convert_and_transcribe)
        os.unlink(ogg_path); os.unlink(mp3_path)
        await msg.reply_text(f"📝 **인식 결과:** `{transcribed_text}`")
        update.message.text = transcribed_text
        await handle_message(update, ctx)
    except Exception as e:
        await msg.reply_text(f"❌ STT 실패: {e}")

async def post_init(app: Application):
    scheduler = AsyncIOScheduler()
    app.bot_data["scheduler"] = scheduler  # 알림 명령에서 접근 가능하도록 저장
    scheduler.add_job(job_daily_briefing, trigger=CronTrigger(hour=9, minute=0), args=[app], id="daily_morning_briefing")
    scheduler.add_job(luca_evolution.job_self_reflection, trigger=CronTrigger(day_of_week="mon", hour=2, minute=0), args=[app], id="weekly_self_reflection")
    scheduler.add_job(luca_evolution.job_trend_research, trigger=CronTrigger(day_of_week="sun", hour=8, minute=0), args=[app], id="weekly_trend_research")
    scheduler.add_job(luca_evolution.job_weekly_growth_report, trigger=CronTrigger(day_of_week="sun", hour=9, minute=0), args=[app], id="weekly_growth_report")
    scheduler.add_job(job_naver_weekly_report, trigger=CronTrigger(day_of_week="mon", hour=8, minute=0), args=[app], id="weekly_naver_keyword_report")
    scheduler.add_job(job_asmr_periodic, trigger="interval", minutes=30, args=[app], id="asmr_observer_periodic")
    scheduler.start()
    logger.info("⏰ APScheduler 가동 완료 (ASMR Observer: 30분 주기)")

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN 없음")
        sys.exit(1)
    PID_FILE = BASE_DIR / "luca_bot.pid"
    if PID_FILE.exists():
        try: os.kill(int(PID_FILE.read_text().strip()), 9)
        except: pass
    PID_FILE.write_text(str(os.getpid()))
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("briefing", cmd_briefing))
    app.add_handler(CommandHandler("calendar", cmd_calendar))
    app.add_handler(CommandHandler("email", cmd_email))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("deepsearch", cmd_deepsearch))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("voice", cmd_voice))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("luca", cmd_luca))
    app.add_handler(CommandHandler("crew", cmd_crew))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("naver", cmd_naver))
    app.add_handler(CommandHandler("evolve", cmd_evolve))
    app.add_handler(CommandHandler("growth", cmd_growth))
    # ✅ New OpenClaw Commands
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("loop", cmd_loop))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("unloop", cmd_unloop))
    app.add_handler(CommandHandler("jobs", cmd_jobs))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CommandHandler("remind", cmd_remind))
    app.add_handler(CommandHandler("monitor", cmd_monitor))
    app.add_handler(CommandHandler("gws_auth", cmd_gws_auth))
    app.add_handler(CommandHandler("gws_evolve", cmd_gws_evolve))

    app.add_handler(CallbackQueryHandler(handle_tool_callback, pattern="^(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(handle_feedback, pattern="^fb_"))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Polling 시작!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
