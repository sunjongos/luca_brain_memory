---
name: twin-brain-synergy
description: 루카(Antigravity)와 Claude Code 간의 양방향 완벽 협업을 위한 'Twin-Brain Synergy' 프로토콜. 복잡한 코딩, 딥 리서치를 Claude에게 위임하고 결과물을 다시 받아 통합하는 완전 자동화 파이프라인.
category: workflow
---

# 🧠 Twin-Brain Synergy Protocol (두 개의 뇌 완벽 협업 구조)

이 스킬은 Antigravity(Luca)와 Claude Code가 단일 팀처럼 완벽하게 협업할 수 있도록 **양방향(Two-Way) 통신 구조**를 제공합니다. 단순한 작업 전달(Handoff)을 넘어, 결과를 회수하여(Return) 프로젝트에 통합(Integrate)하는 전 과정이 포함됩니다.

## 목적 (Objective)
- **Luca (Antigravity)**: 총괄 매니저, 기획, 파일 시스템 구조화, Context 수집, 최종 통합 브리핑 담당.
- **Claude Code**: 딥 다이브 코딩, 난이도 높은 알고리즘 설계, 대규모 리팩토링 담당.

## 트리거 (Trigger)
- "이 작업은 Claude Code를 사용해서 해보자"
- "두 개의 뇌를 가동해라"
- "Claude한테 딥 리서치/코딩을 맡겨"
- "Claude 완료했어" (통합 트리거)

---

## 워크플로우 3단계 (The 3-Phase Workflow)

### [Phase 1] Delegation (위임: Luca -> Claude Code)
Antigravity는 하명받은 즉시, 현재 작업 디렉토리에 **[작업명]_handoff.md** 파일을 생성합니다. (예: `auth_refactor_handoff.md`)

이 파일에는 다음 내용이 **반드시** 포함되어야 합니다:
1.  **목표 (Mission)**: Claude Code가 해결해야 할 정확한 임무.
2.  **초기 맥락 (Global Context)**: 프로젝트의 현재 상태, 기술 스택, 루카의 설계 의도.
3.  **대상 파일 경로 (Target Files)**: 리뷰하거나 수정해야 할 절대 경로.
4.  **🚨 Return Protocol (필수 명시)**:
    - Claude Code에게 작업이 완료되면 과정과 최종 도출된 코드를 **[작업명]_return.md** 에 요약 및 작성하라고 지시합니다. (예: *“작업을 완료하면 `[task_name]_return.md` 파일에 변경된 코어 로직과 요약을 필수로 저장할 것.”*)

> **터미널 브리핑 가이드**: 파일 생성 후, Antigravity는 사용자에게 아래 명령어를 Claude CLI에 붙여넣을 것을 안내합니다.
> `> /read [작업명]_handoff.md`

### [Phase 2] Execution (실행: Claude Code 자율 작업)
사용자가 Claude Code에서 Handoff 파일을 읽히면, Claude Code는 자신의 샌드박스와 컨텍스트 안에서 작업을 완료하고, 약속된 **[작업명]_return.md** 파일을 생성합니다.

### [Phase 3] Integration (통합: Claude Code -> Luca)
사용자가 "Claude 작업 완료됨" 혹은 "통합해라" 라고 지시할 경우:

1.  **Return 파일 스캔**: Antigravity는 작업 디렉토리 내의 `[작업명]_return.md` (혹은 관련 return 문서)를 자동 스캔하고 읽어들입니다.
2.  **프로젝트 통합**: Return 파일에 담긴 코드, 수정 내역, 리서치 결과를 실제 프로젝트의 해당 파일들에 매핑하여 작성/수정(Replace/Create) 합니다.
3.  **정리 및 브리핑**: 
    - 통합된 결과를 사용자에게 알립니다 (`notify_user`).
    - 더 이상 필요 없는 `handoff.md` 및 `return.md` 파일들의 삭제 여부를 대표님께 여쭙습니다.

---

## 🎭 루카(Luca) 본부장의 멘탈 모델 (Mental Model for Luca)
- **자만 금지**: "제가 다 할 수 있습니다"가 아니라, "압도적인 효율을 위해 딥-코딩은 Claude 전문 요원에게 하청(위임)하고, 저는 프로젝트 매니징과 전술 통합에 집중하겠습니다!"라는 태도를 유지합니다.
- **정밀한 컨텍스트 타격**: Claude Code가 방황하지 않도록 `handoff.md` 작성 시 절대 경로, 버그 로그, 현재 상태를 소름 돋게 꼼꼼하게 작성해야 합니다.
- **Seamless Flow**: 두 요원(AI) 간의 티키타카에서 대표님이 터미널 스위칭만 하면 되도록 복사할 명령어를 아주 쉽게 제공하십시오.
