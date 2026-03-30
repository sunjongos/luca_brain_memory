import urllib.request
import urllib.parse
import json
import argparse
from datetime import datetime, timedelta
import ssl
import sys
import io

# utf-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

import os
from pathlib import Path

# 환경 변수 로드 (수동 파싱 로직)
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
            break
        except (UnicodeDecodeError, ValueError):
            continue

# API Credentials
NAVER_SEARCH_CLIENT_ID = os.getenv("NAVER_SEARCH_CLIENT_ID", "KfgaSIkWNVGJ_YSZcffs")
NAVER_SEARCH_CLIENT_SECRET = os.getenv("NAVER_SEARCH_CLIENT_SECRET", "CSYMZPGOdP")

NAVER_DATALAB_CLIENT_ID = os.getenv("NAVER_DATALAB_CLIENT_ID", "q8Y3EuiGXRYGjemuDFYv")
NAVER_DATALAB_CLIENT_SECRET = os.getenv("NAVER_DATALAB_CLIENT_SECRET", "HLddlF0Qc1")

NAVER_CAFE_CLIENT_ID = os.getenv("NAVER_CAFE_CLIENT_ID", "")
NAVER_CAFE_CLIENT_SECRET = os.getenv("NAVER_CAFE_CLIENT_SECRET", "")

def search_naver(query, target="blog", display=10):
    """
    네이버 검색 API를 호출합니다 (blog, news, webkr, kin, cafearticle 중 선택)
    """
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/{target}?query={encText}&display={display}"
    
    request = urllib.request.Request(url)
    
    if target == "cafearticle":
        request.add_header("X-Naver-Client-Id", NAVER_CAFE_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_CAFE_CLIENT_SECRET)
    else:
        request.add_header("X-Naver-Client-Id", NAVER_SEARCH_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_SEARCH_CLIENT_SECRET)
    
    try:
        # SSL 인증서 검증 무시 설정 (필요시)
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(request, context=context)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            print(f"Error Code: {rescode}")
            return None
    except Exception as e:
        print(f"API Request Failed: {e}")
        return None

def get_search_trend(keywords, start_date=None, end_date=None):
    """
    네이버 데이터랩 API를 호출하여 검색어 트렌드를 가져옵니다.
    keywords는 단일 문자열이거나 콤마 단위로 분리된 문자열입니다. "병원,남양주 백병원"
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # Default to 30 days ago
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keyword_list]
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": keyword_groups
    }
    
    body_json = json.dumps(body)
    
    url = "https://openapi.naver.com/v1/datalab/search"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_DATALAB_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_DATALAB_CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")
    
    try:
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(request, data=body_json.encode("utf-8"), context=context)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            print(f"Error Code: {rescode}")
            return None
    except Exception as e:
        print(f"API Request Failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naver API Tool for Luca")
    parser.add_argument("action", choices=["search", "trend"], help="Action to perform: 'search' or 'trend'")
    parser.add_argument("--query", type=str, help="Search query (for search action)")
    parser.add_argument("--target", type=str, default="blog", choices=["blog", "news", "webkr", "kin", "cafearticle"], help="Search target (for search action)")
    parser.add_argument("--keywords", type=str, help="Comma separated keywords (for trend action)")
    parser.add_argument("--display", type=int, default=10, help="Number of results to display")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD) for trend")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD) for trend")
    
    args = parser.parse_args()
    
    if args.action == "search":
        if not args.query:
            print("Error: --query is required for search action")
            sys.exit(1)
            
        print(f"=== Searching Naver {args.target} for '{args.query}' ===")
        results = search_naver(args.query, args.target, args.display)
        
        if results and "items" in results:
            for i, item in enumerate(results["items"], 1):
                title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                link = item.get("link", "")
                desc = item.get("description", "").replace("<b>", "").replace("</b>", "")
                
                print(f"[{i}] {title}\n    Link: {link}")
                if "cafename" in item:
                    print(f"    Cafe: {item.get('cafename', '')}")
                print(f"    Desc: {desc}\n")
        else:
            print("No results found or error occurred.")
            
    elif args.action == "trend":
        if not args.keywords:
            print("Error: --keywords is required for trend action")
            sys.exit(1)
            
        print(f"=== Getting Datalab Trend for '{args.keywords}' ===")
        results = get_search_trend(args.keywords, args.start, args.end)
        
        if results and "results" in results:
            for group in results["results"]:
                print(f"\nKeyword Group: {group['title']}")
                data_points = group.get("data", [])
                total_ratio = sum(item["ratio"] for item in data_points)
                avg_ratio = total_ratio / len(data_points) if data_points else 0
                
                print(f"  - Total Data Points: {len(data_points)}")
                print(f"  - Average Search Ratio (Relative): {avg_ratio:.2f}")
                
                # Show top 3 peak days
                peaks = sorted(data_points, key=lambda x: x["ratio"], reverse=True)[:3]
                if peaks:
                    print("  - Highest Search Volume Days:")
                    for peak in peaks:
                        print(f"      * {peak['period']}: {peak['ratio']:.2f}")
        else:
             print("No results found or error occurred.")
