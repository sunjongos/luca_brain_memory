"""
Google Docs 자동 문서 생성 스크립트
사용법:
  python create_doc.py --title "문서 제목" --content "내용"
  python create_doc.py --title "리서치 리포트" --file result.txt
  python create_doc.py --title "브리핑" --content "내용" --folder-id "드라이브폴더ID"
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from auth import authenticate_google_workspace
from googleapiclient.discovery import build
from datetime import datetime


def get_services():
    creds = authenticate_google_workspace()
    docs = build('docs', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)
    return docs, drive


def create_doc(title: str, content: str, folder_id: str = None) -> str:
    """Google Docs 문서를 생성하고 URL을 반환합니다."""
    docs_service, drive_service = get_services()

    # 문서 생성
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc['documentId']

    # 내용 삽입
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_content = f"[Luca 자동 생성 | {timestamp}]\n\n{content}"

    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': full_content
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    # 폴더 이동 (선택)
    if folder_id:
        file = drive_service.files().get(
            fileId=doc_id, fields='parents'
        ).execute()
        prev_parents = ','.join(file.get('parents', []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=prev_parents,
            fields='id, parents'
        ).execute()

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, doc_url


def main():
    parser = argparse.ArgumentParser(description="Google Docs 자동 생성 도구")
    parser.add_argument("--title", required=True, help="문서 제목")
    parser.add_argument("--content", default=None, help="문서 내용 (직접 입력)")
    parser.add_argument("--file", default=None, help="내용을 읽어올 텍스트 파일 경로")
    parser.add_argument("--folder-id", default=None, help="저장할 Google Drive 폴더 ID")

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        print("❌ --content 또는 --file 중 하나는 필수입니다.")
        sys.exit(1)

    print(f"📝 Google Docs 생성 중: '{args.title}'...")
    doc_id, doc_url = create_doc(
        title=args.title,
        content=content,
        folder_id=args.folder_id
    )

    print(f"✅ 문서 생성 완료!")
    print(f"   제목: {args.title}")
    print(f"   URL:  {doc_url}")
    print(f"   ID:   {doc_id}")


if __name__ == "__main__":
    main()
