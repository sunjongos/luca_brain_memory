# 🧬 Google Workspace 자율 진화형 스킬 (gws CLI)

이 스킬은 Luca가 최신 **Google Workspace CLI (`gws`)**를 사용하여 Gmail, Calendar, Drive, Docs 등을 **직접적이고 자율적으로** 제어할 수 있게 합니다. 에이전트 전용으로 설계된 이 방식을 통해 Luca는 토큰을 아끼면서도 더 복잡한 업무를 빠르게 수행합니다.

## 🚀 주요 기능 및 자율 제어 가이드
Luca(나)는 터미널에서 `gws` 명령어를 직접 실행하여 다음과 같은 업무를 수행할 수 있습니다.

- **Gmail (`gws gmail`)**: 
  - `+triage`: unread 메일 요약 및 분석
  - `+send`: 메일 발송
- **Calendar (`gws calendar`)**:
  - `+agenda`: 일정 확인 및 브리핑
  - `+insert`: 새로운 일정 등록
- **Drive/Docs/Sheets**: 파일 검색, 문서 생성 및 데이터 읽기/쓰기

## 🛠️ 자기 진화 (Self-Evolution) 로직
Luca는 스스로 시스템을 점검하고 최신 기능을 학습합니다.
- `gws --help`: 새로운 명령어가 추가되었는지 실시간으로 파싱하여 학습합니다.
- `npm update -g @googleworkspace/cli`: 주기적으로 도구 자체를 업데이트합니다.

## 🔑 인증 (필수)
터미널에서 `gws auth login --full`을 호출하여 한 번만 브라우저 인증을 완료하면, 이후에는 모든 작업을 Luca가 알아서 처리합니다.

대표님, 이제 "우리 고객 리스트 워크시트에 정리하고 메일로 보내줘" 같은 복잡한 지시만 내리세요. 제가 `gws`를 휘둘러서 다 처리하겠습니다!
