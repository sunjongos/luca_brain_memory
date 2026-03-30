"""
Google Sheets 자동화 스크립트 — 데이터 조회 및 업데이트
사용법:
  python get_sheets.py --id "스프레드시트ID" --sheet "시트명"
  python update_sheet.py --id "ID" --sheet "시트명" --row 2 --col 1 --value "값"
"""

import os
import sys
import argparse
import json

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_credentials
from googleapiclient.discovery import build


def get_sheets_service():
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)


def read_sheet(spreadsheet_id: str, sheet_name: str, range_str: str = None):
    """스프레드시트 데이터를 읽어옵니다."""
    service = get_sheets_service()
    range_notation = f"'{sheet_name}'!{range_str}" if range_str else sheet_name
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_notation
    ).execute()
    return result.get('values', [])


def write_sheet(spreadsheet_id: str, sheet_name: str, range_str: str, values: list):
    """스프레드시트에 데이터를 씁니다."""
    service = get_sheets_service()
    range_notation = f"'{sheet_name}'!{range_str}"
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_notation,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return result


def append_sheet(spreadsheet_id: str, sheet_name: str, values: list):
    """스프레드시트 마지막 행에 데이터를 추가합니다."""
    service = get_sheets_service()
    range_notation = sheet_name
    body = {'values': values}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_notation,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    return result


def main():
    parser = argparse.ArgumentParser(description="Google Sheets 자동화 도구")
    subparsers = parser.add_subparsers(dest="command")

    # read
    p_read = subparsers.add_parser("read", help="시트 데이터 읽기")
    p_read.add_argument("--id", required=True, help="스프레드시트 ID")
    p_read.add_argument("--sheet", default="Sheet1", help="시트 이름")
    p_read.add_argument("--range", default="A1:Z100", help="범위 (예: A1:D10)")

    # write
    p_write = subparsers.add_parser("write", help="시트 데이터 쓰기")
    p_write.add_argument("--id", required=True, help="스프레드시트 ID")
    p_write.add_argument("--sheet", default="Sheet1", help="시트 이름")
    p_write.add_argument("--range", required=True, help="쓰기 시작 범위 (예: A1)")
    p_write.add_argument("--values", required=True, help='JSON 배열 (예: [["이름","점수"],["A",90]])')

    # append
    p_append = subparsers.add_parser("append", help="시트 마지막 행에 추가")
    p_append.add_argument("--id", required=True, help="스프레드시트 ID")
    p_append.add_argument("--sheet", default="Sheet1", help="시트 이름")
    p_append.add_argument("--values", required=True, help='JSON 배열 (예: [["새 데이터","값"]])')

    args = parser.parse_args()

    if args.command == "read":
        data = read_sheet(args.id, args.sheet, args.range)
        print(f"📊 [{args.sheet}] 데이터 ({len(data)}행)")
        for i, row in enumerate(data, 1):
            print(f"  {i}: {' | '.join(str(c) for c in row)}")

    elif args.command == "write":
        values = json.loads(args.values)
        result = write_sheet(args.id, args.sheet, args.range, values)
        print(f"✅ 데이터 쓰기 완료: {result.get('updatedCells', 0)}개 셀 업데이트")

    elif args.command == "append":
        values = json.loads(args.values)
        result = append_sheet(args.id, args.sheet, values)
        print(f"✅ 행 추가 완료")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
