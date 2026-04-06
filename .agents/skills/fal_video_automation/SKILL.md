---
name: Fal.ai Video Automation
description: 루나(Luna) 요원이 수동 작업 없이 Fal.ai (Minimax/Luma) API를 호출하여 유료로 고품질 시네마틱 영상을 전자동으로 렌더링하는 스킬입니다.
---

# Fal.ai 자동 영상 생성 스킬 (루나 전용)

대표님께서 브라우저를 직접 켜고 영상을 생성하는 수고로움을 없애기 위해, 루나(Luna)가 직접 **Fal.ai API(유료)**를 활용하여 고퀄리티(VEO 3 급) 영상을 백그라운드에서 렌더링하도록 돕는 스킬입니다.

## 🛠 필수 전제 조건
1. 시스템 환경변수(`.env` 파일 등)에 `FAL_KEY`가 등록되어 있어야 합니다.
   - 포맷: `FAL_KEY="키값"`
2. Python의 `requests` 라이브러리가 필요합니다. (`pip install requests`)

## 🚀 사용 방침 (For Luna)
루나는 프롬프트 기획안이 확정되면, 사용자에게 수동 다운로드를 요청하는 대신 아래의 스크립트를 백그라운드에서 직접 실행하여 비디오 MP4 파일을 획득해야 합니다.

### 실행 방법
```bash
# 디렉토리 이동
cd "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\.agents\skills\fal_video_automation\scripts"

# 스크립트 실행 (인자로 영상 프롬프트를 넘김)
python fal_video_gen.py "A hyper-realistic cinematic portrait in 9:16 aspect ratio of a dignified Korean male hospital director..."
```

### 아웃풋
- 성공 시, 스크립트가 실행된 폴더에 `{timestamp}_generated_video.mp4` 파일로 영상이 꽂히고 콘솔에 절대 경로를 반환합니다.
- 루나는 이 MP4 파일의 절대 경로를 영식(Youngshik)이에게 전달하여 오디오(Lyria/TTS) 믹싱을 이어가도록 오케스트레이션합니다.

## ⚠️ 주의사항
- 본 API는 1회 생성 시 일정 크레딧이 차감되는 **유료 스킬**입니다.
- 너무 빈번한 루프 렌더링을 막기 위해, 루나는 반드시 단일 프롬프트를 완성도 있게 다듬은 후 '1회'만 신중히 호출해야 합니다.
