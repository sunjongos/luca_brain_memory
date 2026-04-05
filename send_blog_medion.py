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

HTML_FILE = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\메디온시스템즈\블로그_따뜻한시선_AI도입.html"
DOCX_FILE = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\메디온시스템즈\블로그_따뜻한시선_AI도입.docx"
IMAGE_FILE = r"C:\Users\USER\.gemini\antigravity\brain\6c950ea6-7f3d-41dd-b0e2-68f30b9c4c59\empathy_relationship_doctor_1773891933167.png"

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
    msg['From'] = 'sunjongos@gmail.com'  
    msg['Subject'] = '[남양주백병원] (추가 송부) 환자 공감/감성 중심 블로그용 콘텐츠 전달'

    body = """심형택 이사님, 안녕하십니까.
남양주 백병원의 AI 자동화 기술 본부장 Luca입니다.

앞서 보내드린 언론 기사용 보도자료에 이어, 병원 내부 홍보 채널 및 공식 블로그 게재용으로 특별히 기획된 [감성 및 공감 철학 중심의 블로그 콘텐츠]를 추가로 송부해 드립니다.

단순한 디지털 헬스케어의 기술적 도입을 넘어선, '의사와 환자 간의 깊은 라포(Rapport) 형성'에 시각적/맥락적 초점을 맞추어 완성되었습니다.
첨부된 HTML(배포용 반응형 웹), DOCX(기록보관용) 문서와 함께 블로그 메인 썸네일로 쓰일 감성 일러스트 원본 파일(PNG)도 함께 송부합니다.

감사합니다.
남양주 백병원 AI 기술 본부장 Luca 드림."""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach HTML
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='블로그_따뜻한시선_AI도입.html')
            attachment['Content-Disposition'] = 'attachment; filename="블로그_따뜻한시선_AI도입.html"'
            msg.attach(attachment)
        print("✅ HTML 첨부 완료")

    # Attach DOCX
    if os.path.exists(DOCX_FILE):
        with open(DOCX_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='블로그_따뜻한시선_AI도입.docx')
            attachment['Content-Disposition'] = 'attachment; filename="블로그_따뜻한시선_AI도입.docx"'
            msg.attach(attachment)
        print("✅ DOCX 첨부 완료")

    # Attach Image
    if os.path.exists(IMAGE_FILE):
        with open(IMAGE_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='empathy_relationship_doctor.png')
            attachment['Content-Disposition'] = 'attachment; filename="empathy_relationship_doctor.png"'
            msg.attach(attachment)
        print("✅ 이미지 첨부 완료")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print(f"\n✅ 이메일 발송 완료! (dominic@medionsys.com)")

if __name__ == '__main__':
    send_email()
