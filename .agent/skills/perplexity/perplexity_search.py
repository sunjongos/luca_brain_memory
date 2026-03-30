"""
Perplexity AI 검색 스크립트
사용법: python perplexity_search.py "검색 쿼리" [--model sonar-pro] [--json]
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트 기준)
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"

SUPPORTED_MODELS = {
    "sonar": "sonar",                     # 빠른 일반 검색
    "sonar-pro": "sonar-pro",             # 심층 분석
    "sonar-reasoning": "sonar-reasoning", # 복잡한 추론
}


def search_perplexity(query: str, model: str = "sonar", system_prompt: str = None) -> dict:
    """
    Perplexity API로 검색을 수행합니다.

    Args:
        query: 검색 쿼리
        model: 사용할 모델 (sonar / sonar-pro / sonar-reasoning)
        system_prompt: 시스템 프롬프트 (기본값: 한국어 응답 요청)

    Returns:
        검색 결과 딕셔너리 {answer, citations, model}
    """
    if not PERPLEXITY_API_KEY:
        raise EnvironmentError(
            "PERPLEXITY_API_KEY가 설정되지 않았습니다.\n"
            "프로젝트 루트의 .env 파일에 PERPLEXITY_API_KEY=pplx-xxxx 를 추가하세요.\n"
            "API 키 발급: https://www.perplexity.ai/settings/api"
        )

    model_id = SUPPORTED_MODELS.get(model, SUPPORTED_MODELS["sonar"])

    if system_prompt is None:
        system_prompt = (
            "당신은 정확하고 신뢰할 수 있는 정보를 제공하는 AI 리서치 어시스턴트입니다. "
            "한국어로 답변하며, 핵심 정보를 명확하게 정리하고 출처를 명시해주세요."
        )

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "return_citations": True,
        "return_related_questions": True,
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])
    related = data.get("related_questions", [])

    return {
        "query": query,
        "model": model,
        "answer": answer,
        "citations": citations,
        "related_questions": related,
    }


def format_result(result: dict) -> str:
    """검색 결과를 Luca 브리핑 형식으로 포맷합니다."""
    lines = []
    lines.append(f"🔍 [{result['query']}] — Perplexity 딥서치 결과 (모델: {result['model']})")
    lines.append("")
    lines.append("📌 핵심 내용:")
    lines.append(result["answer"])

    if result["citations"]:
        lines.append("")
        lines.append("🔗 주요 출처:")
        for i, url in enumerate(result["citations"][:5], 1):
            lines.append(f"  {i}. {url}")

    if result["related_questions"]:
        lines.append("")
        lines.append("💡 관련 추가 질문:")
        for q in result["related_questions"][:3]:
            lines.append(f"  • {q}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Perplexity AI 검색 도구")
    parser.add_argument("query", help="검색할 내용")
    parser.add_argument(
        "--model",
        choices=list(SUPPORTED_MODELS.keys()),
        default="sonar",
        help="사용할 모델 (기본값: sonar)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="결과를 JSON 형식으로 출력"
    )
    parser.add_argument(
        "--system",
        default=None,
        help="커스텀 시스템 프롬프트"
    )

    args = parser.parse_args()

    try:
        result = search_perplexity(
            query=args.query,
            model=args.model,
            system_prompt=args.system,
        )

        if args.output_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))

    except EnvironmentError as e:
        print(f"❌ 설정 오류: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"❌ API 오류 ({e.response.status_code}): {e.response.text}", file=sys.stderr)
        try:
            detail = e.response.json()
            print(f"   상세: {json.dumps(detail, ensure_ascii=False, indent=2)}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
