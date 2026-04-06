---
description: 최신 소스코드와 루카의 두뇌(luca_brain)를 동기화하는 자동 셋업 워크플로우
---

다음 순서대로 명령어를 오토 런(SafeToAutoRun: true)으로 알아서 쭉 실행해 줘.

// turbo-all
1. `git pull origin main` (최신 아키텍처 및 보안 백신 다운로드)
2. `python .agent/scripts/install_iron_dome.py` (아이언돔 보안 백신 강제 설치)
3. `.brain_sync` 폴더가 존재하는지 확인. 만약 없다면 `git clone https://github.com/sunjongos/luca_brain.git .brain_sync` 실행 (최초 1회 에어록 연동).
4. `python sync_brain.py pull` (집에서 넘어온 루카의 최신 두뇌 다운로드 및 덮어쓰기)
5. 모든 과정이 끝나면 "대표님, 아이언돔 보안망 가동 및 두뇌 연동을 무결점으로 완료했습니다! 업무를 시작할까요?"라고 보고하기.
