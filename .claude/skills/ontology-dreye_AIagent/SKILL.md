---
name: Ontology - Doctor Eye AI Agent (Dr. Claw)
description: 조지아대학교 예동해 박사의 핵심 로직(CoMoE, HSIC, Self-critique)과 파이헬스케어의 닥터아이(Doctor Eye) 온톨로지를 결합하여 엣지(Edge) 디바이스에서 독자적으로 추론하고 검증하는 완벽한 자율 진단 AI 에이전트('닥터클로') 스킬입니다.
---

# 👁️‍🗨️ Doctor Eye AI Agent (Dr. Claw) 스킬 명세서

본 스킬은 단순한 텍스트 기반 AI가 아닌, 안저카메라와 같은 의료 기기 엣지(Edge) 단에서 환각(Hallucination) 없이 완벽한 진단을 내리기 위해 설계된 **최상위 등급의 멀티모달 진단 에이전트**입니다.

## 🌟 3대 핵심 아키텍처 (Core Architecture)

### 1. HSIC (Hilbert-Schmidt Independence Criterion) 기반 정보 분리
*   **원리**: 5가지 질환(DR, AMD, ERM, Glaucoma, Normal) 등 서로 다른 질환을 판단하는 특징(Feature)들이 학습 및 추론 과정에서 뒤섞이지 않도록 통계적으로 완벽히 독립(Decoupling)시킵니다.
*   **역할**: 8개의 전문가(Expert) 모델이 각자의 고유한 특징에만 집중하도록 이끌어, 데이터 편향(Bias)을 원천 차단하는 이 에이전트의 **설계 원칙**입니다.

### 2. Self-Critique (자기 비판 후처리)
*   **원리**: 에이전트가 자체적으로 도출한 추론 결과가 의학적/논리적 모순이 없는지 스스로 점검합니다.
*   **역할**: Multi-Agent 시스템의 **헌법(Constitution)**과 같습니다. 만약 예측 결과가 임곗값(Threshold)에 애매하게 걸치거나, 상호 배타적인 결과(예: 질환 있음 + 정상)가 병존할 경우, 에이전트는 진단을 보류하고 처음부터 확실한 결과가 나올 때까지 재추론을 강제합니다.

### 3. Edge AI 통제 (온톨로지 동기화)
*   **원리**: 이 '닥터클로' 에이전트는 안저카메라에 부착된 미니 PC(Edge)에서 독립적으로 동작하며, 진단 과정을 모두 마친 깨끗한 메타데이터만을 중앙(Central)의 닥터아이 온톨로지 지식 그래프로 전송합니다.

## 🚀 워크플로우 (파이프라인)

에이전트가 `dreye_agent.py`를 실행할 때 따르는 절대적인 순서입니다.

1.  **[Input]** 저자원 환경에서의 안저 사진 및 불완전한 메타데이터 수집
2.  **[Generation]** 모달리티 누락 시 멀티모달 생성 모델을 통한 데이터 보완
3.  **[Decoupling]** HSIC 척도를 적용하여 질환별 특징 분리 분석 (MoE 가동)
4.  **[Constitution]** Self-critique 알고리즘을 통한 1차 추론 결과 검증
5.  **[Correction]** 모순 또는 임곗값 미달 시 재추론 실시 (Loop)
6.  **[Action]** 확정적 예측 결과 도출 및 중앙 온톨로지(Neo4j) 브로드캐스팅

## 🛠 파일 구조
*   `SKILL.md`: 본 스킬의 헌법적 명세서
*   `dreye_agent.py`: HSIC 및 Self-critique 파이프라인이 코드 레벨로 묘사된 닥터클로 에이전트의 실행 엔진.
