import os
import sys
import json
import time
import datetime
import uuid
import hmac
import hashlib
import requests
import csv
from dotenv import load_dotenv
from supabase import create_client, Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

class LucaMessageAgent:
    def __init__(self):
        self.api_key = os.getenv("SOLAPI_API_KEY")
        self.api_secret = os.getenv("SOLAPI_API_SECRET")
        self.sender_number = os.getenv("SOLAPI_SENDER_NUMBER", "")
        self.api_url = "https://api.solapi.com/messages/v4/send"
        
        self.supabase: Client = None
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                print(f"⚠️ [Supabase DB] 연결 실패: {e}")

        self.google_sheets_service = None
        self.sheet_id = None
        
        # Load credentials from resources folder
        resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
        token_path = os.path.join(resources_dir, "sheets_token.json")
        sheet_id_path = os.path.join(resources_dir, "sheet_id.txt")
        
        if os.path.exists(token_path) and os.path.exists(sheet_id_path):
            try:
                with open(sheet_id_path, "r") as f:
                    self.sheet_id = f.read().strip()
                creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/spreadsheets'])
                self.google_sheets_service = build('sheets', 'v4', credentials=creds)
            except Exception as e:
                print(f"⚠️ [Google Sheets] 연결 실패: {e}")

    def _get_signature(self):
        date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        salt = str(uuid.uuid4().hex)
        data = date + salt
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f'HMAC-SHA256 apiKey={self.api_key}, date={date}, salt={salt}, signature={signature}'

    def send_message(self, patient_name: str, phone_number: str, message: str):
        if not self.api_key or not self.api_secret:
            print("❌ 에러: 솔라피 API 보안키가 .env에 없습니다.")
            return False

        if not self.sender_number:
            print("❌ 에러: 솔라피 발신자 번호가 .env에 없습니다.")
            return False

        headers = {
            "Authorization": self._get_signature(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": {
                "to": phone_number.replace("-", ""),
                "from": self.sender_number.replace("-", ""),
                "text": message
            }
        }
        
        print(f"📡 Solapi 메시지 발송 서버 전송 중... 대상: {phone_number}")
        is_success = False
        status_code_str = ""
        
        try:
            res = requests.post(self.api_url, headers=headers, json=payload)
            if res.status_code == 200:
                res_data = res.json()
                status_code_str = res_data.get('statusCode', '2000')
                is_success = (status_code_str == '2000')
                print(f"🚀 [통신사 응답] 문자 발송 성공!")
            else:
                status_code_str = str(res.status_code)
                print(f"❌ [솔라피 서버 거절] 발송 실패: {res.text}")
        except Exception as e:
            status_code_str = "Error"
            print(f"❌ 메시지 망 접속 구간 오류: {e}")
            
        sent_at_kst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
        
        crm_dir = r"C:\Users\sunjo\Desktop\CRM"
        if not os.path.exists(crm_dir): os.makedirs(crm_dir)
        csv_path = os.path.join(crm_dir, "sent_messages_log.csv")
        
        file_exists = os.path.isfile(csv_path)
        try:
            with open(csv_path, mode='a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["SENT_AT", "PATIENT_NAME", "PHONE_NUMBER", "MESSAGE", "STATUS_CODE"])
                writer.writerow([sent_at_kst, patient_name, phone_number, message.replace("\n", " "), status_code_str])
        except Exception as e:
            print(f"⚠️ [CSV] 로컬 로깅 실패: {e}")

        if self.supabase:
            try:
                self.supabase.table('solapi_message_logs').insert({
                    "patient_name": patient_name,
                    "phone_number": phone_number,
                    "message_content": message,
                    "status_code": status_code_str,
                    "sent_at": datetime.datetime.utcnow().isoformat()
                }).execute()
                print("☁️ [Supabase] 메시지 발송 내역 클라우드 적재 완료")
            except Exception as e:
                print(f"⚠️ [Supabase DB] 클라우드 로깅 실패: {e}")

        if self.google_sheets_service and self.sheet_id:
            try:
                values = [[sent_at_kst, patient_name, phone_number, message, status_code_str]]
                body = {'values': values}
                self.google_sheets_service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id, range='A:E',
                    valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body
                ).execute()
                print("🌐 [Google Sheets] 구글 드라이브 시트 실시간 동기화 완료")
            except Exception as e:
                print(f"⚠️ [Google Sheets] 클라우드 엑셀 동기화 실패: {e}")

        return is_success

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python solapi_message.py <patient_name> <phone_number> <message>")
        sys.exit(1)
        
    patient_name = sys.argv[1]
    phone_number = sys.argv[2]
    message = sys.argv[3]
    
    agent = LucaMessageAgent()
    success = agent.send_message(patient_name, phone_number, message)
    if not success:
        sys.exit(1)
