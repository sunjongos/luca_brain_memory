import os
import sys
import json
import requests
from pathlib import Path

# Setup paths and environment
BASE_DIR = Path(__file__).parent.parent.parent.parent
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        _line = _line.replace('\x00', '').strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))

def publish_to_wordpress(title, content):
    """
    Publish content to WordPress via REST API.
    Required .env: WP_URL, WP_USER, WP_APP_PASSWORD
    """
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_pass]):
        return "❌ WordPress API 정보가 설정되지 않았습니다 (.env 확인 필요)."

    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    import base64
    credentials = f"{wp_user}:{wp_pass}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'title': title,
        'content': content,
        'status': 'publish' # 🔓 바로 발행
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        if response.status_code == 201:
            post_link = response.json().get('link')
            return f"✅ WordPress 발행 성공! 링크: {post_link}"
        else:
            return f"❌ WordPress 발행 실패 (Code {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ WordPress 발행 통신 에러: {e}"

def mock_social_post(platform, content):
    """Mock social media posting for LinkedIn/Twitter."""
    print(f"DEBUG: Posting to {platform}...")
    # Real implementations would use 'tweepy' or LinkedIn API
    return f"✅ {platform} 에 공유 완료되었습니다 (시뮬레이션)."

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publisher.py <platform> <content> [title]")
        sys.exit(1)
        
    platform = sys.argv[1].lower()
    content = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "Luca Super Agent Report"
    
    if platform == "wordpress":
        print(publish_to_wordpress(title, content))
    else:
        print(mock_social_post(platform, content))
