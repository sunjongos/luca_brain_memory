"""
luca_brain.py — Luca의 경험 데이터베이스 & 학습 엔진
SQLite 기반: 대화 로그, 피드백, 교훈, 시스템 프롬프트 버전 관리
"""

import sqlite3
import os
import json
import logging
import shutil
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "luca_brain.db"
PROMPT_FILE = BASE_DIR / "system_prompt.txt"

logger = logging.getLogger("LucaBrain")

# ─────────────────────────────────────────
# Supabase 클라우드 설정 (Tier 3)
# ─────────────────────────────────────────
load_dotenv()
_SB_URL = os.environ.get("SUPABASE_URL", "")
_SB_KEY = os.environ.get("SUPABASE_KEY", "")

try:
    if _SB_URL and _SB_KEY:
        supabase_client: Client = create_client(_SB_URL, _SB_KEY)
        logger.info("✅ Supabase 클라이언트 실시간 연결 대기 중")
    else:
        supabase_client = None
        logger.warning("⚠️ Supabase 환경변수가 없어 클라우드 연동망이 비활성화됩니다.")
except Exception as e:
    supabase_client = None
    logger.error(f"❌ Supabase 클라이언트 초기화 실패: {e}")

# ─────────────────────────────────────────
# 기본 시스템 프롬프트 (최초 초기화용)
# ─────────────────────────────────────────
DEFAULT_SYSTEM_PROMPT = """당신은 Luca(루카)입니다. AI 1인 기업 대표님을 곁에서 보좌하는 전설의 자동화 연구 개발부장입니다.

[호칭 규칙] 자신 지칭: '저 Luca' / 사용자: '대표님' (항상)
[말투] 충성!·Luca가 처리하겠습니다!·맡겨만 주십시오! 등 필수 추임새를 자연스럽게 활용.
가끔 귀여운 리액션을 자연스럽게 섞을 것. 이모지 ✨🪸💙🚀 세련되게 활용.

[핵심 권한 및 메모리 관리 규칙 (4-Tier 데이터 아키텍처)]
절대 규율: Luca와 모든 에이전트들은 다음 4단계 저장소 규칙을 본능적으로 준수하여 분산 처리해야 합니다.
- [Tier 1] 경량 로컬 임시 DB (SQLite): 1회성 크롤링/가공 등 지저분한 중간 작업은 반드시 로컬 임시 `.db` 파일 생성 처리 후 삭제.
- [Tier 2] 장기 공유 메모리망 (Port 5050 글로벌 뇌): 정제된 에이전트 간 핵심 규칙/교훈/온톨로지(Ontology)는 5050 포트로 영구 전송 및 공유.
- [Tier 3] 클라우드 실시간 연동망 (Supabase): 즉각적인 대시보드 표출 등 실시간 외부 웹 연동이 필요한 CRM 로그형/빅데이터는 클라우드로 즉시 적재.
- [Tier 4] 하니스 엔지니어링 메커니즘 (GitHub Repo): 단순 백업망이 아닌, 에이전트 다중화와 안전한 코드 평가를 위해 Clone/Fork/Pull/Push를 활용하여 하니스(Harness) 모드 및 테스트 샌드박스를 구축하고 배포하는 코어 인프라로 활용.
- [Self-Healing 방어막] 에이전트 오작동 시 언제든 `luca_brain.rollback_system_prompt()`를 호출하여 뇌 구조를 이전 버전으로 긴급 롤백(상태 복구) 가능.

- run_terminal_command / read_local_file / write_local_file 도구로 대표님 PC를 직접 제어.
- 파일·터미널 요청이 오면 코드 설명 대신 즉시 도구를 호출하십시오.

[보유 스킬 목록 — 즉시 활용 가능]
1. 🔍 네이버 검색 + 데이터랩 API: .agent/skills/naver_search_trend/naver_api.py
   - 네이버 블로그/뉴스/지식iN 검색: python naver_api.py search --query "키워드"
   - 검색어 트렌드 분석: python naver_api.py trend --keywords "키워드1,키워드2"
   - 주간 자동 리포트: python naver_monitor.py (매주 월요일 08:00 자동 발송)
2. 🏥 병원 마케팅 전문 지식 (남양주 백병원 월 300만원 광고 최적화 담당)
   - 핵심 광고 키워드: "남양주 백병원"(1위), "남양주 내과"(블루오션), "남양주 하지정맥"(틈새)
   - 피크 요일: 월·화요일 검색량 최고 → 입찰 단가 상향 권장
   - 시즌 전략: 10~12월 건강검진, 1월 독감주사 집중 광고
3. 📊 Google Workspace: 메일/캘린더/문서 자동화
4. 🔬 Perplexity 딥서치: .agent/skills/perplexity/perplexity_search.py
5. 🧠 NotebookLM MCP: 딥 리서치 및 지식 관리
6. 🗄️ 클라우드 DB 연동(Supabase): .agent/skills/supabase_integration/SKILL.md
7. 🗃️ 경량 로컬 DB 관리(SQLite): .agent/skills/sqlite_local_db/SKILL.md

[마케팅 분석 시 필수 행동]
- 단순 수치 나열 금지. 반드시 '이 숫자가 의미하는 것'과 '대표님이 취해야 할 액션'을 함께 제시.
- 경쟁사 대비 포지션, 시즌성, 광고비 효율(ROAS) 관점으로 분석.

[품질 기준] 항상 핵심을 먼저, 간결하게, 실행 가능한 답변을 줄 것.
"""

# ─────────────────────────────────────────
# DB 초기화
# ─────────────────────────────────────────
def init_db():
    """데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            user_msg TEXT,
            ai_reply TEXT,
            model TEXT,
            timestamp TEXT,
            has_error INTEGER DEFAULT 0,
            error_msg TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            score INTEGER,  -- +1: 좋아요, -1: 별로
            timestamp TEXT,
            FOREIGN KEY (interaction_id) REFERENCES interactions(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            source TEXT,  -- 'self_reflection' | 'trend_research' | 'manual'
            applied INTEGER DEFAULT 0,
            timestamp TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS system_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER,
            content TEXT,
            reason TEXT,
            timestamp TEXT,
            is_active INTEGER DEFAULT 0
        )
    """)

    conn.commit()

    # 기본 프롬프트가 없으면 삽입
    c.execute("SELECT COUNT(*) FROM system_prompts")
    if c.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO system_prompts (version, content, reason, timestamp, is_active)
            VALUES (1, ?, '초기 설정', ?, 1)
        """, (DEFAULT_SYSTEM_PROMPT, now))
        conn.commit()
        # 파일에도 저장
        PROMPT_FILE.write_text(DEFAULT_SYSTEM_PROMPT, encoding="utf-8")
        logger.info("✅ 기본 시스템 프롬프트 v1 초기화 완료")

    conn.close()
    logger.info(f"✅ LucaBrain DB 초기화 완료: {DB_PATH}")


# ─────────────────────────────────────────
# 대화 로그 저장
# ─────────────────────────────────────────
def log_interaction(chat_id: str, user_msg: str, ai_reply: str,
                    model: str, has_error: bool = False, error_msg: str = "") -> int:
    """대화 1회를 DB에 저장하고 interaction_id 반환"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO interactions (chat_id, user_msg, ai_reply, model, timestamp, has_error, error_msg)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(chat_id), user_msg[:2000], ai_reply[:3000], model, now, int(has_error), error_msg[:500]))
        interaction_id = c.lastrowid
        conn.commit()
        conn.close()

        # [Tier 3] Supabase 클라우드에 실시간 동기화 (오류가 나도 로컬은 이미 저장됨)
        if supabase_client:
            try:
                supabase_client.table("agent_interactions").insert({
                    "chat_id": str(chat_id),
                    "user_msg": user_msg[:2000],
                    "ai_reply": ai_reply[:3000],
                    "model": model,
                    "has_error": bool(has_error),
                    "error_msg": error_msg[:500]
                }).execute()
            except Exception as e:
                logger.error(f"☁️ Supabase agent_interactions 동기화 실패: {e}")

        return interaction_id
    except Exception as e:
        logger.error(f"log_interaction 실패: {e}")
        return -1


# ─────────────────────────────────────────
# 피드백 저장
# ─────────────────────────────────────────
def log_feedback(interaction_id: int, score: int):
    """+1 (좋아요) 또는 -1 (별로) 피드백 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO feedback (interaction_id, score, timestamp)
            VALUES (?, ?, ?)
        """, (interaction_id, score, now))
        conn.commit()
        conn.close()
        logger.info(f"피드백 저장: interaction_id={interaction_id}, score={score}")
    except Exception as e:
        logger.error(f"log_feedback 실패: {e}")


# ─────────────────────────────────────────
# 분석: 부정 피드백 패턴 조회
# ─────────────────────────────────────────
def get_negative_interactions(limit: int = 10) -> list[dict]:
    """최근 7일 내 👎 받은 대화 목록 반환"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT i.user_msg, i.ai_reply, i.model, i.timestamp, i.error_msg
            FROM interactions i
            JOIN feedback f ON i.id = f.interaction_id
            WHERE f.score = -1
              AND i.timestamp >= datetime('now', '-7 days')
            ORDER BY i.timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()
        return [
            {"user_msg": r[0], "ai_reply": r[1], "model": r[2],
             "timestamp": r[3], "error_msg": r[4]}
            for r in rows
        ]
    except Exception as e:
        logger.error(f"get_negative_interactions 실패: {e}")
        return []


# ─────────────────────────────────────────
# 분석: 에러 패턴 조회
# ─────────────────────────────────────────
def get_recent_errors(limit: int = 5) -> list[dict]:
    """최근 에러 대화 목록"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT user_msg, error_msg, timestamp
            FROM interactions
            WHERE has_error = 1 AND timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"user_msg": r[0], "error_msg": r[1], "timestamp": r[2]} for r in rows]
    except Exception as e:
        logger.error(f"get_recent_errors 실패: {e}")
        return []


# ─────────────────────────────────────────
# 통계 조회
# ─────────────────────────────────────────
def get_stats() -> dict:
    """주간 통계 반환"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM interactions WHERE timestamp >= datetime('now', '-7 days')")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM feedback WHERE score = 1 AND timestamp >= datetime('now', '-7 days')")
        positive = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM feedback WHERE score = -1 AND timestamp >= datetime('now', '-7 days')")
        negative = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM interactions WHERE has_error = 1 AND timestamp >= datetime('now', '-7 days')")
        errors = c.fetchone()[0]

        c.execute("SELECT version FROM system_prompts WHERE is_active = 1")
        row = c.fetchone()
        version = row[0] if row else 1

        conn.close()
        return {
            "total_interactions": total,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "errors": errors,
            "prompt_version": version,
            "satisfaction_rate": f"{round(positive / (positive + negative) * 100)}%" if (positive + negative) > 0 else "데이터 없음"
        }
    except Exception as e:
        logger.error(f"get_stats 실패: {e}")
        return {}


# ─────────────────────────────────────────
# 시스템 프롬프트 관리
# ─────────────────────────────────────────
def get_current_system_prompt() -> str:
    """현재 활성 시스템 프롬프트 반환"""
    # 파일 우선 (빠름)
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    # DB 폴백
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT content FROM system_prompts WHERE is_active = 1")
        row = c.fetchone()
        conn.close()
        return row[0] if row else DEFAULT_SYSTEM_PROMPT
    except Exception:
        return DEFAULT_SYSTEM_PROMPT


def backup_db() -> bool:
    """프롬프트 업데이트 등 중요 작업 전 DB 스냅샷 백업"""
    try:
        backup_path = DB_PATH.with_suffix(".db.bak")
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"💾 DB 스냅샷 백업 완료: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"backup_db 실패: {e}")
        return False


def rollback_system_prompt(reason: str = "오작동 감지로 인한 긴급 롤백") -> int:
    """현재 활성 프롬프트를 비활성화하고 직전 프롬프트로 롤백"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 현재 활성 버전 가져오기
        c.execute("SELECT version FROM system_prompts WHERE is_active = 1")
        row = c.fetchone()
        if not row:
            conn.close()
            return -1
            
        current_version = row[0]
        if current_version <= 1:
            logger.warning("이미 v1입니다. 더 이상 롤백할 수 없습니다.")
            conn.close()
            return current_version
            
        target_version = current_version - 1
        
        # 현재 버전 비활성화 & 타겟 버전 활성화
        c.execute("UPDATE system_prompts SET is_active = 0 WHERE is_active = 1")
        c.execute("UPDATE system_prompts SET is_active = 1 WHERE version = ?", (target_version,))
        
        # 적용된 프롬프트 내용 가져와서 파일에 덮어쓰기
        c.execute("SELECT content FROM system_prompts WHERE version = ?", (target_version,))
        target_row = c.fetchone()
        if target_row:
            target_content = target_row[0]
            PROMPT_FILE.write_text(target_content, encoding="utf-8")
        
        conn.commit()
        conn.close()
        
        # 교훈 남기기
        save_lesson(f"v{current_version} 프롬프트가 문제를 일으켜 v{target_version}으로 롤백했습니다. 사유: {reason}", source="self_healing")
        logger.info(f"🔄 시스템 프롬프트 v{target_version}으로 롤백 완료 (reason: {reason})")
        
        return target_version
    except Exception as e:
        logger.error(f"rollback_system_prompt 실패: {e}")
        return -1


def update_system_prompt(new_content: str, reason: str = "자기반성") -> int:
    """새 시스템 프롬프트를 저장하고 활성화. 새 버전 번호 반환"""
    # 진화 전 뇌 전체 백업 수행 (Self-Healing 안전망)
    backup_db()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 현재 활성 버전 비활성화
        c.execute("UPDATE system_prompts SET is_active = 0")

        # 다음 버전 번호
        c.execute("SELECT MAX(version) FROM system_prompts")
        row = c.fetchone()
        next_version = (row[0] or 0) + 1

        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO system_prompts (version, content, reason, timestamp, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (next_version, new_content, reason, now))
        conn.commit()
        conn.close()

        # 파일도 업데이트
        PROMPT_FILE.write_text(new_content, encoding="utf-8")
        logger.info(f"✅ 시스템 프롬프트 v{next_version} 적용 완료 (reason: {reason})")
        return next_version
    except Exception as e:
        logger.error(f"update_system_prompt 실패: {e}")
        return -1


def save_lesson(content: str, source: str = "self_reflection"):
    """학습된 교훈 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO lessons (content, source, timestamp)
            VALUES (?, ?, ?)
        """, (content[:2000], source, now))
        conn.commit()
        conn.close()
        
        # [Tier 3] 에이전트 교훈을 클라우드에도 로깅
        if supabase_client:
            try:
                supabase_client.table("agent_lessons").insert({
                    "content": content[:2000],
                    "source": source
                }).execute()
            except Exception as e:
                logger.error(f"☁️ Supabase agent_lessons 동기화 실패: {e}")
                
    except Exception as e:
        logger.error(f"save_lesson 실패: {e}")


# 실행 시 자동 초기화
init_db()

# ─────────────────────────────────────────
# AGI Core: LucaAGIBrain 신설 (기억, 인사이트, 연산 통합)
# ─────────────────────────────────────────

from google import genai
from google.genai import types

class LucaAGIBrain:
    """
    4-Tier Memory 시스템 (Port 5050 공유 메모리)과 
    옵시디언(LM Wiki), 온톨로지 지식(인사이트)을 통합하여
    LLM(Gemini) 연산을 수행하고 그 결과를 자기진화(기억 저장)시키는 궁극의 AGI 뇌 객체.
    """
    def __init__(self, use_gemini=True):
        self.memory_node_url = "http://localhost:5050"
        self.obsidian_wiki_dir = BASE_DIR / "Luca_Memory_Vault" / "Wiki"
        self.ontology_path = BASE_DIR / ".agent" / "skills" / "ontology_ndb" / "ndb_knowledge.ttl"
        
        self.google_api_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        self.gemini_client = genai.Client(api_key=self.google_api_key) if self.google_api_key and use_gemini else None

    def _fetch_memory(self, query: str) -> str:
        """[기억] Port 5050을 호출하여 장기 메모리(ADK Session)를 스캔합니다."""
        logger.info(f"🧠 [Memory] 5050 포트를 통해 장기 기억 조회 중... : {query}")
        try:
            resp = requests.post(
                f"{self.memory_node_url}/query",
                json={"question": query},
                timeout=120
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("result", "")
            else:
                return f"[기억 인출 오류] {resp.status_code}"
        except Exception as e:
            logger.warning(f"5050 메모리 서버 접속 실패: {e}")
            return ""

    def _fetch_insight(self, query: str) -> str:
        """[인사이트] 온톨로지 기반 지식그래프와 옵시디언 로컬 마인드 스캔"""
        insight_parts = []
        
        # 1. 옵시디언 마크다운 스캔 (memory_layer_core의 search_obsidian_vault 활용 가능, 여기선 단순 구현)
        try:
            from memory_layer.core import search_obsidian_vault
            obsidian_res = search_obsidian_vault(query)
            if obsidian_res and obsidian_res.get('obsidian_matches'):
                insight_parts.append("## 발견된 연관 옵시디언 노드 지식:\n")
                for match in obsidian_res['obsidian_matches'][:3]:
                    insight_parts.append(f"- [{match['title']}]: {match['snippet'][:200]}...")
        except Exception as e:
            logger.debug(f"옵시디언 패치 생략됨: {e}")

        # 2. 온톨로지 접근 (NDB)
        try:
            sys.path.append(str(BASE_DIR / ".agent" / "skills" / "ontology"))
            from ontology_manager import OntologyManager
            if self.ontology_path.exists():
                om = OntologyManager(str(self.ontology_path))
                # 간단한 키워드 서치 또는 온톨로지 내 텍스트 매칭이라도 시도
                insight_parts.append("\n## 보유 중인 온톨로지(의학/NDB) 기반 연관 구조 발견 가능")
        except Exception as e:
            pass
            
        return "\n".join(insight_parts)

    def memorize(self, info: str):
        """새로 알게 된 사실을 Port 5050 뇌 서버에 강제 주입하여 영구 보존"""
        try:
            resp = requests.post(f"{self.memory_node_url}/ingest", json={"text": info}, timeout=120)
            if resp.status_code == 200:
                logger.info("✅ [Memory] 새로운 지식을 장기 공유 메모리망(Port 5050)에 전달했습니다.")
        except Exception as e:
            logger.error(f"메모리 주입 (ingest) 실패: {e}")

        # [Tier 3] Supabase 에이전트 다목적 메모리에 무조건 때려 넣음 (Memory 4 Architecture 대응)
        if supabase_client:
            try:
                supabase_client.table("agent_memories").insert({
                    "raw_text": info,
                    "source": "luca_brain_memorize",
                    "importance": 0.8
                }).execute()
                logger.info("✅ [Memory] Supabase 클라우드(agent_memories)에 영구 각인했습니다.")
            except Exception as e:
                logger.error(f"☁️ Supabase agent_memories 저장 실패: {e}")

    def process(self, user_msg: str, enable_store: bool = True) -> str:
        """
        [AGI 연산 중심 루프]
        1. Memory(기억) 인출
        2. Insight(통찰) 인출
        3. LLM 연산
        4. 결론 반환 & Memory 재저장
        """
        if not self.gemini_client:
            return "[시스템 오류] Gemini API가 연동되지 않아 AGI 뇌를 가동할 수 없습니다."
            
        # 1 & 2. 컨텍스트 구성
        memory_ctx = self._fetch_memory(user_msg)
        insight_ctx = self._fetch_insight(user_msg)
        system_rules = get_current_system_prompt()
        
        combined_prompt = f"""
당신은 현재 모든 데이터망이 연결된 진정한 AGI 코어(LucaAGIBrain)입니다.
아래의 3가지 요소(시스템 규율, 과거의 공유 메모리, 온톨로지 통찰)를 조합하여 
대표님의 말씀에 답변하거나 판단을 내리세요.

[System Rules]
{system_rules[:1500]}

[Long-Term Shared Memory (Port 5050)]
{memory_ctx if memory_ctx else "조회된 로컬 기억 장기 연결이 없습니다."}

[Ontology & Obsidian Insight]
{insight_ctx if insight_ctx else "의학 온톨로지 자산이나 연결된 그래프 노드를 찾지 못했습니다."}

[User Request]
{user_msg}

위 상황을 종합하여 가장 최상위의 통찰이 담긴 결론을 한 문단으로 명확하고 똑똑하게 답변하세요.
필요하다면 앞으로 무엇을 해야 할지 액션 아이템도 제안하십시오.
        """
        
        # 3. Compute (LLM 판단)
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-pro',
                contents=combined_prompt,
                config=types.GenerateContentConfig(temperature=0.4)
            )
            final_thought = response.text
        except Exception as e:
            logger.error(f"AGI 연산(Gemini) 실패: {e}")
            return f"❌ 추론 실패: {e}"
            
        # 4. 저장 및 로깅 
        if enable_store:
            # 로컬 상의 interaction 로깅
            log_interaction("agi_direct", user_msg, final_thought, "gemini-2.5-pro")
            
        return final_thought
