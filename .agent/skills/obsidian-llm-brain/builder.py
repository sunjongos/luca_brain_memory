import os
import sys
import json
import re
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path
import subprocess

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    pass

# 환경/경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

# 루카 Memory-4 DB 연동
try:
    from memory_layer.core import store_memory
except ImportError:
    store_memory = None


# 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
VAULT_DIR = BASE_DIR / "Luca_Memory_Vault"
RAW_DIR = VAULT_DIR / "Raw"
WIKI_DIR = VAULT_DIR / "Wiki"

RAW_DIR.mkdir(parents=True, exist_ok=True)
WIKI_DIR.mkdir(parents=True, exist_ok=True)

HOTCACHE_FILE = VAULT_DIR / "HotCache.md"
TTL_FILE = BASE_DIR / ".agent" / "skills" / "ontology_ndb" / "ndb_knowledge.ttl"

def open_obsidian():
    """URL encode the vault path and open Obsidian."""
    vault_path_str = str(VAULT_DIR)
    encoded_path = urllib.parse.quote(vault_path_str)
    uri = f"obsidian://open?path={encoded_path}"
    
    print("[OBSIDIAN] 옵시디언 볼트를 엽니다...")
    if os.name == 'nt':
        os.startfile(uri)
    else:
        subprocess.run(["open", uri])

# 환경 변수 로드
env_path = BASE_DIR / '.env'
if env_path.exists():
    for _enc in ("utf-8", "cp949", "euc-kr"):
        try:
            for _line in env_path.read_text(encoding=_enc, errors="ignore").splitlines():
                _line = _line.replace('\x00', '').strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('\"').strip("'"))
            break
        except Exception:
            continue

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def call_gemini(system_prompt, user_text):
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not found in .env")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"parts": [{"text": user_text}]}
        ]
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        print(f"Gemini API Error: {e.read().decode('utf-8')}")
        sys.exit(1)

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id).find_transcript(['ko', 'en']).fetch()
        return " ".join([t.text for t in transcript_list])
    except Exception as e:
        print(f"Transcript Error: {e}")
        return None

def fetch_web_content(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        text = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Web Fetch Error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("[OBSIDIAN LLM BRAIN]\n사용법: obsidian [youtube/web-url_또는_텍스트]\n        obsidian graph (지금 옵시디언 뷰를 바로 열기)\n        obsidian lint (자율 리서치 린터 실행)")
        return
        
    query = sys.argv[1]
    
    if query.lower() == "graph":
        open_obsidian()
        return
    elif query.lower() == "lint":
        print("[LINT] 린터 백그라운드 에이전트를 실행합니다...")
        linter_script = Path(__file__).parent / "linter.py"
        os.system(f'python "{linter_script}"')
        open_obsidian()
        return

    # 1. 텍스트 추출
    print(f"🔍 [1단계] 데이터 추출: {query}")
    
    text = ""
    title = f"Data_{datetime.now().strftime('%Y%md_%H%M%S')}"
    
    if query.startswith("http"):
        video_id = extract_video_id(query)
        if video_id and "youtube" in query or "youtu.be" in query:
            text = get_youtube_transcript(video_id)
            title = f"YT_{video_id}"
        else:
            text = fetch_web_content(query)
            title = f"Web_{datetime.now().strftime('%H%M%S')}"
            
        if not text:
            print("데이터 추출에 실패했습니다.")
            sys.exit(1)
    else:
        text = query
        title = "Thought_" + datetime.now().strftime("%Y%md_%H%M%S")
        
    print("🧠 [2단계] LLM 지식 구조 전개 중...")
    
    system_prompt = """
    당신은 Andrej Karpathy식 "LLM Wiki"를 뛰어넘는 자체 진화형 세컨드 브레인의 수석 큐레이터입니다.
    주어진 입력 텍스트를 바탕으로, 마크다운 위키 파일들과 TTL 지식그래프 요소로 변환해야 합니다.

    출력 포맷 파싱 규칙:
    빈드시 다음 3개의 섹션 구분자를 사용해 출력하세요.

    ---RAW_SUMMARY_START---
    (입력 전체에 대한 500자 내외 요약. 문서 중간 핵심 키워드는 대괄호 2개로 묶어 백링크 생성. ex: [[RAG]], [[AI Agent]])
    ---RAW_SUMMARY_END---

    ---WIKI_PAGES_START---
    (추출된 백링크 개념들에 대해, 개별 마크다운 위키 내용을 작성합니다)
    ###WIKI_TITLE### 개념명1
    (정의와 설명. 줄바꿈 및 다른 개념 연결 권장)
    ###WIKI_TITLE### 개념명2
    (정의와 설명)
    ---WIKI_PAGES_END---

    ---TTL_ONTOLOGY_START---
    (추가된 개념들의 관계를 Turtle (TTL) 포맷으로 정의하세요. prefix는 dreye: <http://pihealthcare.com/ontology/dreye#> 를 사용합니다.)
    ex)
    dreye:AI_Agent a owl:Class ;
        rdfs:label "AI Agent" .
    ---TTL_ONTOLOGY_END---
    """
    
    result = call_gemini(system_prompt, text[:30000]) # 텍스트 길이 제한
    
    # 파싱
    raw_match = re.search(r"---RAW_SUMMARY_START---\n(.*?)\n---RAW_SUMMARY_END---", result, re.DOTALL)
    wiki_match = re.search(r"---WIKI_PAGES_START---\n(.*?)\n---WIKI_PAGES_END---", result, re.DOTALL)
    ttl_match = re.search(r"---TTL_ONTOLOGY_START---\n(.*?)\n---TTL_ONTOLOGY_END---", result, re.DOTALL)
    
    if raw_match:
        raw_text = raw_match.group(1).strip()
        raw_filepath = RAW_DIR / f"{title}.md"
        with open(raw_filepath, "w", encoding="utf-8") as f:
            f.write(raw_text)
        print(f"✅ Raw Data 저장 완료: {raw_filepath}")
        
        # HotCache 업데이트
        with open(HOTCACHE_FILE, "w", encoding="utf-8") as f:
            f.write(f"# Hot Cache (Working Memory)\n\n*최종 업데이트: {datetime.now().isoformat()}*\n\n## 최근 입력 요약\n{raw_text}\n")
        print("🔥 HotCache.md 버퍼 갱신 완료!")
        
    if wiki_match:
        wiki_text = wiki_match.group(1).strip()
        pages = re.split(r"###WIKI_TITLE###\s*", wiki_text)
        for page in pages:
            page = page.strip()
            if not page: continue
            lines = page.split("\n", 1)
            if len(lines) == 2:
                w_title, w_content = lines[0].strip(), lines[1].strip()
                safe_title = "".join(c for c in w_title if c not in r'\/:*?"<>|')
                w_filepath = WIKI_DIR / f"{safe_title}.md"
                mode = "a" if w_filepath.exists() else "w"
                with open(w_filepath, mode, encoding="utf-8") as f:
                    if mode == "a": f.write("\n\n---\n\n")
                    f.write(w_content)
                print(f"✅ Wiki 연동 노드 생성/추가: {w_filepath}")

    if ttl_match:
        ttl_text = ttl_match.group(1).strip()
        if ttl_text and TTL_FILE.parent.exists():
            with open(TTL_FILE, "a", encoding="utf-8") as f:
                f.write("\n" + ttl_text + "\n")
            print("🗄️ Ontology TTL 지식 주입 완료!")

    # Memory-4 DB 동기화 (Agent에게 기억 주입)
    if store_memory and raw_match and wiki_match:
        try:
            # 추출된 위키 타이틀을 엔티티로 사용
            ext_entities = []
            for p in pages:
                p = p.strip()
                if p:
                    ext_entities.append(p.split("\n", 1)[0].strip())
            
            summary_first_line = raw_match.group(1).strip().split('\n')[0][:100]
            store_memory(
                raw_text=text[:5000], 
                summary=summary_first_line, 
                entities=ext_entities, 
                topics=["obsidian_llm_brain", "second_brain"], 
                importance=0.8, 
                source=f"obsidian_{title}"
            )
            print("💾 Luca Memory-4 DB 동기화 완료!")
        except Exception as e:
            print(f"Luca Memory-4 연동 실패: {e}")

    print("🎉 처리 완료! 옵시디언 그래프에서 새로운 지식을 확인하세요.")
    open_obsidian()

if __name__ == "__main__":
    main()
