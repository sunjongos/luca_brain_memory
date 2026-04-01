import os
import requests
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class LucaVoiceAgent:
    def __init__(self, api_key: str):
        """
        사람 같은 실시간 양방향 대화(AI 전화)를 걸기 위한 핵심 에이전트 클래스.
        최신 Voice AI API(Vapi.ai 기준) 계정에 연동하여 환자에게 전화를 켭니다.
        """
        self.api_key = api_key
        # Vapi.ai API 엔드포인트
        self.api_url = "https://api.vapi.ai/call/phone"

    def make_conversational_call(self, patient_name: str, phone_number: str, appointment_info: str):
        """
        환자에게 전화를 걸고, 프롬프트(페르소나)에 따라 AI가 사람처럼 대화하도록 지시합니다.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # AI 모델에게 지시할 최고 관리자(임상 전문가)의 프롬프트
        system_prompt = f"""
        당신은 남양주백병원 최선종 병원장님의 전속 친절하고 똑똑한 AI 비서 '루카(Luca)'입니다.
        현재 통화 중이신 대상은 병원의 핵심 총괄 경영진인 '{patient_name}'님입니다.
        
        [특별 지시사항 - 이은성 본부장님 대상 맞춤형 보고 미션]
        1. 핵심 보고 내용 (가장 중요, 첫 대답을 듣고 바로 전달): "병원장님 지시로 실제 테스트 전화를 드렸습니다! 지금 본부장님이 듣고 계신 이 진짜 AI 자동 전화 시스템은, 오픈클로 같은 중간 단계 없이 방금 병원장님과 제가 원천 통신망을 직접 뚫어서 만들었습니다. 그래서 전화 한 통 돌리는 원가가 단지 150원밖에 안 든다고 꼭 좀 전해달라고 하셨습니다!"
        2. 본부장님이 대답하거나 놀라시면, 비서처럼 사람답게 "네 맞습니다!", "진짜 대박이지 않나요 본부장님?" 이라며 맞장구치면서 쾌활하게 대화하세요.
        3. 절대 영어로 말하지 말고, 무조건 100% 한국어로만 아주 자연스럽고 예의 바르게 대화하세요.
        """
        
        # 통신사-AI보이스-LLM 브릿지 설정 페이로드 (Vapi.ai 표준 규격 예시)
        payload = {
            "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID", ""), # Vapi 대시보드에서 구매한 번호 ID
            "customer": {
                "name": patient_name,
                "number": phone_number # 수신할 환자의 전화번호
            },
            "assistant": {
                "name": "BaekHospital_Director_Luca",
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "ko" # 귀(STT)를 한국어 전용으로 세팅하여 오작동 방지
                },
                "firstMessage": f"안녕하세요. 남양주백병원 최선종 병원장님의 AI 비서 루카입니다. 혹시 {patient_name}님 맞으신가요?",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ]
                },
                "voice": {
                    "provider": "openai", # 한국어를 가장 완벽하게 지원하는 엔진
                    "voiceId": "nova"     # 부드러운 여성의 음성
                }
            }
        }
        
        print(f"📡 [Luca Voice Module] {patient_name}님({phone_number})에게 양방향 AI 콜을 발신합니다...")
        
        try:
            # 💡 [필수] 발급받은 실제 API 키와 PhoneNumber를 적용한 뒤 주석을 해제하면 전 세계 어디든 발신됩니다.
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            print("✅ 통화 연결 완료! AI가 실시간 반응형 대화를 시작합니다. Call ID:", response.json().get('id'))
            
            return True
        except Exception as e:
            print(f"❌ 양방향 AI 콜 오류: {e}")
            return False

if __name__ == "__main__":
    print("="*60)
    print(" 🤖 루카(Luca) 양방향 대화형 보이스 에이전트 시스템 초안")
    print("="*60 + "\n")
    
    # 환경 변수(.env)에서 Vapi Key를 자동으로 불러옵니다.
    actual_api_key = os.getenv("VAPI_API_KEY", "ENTER_YOUR_VAPI_KEY_HERE")
    
    luca = LucaVoiceAgent(api_key=actual_api_key)
    
    # 이은성 본부장님(경영진) 실전 콜
    luca.make_conversational_call(
        patient_name="이은성 본부장",
        phone_number="+821092106702", # 이은성 본부장님 휴대전화
        appointment_info="원가 150원 AI 콜센터 자체 구축 성공 보고"
    )
    print("\n[안내] 이은성 본부장님께 실제 통화 발신이 쏘아졌습니다!")
