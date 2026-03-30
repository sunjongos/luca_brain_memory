import os
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

class NDBOntologyManager:
    """
    남양주백병원(NDB) 온톨로지 매니저
    환자의 문제(증상 등)를 입력받아 백병원의 철학과 6대 진료센터에 기반한 해결책/연결 병과를 쿼리합니다.
    """
    def __init__(self, ttl_path=None):
        self.g = Graph()
        self.EX = Namespace("http://example.org/ndb/")
        self.g.bind("ex", self.EX)
        if not ttl_path:
            ttl_path = os.path.join(os.path.dirname(__file__), "ndb_knowledge.ttl")
            
        if os.path.exists(ttl_path):
            self.g.parse(ttl_path, format="turtle")
            print(f"✅ NDB 온톨로지 로드 완료. (총 {len(self.g)} 트리플)")
            
    def get_hospital_philosophy(self):
        query = """
            PREFIX ex: <http://example.org/ndb/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?philLabel
            WHERE {
                ex:NamyangjuBaekHospital ex:establishedPhilosophy ?phil .
                ?phil rdfs:label ?philLabel .
            }
        """
        return [str(row.philLabel) for row in self.g.query(query)]

    def recommend_center_by_symptom(self, symptom_keyword):
        """임상 증상 키워드로 관련 6대 센터를 검색합니다."""
        query = f"""
            PREFIX ex: <http://example.org/ndb/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?centerLabel ?symptomLabel
            WHERE {{
                ?center a ex:MedicalCenter ;
                        rdfs:label ?centerLabel ;
                        ex:treatsSymptom ?symptom .
                ?symptom rdfs:label ?symptomLabel .
                FILTER(CONTAINS(?symptomLabel, "{symptom_keyword}"))
            }}
        """
        results = self.g.query(query)
        recommendations = []
        for row in results:
            recommendations.append({"Center": str(row.centerLabel), "Matched Symptom": str(row.symptomLabel)})
        return recommendations

    def execute_fast_track(self, symptom_keyword):
        """
        [Fast-Track 실행]
        복잡한 단계를 생략하고, 증상(Problem) 파악 즉시 센터를 매칭(Logic)하여 
        협진 기안/예약 등의 타격(Action)을 즉각 수행하는 시뮬레이션입니다.
        """
        print(f"\n⚡ [Fast-Track 즉시 실행 모드 가동: '{symptom_keyword}']")
        recs = self.recommend_center_by_symptom(symptom_keyword)
        if not recs:
            return "❌ 일치하는 긴급 대응 매뉴얼(센터)이 온톨로지에 없습니다."
        
        # 첫 번째 매칭된 센터로 즉시 Action 기안
        target_center = recs[0]['Center']
        action_plan = (
            f"✅ [Action 기안] 환자의 '{symptom_keyword}' 증상을 감지하여 중간 단계를 생략합니다.\n"
            f"   -> 타겟 부서: {target_center} 전문의 긴급 호출 및 예약 슬롯 최우선 확보 지시 완료."
        )
        return action_plan

if __name__ == "__main__":
    manager = NDBOntologyManager()
    print("\n[🎯 남양주백병원 진료 철학]")
    for p in manager.get_hospital_philosophy():
        print(f" - {p}")
        
    symptom = "다리 저림"
    print(f"\n[💡 증상 쿼리 테스트: '{symptom}']")
    recs = manager.recommend_center_by_symptom(symptom)
    if recs:
        for r in recs:
            print(f" -> 제안 센터: {r['Center']} (증상 매칭: {r['Matched Symptom']})")
    
    # Fast-Track 테스트
    symptom_urgent = "허리 통증"
    print(manager.execute_fast_track(symptom_urgent))
