---
description: 장기 공유 메모리를 옵시디언(Obsidian) 스타일의 지식그래프로 렌더링하고 Vault로 추출합니다.
---
# Obsidian-style Memory Graph & Vault Workflow

이 워크플로우를 실행하면 Port 5050의 공유 장기 메모리에 쿼리를 보내 현재 기억된 개념과 관계를 모델링합니다. HTML 웹 브라우저 렌더링 외에도 완벽한 구조의 마크다운 기반 Obsidian Vault 폴더로 직접 추출할 수 있습니다.

💡 **특정 주제(예: 루카, Doctor Eye 등)만 HTML로 보고 싶다면?**
명령어 뒤에 주제를 붙여서 웹 그래프 뷰로 실행이 가능합니다! (예: `/memory_graph 루카`)

1. 메모리 서버(Port 5050) 최신 상태 체크 (Auto-Consolidation 여부 확인)
// turbo
2. (옵션 1) 웹 브라우저 인터렉티브 지식 그래프로 띄우기
```powershell
python "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\memory_layer\generate_memory_graph.py"
```

3. (옵션 2) Andrej Karpathy식 완전한 Obsidian Vault로 내보내기 (권장)
이 명령어를 실행하면 `Luca_Memory_Vault` (Raw, Wiki, Log, Index 구성) 마크다운 볼트 풀세트가 즉시 구축됩니다!
// turbo
```powershell
python "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\memory_layer\export_to_obsidian.py"
```
