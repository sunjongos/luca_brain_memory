import os
import csv
import time
import datetime
import uuid
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# Try importing supabase and google apis, but don't fail if missing
try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None

load_dotenv()

class LucaMessageAgent:
    def __init__(self):
        self.api_key = os.getenv("SOLAPI_API_KEY")
        self.api_secret = os.getenv("SOLAPI_API_SECRET")
        self.sender_number = os.getenv("SOLAPI_SENDER_NUMBER", "")
        self.api_url = "https://api.solapi.com/messages/v4/send"

        self.supabase = None
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if create_client and supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                print(f"[WARN] Supabase 연결 실패: {e}")

        self.google_sheets_service = None
        self.sheet_id = None
        token_path = "sheets_token.json"
        sheet_id_path = "sheet_id.txt"
        if build and os.path.exists(token_path) and os.path.exists(sheet_id_path):
            try:
                with open(sheet_id_path, "r", encoding="utf-8") as f:
                    self.sheet_id = f.read().strip()
                creds = Credentials.from_authorized_user_file(
                    token_path,
                    ['https://www.googleapis.com/auth/spreadsheets']
                )
                self.google_sheets_service = build('sheets', 'v4', credentials=creds)
            except Exception as e:
                print(f"[WARN] Google Sheets 연결 실패: {e}")

    def _utc_now_str(self):
        return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def _get_signature(self):
        date = self._utc_now_str()
        salt = uuid.uuid4().hex
        data = date + salt
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()
        return f'HMAC-SHA256 apiKey={self.api_key}, date={date}, salt={salt}, signature={signature}'

    def _headers(self):
        return {
            "Authorization": self._get_signature(),
            "Content-Type": "application/json",
        }

    def _poll_delivery_result(self, group_id: str, message_id: str = None, max_attempts: int = 6, wait_seconds: int = 2):
        final_status = {
            "success": False,
            "status_code": "PENDING",
            "detail": "",
            "group_id": group_id,
            "message_id": message_id,
        }

        for _ in range(max_attempts):
            time.sleep(wait_seconds)
            group_res = requests.get(
                f"https://api.solapi.com/messages/v4/groups/{group_id}",
                headers=self._headers(),
                timeout=30,
            )
            if group_res.status_code != 200:
                continue

            group_data = group_res.json()
            count = group_data.get("count", {})
            if count.get("sentSuccess", 0) > 0:
                final_status["success"] = True
                final_status["status_code"] = "DELIVERED"
                final_status["detail"] = "carrier delivered"
                return final_status

            if count.get("sentFailed", 0) > 0:
                msg_res = requests.get(
                    f"https://api.solapi.com/messages/v4/groups/{group_id}/messages",
                    headers=self._headers(),
                    timeout=30,
                )
                if msg_res.status_code == 200:
                    msg_list = msg_res.json().get("messageList", {})
                    target_msg = None
                    if message_id and message_id in msg_list:
                        target_msg = msg_list[message_id]
                    elif msg_list:
                        target_msg = next(iter(msg_list.values()))

                    if target_msg:
                        final_status["status_code"] = str(target_msg.get("statusCode", "FAILED"))
                        logs = target_msg.get("log", [])
                        if logs:
                            final_status["detail"] = logs[-1].get("message", "")
                else:
                    final_status["status_code"] = "FAILED"
                    final_status["detail"] = f"group message lookup failed: HTTP {msg_res.status_code}"
                return final_status

        return final_status

    def send_message(self, patient_name: str, phone_number: str, message: str, is_kakao: bool = True):
        print(f"[Luca Message Module] {patient_name} ({phone_number}) 발송 시작")
        if not self.api_key or not self.api_secret:
            print("[ERROR] SOLAPI_API_KEY / SOLAPI_API_SECRET가 없습니다.")
            return False

        if not self.sender_number:
            print("[ERROR] SOLAPI_SENDER_NUMBER가 없습니다.")
            return False

        final_message = f"[남양주백병원 안내]\n안녕하세요 {patient_name}님.\n\n{message}\n\n감사합니다.\n- 최선종 병원장 드림"
        if "사랑하는 공주" in patient_name:
            final_message = message

        payload = {
            "message": {
                "to": phone_number.replace("-", ""),
                "from": self.sender_number.replace("-", ""),
                "text": final_message,
            }
        }

        is_success = False
        status_code_str = ""
        failure_detail = ""
        group_id = None
        message_id = None

        try:
            print("[INFO] Solapi 발송 요청 중...")
            res = requests.post(self.api_url, headers=self._headers(), json=payload, timeout=30)
            if res.status_code == 200:
                res_data = res.json()
                group_id = res_data.get("groupId")
                message_id = res_data.get("messageId")
                status_code_str = str(res_data.get("statusCode", "2000"))
                if group_id:
                    polled = self._poll_delivery_result(group_id, message_id)
                    is_success = polled["success"]
                    status_code_str = polled["status_code"]
                    failure_detail = polled["detail"]
                else:
                    is_success = (status_code_str == "2000")
            else:
                status_code_str = str(res.status_code)
                failure_detail = res.text
                print(f"[ERROR] Solapi 서버 거절: {res.text}")
        except Exception as e:
            status_code_str = "ERROR"
            failure_detail = str(e)
            print(f"[ERROR] 메시지 전송 예외: {e}")

        sent_at_kst = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')

        csv_path = "sent_messages_log.csv"
        file_exists = os.path.isfile(csv_path)
        try:
            with open(csv_path, mode='a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["SENT_AT", "PATIENT_NAME", "PHONE_NUMBER", "MESSAGE", "STATUS_CODE", "DETAIL", "GROUP_ID", "MESSAGE_ID"])
                writer.writerow([
                    sent_at_kst,
                    patient_name,
                    phone_number,
                    final_message.replace("\n", " "),
                    status_code_str,
                    failure_detail,
                    group_id,
                    message_id,
                ])
        except Exception as e:
            print(f"[WARN] CSV 로깅 실패: {e}")

        if self.supabase:
            try:
                self.supabase.table('solapi_message_logs').insert({
                    "patient_name": patient_name,
                    "phone_number": phone_number,
                    "message_content": final_message,
                    "status_code": status_code_str,
                    "detail": failure_detail,
                    "group_id": group_id,
                    "message_id": message_id,
                    "sent_at": datetime.datetime.now(datetime.UTC).isoformat(),
                }).execute()
                print("[INFO] Supabase 메시지 로그 적재 완료")
            except Exception as e:
                print(f"[WARN] Supabase 로깅 실패: {e}")

        if is_success:
            print(f"[OK] 실제 문자 전송 성공: {patient_name} / {phone_number}")
        else:
            print(f"[FAIL] 실제 문자 전송 실패: status={status_code_str} detail={failure_detail}")

        return is_success

if __name__ == "__main__":
    agent = LucaMessageAgent()
    agent.send_message(
        patient_name="테스트 수신자",
        phone_number="010-0000-0000",
        message="루카 메시지 모듈 테스트입니다.",
        is_kakao=False,
    )
