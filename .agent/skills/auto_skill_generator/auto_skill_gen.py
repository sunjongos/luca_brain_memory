import os
import json
import logging
from pathlib import Path

# luca_evolution에서 환경변수가 이미 로드되었을 수 있으므로 필요한 부분만 임포트
from google import genai
from google.genai import types

logger = logging.getLogger("AutoSkillGen")

SKILLS_DIR = Path(__file__).parent.parent
api_key = os.getenv("GOOGLE_API_KEY", "")
client = genai.Client(api_key=api_key) if api_key else None

def generate_skill(request_description: str) -> dict:
    """
    LLM(Gemini)에 요청하여 새로운 스킬의 이름, 파이썬 코드, SKILL.md 컨텐츠를 JSON으로 반환받아,
    자동으로 폴더를 생성하고 스킬을 장착합니다.
    (Self-Proliferating)
    """
    if not client:
        logger.error("AutoSkillGen: No Gemini config")
        return {"success": False, "error": "No Gemini API key."}
        
    prompt = f"""
당신은 자가 증식(Self-Proliferating)이 가능한 최상위 AGI 코어입니다.
아래의 트렌드/요구사항을 달성하기 위해, 새로운 파이썬 모듈(스킬)을 자체 생성하려고 합니다.

[작업 요구사항]
{request_description}

다음 JSON 구조에 맞춰 한 치의 오차 없이 답변해 주십시오. (마크다운 백틱 없이 순수 JSON만 출력)
{{
    "skill_name": "스킬을 대표하는 짧은 영문 폴더명 (예: web_scraper_v2)",
    "python_filename": "실행할 파이썬 파일명 (예: scraper.py)",
    "python_code": "해당 기능을 수행하는 완벽한 파이썬 스크립트 내용. 함수, 클래스, 에러처리, argparse 등이 모두 포함될 것.",
    "skill_md": "---\\nname: skill_name\\ndescription: 어쩌구저쩌구\\n---\\n\\n# Skill Name\\n사용법 및 마크다운..."
}}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        
        skill_name = data.get("skill_name")
        python_filename = data.get("python_filename", "main.py")
        python_code = data.get("python_code", "")
        skill_md = data.get("skill_md", "")
        
        if not skill_name or not python_code:
            return {"success": False, "error": "LLM returned incomplete skill definition."}
            
        target_dir = SKILLS_DIR / skill_name
        if target_dir.exists():
            return {"success": False, "error": f"Skill {skill_name} already exists."}
            
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Write Python Script
        with open(target_dir / python_filename, "w", encoding="utf-8") as f:
            f.write(python_code)
            
        # Write SKILL.md
        with open(target_dir / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(skill_md)
            
        logger.info(f"✨ AutoSkillGen: 신규 스킬 [{skill_name}] 자가 증식 성공!")
        return {"success": True, "skill_name": skill_name, "path": str(target_dir)}
        
    except Exception as e:
        logger.error(f"AutoSkillGen Error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = generate_skill(sys.argv[1])
        print(res)
