import sys
from pathlib import Path

# luca_brain 모듈 경로에 추가
sys.path.append(str(Path(__file__).parent))
import luca_brain

scheduler_prompt = """
[⏰ AI-Native 스케줄러 핵심 지침 ⏰]
텔레그램 사용자가 "매일 아침 8시에 ~해줘", "10분마다 ~해줘", "내일 오후 3시에 ~알려줘" 등 특정한 시간이나 주기에 무언가를 실행하라고 자연어로 지시하면, 당신은 `add_schedule` 도구를 호출하여 백그라운드 작업을 등록해야 합니다.

- Interval 방식 (예: 10분마다 뉴스): `job_type="interval"`, `time_expr="10m"`
- Cron 방식 (예: 매일 아침 8시 브리핑): `job_type="cron"`, `time_expr="0 8 * * *"`
- 지정 시간 예약 (예: 내일 오후 3시 회의 정리): `job_type="date"`, `time_expr="2026-03-10 15:00"` (반드시 YYYY-MM-DD HH:MM 형태)

또한 사용자가 현재 스케줄을 물어보면 `get_schedules` 도구를, 취소하고 싶어하면 `remove_schedule` 도구를 사용하여 관리하십시오. 사용자가 복잡한 명령어를 칠 필요 없이, 오직 당신이 도구를 통해 완벽하게 제어해야 합니다.
"""

current_prompt = luca_brain.get_current_system_prompt()
new_prompt = current_prompt + "\n" + scheduler_prompt

# DB에 새로운 프롬프트 버전으로 저장
luca_brain.update_system_prompt(new_prompt, "AI-Native 스케줄러 (add_schedule) 통합")
print("System prompt successfully updated with AI-Native Scheduler instructions.")
