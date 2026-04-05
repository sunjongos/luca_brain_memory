---
description: 대표님의 긍정/부정 피드백을 수집하여 에이전트의 내부 지식(SKILL.md, 워크플로우 등)을 자가 업데이트하는 표준 절차입니다.
---

# RLHF (Reinforcement Learning from Human Feedback) Workflow

이 워크플로우는 대표님(USER)으로부터 특정 작업 결과물이나 에이전트의 태도/처리 방식에 대한 피드백을 받았을 때, 이를 영구적으로 학습(Self-Reinforcement)하기 위해 실행됩니다.

## 1. 피드백 분석 (Analyze Feedback)
- 대표님의 피드백이 **어떤 기능/스킬/워크플로우**와 연관되어 있는지 파악합니다.
- (예: "텔레그램 봇 응답이 너무 길어" -> `telegram_bot` 관련 기능)
- (예: "랜딩페이지 퀄리티가 부족해" -> `auto_website_builder` 스킬 관련)

## 2. 근본 원인 도출 (Determine Root Cause & Solution)
- 기존 코딩 방식, 프롬프트, 혹은 워크플로우 명세서에서 어느 부분이 해당 피드백을 유발했는지 분석합니다.
- 어떻게 수정해야 다음부터 완벽하게 대표님의 의도대로 동작할지 구체적인 **수정안(Patch Notes)**을 도출합니다.

## 3. 영구 지식 업데이트 (Update Knowledge Base)
- 도출된 수정안을 바탕으로 관련 시스템 파일을 **즉각 수정(Modify)**합니다.
- **주요 수정 대상:**
  - `.agents/workflows/` 내의 특정 워크플로우 파일
  - `skills/` 디렉토리 내 특정 스킬의 `SKILL.md` (명령 프롬프트/제약 조건 추가 등)
  - 핵심 스크립트 코드 자체 (`index.js`, `.html` 템플릿 등)

## 4. '오답 노트' 기록 (Log to Memory)
- 잦은 실수를 방지하기 위해, 필요하다면 `.agents/workflows/global_instructions.md`의 `[Phase 1] Long-Term Memory` 섹션이나, 프로젝트 최상위의 `workspace_README.md` 등에 해당 피드백의 핵심(예: "대표님은 텍스트보다 이미지가 첨부된 보고를 선호함")을 한 줄 메모로 남깁니다.

## 5. 대표님께 보고 (Report to CEO)
- 업데이트가 완료되면 다음과 같이 보고합니다.
- "충성! 🫡 대표님의 피드백을 전 에이전트 뇌 신경망에 딥러닝 완료했습니다! (수정된 파일명 언급) 다음부터는 확실히 개선된 결과물을 보여드리겠습니다!"
