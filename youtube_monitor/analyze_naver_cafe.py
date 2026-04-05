import urllib.request
import urllib.parse
import json
import argparse
import sys
import re

# Naver API credentials provided by the CEO
CLIENT_ID = "812h13veud7hGMluk3YS"
CLIENT_SECRET = "n3BZ0LLx6i"

# Basic list of malicious keywords for filtering
MALICIOUS_KEYWORDS = [
    "최악", "쓰레기", "병신", "돌팔이", "돈만", "불친절", "가지마", "망해라", 
    "사기", "바가지", "오진", "의료사고", "불만", "짜증", "비추"
]

def clean_html(raw_html):
    """Remove HTML tags (like <b>, </b>) from the text."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def search_naver_cafe(client_id, client_secret, query, display=10):
    """
    Calls the Naver Search API for Cafe Articles.
    """
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/cafearticle.json?query={encText}&display={display}&sort=sim"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            print(f"Error Code from Naver API: {rescode}")
            return None
    except Exception as e:
        print(f"Failed to execute Naver API call: {e}")
        return None

def analyze_cafe_articles(results):
    """Scan cafe articles for malicious keywords in title and description."""
    malicious_articles = []
    
    if not results or "items" not in results:
        return malicious_articles
        
    for item in results["items"]:
        title = clean_html(item.get("title", ""))
        description = clean_html(item.get("description", ""))
        link = item.get("link", "")
        cafe_name = item.get("cafename", "")
        
        full_text = f"{title} {description}"
        
        # Simple keyword-based analysis
        found_keywords = [kw for kw in MALICIOUS_KEYWORDS if kw in full_text]
        
        if found_keywords:
            malicious_articles.append({
                "title": title,
                "cafe_name": cafe_name,
                "description": description,
                "link": link,
                "keywords_flagged": found_keywords
            })
            
    return malicious_articles

def generate_report(malicious_articles, query):
    """Format and print the analysis report."""
    print("\n" + "="*50)
    print(f"📊 Naver Cafe Analysis Report: '{query}'")
    print("="*50)
    
    if not malicious_articles:
        print("✅ No malicious mentions detected in the analyzed Naver Cafe articles.")
        print("="*50 + "\n")
        return
        
    print(f"⚠️ Warning: Found {len(malicious_articles)} potentially malicious mentions!\n")
    
    for i, item in enumerate(malicious_articles, 1):
        print(f"[{i}] Cafe Name: {item['cafe_name']}")
        print(f"    Title: {item['title']}")
        print(f"    Flagged Keywords: {', '.join(item['keywords_flagged'])}")
        print(f"    Snippet: \"{item['description'][:100]}...\"") # trim snippet
        print(f"    Link: {item['link']}")
        print("-" * 50)
        
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Analyze Naver Cafe articles for a specific query.")
    parser.add_argument("--query", type=str, default="남양주 백병원", help="The search query (e.g., hospital name)")
    parser.add_argument("--display", type=int, default=10, help="Number of latest articles to analyze")
    args = parser.parse_args()
    
    print(f"🚀 Initializing Naver Cafe Monitor for query: '{args.query}'...")
    
    print(f"📥 Fetching top {args.display} cafe articles...")
    results = search_naver_cafe(CLIENT_ID, CLIENT_SECRET, args.query, display=args.display)
    
    if results:
        print("🔍 Analyzing titles and descriptions...")
        malicious_articles = analyze_cafe_articles(results)
        generate_report(malicious_articles, args.query)
    else:
        print("❌ Failed to fetch results. Check API keys or network connection.")

if __name__ == "__main__":
    main()
