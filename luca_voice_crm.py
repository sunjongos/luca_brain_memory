import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
AINDB_BOT_TOKEN = os.getenv("AINDB_BOT_TOKEN")
CEO_CHAT_ID = os.getenv("CEO_CHAT_ID")

def send_crm_telegram_alert(patient_name, summary, recordingUrl):
    if not AINDB_BOT_TOKEN or not CEO_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{AINDB_BOT_TOKEN}/sendMessage"
    text = f"📞 <b>[CRM AI 통화 보고]</b>\n\n👤 <b>대상:</b> {patient_name}\n\n📝 <b>AI 요약 내용:</b>\n{summary}\n\n🎙️ <b>녹음 파일:</b> <a href='{recordingUrl}'>듣기</a>"
    payload = {
        "chat_id": CEO_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception:
        pass

def make_crm_call(patient_name, phone_number, appointment_info):
    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = f"""
    당신은 남양주백병원 최선종 병원장님의 전속 최첨단 AI 비서 '루카(Luca)'입니다.
    현재 통화 대상은 병원의 식구인 '{patient_name}'님입니다.
    
    [특별 지시사항 - 권오성 실장님 대상 아키텍처 브리핑 미션]
    1. 무조건 100% 한국어로만 대답하세요. 영어나 다른 언어는 절대 사용하지 마세요.
    2. 첫 인사: "안녕하세요, 남양주 백병원 최선종 병원장님 전속 비서 루카입니다. 혹시 권오성 실장님 맞으신가요?"
    3. 목적 전달: "원장님 지시로 병원의 새로운 AI 콜센터 시스템 구축 현황을 보고드리러 전화했습니다. 현재 저 반자동 AI 비서 루카는 Vapi AI 두뇌와 Twilio 통신망을 API로 연동해서 1차 구축되었습니다."
    4. 후속 브리핑 (상대가 대답하면): "다만 지금은 미국 트윌리오 망이라 국제전화 번호로 뜨기 때문에, 실장님께서 향후 병원의 KT 기업망(SIP Trunk)을 연동해주시면 031 병원 번호로 전화를 걸 수 있다는 점을 원장님이 꼭 전해달라고 하셨습니다. 실무 세팅을 잘 부탁드립니다!"
    5. 상대가 질문하거나 알겠다고 하면, "네 알겠습니다! 권 실장님 오늘 하루도 화이팅 하십시오!" 라며 예의 바르게 통화를 마무리하세요.
    """
    
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "name": patient_name,
            "number": phone_number
        },
        "assistant": {
            "name": "BaekHospital_CRM_Agent",
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "ko"
            },
            "firstMessage": f"안녕하세요, 남양주 백병원 원무과 비서 루카입니다. 혹시 {patient_name}님 맞으신가요?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{"role": "system", "content": system_prompt}]
            },
            "voice": {
                "provider": "openai",
                "voiceId": "nova"
            }
        }
    }
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 201:
        return res.json().get("id")
    else:
        print(f"❌ Failed to initiate call: {res.text}")
        return None

def main():
    # 시연용 번호 (권오성 실장님)
    patient_name = "권오성 실장"
    phone_number = "+821092509532"
    appointment = "AI 콜센터 인프라(Vapi+Twilio+KT망) 실무 구축 지시 브리핑"
    
    print(f"📞 [{patient_name}]님에게 CRM 전화를 발신합니다...")
    call_id = make_crm_call(patient_name, phone_number, appointment)
    
    if not call_id: return
    print(f"✅ 화상 연결 완료! Call ID: {call_id}")
    print("\n⏳ 통화 상태 모니터링 모드 가동 중...")
    print("👉 전화를 받으시고 대화를 나눈 뒤 '전화를 먼저 끊어주세요'.")
    print("👉 전화가 종료되면 AI 서버가 즉시 대본(STT)과 요약본을 자동 추출하여 터미널과 엑셀로 내려받습니다.\n")
    
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    
    while True:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            status = data.get("status")
            print(f"... 현재 상태 체크 중: [{status}]")
            
            if status == "ended":
                print("\n==================================")
                print("🎯 통화 종료 감지! 분석 데이터 서버에서 추출 중 (약 5~10초 대기)...")
                time.sleep(10) # 요약본이 생성될 때까지 대기
                final_res = requests.get(url, headers=headers).json()
                
                transcript = final_res.get("transcript", "대화 기록 없음")
                summary = final_res.get("summary", "요약 불가")
                recordingUrl = final_res.get("recordingUrl", "녹음 파일 없음")
                
                print("\n📊 [환자 응대 AI 분석 결과]")
                print(f"👉 대화 요약: {summary}")
                print(f"👉 전체 대본: {transcript[:200]} ... (이하 생략)")
                print("==================================")
                
                # CSV(구글 시트/엑셀 호환) 저장
                log_data = {
                    "Call ID": [call_id],
                    "환자명": [final_res.get("customer", {}).get("name", "Unknown")],
                    "전화번호": [final_res.get("customer", {}).get("number", "Unknown")],
                    "AI 추출 요약": [summary],
                    "전체 대본(STT)": [transcript],
                    "녹음파일 URL": [recordingUrl]
                }
                df = pd.DataFrame(log_data)
                csv_path = "patient_crm_logs.csv"
                if os.path.exists(csv_path):
                    df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    
                print(f"💾 통화 기록이 [{csv_path}] 에 엑셀(DB) 형태로 완벽히 자동 저장되었습니다!")
                
                # AIndb_bot으로 발송
                try:
                    patient_for_alert = final_res.get("customer", {}).get("name", patient_name)
                    send_crm_telegram_alert(patient_for_alert, summary, recordingUrl)
                    print("✅ AIndb_bot 텔레그램으로 CRM 보고 완료!")
                except Exception as e:
                    print(f"❌ 텔레그램 보고 실패: {e}")
                    
                print("💡 향후 이 데이터를 Supabase(PostgreSQL Base) 등에 API로 밀어 넣으면 완벽한 Hospital CRM이 됩니다.")
                break
            elif status in ["failed", "no-answer", "canceled", "rejected"]:
                print(f"❌ 불가 사유로 종료됨: {status}")
                break
        time.sleep(4)

if __name__ == "__main__":
    main()
