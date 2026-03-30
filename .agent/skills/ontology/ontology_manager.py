import os
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

class OntologyManager:
    """
    온톨로지(RDF 기반) 그래프를 로드하고 쿼리하는 매니저 클래스.
    닥터아이(Doctor Eye) 프로젝트 등 지식 그래프 연동에 활용.
    """
    def __init__(self, ttl_path=None):
        self.g = Graph()
        self.EX = Namespace("http://example.org/doctoreye/")
        self.g.bind("ex", self.EX)
        
        if ttl_path and os.path.exists(ttl_path):
            self.load_ontology(ttl_path)
            
    def load_ontology(self, filepath):
        """Turtle (.ttl) 형식의 온톨로지 파일을 로드합니다."""
        try:
            self.g.parse(filepath, format="turtle")
            print(f"✅ 온톨로지 로드 완료: {filepath} (총 {len(self.g)} 개의 트리플)")
        except Exception as e:
            print(f"❌ 온톨로지 로드 실패: {str(e)}")

    def get_project_targets(self, project_name="DoctorEyeProject"):
        """특정 프로젝트가 타겟팅하는 질환 목록을 조회합니다."""
        query = f"""
            PREFIX ex: <http://example.org/doctoreye/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?diseaseLabel
            WHERE {{
                ex:{project_name} ex:targetsDisease ?disease .
                ?disease rdfs:label ?diseaseLabel .
            }}
        """
        results = self.g.query(query)
        diseases = [str(row.diseaseLabel) for row in results]
        return diseases

    def get_team_members(self):
        """관여된 주요 인물 및 소속 정보를 조회합니다."""
        query = """
            PREFIX ex: <http://example.org/doctoreye/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?name ?role
            WHERE {
                ?person a ex:Person ;
                        rdfs:label ?name ;
                        ex:hasRole ?role .
            }
        """
        results = self.g.query(query)
        return [{"name": str(row.name), "role": str(row.role)} for row in results]

    def ask_agent_query(self, sparql_query):
        """AI 에이전트가 커스텀 SPARQL 쿼리를 날릴 수 있도록 열어둔 인터페이스"""
        try:
            results = self.g.query(sparql_query)
            return [dict(row) for row in results]
        except Exception as e:
            return f"❌ 쿼리 에러: {str(e)}"

# 테스트 실행 코드
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ttl_file = os.path.join(current_dir, "doctor_eye_base.ttl")
    
    manager = OntologyManager(ttl_file)
    
    print("\n[🎯 닥터아이 프로젝트 진단 대상 질환]")
    targets = manager.get_project_targets()
    for t in targets:
        print(f" - {t}")
        
    print("\n[👥 관련된 핵심 인물/역할]")
    members = manager.get_team_members()
    for m in members:
        print(f" - {m['name']} (역할: {m['role']})")
