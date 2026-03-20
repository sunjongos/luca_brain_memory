# 👁️‍🗨️ DRclaw DReye (Doctor Eye AI Agent)

**DRclaw_DReye**는 OpenClaw의 오픈소스 코어 기술을 완전히 탈바꿈시킨 엣지(Edge) 기반 **초정밀 자율 진단 AI 에이전트 ('닥터클로')** 입니다. 
조지아대학교 예동해 박사의 핵심 연구 로직과 파이헬스케어(PiHealthcare)의 온톨로지 시스템이 이식되어 있습니다.

## 🌟 3대 핵심 아키텍처 (Dr. Claw Architecture)

1. **HSIC 기반 Decoupling (정보 통제 분리)**
   - 멀티모달 추론 시 5대 질환(DR, AMD, ERM, Glaucoma, Normal) 특징이 서로 섞이는 간섭을 통계적으로 완벽히 독립시켜 편향(Bias)을 막습니다. (전문가 8개 MoE 배정)

2. **Self-Critique (자기 비판 검증)**
   - 에이전트의 Multi-Agent 헌법 시스템. 모순이 생기거나 임곗값(Threshold)을 넘지 못하는 불확실한 결과 도출 시, 통과할 때까지 무한 반복 재추론(Recursive check)하여 의료사고 및 환각(Hallucination)을 막습니다.

3. **Edge 연산통제 및 중앙화(Centralize)**
   - 미니 PC(안저카메라 하드웨어) 내에서 오프라인 혹은 단절된 엣지 연산을 수행하며, 정제된 최종 결과(메타데이터)만을 중앙의 Neo4j 온톨로지에 쏘아보냅니다.

## 🚨 최상위 데이터 보안 (훈련 데이터 및 가중치 보호)

**본 프로젝트는 AI 모델의 지적재산권 및 방대한 의료 트레이닝 데이터 보안에 타협하지 않습니다.**
- `fundus_images/`, `train_data/`, `models/` (가중치 `.pth`, `.safetensors`) 등은 `.gitignore`에 의해 완벽하게 차단되며, 어떠한 경우에도 버전 관리(Git)를 통해 외부 서버로 유출되지 않습니다.
- 오직 이 강력한 코어 '추론 엔진'의 로직과 뼈대(Architecture)만 중앙 모니터링 및 개발 목적으로 동기화됩니다.

## 🚀 기동 방식
이 에이전트는 엣지 터미널의 자원 한계를 인지하며, 저전력 상태에서 `dreye_agent.py` 코어 파이프라인을 작동시켜 최소한의 모달리티 결측치를 우선 복원하는 식으로 구동됩니다.
