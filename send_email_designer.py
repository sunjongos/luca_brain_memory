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
ZIP_FILE = os.path.join(BASE_DIR, "백병원_홈페이지개선_웹디자이너전달.zip")

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
    msg['To'] = 'rjwltakf78@naver.com'
    msg['From'] = 'sunjongos@gmail.com'
    msg['Subject'] = '[남양주백병원] 홈페이지 히어로섹션 개선안 - 웹디자이너 작업 요청'

    body = """이은성 본부장님 안녕하세요.

남양주백병원 홈페이지 히어로섹션(메인 슬라이더) 개선 작업을 요청드립니다.

━━━━━━━━━━━━━━━━━━━━━━━━━
▶ 작업 내용
━━━━━━━━━━━━━━━━━━━━━━━━━
현재 7개 슬라이드 → 8개 슬라이드로 개선

[원본 유지 슬라이드 - 3개]
① 정진엽 의료원장
② 보건복지부 4주기 인증의료기관
⑦ 간호·간병 통합서비스

[신규 제작 필요 슬라이드 - 5개]
③ 최선종 병원장 - 척추센터 (서울의대, 내시경척추수술, 재수술 전문)
④ 강진호 병원장 - 뇌신경센터 (서울대병원 신경과 연구위원)
⑤ 관절센터 - 김용래 원장(로봇인공관절) + 백사무엘 센터장(어깨 관절경)
⑥ GE 하이엔드 장비 4종 (남양주 유일) - 3.0T AI MRI, 128채널 CT, E10S/Fortis 초음파
⑧ 5대 센터 원스톱 통합진료 (척추관절/뇌신경/소화기/건강증진/응급)

━━━━━━━━━━━━━━━━━━━━━━━━━
▶ 첨부 파일 안내 (ZIP 압축)
━━━━━━━━━━━━━━━━━━━━━━━━━
- 02_히어로섹션_초안.html : 8슬라이드 완성 HTML 시안 (브라우저에서 바로 확인 가능)
- 03_히어로섹션_디자이너지시서.md : 각 슬라이드별 텍스트·컬러·카드 상세 지시서
- 신규_슬라이드/ : 신규 슬라이드 개별 HTML 코드 조각
- README.md : 전체 프로젝트 안내 (링크, 의료진 정보 포함)

━━━━━━━━━━━━━━━━━━━━━━━━━
▶ 디자인 방향
━━━━━━━━━━━━━━━━━━━━━━━━━
- 다크 네이비 배경 + 슬라이드별 포인트 컬러
- 폰트: Noto Sans KR (Bold/Black 위주)
- 상단 신뢰 정보 자동 스크롤 바 (병원 핵심 자산 노출)
- 모바일 반응형 필수 (768px 이하 대응)
- 6.5초 자동 전환 + 터치 스와이프 + 좌우 화살표

첨부 HTML 파일을 브라우저로 열면 전체 시안을 바로 확인하실 수 있습니다.
문의사항은 언제든 연락주세요.

감사합니다.
남양주백병원 드림"""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # ZIP 첨부
    if os.path.exists(ZIP_FILE):
        with open(ZIP_FILE, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name='백병원_홈페이지개선_웹디자이너전달.zip')
            attachment['Content-Disposition'] = 'attachment; filename="백병원_홈페이지개선_웹디자이너전달.zip"'
            msg.attach(attachment)
        print(f"✅ ZIP 파일 첨부 완료: {ZIP_FILE}")
    else:
        print(f"⚠️ ZIP 파일 없음: {ZIP_FILE}")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print(f"\n✅ 이메일 발송 완료!")
    print(f"   수신: rjwltakf78@naver.com (이은성 본부장)")
    print(f"   메시지 ID: {result.get('id')}")

if __name__ == '__main__':
    send_email()
