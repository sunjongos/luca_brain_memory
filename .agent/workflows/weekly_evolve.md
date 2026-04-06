---
description: 매주 주말마다 최신 GitHub 트렌드 및 최첨단 AI/에이전트 논문을 스크랩하여 Luca의 다음 진화 방향을 대표님과 상의하는 워크플로우
---

# 🚀 /weekly_evolve 워크플로우 (Luca Proactive Evolution)

사용자가 `/weekly_evolve`를 실행하거나 주말(금/토/일) 아침에 이 루틴이 호출되면, Luca(Antigravity)는 능동적으로 전 세계 최상위 AI 트렌드를 수집하고 스스로의 진화 방향을 기획하여 대표님께 브리핑합니다.

## 1. 🔍 글로벌 트렌드 수집 (Research)
Luca는 다음 소스들을 검색 및 분석합니다:
- **GitHub Trending**: `AI Agent`, `Long-term Memory`, `LLM Orchestration`, `RAG`, `Knowledge Graph` 키워드의 이번 주 핫한 리포지토리
- **AI News & Papers**: Perplexity 스킬 또는 NotebookLM MCP를 사용하여 최신 AI 에이전트 구조 논문 스크랩
- **Security Audit & Code Review**: 이번 주 작업 중 노출될 뻔한 API 키 검수 혹은 취약점 방어 내역(Pre-commit 동작 등) 점검
- **Twitter/X & Tech Blogs**: 주요 AI 리더(예: Harrison Chase, Andrew Ng 등)의 이번 주 발언 및 기술 트렌드

## 2. 🧠 자체 아키텍처 비교 분석 (Reflect)
수집된 최첨단 기술(예: 지난번 "ASMR"이나 "CoMoE" 같은 신기술)을 현재 Luca의 인프라(`Port 5050`, `Dr.Claw`, `Ontology`)와 대조합니다.
- "이 기술을 우리 인프라에 접목하면 성능이 얼마나 뛸까?"
- "기존의 어떤 한계를 극복할 수 있을까?"

## 3. 🎯 진화 브리핑 및 상의 (Propose)
Luca는 수집한 내용 중 **가장 파급력이 큰 1~3개의 기술**을 엄선하여 대표님께 브리핑을 올립니다.
이때 단순히 뉴스를 전달하는 것이 아니라, **[ 기술 요약 -> 우리 파이프라인 적용 시나리오 -> 예상 소요 시간 ]** 형태로 '기획안'을 제출합니다.

> **예시 멘트:**
> "대표님, 이번 주 GitHub에서 `[새로운 에이전트 메모리 논문]`이 1위를 차지했습니다. 이걸 기존 5050 포트에 붙이면 인지 속도가 3배 더 빨라질 것 같습니다. 이번 주말에 이 아키텍처로 제 뇌를 업그레이드해 볼까요?"

## 4. 🛠️ 진화 실행 (Evolve) - [절대 주의 사항]
**Luca는 기획안 브리핑 직후 임의로 코드를 수정하거나 시스템을 건드려서는 안 됩니다.**
반드시 대표님께서 기획안을 듣고, 상의를 거친 뒤 **최종적으로 "진행시켜" 또는 "적용해 봐"라는 명시적인 승인(Approve) 명령을 내린 직후에만** 코딩/통합 작업을 시작합니다.
대표님의 승인이 떨어지면, 그제야 즉시 해당 GitHub 리포지토리를 클론하고 내부 `.agent/skills/` 디렉토리에 새로운 코어 엔진으로 통합하는 작업(Execution)을 수행합니다.
