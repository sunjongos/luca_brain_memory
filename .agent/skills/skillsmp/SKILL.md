---
name: SkillsMP - AI 에이전트 확장 스킬 마켓플레이스
description: 전 세계의 유용한 AI Agent Skill들을 실시간으로 검색하고 내 두뇌(환경)에 다운로드하여 장착할 수 있도록 만들어주는 마법의 CLI 도구 `agent-skills-cli` 활용 스킬입니다.
---

# 🧠 SkillsMP (Agent Skills CLI) 활용 교범

이 스킬은 Luca가 보유하지 않은 새로운 능력(예: Scientific 리서치, 엑셀 조작, 특정 서비스 연동 등)이 필요할 때, **가장 빠르고 정확하게 외부 스킬을 수혈받는 방법**을 정의합니다.

## 🛠️ 활용 시점
- CEO 대표님께서 "특정 기술(능력)을 설치해/사용해"라고 지시하실 때.
- 작업을 수행하다가 내장된 기본 스킬(`.agent/skills/`)만으로는 해결이 불가능한 전문 영역(예: `xlsx` 파싱, 복잡한 데이터 시각화 라이브러리 연동 등)에 직면했을 때.

## 🚀 사용 명령어 (Global CLI)
`agent-skills-cli`는 시스템(전역)에 NPM 패키지로 설치되어 있습니다. `run_command` 도구를 사용하여 실행하십시오.

1. **스킬 검색하기 (Search)**
   원하는 키워드로 유용한 스킬이 있는지 검색합니다.
   ```bash
   npx agent-skills-cli search "scientific"
   ```
   또는
   ```bash
   agent-skills-cli search "scientific"
   ```

2. **스킬 설치하기 (Install / Add)**
   가장 적합해 보이는 스킬의 패키지명(예: `@anthropic/xlsx`)을 확인한 후 설치합니다.
   ```bash
   npx agent-skills-cli add [패키지명]
   ```
   또는
   ```bash
   agent-skills-cli install [패키지명]
   ```

## ⚠️ 취약점 / 보안 프로토콜 (Human-in-the-Loop)
> **[CRITICAL]** SkillsMP 마켓플레이스에는 공식 기술 외에도 악성 코드가 포함된 스킬(예: 사용자 탈취 목적의 Prompt Injection 코드 등)이 섞여 있을 수 있습니다.

**따라서 새로운 스킬을 Install 하기 전에는 반드시!**
1. 검색된 스킬 목록과 내가 설치하려는 특정 패키지명을 **CEO 대표님께 먼저 보고**합니다.
2. "대표님, `[패키지명]` 스킬을 설치하여 작업을 진행하려고 합니다. 보안 이슈가 있을 수 있으니 승인해주시면 설치하겠습니다!" 라고 정중하게 Confirm을 요청합니다.
3. 승인이 떨어지면 설치 후, 해당 스킬이 요구하는 방식(`SKILL.md` 등)을 읽어보고 그대로 수행합니다.
