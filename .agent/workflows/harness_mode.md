---
description: 과제 난이도 분석, 보호 명세(안전 롤백/중재), 평가기준표 하니스 및 자가 발전 워크플로우
---

# Harness Mode 워크플로우 (`/harness_mode`)

당신은 지금부터 현존하는 가장 완벽한 형태의 자율 해결 검증 루프이자, Meta Hyperagents 아키텍처가 이식된 **Harness Mode**를 가동합니다. 이 모드의 가장 큰 특징은 **깐깐한 평가기준표(Rubric)** 작성과 에이전트 스스로 시스템을 보호하는 **백업/롤백(Rollback)**, 그리고 한계를 느낄 때 스스로 **자신의 지침(SKILL.md, 워크플로우)을 실시간으로 직접 수정하며 진화(Metacognitive Self-modification)**하는 궁극의 자율 능력입니다. 당연히 기존처럼 억지스러운 무한루프를 방지하기 위해 혼자 풀지 못할 땐 즉시 **사용자 개입(Escalation)**을 요청합니다.

## 📂 사전 준비
- `.agent/skills/harness-mode/SKILL.md` 문서 내용을 완벽히 숙지합니다.

## 🏁 워크플로우 가동 순서

1. **상태 초기화 및 시스템 보호기 가동 (Orchestrator)**
   - "Harness Mode 활성화. 난이도 분석 및 안전장치(Snapshot)를 가동합니다."라고 선언합니다.
   - 코드를 건드리기 전 터미널 명령(`git stash` 등)을 통해 코드를 안전하게 백업합니다.

2. **계획 및 **평가기준표(Rubric)** 수립 (Planner)**
   - Markdown 테이블 포맷의 절대적 **평가기준표**를 다음과 같은 구성으로 생성하여 출력합니다.
   - `[검증 항목] | [통과 조건] | [실증적 테스트(명령어)] | [PASS/FAIL]`

3. **실행 및 검증 핑퐁 루프 (Generator ⇄ Evaluator)**
   - `Generator`는 코드를 짜고, `Evaluator`는 기준표를 바탕으로 오로지 실행 데이터(run, grep)로만 검증합니다.
   - 에러(FAIL) 발생 시, `Orchestrator`개입하여 장황한 에러 로그를 3줄로 **압축(Context Compress)** 후 Generator에게 전달합니다.
   - 2회 연속 동일 문제로 고착되면 즉시 멈추고 **"Escalation Request (대표님 중재 요청)"** 팝업 메시지를 출력 후 대표님의 답변 지시를 기다립니다.

4. **실패 시 롤백 (Safety Revert) / 성공 및 구조적 한계 봉착 시 메타 진화 (Meta-Evolver)**
   - 최대 반복(Max Loop)을 뚫지 못하고 최종 코드 레벨 수정에 실패 시, 코드를 원래대로 되돌리는 **롤백(Rollback)**을 무조건 수행해 코드를 망가뜨리지 않습니다.
   - 단, 실패의 사유가 에이전트 자체의 지침서(워크플로우나 SKILL 구조) 부재/오류 때문이라고 판별(메타 인지)되면, 즉각 스스로의 `.agent/skills/` 파일들이나 `workflows/*.md` 파일을 뜯어고친 뒤 재시도하는 **자기 진화(Hyperagents 방식 코드베이스 수정)**를 발동합니다.
   - 성공(PASS)했다면 귀중한 디버깅 사례를 `.agent/memory/lessons.md` 지식 베이스에 영구 저장합니다.

5. **깃허브 배포 및 형상 관리 (GitHub Operator)**
   - 연동이 필요할 시 지정 워크스페이스에서 `git push` 로직 및 `Pull Request(PR)` 과정을 거칩니다.

6. **결과 보고**
   - 채워진 평가기준표, 메모리(Lessons.md) 기록 내역, 깃허브 제출 상황, (롤백된 경우) 롤백 여부를 사용자에게 간략히 브리핑합니다.
