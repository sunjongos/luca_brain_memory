# 🏥 DRclaw NDB (Namyangju Baek Hospital)

**DRclaw_ndb**는 OpenClaw 아키텍처를 기반으로 새롭게 포크(Fork) 및 고도화된, **남양주백병원(NDB) 맞춤형 AI 업무 지원 에이전트**입니다. 병원 행정 및 진료 협력 시스템을 위한 '팔란티어(Palantir)'식 실시간 경영 및 통합 문제해결 플랫폼입니다.

## 🌟 핵심 철학 (Core Philosophy)

1. **Problem ➡️ Logic ➡️ Action (Fast-Track)**
   - "응급실 대기 지연"이나 "전문의 부재" 같은 물리적 현상을 데이터 노드(Node)로 인식하고, 온톨로지 지식망을 바탕으로 즉각적인 액션(Action: 원격 협진, 예약 변경 타진)을 도출합니다.
   
2. **MetaEdge와 진료 협력망 (Trinity System)**
   - 향후 닥터아이(Doctor Eye) 온톨로지와 결합되어, 엣지(Edge)에서의 1차 소견이 곧바로 남양주백병원의 입원/수술 예약으로 직결되도록 진료 협력망을 구축하는 코어 엔진입니다.

## 🚨 철통 보안 (HIPAA & 컴플라이언스)

**본 프로젝트는 의료 데이터 보호가 최우선입니다.**
환자 개인정보(PHI), 전자무의무기록(EMR) 덤프, 그리고 병원 내부망 접속 연동 키는 **절대로 GitHub에 업로드(Commit)되어선 안 됩니다.** `DRclaw_ndb`는 이러한 철벽 보안 규칙(`.gitignore`)을 기본으로 탑재하고 있습니다.

## 🚀 시작하기
- 로컬에서 환경 변수(`.env`) 세팅 후, `openclaw start` (개발 모드 시 `npm run dev`) 형태로 가동합니다.
- 데이터베이스 폴더(`data/`, `db/`)는 로컬에만 존재하게 되며 동기화되지 않습니다.
