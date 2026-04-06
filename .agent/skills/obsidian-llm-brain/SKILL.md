---
name: obsidian-llm-brain
description: Andrej Karpathy식 LLM Wiki 및 Obsidian 제2의 뇌 (Second Brain) 구축 스킬
---
# Obsidian LLM Brain 스킬

**목적:** 단순히 RAG를 위한 임베딩/VectorDB가 아니라, 사람이 직관적으로 검색하고 탐구할 수 있는 Markdown 파일 모음(지식 위키)을 LLM으로부터 직접 구축합니다. 

## 지식 폴더 구조 체계
이 스킬은 Luca_Memory_Vault 디렉토리 하위에 다음과 같은 구성을 생성/관리합니다:
- **Raw/**: 유튜브 자막이나 스크랩된 원본 글, 혹은 1차 요약본이 저장됩니다. 글 내에 Wiki 문서로 연결되는 백링크([[개념]])가 삽입되어 있습니다.
- **Wiki/**: 고도로 정제된 엔티티/개념 설명 문서들이 들어갑니다. (예: [[LLM Agent]].md)
- **Log/**: 지식 주입 및 배치 로그.

## 사용법 (CLI)
사용자가 터미널에서 obsidian [url] 또는 obsidian graph 명령어를 입력하면 obsidian.bat을 통해  uilder.py가 백그라운드에서 동작합니다.
- obsidian graph : 지식 추출 후, 옵시디언 URI (obsidian://open?path=...)를 호출하여 시각적인 지식 그래프를 즉각적으로 화면에 띄웁니다.

## 에이전트 가이드라인
1. 사용자가 특정 링크나 주제에 대해 옵시디언화를 요청할 경우, 에이전트가 직접 `python .agent/skills/obsidian-llm-brain/builder.py [링크]` 형태의 명령어를 실행하여 지식을 추출하십시오.
2. 스크립트 실행이 성공적으로 완료되면, 에이전트가 **직접 터미널 커맨드(powershell -Command "Start-Process 'obsidian://open?path=c:\Users\sunjo\Desktop\luca 연구자동화에이전트\Luca_Memory_Vault'")를 실행**하여 사용자 화면에 지식 맵을 띄워 주십시오. 절대 사용자에게 단축어를 입력하라고 지시하지 말고 에이전트가 전부 자동화하여 완료해야 합니다.