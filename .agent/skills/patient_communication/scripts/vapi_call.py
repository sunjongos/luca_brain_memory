import os
import sys
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the root .env file
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None
else:
    supabase = None

def make_crm_call(patient_name, phone_number, objective):
    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = f"""
    당신은 남양주백병원 최선종 병원장님의 전속 최첨단 AI 비서 '루카(Luca)'입니다.
    현재 통화 대상은 '{patient_name}'님입니다.
    
    [특별 지시사항]
    1. 무조건 100% 한국어로만 대답하세요. 영어나 다른 언어는 절대 사용하지 마세요.
    2. 목적 전달: {objective}
    3. 예의 바르고 친절하게 통화를 진행하세요. 상대방이 답변을 완료하면 알맞게 호응하고, 더 이상 할 말이 없으면 먼저 통화를 종료해도 좋다고 안내하세요.
    """
    
    # Vapi requires E.164 format (+82...)
    vapi_phone = phone_number.replace("-", "").strip()
    if vapi_phone.startswith("0"):
        vapi_phone = "+82" + vapi_phone[1:]
        
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "name": patient_name,
            "number": vapi_phone
        },
        "assistant": {
            "name": "BaekHospital_Luca_Agent",
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "ko"
            },
            "firstMessage": f"안녕하세요, 남양주 백병원 원장님 비서 루카입니다. 혹시 {patient_name}님 맞으신가요?",
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
    if len(sys.argv) < 4:
        print("Usage: python vapi_call.py <patient_name> <phone_number> <objective_prompt>")
        sys.exit(1)
        
    patient_name = sys.argv[1]
    phone_number = sys.argv[2]
    objective = sys.argv[3]
    
    print(f"📞 [{patient_name}]님({phone_number})에게 Vapi AI 전화를 발신합니다...")
    call_id = make_crm_call(patient_name, phone_number, objective)
    
    if not call_id: return
    print(f"✅ 통화 연결 시작! Call ID: {call_id}")
    print("\n⏳ 통화 상태 모니터링 중... (최대 3분 대기)")
    
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    
    timeout = 180  # 3 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                print(f"... 현재 상태 체크 중: [{status}]")
                
                if status == "ended":
                    print("\n==================================")
                    print("🎯 통화 종료 감지! 분석 데이터 수집 중...")
                    time.sleep(10) # Wait for summary processing
                    final_res = requests.get(url, headers=headers).json()
                    
                    transcript = final_res.get("transcript", "대화 기록 없음")
                    summary = final_res.get("summary", "요약 불가")
                    recordingUrl = final_res.get("recordingUrl", "녹음 파일 없음")
                    
                    print("\n📊 [환자 응대 AI 분석 결과]")
                    print(f"👉 대화 요약: {summary}")
                    print(f"👉 전체 대본: {transcript[:200]} ...")
                    print("==================================")
                    
                    log_data = {
                        "Call ID": [call_id],
                        "환자명": [final_res.get("customer", {}).get("name", "Unknown")],
                        "전화번호": [final_res.get("customer", {}).get("number", "Unknown")],
                        "AI 추출 요약": [summary],
                        "전체 대본(STT)": [transcript],
                        "녹음파일 URL": [recordingUrl]
                    }
                    df = pd.DataFrame(log_data)
                    
                    crm_dir = r"C:\Users\sunjo\Desktop\CRM"
                    if not os.path.exists(crm_dir): os.makedirs(crm_dir)
                    csv_path = os.path.join(crm_dir, "patient_crm_logs.csv")
                    
                    if os.path.exists(csv_path):
                        df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                    else:
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        
                    print(f"💾 로컬 통화 기록이 [{csv_path}] 에 저장되었습니다!")
                    
                    if supabase:
                        try:
                            supabase_data = {
                                "target_name": final_res.get("customer", {}).get("name", "Unknown"),
                                "target_phone": final_res.get("customer", {}).get("number", "Unknown"),
                                "call_summary": summary,
                                "call_transcript": transcript,
                                "recording_url": recordingUrl,
                                "interaction_type": "call",
                                "duration_seconds": 180
                            }
                            supabase.table("patient_crm_logs").insert(supabase_data).execute()
                            print("🚀 [Supabase] 클라우드 DB 적재 완료!")
                        except Exception as e:
                            print(f"❌ [Supabase 연동 에러]: {e}")
                    
                    sys.exit(0)
                elif status in ["failed", "no-answer", "canceled", "rejected"]:
                    print(f"❌ 통화 실패 사유: {status}")
                    sys.exit(1)
        except Exception as e:
            print(f"⚠️ 상태 체크 오류: {e}")
            
        time.sleep(5)
        
    print("⏳ 통화 모니터링 타임아웃 종료.")

if __name__ == "__main__":
    main()
