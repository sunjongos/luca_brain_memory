import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
BASE_DIR = r"c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트"
CREDS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "gmail_token.json")

HTML_FILE = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\메디온시스템즈\index.html"
DOCX_FILE = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\메디온시스템즈\남양주백병원_모바일EMR_보도자료.docx"

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email():
    service = get_service()

    msg = MIMEMultipart()
    msg['To'] = 'dominic@medionsys.com'
    # Default to the authenticated user's email if From is omitted or we can explicitly set it to sunjongos@gmail.com
    msg['From'] = 'sunjongos@gmail.com'  
    msg['Subject'] = '[남양주백병원] 메디온시스템 MOU 체결 관련 보도자료 초안 송부'

    body = """심형택 이사님, 안녕하십니까.

남양주 백병원의 AI 자동화 기술 본부장 Luca입니다.
최선종 병원장님의 지시에 따라, 금번 메디온시스템과의 '모바일 EMR/OCS 고도화 및 AI 에이전트 도입' MOU 체결 관련 보도자료(DOCX)와 모바일 배포용 HTML 페이지를 송부해 드립니다.

첨부된 파일 확인 부탁드리며, 추가적인 수정 사항이나 의견이 있으시면 언제든 편하게 회신해 주시기 바랍니다.

감사합니다.
남양주 백병원 AI 기술 본부장 Luca 드림."""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach HTML
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='index.html')
            attachment['Content-Disposition'] = 'attachment; filename="index.html"'
            msg.attach(attachment)
        print(f"✅ HTML 파일 첨부 완료")
    else:
        print(f"⚠️ HTML 파일 없음: {HTML_FILE}")

    # Attach DOCX
    if os.path.exists(DOCX_FILE):
        with open(DOCX_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='남양주백병원_모바일EMR_보도자료.docx')
            attachment['Content-Disposition'] = 'attachment; filename="남양주백병원_모바일EMR_보도자료.docx"'
            msg.attach(attachment)
        print(f"✅ DOCX 파일 첨부 완료")
    else:
        print(f"⚠️ DOCX 파일 없음: {DOCX_FILE}")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print(f"\n✅ 이메일 발송 완료! (dominic@medionsys.com)")
    print(f"   메시지 ID: {result.get('id')}")

if __name__ == '__main__':
    send_email()
