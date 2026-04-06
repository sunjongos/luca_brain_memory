import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Configuration & Constants
# -------------------------------------------------------------------
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
AINDB_BOT_TOKEN = os.getenv("AINDB_BOT_TOKEN")
CEO_CHAT_ID = os.getenv("CEO_CHAT_ID")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
TELEGRAM_URL_TEMPLATE = "https://api.telegram.org/bot{token}/sendMessage"

API_TIMEOUT_SECONDS = 120  # Perplexity can take some time for deep research
MAX_RETRIES = 3           # Max retries for transient errors
BACKOFF_FACTOR = 1.0      # Backoff multiplier: {backoff factor} * (2 ** ({number of total retries} - 1))

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
def setup_logger() -> logging.Logger:
    logger = logging.getLogger("AIndb_Briefing")
    logger.setLevel(logging.INFO)
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # File Handler
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, "RiskBriefing.log")
    try:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
        fh = None
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    if fh:
        fh.setFormatter(formatter)
        
    logger.addHandler(ch)
    if fh:
        logger.addHandler(fh)
        
    return logger

logger = setup_logger()

# -------------------------------------------------------------------
# Robust HTTP Session setup
# -------------------------------------------------------------------
def get_resilient_session() -> requests.Session:
    """Returns a requests Session with retry logic configured."""
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        read=MAX_RETRIES,
        connect=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# -------------------------------------------------------------------
# Core Logic Functions
# -------------------------------------------------------------------
def build_prompt() -> str:
    """Builds the deep research prompt with structured expectations."""
    date_str = datetime.now().strftime('%Y년 %m월 %d일')
    return f"""
오늘 날짜({date_str}) 기준으로, 한국의 병원 경영과 관련된 최신 뉴스 및 트렌드를 웹에서 심층 검색하세요.

[필수 검색 및 분석 영역 4가지]
1. 재료 수급 리스크: 나프타, 플라스틱 원룟값, 물류 대란 등 원자재 이슈와 이로 인해 가격이 인상될 수 있는 병원 소모품(주사기, 수술장갑, 3000cc 수액, 약봉투, 쓰레기봉투 등) 수급 동향
2. 관리급여 리스크: 의료계 인건비 동향, 최저임금, 노무/근로 규제 등
3. 실비보험 개편: 플랫폼 청구 간소화, 금융감독원/정부의 비급여 실손 지급 기준 강화 등
4. 수가 개편: 건강보험 상대가치점수 변화, 심평원 삭감 이슈, 필수의료 수가 등

요청사항: 
위 4가지 영역을 전체적으로 스캔한 뒤, '오늘 병원장 관점에서 가장 시급하게 체크하고 선제 대응(선결제, 대비책 마련 등)해야 할 핵심 액션 아이템'을 1~3가지로 요약하여 보고해주세요.
반드시 텔레그램 메세지에 바로 보낼 수 있도록 마크다운(* 기호 등)이나 HTML 태그(<b>, <ol> 등)를 절대 사용하지 말고, 순수 텍스트와 이모지만 사용하여 가독성 있게 작성해주세요. 불필요한 서론은 빼고 요점만 작성해주세요.
"""

def fetch_hospital_risks(session: requests.Session) -> Optional[str]:
    """Fetches insights from Perplexity API with robust error handling."""
    if not PERPLEXITY_API_KEY:
        logger.error("PERPLEXITY_API_KEY is not set in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "당신은 병원 경영 전략을 돕는 최고의 AI 리서치 어시스턴트입니다."},
            {"role": "user", "content": build_prompt()}
        ]
    }

    logger.info("🔍 Requesting daily risk analysis from Perplexity API...")
    
    try:
        response = session.post(
            PERPLEXITY_URL, 
            headers=headers, 
            json=payload, 
            timeout=API_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        
        if not content:
            logger.warning("Perplexity API returned successful status but empty content.")
            return None
            
        logger.info("✅ Successfully received research insights from Perplexity.")
        return content

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network/HTTP Error during Perplexity API call: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON response from Perplexity API: {e}")
    except Exception as e:
        logger.error(f"❌ Critical unexpected error during Perplexity API call: {e}", exc_info=True)
        
    return None

def send_telegram_alert(session: requests.Session, message: str) -> bool:
    """Sends a Telegram alert to the mapped CEO Chat ID safely."""
    if not AINDB_BOT_TOKEN or not CEO_CHAT_ID:
        logger.error("AINDB_BOT_TOKEN or CEO_CHAT_ID is missing. Cannot send Telegram alert.")
        return False
        
    url = TELEGRAM_URL_TEMPLATE.format(token=AINDB_BOT_TOKEN)
    final_message = f"📈 [AIndb 일일 병원 경영 리스크 브리핑]\n\n{message}"
    
    payload = {
        "chat_id": CEO_CHAT_ID,
        "text": final_message,
        "disable_web_page_preview": False
    }
    
    logger.info("📫 Dispatching briefing data to Telegram...")
    try:
        response = session.post(url, json=payload, timeout=15)
        response.raise_for_status()
        logger.info("✅ Briefing payload successfully delivered to Telegram!")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send Telegram alert: {e}")
        try:
            logger.debug(f"Response details: {response.text}")
        except Exception:
            pass
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending to Telegram: {e}", exc_info=True)
        return False

# -------------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------------
def main():
    logger.info("=== Starting Daily Hospital Risk Briefing Script ===")
    
    with get_resilient_session() as session:
        report_content = fetch_hospital_risks(session)
        
        if report_content:
            success = send_telegram_alert(session, report_content)
            if success:
                logger.info("=== Workflow Completed Successfully ===")
            else:
                logger.error("=== Workflow Failed at Delivery Stage ===")
        else:
            logger.error("=== Workflow Aborted: No valid payload generated ===")
            # Optionally send a failure notification to Telegram
            error_message = "🚨 오늘자 위험 리스크 조사를 실패했습니다. 서버 로그를 다시 확인해 주세요."
            send_telegram_alert(session, error_message)

if __name__ == "__main__":
    main()
