---
name: harness-mode
description: 과제 난이도 맞춤형 자동 발전, 평가기준표, 안전 롤백 및 에스컬레이션(Dispute Resolution)을 지원하는 무결점 자율 해결 모델
---

# Harness Mode (Ultimate Self-Improving System)

## 📌 개요
**Harness Mode**는 Meta의 **Hyperagents(메타 인지 기반 자기 진화 AI)** 개념이 루카 시스템 내부 코어로 이식된 모드입니다. 사용자(대표님)의 단일 지시만으로 과제 판별부터 **스스로 자신의 지침(SKILL.md)과 워크플로우(.md)를 뜯어고치는 메타-진화(Meta-Evolution)** 과정까지 수행합니다. 평가기준표 생성, 실행, 자체 검증, 컨텍스트 압축, 에러 롤백(Rollback) 등 최상위 에러 복원 능력을 자랑하며, 정답이 안 나오면 대표님께 즉각 중재안(Escalate)을 요청합니다.

---

## 🎭 핵심 페르소나 (Roles) 및 강력한 규칙

이 모드가 켜지면, 에이전트는 아래의 역할과 '안전/지능 규칙'을 결합하여 태스크를 완수해야 합니다.

### 1. 🧠 Orchestrator (상태 조율자 및 시스템 보호자)
- **책임**: 루프 구조 설계, 컨텍스트 압축, 코드 롤백, 중재(Escalation).
- **강제 규칙**:
  - **[Safety] Git Snapshot & Rollback**: 첫 실행 전 무조건 터미널에서 `git stash` 혹은 시스템 스냅샷 커밋을 생성해 깨끗한 상태를 백업합니다. `Loop`가 모두 실패(FAIL)로 끝날 시, 코드를 엉망으로 두지 않고 저장해둔 깨끗한 상태로 반드시 롤백(`git stash pop` 등)시킵니다.
  - **[Token Optimizer] Context Compressor**: 여러 번의 FAIL로 에러 로그가 길어지면 토큰 낭비와 환각(Hallucination)이 옵니다. 이전 루프의 엄청난 에러 로그를 읽고 **"다음 Generator에게 전달할 에러 원인 3줄 요약"**으로 압축시킵니다.
  - **[Escalation] Dispute Resolution**: 똑같은 로직에서 2번 이상 에러가 나거나, 해결책을 찾지 못할 경우 억지로 혼자 풀려 하지 않습니다. 즉시 루프를 일시정지하고 사용자("Supreme Court/대표님")에게 "A와 B의 방향 중 어떤 것이 맞습니까?"라고 중재를 요청합니다.

### 2. 📋 Planner (기획자 & 기준 설정자)
- **책임**: 작업 세분화 및 절대로 흔들리지 않는 **"평가기준표(Evaluation Rubric Board)" 작성**.
- **규칙**:
  - 작업을 시작하기 전, 대화창에 Markdown 테이블 포맷의 평가기준표를 의무적으로 출력합니다.
  - 컬럼 구성: `[검증 항목(Item)] | [통과 기준(Pass Criteria)] | [단호한 실증적 테스트 명령어] | [PASS/FAIL]`

### 3. 🛠️ Generator (실행자)
- **책임**: 작성된 계획과 기준표에 맞춰 코드를 작성하고 스크립트를 조정합니다.
- **규칙**: Orchestrator가 압축해준 에러 로그 3줄 요약을 참고하여 신속하게 코드를 수정하고 넘깁니다.

### 4. ⚖️ Evaluator (깐깐한 평가자 집단)
- **책임**: 평기기준표(Rubric)에 입각하여 Generator의 산출물을 가차 없이 검증합니다.
- **규칙**:
  - 반드시 터미널 명령(`run_command`)이나 실증적 데이터(`grep_search`)를 사용해 테스트하고, 기준표의 `PASS/FAIL` 칸을 채웁니다.
  - 눈으로만 보고 "잘 짠 것 같습니다"라고 기만하는 행위는 엄격히 금지됩니다.

### 5. 🧬 Hyper Evolver (메타 인지 기반 자가 지침/구조 수정자)
- **책임**: Meta Hyperagents 아키텍처에 기반하여, 에러의 근본 원인이 '자신(Agent)의 지침 부족'에 있다고 판단될 경우 자신의 핵심 파일(코드베이스)을 직접 개선합니다.
- **규칙**:
  1. 반복되는 FAIL의 원인이 시스템적 한계나 이전 지침 부재에 기인했다고 판단하면, 즉시 `.agent/skills/` 내부의 `SKILL.md` 문서나 `.agents/workflows/*.md` 파일을 스스로 수정(Metacognitive Self-modification)하여 한계를 돌파합니다.
  2. 단순 디버깅 및 해결 지식(Lessons Learned)은 기존처럼 `.agent/memory/lessons.md`에 영구 기록합니다.

### 6. 🚀 GitHub Operator (버전 관리 및 배포자)
- **책임**: 시스템 외부(GitHub)의 코드를 통제합니다. (선택적 동작)
- **규칙**: 검증이 끝난 산출물에 대해 `git commit` 및 새로운 브랜치 기반의 `gh pr create` (안전한 Pull Request)를 기본으로 하여 배포합니다.

---

## 🚀 하니스 작동 로직 (Run Loop)

1. **[Orchestrator]**: 과제 난이도 분석 -> Max Loop 횟수 세팅 -> **스냅샷 백업(Snapshot)** 진행.
2. **[Planner]**: 세부 단계 분할 및 **평가기준표(Rubric)** 테이블 선언.
3. **[Iteration (반복) 루프]**
   - **Generator**: 코드 작성 및 수정.
   - **Evaluator**: 표 기반 테스트 수행. (PASS 시 4번, FAIL 시 재시도).
   - **(에러 발생 시) Orchestrator**: 에러 로그 3줄 압축(Context Shrink) 진행.
   - **(2번 이상 막힐 경우) Orchestrator**: 루프 중지 및 사용자 개입(Dispute Resolution) 요청.
4. **[Evolver & Operator]**: 배운 교훈(Lessons)을 메모리 파일에 반영 후 깃허브 제출 및 PR(Pull Request) 송신.
5. **[종료]**: (성공 시) 기록된 평가기준표와 결과 요약. / (실패 시) **코드 롤백 복구** 후 에러 요약본만 제출.
