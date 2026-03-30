import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.agent', 'skills', 'perplexity'))
import asyncio

async def main():
    try:
        from perplexity_search import call_perplexity
        result = await call_perplexity(
            """https://youtu.be/Y5pzLHmMobc 이 영상의 핵심 내용과, 
            이 영상에서 설명하는 온톨로지(Ontology) 개념이 팔란티어(Palantir)의 고담/파운드리 플랫폼과 어떤 연관이 있는지 분석해줘.
            그리고 의료계(병원 경영 및 심혈관/안저카메라 기반 진단 닥터아이)에 팔란티어식 온톨로지를 적용하려면 어떻게 해야 하는지 구체적인 적용 방안을 제시해줘."""
        )
        with open("tmp_perplexity.txt", "w", encoding="utf-8") as f:
            f.write(result['content'])
            f.write("\n\nSources:\n")
            for url in result['citations']:
                f.write(url + "\n")
        print("Done")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
