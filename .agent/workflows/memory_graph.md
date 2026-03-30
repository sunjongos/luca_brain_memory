---
description: 장기 공유 메모리를 옵시디언(Obsidian) 스타일의 지식그래프로 렌더링하여 웹 브라우저에서 확인합니다.
---
# Obsidian-style Memory Graph Workflow

이 워크플로우를 실행하면 Port 5050의 공유 장기 메모리에 쿼리를 보내 현재 기억된 개념과 관계를 추출한 뒤, 옵시디언의 지식 그래프처럼 멋진 네트워크 UI로 그려서 웹 브라우저로 열어줍니다.

💡 **특정 주제(예: 루카, Doctor Eye 등)만 보고 싶다면?**
명령어 뒤에 주제를 붙여서 실행이 가능합니다! (예: `/memory_graph 루카` 로 실행하면 루카 중심의 그래프만 그려줍니다.)

1. 메모리 서버(Port 5050)에서 데이터를 읽어옵니다.
// turbo
2. Python 스크립트를 실행하여 브라우저에 지식 그래프를 띄웁니다.
```powershell
python "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\memory_layer\generate_memory_graph.py"
```
