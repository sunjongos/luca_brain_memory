import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.agent', 'skills', 'perplexity'))

try:
    from perplexity_search import search_perplexity
    result = search_perplexity(
        """유튜브 https://youtu.be/Y5pzLHmMobc (제목: 팔란티어 고담, 파운드리, 온톨로지 총정리 등) 영상의 핵심 내용을 요약해줘. 
        1. 이 영상에서 설명하는 '온톨로지(Ontology)' 개념이 팔란티어(Palantir) 비즈니스 모델(고담/파운드리 플랫폼)과 어떤 연관이 있는지 핵심만 설명해줘.
        2. 이 팔란티어식 온톨로지 접근법을 우리가 구축 중인 남양주백병원 경영 관리(ontology_ndb)와 파이헬스케어 닥터아이 진단 보조 플랫폼(ontology_dreye)에 적용하려면 어떻게 설계하고 활용해야 할지 구체적인 아이디어를 '의료계의 팔란티어' 관점에서 제시해줘.""",
        model="sonar-pro"
    )
    with open("tmp_perplexity.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Done")
except Exception as e:
    print(f"Error: {e}")
