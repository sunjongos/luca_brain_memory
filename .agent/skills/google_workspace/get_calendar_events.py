import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def get_upcoming_events():
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("인증 실패: token.json이 유효하지 않습니다.")
            return

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 오늘 날짜 기준으로 다가오는 10개의 일정 가져오기
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('예정된 일정이 없습니다. 편안한 하루 보내십시오, 대표님!')
            return

        print('=== 다가오는 일정 목록 ===')
        for event in events:
            # datetime이 있으면 시간을, 없으면 날짜(종일 일정)를 가져옴
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '(제목 없음)')
            # 보기 편하게 문자열 파싱 (예: 2026-02-28T15:00:00+09:00 -> 2026-02-28 15:00)
            if 'T' in start:
                date_part, time_part = start.split('T')
                time_str = time_part[:5] # 시:분만 추출
                print(f"- {date_part} {time_str} | {summary}")
            else:
                print(f"- {start} (종일) | {summary}")

    except HttpError as error:
        print(f'오류가 발생했습니다: {error}')

if __name__ == '__main__':
    get_upcoming_events()
