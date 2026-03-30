"""
웹 모니터링 스크립트 — 키워드 기반 뉴스 및 사이트 변경 감지
사용법:
  python web_monitor.py --keywords "AI 에이전트,GPT,Claude" --save
  python web_monitor.py --url "https://example.com" --check-change
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path

# 모니터링 결과 저장 경로
MONITOR_DIR = os.path.join(os.path.dirname(__file__), 'monitor_data')
os.makedirs(MONITOR_DIR, exist_ok=True)


def search_news(keywords: list, max_per_keyword: int = 3) -> list:
    """
    Perplexity를 활용한 키워드 뉴스 검색.
    perplexity_search.py 스크립트 연동.
    """
    results = []
    perplexity_script = os.path.join(
        os.path.dirname(__file__), '..', 'perplexity', 'perplexity_search.py'
    )

    for kw in keywords:
        query = f"최신 뉴스 {kw} 오늘 2026"
        print(f"🔍 검색 중: {kw}")
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, perplexity_script, query, '--model', 'sonar', '--json'],
                capture_output=True, text=True, timeout=30,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                results.append({
                    "keyword": kw,
                    "answer": data.get("answer", "")[:300],
                    "citations": data.get("citations", [])[:3],
                    "searched_at": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"  ⚠️ '{kw}' 검색 실패: {e}")

    return results


def check_page_change(url: str) -> dict:
    """웹 페이지 변경 여부를 감지합니다."""
    import urllib.request
    safe_name = hashlib.md5(url.encode()).hexdigest()[:12]
    cache_file = os.path.join(MONITOR_DIR, f"{safe_name}.json")

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}

    current_hash = hashlib.md5(content.encode()).hexdigest()
    now = datetime.now().isoformat()

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            prev = json.load(f)
        changed = prev.get("hash") != current_hash
        result = {
            "url": url,
            "changed": changed,
            "last_check": prev.get("checked_at"),
            "current_check": now,
            "status": "changed" if changed else "no_change"
        }
    else:
        result = {"url": url, "changed": False, "current_check": now, "status": "first_check"}

    with open(cache_file, 'w') as f:
        json.dump({"hash": current_hash, "checked_at": now, "url": url}, f, ensure_ascii=False)

    return result


def save_results(results: list, filename: str = None):
    if not filename:
        filename = f"monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    path = os.path.join(MONITOR_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 결과 저장: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description="웹 모니터링 도구")
    parser.add_argument("--keywords", help="모니터링 키워드 (콤마 구분)")
    parser.add_argument("--url", help="변경 감지할 URL")
    parser.add_argument("--save", action="store_true", help="결과 파일 저장")
    args = parser.parse_args()

    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
        print(f"🌐 키워드 뉴스 모니터링: {keywords}\n")
        results = search_news(keywords)
        for r in results:
            print(f"\n📰 [{r['keyword']}]")
            print(f"   {r['answer'][:200]}...")
            for url in r.get('citations', []):
                print(f"   🔗 {url}")
        if args.save:
            save_results(results)

    elif args.url:
        result = check_page_change(args.url)
        status_icon = "🔴" if result.get("changed") else "🟢"
        print(f"{status_icon} [{result['status']}] {args.url}")
        if result.get("changed"):
            print("   ⚠️ 페이지 변경 감지됨!")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
