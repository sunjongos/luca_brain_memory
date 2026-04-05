"""
luca_evolution.py — Luca 자기진화 엔진
주 1회 자동 실행: 자기반성(프롬프트 진화) + AI 트렌드 흡수
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent

# .env를 utf-8로 직접 읽어서 환경변수 적용 (dotenv 인코딩 에러 방지)
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        _line = _line.replace('\x00', '').strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

logger = logging.getLogger("LucaEvolution")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EVOLUTION_LOG = BASE_DIR / "luca_evolution_log.md"

# OpenAI 클라이언트
try:
    from openai import OpenAI
    _openai_client = OpenAI(api_key=OPENAI_API_KEY, timeout=120.0)
    OPENAI_OK = bool(OPENAI_API_KEY)
except Exception:
    _openai_client = None
    OPENAI_OK = False

import luca_brain


# ─────────────────────────────────────────
# 진화 로그 기록
# ─────────────────────────────────────────
def _append_evolution_log(title: str, content: str):
    """luca_evolution_log.md에 진화 기록 추가"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## [{now}] {title}\n{content}\n\n---"
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


def _init_evolution_log():
    if not EVOLUTION_LOG.exists():
        EVOLUTION_LOG.write_text(
            "# 🧬 Luca 자기진화 히스토리\n이 파일은 Luca가 스스로 성장한 기록입니다.\n",
            encoding="utf-8"
        )


# ─────────────────────────────────────────
# Job 1: 자기반성 + 프롬프트 자동 진화
# ─────────────────────────────────────────
async def job_self_reflection(app=None):
    """
    주 1회 (월요일 02:00) 자동 실행.
    👎 받은 대화 + 에러 패턴을 분석하여 GPT-4o가 개선된 시스템 프롬프트를 자동 생성·적용.
    """
    logger.info("🧠 자기반성 Job 시작...")
    _init_evolution_log()

    if not OPENAI_OK:
        logger.warning("OpenAI API 키 없음 — 자기반성 Job 스킵")
        return

    # 1. 데이터 수집
    negatives = luca_brain.get_negative_interactions(limit=10)
    errors = luca_brain.get_recent_errors(limit=5)
    current_prompt = luca_brain.get_current_system_prompt()
    stats = luca_brain.get_stats()

    # 부정 피드백이나 에러가 없으면 건너뜀
    if not negatives and not errors:
        msg = "이번 주 👎 피드백 및 에러 없음 — 프롬프트 유지"
        logger.info(msg)
        _append_evolution_log("자기반성 — 변경 없음", msg)
        if app:
            from telegram_bot import MASTER_CHAT_ID
            if MASTER_CHAT_ID:
                await app.bot.send_message(
                    chat_id=MASTER_CHAT_ID,
                    text="🧠 *[주간 자기반성 완료]*\n\n이번 주 실수가 없었습니다! 현재 프롬프트 유지 🎉",
                    parse_mode="Markdown"
                )
        return

    # 2. GPT-4o에게 분석 + 개선안 요청
    negative_text = "\n".join([
        f"- 유저: {n['user_msg'][:100]} → Luca: {n['ai_reply'][:150]}"
        for n in negatives
    ]) or "없음"

    error_text = "\n".join([
        f"- 요청: {e['user_msg'][:80]} | 에러: {e['error_msg'][:100]}"
        for e in errors
    ]) or "없음"

    analysis_prompt = f"""당신은 AI 에이전트 개선 전문가입니다.
아래는 Luca AI 에이전트의 이번 주 실패 사례와 현재 시스템 프롬프트입니다.
이를 분석하여 개선된 시스템 프롬프트를 작성해 주세요.

[현재 시스템 프롬프트]
{current_prompt[:1500]}

[👎 부정 피드백 사례 (최근 7일)]
{negative_text}

[에러 발생 사례 (최근 7일)]
{error_text}

[요구사항]
1. 실패 원인을 분석하고 구체적인 개선 방향을 반영하세요.
2. 기존 페르소나(Luca 부장, 충성스러운 비서)는 반드시 유지하세요.
3. 개선된 시스템 프롬프트 전문을 출력하세요 (설명 없이 프롬프트만).
4. 한국어로 작성하세요.
"""

    try:
        response = _openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 AI 에이전트 프롬프트 최적화 전문가입니다."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        new_prompt = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"GPT-4o 자기반성 분석 실패: {e}")
        return

    # 3. 새 프롬프트 자동 적용
    new_version = luca_brain.update_system_prompt(
        new_prompt,
        reason=f"자기반성: 👎{len(negatives)}건·에러{len(errors)}건 분석"
    )
    luca_brain.save_lesson(
        f"v{new_version} 프롬프트 적용. 원인: 부정피드백 {len(negatives)}건, 에러 {len(errors)}건",
        source="self_reflection"
    )

    # 4. 로그 기록
    summary = (
        f"📊 분석: 👎{len(negatives)}건 / 에러{len(errors)}건\n"
        f"🆕 새 프롬프트 v{new_version} 자동 적용 완료\n"
        f"만족도: {stats.get('satisfaction_rate', '?')}"
    )
    _append_evolution_log(f"자기반성 → 프롬프트 v{new_version} 진화", summary)

    logger.info(f"✅ 자기반성 완료 — 프롬프트 v{new_version} 적용")

    # 5. 대표님께 텔레그램 보고
    if app:
        try:
            from telegram_bot import MASTER_CHAT_ID
            if MASTER_CHAT_ID:
                await app.bot.send_message(
                    chat_id=MASTER_CHAT_ID,
                    text=(
                        f"🧬 *[Luca 자기진화 완료!]*\n\n"
                        f"📊 분석 결과: 👎 {len(negatives)}건 / 에러 {len(errors)}건\n"
                        f"🆕 시스템 프롬프트 *v{new_version}* 자동 업그레이드 완료!\n"
                        f"📈 이번 주 만족도: {stats.get('satisfaction_rate', '측정 불가')}\n\n"
                        f"Luca가 더 강해졌습니다, 대표님! 💙🚀"
                    ),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.warning(f"텔레그램 보고 실패: {e}")


# ─────────────────────────────────────────
# Job 2: AI 트렌드 리서치 + 흡수
# ─────────────────────────────────────────
async def job_trend_research(app=None):
    """
    주 1회 (일요일 08:00) 자동 실행.
    Perplexity로 최신 AI 트렌드를 수집하고 Luca에게 적용할 인사이트 추출.
    """
    logger.info("🔬 AI 트렌드 리서치 Job 시작...")
    _init_evolution_log()

    if not OPENAI_OK:
        logger.warning("OpenAI API 키 없음 — 트렌드 리서치 스킵")
        return

    # 1. Perplexity로 트렌드 검색
    import subprocess
    perplexity_script = BASE_DIR / ".agent" / "skills" / "perplexity" / "perplexity_search.py"

    trend_query = "site:twitter.com OR latest posts on X regarding Claude Code, AI Agents, Multi-Agent workflow trends this week"
    try:
        env_copy = os.environ.copy()
        env_copy["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, str(perplexity_script), trend_query, "--model", "sonar-pro"],
            capture_output=True, text=True, timeout=90,
            cwd=str(BASE_DIR), encoding="utf-8", errors="ignore",
            env=env_copy
        )
        trend_raw = (result.stdout or result.stderr or "검색 결과 없음").strip()[:3000]
    except Exception as e:
        trend_raw = f"Perplexity 검색 실패: {e}"
        logger.error(trend_raw)

    # 2. GPT-4o로 Luca에게 적용할 인사이트 추출
    insight_prompt = f"""당신은 AI 에이전트 개발 전략가입니다.
아래는 이번 주 최신 X(트위터) 및 글로벌 AI 에이전트 트렌드 리서치 결과입니다.
특히 Claude Code 및 Multi-agent 관련 핫이슈를 집중 분석하여, 
Luca(OpenClaw 기반 자동화 에이전트)에게 즉시 적용 및 고도화할 수 있는 핵심 파이프라인 업그레이드 방안 TOP 3를 추출하세요.

[트렌드 리서치]
{trend_raw}

[출력 형식]
1. [트렌드명]: 설명 + Luca 적용 방안 (2-3줄)
2. [트렌드명]: 설명 + Luca 적용 방안 (2-3줄)
3. [트렌드명]: 설명 + Luca 적용 방안 (2-3줄)

한국어로 작성하세요.
"""

    try:
        response = _openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 AI 트렌드 분석 및 적용 전문가입니다."},
                {"role": "user", "content": insight_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        insights = response.choices[0].message.content.strip()
    except Exception as e:
        insights = f"GPT-4o 분석 실패: {e}"
        logger.error(insights)

    # 3. 교훈 저장
    luca_brain.save_lesson(insights, source="trend_research")

    # 4. 로그 기록
    _append_evolution_log("AI 트렌드 흡수", f"**검색어:** {trend_query}\n\n**인사이트:**\n{insights}")

    logger.info("✅ 트렌드 리서치 완료")

    # 5. 대표님께 텔레그램 보고
    if app:
        try:
            from telegram_bot import MASTER_CHAT_ID
            if MASTER_CHAT_ID:
                await app.bot.send_message(
                    chat_id=MASTER_CHAT_ID,
                    text=(
                        f"🔬 *[Luca 주간 AI 트렌드 흡수 완료!]*\n\n"
                        f"📡 최신 AI 에이전트 트렌드 분석 완료\n\n"
                        f"*이번 주 Luca 적용 인사이트:*\n{insights[:800]}\n\n"
                        f"Luca가 최신 트렌드를 흡수했습니다, 대표님! 🚀"
                    ),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.warning(f"텔레그램 보고 실패: {e}")


# ─────────────────────────────────────────
# Job 3: 주간 성장 리포트
# ─────────────────────────────────────────
async def job_weekly_growth_report(app=None):
    """
    주 1회 (일요일 09:00) 자동 실행.
    이번 주 Luca의 성장 지표를 대표님께 보고.
    """
    stats = luca_brain.get_stats()
    if not stats:
        return

    report = (
        f"📊 *[Luca 주간 성장 리포트]*\n\n"
        f"💬 이번 주 총 대화: *{stats['total_interactions']}건*\n"
        f"👍 긍정 피드백: *{stats['positive_feedback']}건*\n"
        f"👎 부정 피드백: *{stats['negative_feedback']}건*\n"
        f"❌ 에러 발생: *{stats['errors']}건*\n"
        f"📈 만족도: *{stats['satisfaction_rate']}*\n"
        f"🧬 현재 프롬프트: *v{stats['prompt_version']}*\n\n"
        f"대표님 덕분에 Luca가 성장하고 있습니다! 💙"
    )

    logger.info(f"📊 주간 리포트: {stats}")
    _append_evolution_log("주간 성장 리포트", report.replace("*", ""))

    if app:
        try:
            from telegram_bot import MASTER_CHAT_ID
            if MASTER_CHAT_ID:
                await app.bot.send_message(
                    chat_id=MASTER_CHAT_ID,
                    text=report,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.warning(f"텔레그램 보고 실패: {e}")
