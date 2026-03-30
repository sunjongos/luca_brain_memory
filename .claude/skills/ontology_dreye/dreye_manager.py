import os
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

class DoctorEyeOntologyManager:
    """
    파이헬스케어 닥터아이(Doctor Eye) 온톨로지 매니저
    바이오마커(안저카메라 이미지 지표)와 타겟 질환 사이의 의학적, 기획적 연결 관계를 추론합니다.
    """
    def __init__(self, ttl_path=None):
        self.g = Graph()
        self.EX = Namespace("http://example.org/dreye/")
        self.g.bind("ex", self.EX)
        if not ttl_path:
            ttl_path = os.path.join(os.path.dirname(__file__), "dreye_knowledge.ttl")
            
        if os.path.exists(ttl_path):
            self.g.parse(ttl_path, format="turtle")
            print(f"✅ Doctor Eye 온톨로지 로드 완료. (총 {len(self.g)} 트리플)")

    def get_related_diseases_by_biomarker(self, biomarker_keyword):
        """특정 바이오마커 키워드를 통해 진단 가능한 타겟 질환을 쿼리합니다."""
        query = f"""
            PREFIX ex: <http://example.org/dreye/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?biomarkerLabel ?diseaseLabel
            WHERE {{
                ?biomarker a ex:Biomarker ;
                           rdfs:label ?biomarkerLabel ;
                           ex:indicatesRiskFor ?disease .
                ?disease rdfs:label ?diseaseLabel .
                FILTER(CONTAINS(?biomarkerLabel, "{biomarker_keyword}"))
            }}
        """
        results = self.g.query(query)
        links = []
        for row in results:
            links.append({"Biomarker": str(row.biomarkerLabel), "Disease": str(row.diseaseLabel)})
        return links

    def run_deep_track_pipeline(self, biomarker_keyword):
        """
        [Deep-Track 실행]
        의료 기기 인허가(FDA/KFDA) 및 절대적 정확도를 위해 
        8단계 파이프라인(진단 프로세스 자동화)을 엄격히 밟는 시뮬레이션입니다.
        """
        print(f"\n🔬 [Deep-Track 8단계 파이프라인 가동: 타겟 '{biomarker_keyword}']")
        print(" 1️⃣ 파싱(Parsing): 안저카메라 원본 이미지 및 소견서 해독 중...")
        print(" 2️⃣ 청킹(Chunking): 망막 혈관 구역별 데이터 분할 중...")
        print(" 3️⃣ 임베딩(Vector): 병변 데이터 차원 변환 및 ChromaDB 대조 중...")
        print(" 4️⃣ 그래프 구조화(Neo4j): 추출된 지표를 온톨로지 노드에 매핑...")
        print(" 5️⃣ 메타온톨로지 규정: KFDA 진단 가이드라인 룰셋 적용 중...")
        print(" 6️⃣ ReBAC 통제: 담당 주치의(이순태 교수) 열람 권한 확인 스캔...")
        print(" 7️⃣ 오케스트레이션: LangGraph 추론 사이클 시작...")
        
        links = self.get_related_diseases_by_biomarker(biomarker_keyword)
        if not links:
            return " ❌ 8️⃣ 에이전트 Action: 유의미한 질환 연관성이 검증되지 않았습니다. (진단 보류)"
            
        print(" 8️⃣ 에이전트 Action: 투명성(XAI) 기반 최종 진단 리포트 생성 완료.")
        report = "      [최종 추론 결과]\n"
        for link in links:
            report += f"      - 식별된 바이오마커 [{link['Biomarker']}]는 [{link['Disease']}]의 명확한 인디케이터로 작용함.\n"
        return report

if __name__ == "__main__":
    manager = DoctorEyeOntologyManager()
    
    biomarker = "혈관"
    print(f"\n[기본 바이오마커 쿼리 테스트: '{biomarker}']")
    links = manager.get_related_diseases_by_biomarker(biomarker)
    for link in links:
        print(f" -> 발견 지표: [{link['Biomarker']}] ===> 관련(위험) 질환: {link['Disease']}")
        
    # Deep-Track 테스트
    print(manager.run_deep_track_pipeline(biomarker))
