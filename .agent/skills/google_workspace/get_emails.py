"""
Gmail 자동화 스크립트 — 최근 메일 조회 및 요약
사용법:
  python get_emails.py                  # 최근 10개 중요 메일
  python get_emails.py --count 20       # 최근 20개
  python get_emails.py --label INBOX    # 받은 편지함
  python get_emails.py --unread         # 읽지 않은 메일만
"""

import os
import sys
import json
import argparse
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_credentials
from googleapiclient.discovery import build


def get_gmail_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)


def decode_body(payload):
    """메일 본문 디코딩"""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload.get('body', {}).get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body[:500]  # 500자로 제한


def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ''


def fetch_emails(count=10, label='INBOX', unread_only=False):
    service = get_gmail_service()

    query = 'is:unread' if unread_only else ''
    result = service.users().messages().list(
        userId='me',
        labelIds=[label],
        q=query,
        maxResults=count
    ).execute()

    messages = result.get('messages', [])
    if not messages:
        print("📭 조회된 메일이 없습니다.")
        return

    print(f"📬 Gmail 최근 메일 ({len(messages)}개)\n{'='*60}")

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId='me',
            id=msg_ref['id'],
            format='full'
        ).execute()

        headers = msg['payload']['headers']
        subject = get_header(headers, 'Subject') or '(제목 없음)'
        sender = get_header(headers, 'From')
        date_str = get_header(headers, 'Date')
        snippet = msg.get('snippet', '')

        labels = msg.get('labelIds', [])
        is_unread = 'UNREAD' in labels
        status = '🔴 안읽음' if is_unread else '✅ 읽음'

        print(f"\n{status} [{date_str[:16]}]")
        print(f"   발신: {sender[:50]}")
        print(f"   제목: {subject[:70]}")
        print(f"   요약: {snippet[:100]}...")
        print(f"   ID:   {msg_ref['id']}")

    print(f"\n{'='*60}")
    print(f"✅ 총 {len(messages)}개 메일 조회 완료")


def main():
    parser = argparse.ArgumentParser(description="Gmail 메일 조회 도구")
    parser.add_argument("--count", type=int, default=10, help="조회할 메일 수 (기본값: 10)")
    parser.add_argument("--label", default="INBOX", help="레이블 (기본값: INBOX)")
    parser.add_argument("--unread", action="store_true", help="읽지 않은 메일만 조회")
    parser.add_argument("--json", action="store_true", dest="output_json", help="JSON 출력")

    args = parser.parse_args()
    fetch_emails(count=args.count, label=args.label, unread_only=args.unread)


if __name__ == "__main__":
    main()
