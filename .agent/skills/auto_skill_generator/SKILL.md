---
name: auto_skill_generator
version: 1.0.0
description: Luca가 스스로 필요하다고 판단되는 파이썬 모듈과 SKILL.md 규격을 자체 생성하여 자가 증식(Self-Proliferating)하는 최고 권한의 진화 엔진 스킬. (World Best Practice)
tags: [evolution, self-modifying, agi, code-generation]
---

# Auto Skill Generator (자가 스킬 증식기) 🧬

이 모듈은 Andrej Karpathy가 제시한 LLM OS의 수준을 초월하기 위해 설계되었습니다.
단순히 프롬프트를 바꾸는 것을 넘어, **자신의 물리적 한계점(할 수 없는 작업)을 인지하면 즉각적으로 Python 코드와 통합 도구를 스스로 작성하여 `skills/` 폴더 내에 마운트**합니다.

## 핵심 구동 원리
1. **Trend & Insight 획득**: 매주 진행되는 `job_trend_research`에서 혁신적인 AI/프레임워크 트렌드를 찾아냅니다.
2. **LLM Function (JSON) 호출**: Gemini-2.5-pro 모델에 트렌드를 던지고, 이를 실현하기 위한 `skill_name`, `python_code`, `SKILL.md` 내용을 JSON으로 뽑아냅니다.
3. **물리적 파일 생성 (Self-Modifying)**: `.agent/skills/` 디렉토리 아래에 신규 폴더를 생성하고 반환된 코드를 이식하여 재부팅 없이 다음 번 런타임에 도구가 자동 로드되도록 대기합니다.
4. **AGI Brain 각인**: 이렇게 추가된 스킬 내역은 `LucaAGIBrain`을 통해 NDB 온톨로지와 5050 공유 메모리망에 영구 기록됩니다.

> [!WARNING]  
> 이 모듈 스킬은 **에이전트의 통제되지 않는 폭발적 증식을 막기 위해 코드 단에서 주 1회 작동하도록 물리적 제동**이 걸려 있습니다.
