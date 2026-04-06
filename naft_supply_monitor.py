import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

AINDB_BOT_TOKEN = os.getenv("AINDB_BOT_TOKEN")
CEO_CHAT_ID = os.getenv("CEO_CHAT_ID")

def send_telegram_alert(message):
    if not AINDB_BOT_TOKEN or not CEO_CHAT_ID:
        print("❌ Error: AINDB_BOT_TOKEN or CEO_CHAT_ID not found in .env")
        return
        
    url = f"https://api.telegram.org/bot{AINDB_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CEO_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Alert sent via Telegram (AIndb_bot)")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}\nResponse: {response.text if 'response' in locals() else ''}")

def monitor_hospital_supply_news():
    # Keywords indicating hospital supply chain risk
    queries = ["나프타 대란 OR 나프타 수급", "쓰레기봉투 대란", "석유화학 파업", "플라스틱 원룟값 폭등 OR 석유화학 수급"]
    
    found_articles = []
    
    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            res = requests.get(url)
            res.raise_for_status()
            root = ET.fromstring(res.content)
            
            # Get the first 2 items
            for item in root.findall(".//item")[:2]:
                title = item.findtext("title")
                link = item.findtext("link")
                found_articles.append(f"• <a href='{link}'>{title}</a>")
                
        except Exception as e:
            continue
            
    # Send test message first so the user can verify integration regardless of news presence
    send_telegram_alert("✅ <b>[AIndb_bot 테스트]</b> 병원 소모품(나프타/플라스틱) 공급망 모니터링 모듈이 정상 가동되었습니다.")

    if found_articles:
        unique_articles = list(set(found_articles))[:5] # limit to 5
        
        alert_msg = "🚨 <b>[경영 리스크 감지] 원자재(나프타 등) 수급 불안 및 관련 뉴스</b>\n\n"
        alert_msg += "공급망 이슈가 감지되었습니다. <b>추천 대응 가이드</b>를 긴급 보고 드립니다.\n\n"
        alert_msg += "✅ <b>즉시 선결제 및 물량 우선 확보 권고 항목:</b>\n"
        alert_msg += "- 병원 주사기\n"
        alert_msg += "- 수술용 장갑\n"
        alert_msg += "- 3000cc 수액\n"
        alert_msg += "- 원보 및 약봉투 등 주요 비닐/플라스틱\n\n"
        alert_msg += "<b>📌 관련 최신 뉴스:</b>\n"
        alert_msg += "\n".join(unique_articles)
        
        send_telegram_alert(alert_msg)
    else:
        print("✅ No critical supply chain news detected at this moment.")

if __name__ == "__main__":
    print("🔍 Starting Naft supply chain monitor...")
    monitor_hospital_supply_news()
