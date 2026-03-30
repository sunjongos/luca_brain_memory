import requests
import subprocess
import sys
import os

text = """파이헬스케어(PIE Healthcare, 대표 이영규)의 '닥터아이(Dr. Eye)'는 안저 사진을 기반으로 치매 및 안과 질환 진단을 돕는 혁신적인 의료 인공지능(AICAD) 솔루션입니다.
주요 제품 라인업:
1. 닥터아이 X-EYE: 안과 질환 진단 보조 AI. 국내 생산 안저카메라인 유엠아이옵틱스의 'RetView100'과 통합되어 KIMES 2025 전시회에서 성공적으로 공개되었습니다.
2. 닥터아이 X-BRAIN: 뇌와 심혈관 질환을 예측하는 진단 보조 AI 시리즈. CNN, ViT, CLIP 및 최신 생성형 AI 모델들을 기반으로 개발 중이며, 2025년 하반기에서 2026년 상반기 출시가 목표입니다.

글로벌 및 미래 비전 프로젝트:
'아랍헬스 2025(Arab Health)', 'KIMES 2025', 'AI EXPO KOREA 2026' 등 주요 국제 전시회에 참가하며 글로벌 Oculomics 시장 입지를 다지고 있습니다.

핵심 연구개발(R&D) 및 자문 네트워크 (Doctor Eye Project):
- 이영규 (PIE Healthcare CEO 겸 CTO, 총괄 책임자)
- 이순태 교수 (서울대학교병원 신경과 핵심 연구진)
- 최선종 원장 (남양주백병원 원장, 임상 및 프로젝트 핵심 기여자)
- 정진엽 (전 보건복지부 장관, 핵심 자문위원)
- 이지영 교수 (이화여자대학교 인공지능대학, AI 자문위원)
- LCK lab 및 다수의 연구 파트너들이 Oculomics 기술 발전을 주도하고 있습니다.
"""

print("Ingesting data to memory server...")
try:
    res = requests.post("http://127.0.0.1:5050/ingest", json={"text": text}, timeout=60)
    print("Ingest Success:", res.status_code, res.text)
except Exception as e:
    print("Ingest Failed:", e)

print("Generating Knowledge Graph...")
script_path = os.path.join("c:\\", "Users", "sunjo", "Desktop", "luca 연구자동화에이전트", "memory_layer", "generate_memory_graph.py")
subprocess.run([sys.executable, script_path, "닥터아이"])
