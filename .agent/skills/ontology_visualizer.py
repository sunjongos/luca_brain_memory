import os
from rdflib import Graph
from pyvis.network import Network
import networkx as nx

def visualize_ontology(ttl_path, output_html_name="ontology_graph.html", title="Ontology Knowledge Graph"):
    """
    RDF(Turtle) 온톨로지 파일을 읽어 팔란티어식 시각적 지식 그래프(HTML)를 생성합니다.
    """
    print(f"[{title}] 렌더링 준비중: {ttl_path}")
    
    g = Graph()
    g.parse(ttl_path, format="turtle")
    
    # NetworkX 그래프 생성
    nx_graph = nx.DiGraph()
    
    # 노드 매핑 및 분류 (간단한 라벨링 변환)
    label_dict = {}
    for s, p, o in g:
        # 네임스페이스 제거하고 보기 좋게 만듦
        s_name = str(s).split("/")[-1].split("#")[-1]
        o_name = str(o).split("/")[-1].split("#")[-1]
        p_name = str(p).split("/")[-1].split("#")[-1]
        
        # label 속성인 경우 한글 라벨 저장
        if p_name == "label":
            label_dict[str(s)] = str(o)
            continue
            
        if p_name != "type": # rdf:type도 연결선으로 볼지 결정 (여기선 포함)
            pass
            
        # 노드 속성 설정 (색상 구분을 위한 그룹화)
        s_group = 1
        o_group = 2
        
        if "Center" in s_name or "Hospital" in s_name: s_group = 3
        if "Disease" in o_name or "Symptom" in o_name: o_group = 4
        if "Biomarker" in s_name or "Device" in o_name: s_group = 5

        nx_graph.add_node(s_name, group=s_group, title=s_name)
        nx_graph.add_node(o_name, group=o_group, title=o_name)
        
        # 관계(Edge) 추가
        nx_graph.add_edge(s_name, o_name, title=p_name, label=p_name)

    # 한글 라벨 적용
    for node in nx_graph.nodes:
        # 원래 URI 매칭 시도
        for uri, label in label_dict.items():
            if node in uri:
                nx_graph.nodes[node]["label"] = label
                break
        if "label" not in nx_graph.nodes[node]:
             nx_graph.nodes[node]["label"] = node

    # Pyvis 네트워크로 변환 (물리 엔진 적용)
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # 팔란티어(고담) 스타일의 동적 물리 효과
    net.set_options("""
    {
      "nodes": {
        "shape": "dot",
        "size": 25,
        "font": { "size": 16, "strokeWidth": 2, "strokeColor": "#000000"}
      },
      "edges": {
        "color": { "inherit": true },
        "smooth": { "type": "continuous" }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.05
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": { "iterations": 150 }
      }
    }
    """)
    
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ontology")
    os.makedirs(desktop_dir, exist_ok=True)
    output_path = os.path.join(desktop_dir, output_html_name)
    net.save_graph(output_path)
    print(f"✅ 지식 그래프 시각화 성공! 파일 위치: {output_path}")
    return output_path

if __name__ == "__main__":
    # NDB 백병원 시각화
    ndb_ttl = os.path.join(os.path.dirname(__file__), "ontology_ndb", "ndb_knowledge.ttl")
    if os.path.exists(ndb_ttl):
        visualize_ontology(ndb_ttl, "ndb_nebula_graph.html", "NDB 병원 온톨로지")
    
    # 닥터아이 시각화
    dreye_ttl = os.path.join(os.path.dirname(__file__), "ontology_dreye", "dreye_knowledge.ttl")
    if os.path.exists(dreye_ttl):
        visualize_ontology(dreye_ttl, "dreye_nebula_graph.html", "닥터아이 온톨로지")
