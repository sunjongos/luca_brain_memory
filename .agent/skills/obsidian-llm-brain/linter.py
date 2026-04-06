import os
import re
import sys
from pathlib import Path
from datetime import datetime

# sys.path 설정하여 perplexity 모듈 임포트
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR / ".agent" / "skills" / "perplexity"))

try:
    from perplexity_search import search_perplexity
except ImportError:
    print("perplexity_search.py 모듈을 찾을 수 없습니다.")
    search_perplexity = None

WIKI_DIR = BASE_DIR / "Luca_Memory_Vault" / "Wiki"

def find_dead_links():
    links_found = set()
    files_found = set()
    
    if not WIKI_DIR.exists(): 
        return set()
    
    for md_file in WIKI_DIR.glob("*.md"):
        files_found.add(md_file.stem)
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            # Extract [[Link]]
            matches = re.findall(r"\[\[(.*?)\]\]", content)
            for m in matches:
                links_found.add(m.strip())
        except Exception:
            continue
            
    dead_links = links_found - files_found
    # 필터: 너무 길거나 비정상적인 링크 제외
    dead_links = {l for l in dead_links if len(l) > 0 and len(l) < 35 and "|" not in l}
    return dead_links

def autonomous_research(concept):
    system_prompt = "당신은 AI/IT 개념을 옵시디언 위키 파일용 마크다운으로 깔끔하게 정리하는 리서처입니다. 제목 없이 정의, 핵심 원리, 최신 트렌드 위주로 500자 내외로 작성하세요. 본문 작성 중 다른 핵심 개념이 나오면 [[다른 개념]] 처럼 백링크 형식을 자연스럽게 포함하세요."
    query = f"옵시디언 위키 문서를 작성하기 위해 '{concept}' 라는 개념에 대해 상세히 조사해서 알려주세요."
    
    # 먼저 Perplexity 연동 시도
    if search_perplexity:
        try:
            res = search_perplexity(query, model="sonar-pro", system_prompt=system_prompt)
            text = res.get("answer", "")
            if res.get("citations"):
                text += "\n\n---\n### 🔗 참조 출처\n"
                for url in res["citations"]:
                    text += f"- {url}\n"
            if text:
                return text
        except Exception as e:
            print(f"Perplexity Search Failed ({e}), Gemini로 Fallback 합니다...")
    
    # 실패 시 Gemini로 텍스트 생성 폴백
    try:
        from builder import call_gemini
        fallback_query = query + "\n인터넷 검색 대신 당신의 지식을 활용해 상세히 작성해줘."
        text = call_gemini(system_prompt, fallback_query)
        text += "\n\n---\n### 🤖 Gemini Fallback 생성\n- 실시간 참조 대신 내부 지식으로 생성되었습니다."
        return text
    except Exception as e:
        print(f"Gemini Fallback Error for {concept}: {e}")
        return None

def main():
    print("[LINTER] 옵시디언 볼트 무결성 검사를 시작합니다...")
    dead_links = list(find_dead_links())
    print(f"발견된 Dead Links (빈껍데기 개념): {len(dead_links)}개")
    
    if not dead_links:
        print("🎉 모든 지식이 온전하게 연결되어 있습니다!")
        return

    # 비용/속도 최적화를 위해 1회 실행 시 최대 2개의 개념만 치유
    max_heal = 2
    to_heal = dead_links[:max_heal]
    
    print(f"이번 주기에 치유할 노드: {to_heal}")
    
    for concept in to_heal:
        print(f"🩺 자율 리서치 및 치유 중: [[{concept}]]")
        content = autonomous_research(concept)
        if content:
            safe_title = "".join(c for c in concept if c not in r'\/:*?"<>|')
            new_file_path = WIKI_DIR / f"{safe_title}.md"
            with open(new_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 노드 생성 및 치유 완료: {new_file_path}")
            
    print("✨ Linter 작업 완료!")

if __name__ == "__main__":
    main()
