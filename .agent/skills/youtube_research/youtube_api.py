import os
import sys
import argparse
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 환경 변수 로드 (수동 파싱 로직 추가)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / '.env'

if env_path.exists():
    for _enc in ("utf-8", "cp949", "euc-kr"):
        try:
            for _line in env_path.read_text(encoding=_enc, errors="ignore").splitlines():
                _line = _line.replace('\x00', '').strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))
            break  # 성공한 인코딩
        except (UnicodeDecodeError, ValueError):
            continue

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("Error: YOUTUBE_API_KEY is not set in the .env file.", file=sys.stderr)
    sys.exit(1)

def get_youtube_client():
    """YouTube API 클라이언트 생성"""
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def search_videos(query, max_results=5):
    """지정된 키워드로 YouTube 동영상을 검색합니다."""
    youtube = get_youtube_client()
    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        
        results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            results.append({
                "title": snippet["title"],
                "channel_title": snippet["channelTitle"],
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published_at": snippet["publishedAt"]
            })
            
        return json.dumps(results, ensure_ascii=False, indent=2)
            
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def get_video_details(video_id):
    """지정된 YouTube 동영상의 상세 정보(통계 등)를 가져옵니다."""
    youtube = get_youtube_client()
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        response = request.execute()
        
        items = response.get("items", [])
        if not items:
            return json.dumps({"error": "Video not found"})
            
        item = items[0]
        snippet = item["snippet"]
        statistics = item["statistics"]
        
        details = {
            "title": snippet["title"],
            "channel_title": snippet["channelTitle"],
            "description": snippet["description"],
            "published_at": snippet["publishedAt"],
            "view_count": statistics.get("viewCount", "0"),
            "like_count": statistics.get("likeCount", "0"),
            "comment_count": statistics.get("commentCount", "0")
        }
        
        return json.dumps(details, ensure_ascii=False, indent=2)
        
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}", file=sys.stderr)
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Research API Skill")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # search 명령어
    search_parser = subparsers.add_parser("search", help="Search for YouTube videos")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--max-results", type=int, default=5, help="Maximum number of results to return")
    
    # details 명령어
    details_parser = subparsers.add_parser("details", help="Get details for a specific video")
    details_parser.add_argument("video_id", type=str, help="YouTube Video ID")
    
    args = parser.parse_args()
    
    if args.command == "search":
        print(search_videos(args.query, args.max_results))
    elif args.command == "details":
        print(get_video_details(args.video_id))
    else:
        parser.print_help()
