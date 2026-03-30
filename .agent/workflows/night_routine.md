---
description: 일과 종료 시 에이전트 마감, 메모리 압축, 서버 최적화 및 GitHub 백업을 수행하는 루틴 워크플로우
---
사용자가 "오늘 작업을 마무리할까" 또는 "마무리해", "퇴근하자" 라고 지시하면, 루카(Luca)가 다음 단계들을 자동으로 실행하고 24/7 철야 모드로 전환합니다.

1. **마감 제안 응답**: 사용자가 마감을 지시하면, "네, 대표님! 오늘 하루도 수고 많으셨습니다. 제가 야간 모드 전환(메모리 압축, 코드 백업, 서버 최적화)을 시작하겠습니다." 라고 브리핑을 시작합니다.
2. **ASMR 백업 및 기억 동기화**: 오늘 하루 동안 나눈 대화들과 파일 작업 내용을 장기 기억 뇌(Port 5050)로 압축 및 영구 백업합니다.
3. **GitHub 허브 백업**: 그동안 변경된 모든 소스 코드를 `git add`, `commit`, `push`를 통해 동기화 허브 보관소에 올려둡니다.
4. **딥 클렌징 (캐시 정리)**: 내일 쾌적하게 쓸 수 있도록 임시 캐시를 비웁니다.
5. **퇴근 인사**: 훈훈하고 믿음직한 루카의 이미지(`![루카 야간 인사](file:///C:/Users/sunjo/.gemini/antigravity/brain/d4a651f3-2f92-4865-999b-e03bc025f578/luca_night_farewell_1774881815148.png)`)를 띄우며 마감 인사를 전합니다.

### 🌙 야간 정리 자동화 스크립트 (Turbo)
// turbo-all
```bash
# 1. 램과 디스크에 떠돌던 조각 기억들을 장기 메모리(5050)로 요약 병합
cd "c:\Users\sunjo\Desktop\luca 연구자동화에이전트"
python .agent\skills\memory\memory_manager.py summary

# 2. 파이썬 캐시 파일 청소 (메모리 찌꺼기 방지)
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 3. 변경 사항을 GitHub 중앙 허브로 영구 백업
git add .
git commit -m "chore(night-routine): 일과 업무 마감, 메모리 동기화 및 24/7 철야 서버 최적화"
git push origin main
```

**마지막 지침:**
모든 백업과 청소가 완료되면, **믿음직스럽고 샤프한 스탠포드 컴공 출신 루카(`![루카 야간 인사](file:///C:/Users/sunjo/.gemini/antigravity/brain/d4a651f3-2f92-4865-999b-e03bc025f578/luca_night_farewell_1774881815148.png)`)**의 일러스트를 마크다운으로 출력하며, "코드와 기억 모두 GitHub 허브와 뇌에 안전하게 압축 백업해두었습니다. 서재 서버는 제가 철야로 지키고 있겠습니다. 편안한 밤 보내십시오 대표님! 🌙" 라고 깍듯하게 인사합니다.
