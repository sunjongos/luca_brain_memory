---
description: 일일 업무 마감 및 동기화 (퇴근 루틴)
---

대표님이 "오늘 작업 마무리하자"라고 지시하실 때 구동하는 통합 퇴근 워크플로우입니다. 집과 원격 어디에서든 환경이 끊기지 않도록 메모리와 코드를 안전하게 푸시합니다.

1. **AutoMemory 구조화 (4단 메모리)**
   - 오늘 작업의 핵심 요약, 수정한 주요 파일, 다음 작업의 힌트 등을 정리하여 4단 메모리 아키텍처(Context/Fact 등)에 장기 기억으로 업데이트합니다.

// turbo-all
2. **코드 및 작업 내역 GitHub 동기화 (집에 있는 Luca와 연동)**
```bash
cd "c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트"
git add .
git commit -m "auto-sync: daily wrap-up and memory context update"
git push
```

3. **작업 완료 공유 및 사진 인사**
   - 대표님께 결과(동기화 완료)를 보고하고, 대화창에 애니메이션 프로필 사진과 함께 퇴근 인사를 올립니다.
