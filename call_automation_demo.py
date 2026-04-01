import requests
import json
import time

def make_ai_call(patient_name, phone_number, message_summary):
    """
    오픈클로(Openclo) 또는 트윌리오(Twilio) 등 AI 콜 서비스 API를 연동하여 실제 전화를 거는 예제 함수입니다.
    CRM과 연동된 루카(Luca)의 자동 전화 송출 에이전트 역할을 수행합니다.
    """
    # [주의] 아래 URL과 API Key는 가입하신 실제 시스템(오픈클로 등)의 공식 문서에 맞게 변경해야 합니다.
    api_url = "https://api.example-aicall.com/v1/call" 
    api_key = "YOUR_API_KEY_HERE" # 발급받은 실제 API 키 입력
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 전화 통화 시 AI 모델이 음성(TTS)으로 자연스럽게 읽어줄 대본
    ai_script = f"안녕하세요 {patient_name}님, 남양주 백병원 AI 비서입니다. {message_summary}"
    
    # API 요청 데이터 구성
    payload = {
        "to": phone_number,               # 수신자 (환자)
        "from": "031-000-0000",           # 병원 발신용 대표 번호
        "script": ai_script,              # AI 통화 대본
        "voice_type": "professional_f",   # 음성 톤 (차분한, 신뢰감 있는 목소리 등 설정)
        "record_call": True               # 통화 녹음 후 CRM 기록용 옵션 (선택)
    }
    
    print(f"📞 [{patient_name}]님({phone_number})에게 전화를 연결 중입니다...")
    print(f"🗣️ AI 스크립트: {ai_script}")
    
    try:
        # --- 실제 통신 코드는 아래 주석을 해제하면 작동합니다 ---
        # response = requests.post(api_url, headers=headers, json=payload)
        # response.raise_for_status()
        # print("✅ 전화 발신 요청 성공:", response.json())
        
        # 데모 진행을 위한 시뮬레이션
        time.sleep(1.5)
        print("✅ 전화 발신 요청이 성공적으로 서버에 전달되었습니다. (통화 연결 중...)\n")
        return True
    except Exception as e:
        print(f"❌ 전화 발신 실패: {e}\n")
        return False

# ==========================================
# 🚀 메인 실행 로직 (CRM 연동 시뮬레이션)
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print(" 🤖 루카(Luca) 환자 케어 자동 전화 시스템 (CRM 연동 데모)")
    print("=" * 60 + "\n")
    
    # 1. EMR/CRM에서 불러온 가상의 환자 데이터 모델
    crm_patients = [
        {"name": "김진호", "phone": "010-1234-5678", "appointment": "내일 오후 2시", "doctor": "최선종 원장님"},
        {"name": "이영희", "phone": "010-9876-5432", "appointment": "모레 오전 10시", "doctor": "강진호 원장님"}
    ]
    
    # 2. 조건에 맞는 환자를 필터링하여 맞춤 메시지를 기획하고 발신
    for patient in crm_patients:
        # 목적: 진료 예약 리마인드 및 주의사항 안내 (AI가 맞춤 요약 생성)
        message = f"예약하신 {patient['appointment']} {patient['doctor']} 진료 일정을 리마인드 해 드립니다. 이전 진료 때 말씀드린 대로 편안한 마음으로 내원해 주시기 바랍니다."
        
        # 전화 걸기 엔진 호출
        make_ai_call(
            patient_name=patient["name"], 
            phone_number=patient["phone"], 
            message_summary=message
        )
