---
name: YouTube Research Skill
description: YouTube Data API v3를 활용하여 유튜브 동영상을 검색하고, 트렌드를 분석하는 연구 자동화 스킬입니다.
---

# YouTube Research Skill

이 스킬은 Luca가 YouTube Data API v3를 통해 유튜브 콘텐츠를 리서치하고 데이터를 수집할 수 있도록 돕습니다. 주로 특정 키워드에 대한 동영상을 검색하거나 영상의 세부 메타데이터(조회수, 좋아요, 설명 등)를 가져올 때 활용합니다.

## 시스템 요구사항
- `.env` 파일에 `YOUTUBE_API_KEY`가 설정되어 있어야 합니다.
- `google-api-python-client` 패키지가 설치되어 있어야 합니다.

## 스킬 파일 구조
- `youtube_api.py`: YouTube API와 상호작용하는 핵심 Python 스크립트.

## 사용법 (Agent/CLI)

이 스킬은 `run_command` 도구를 통해 터미널에서 실행합니다.

### 1. 동영상 검색 (Video Search)
특정 키워드로 유튜브 동영상을 검색합니다.

```bash
python .agent/skills/youtube_research/youtube_api.py search "검색할 키워드" [--max-results 5]
```

**출력 예시:**
검색된 동영상의 제목, 채널명, 동영상 URL이 JSON 또는 텍스트 형태로 출력됩니다.

### 2. 동영상 상세 정보 조회 (Video Details)
특정 유튜브 영상의 조회수, 좋아요 수, 게시일, 상세 설명 등을 조회합니다.

```bash
python .agent/skills/youtube_research/youtube_api.py details "비디오ID"
```

## 에이전트 행동 지침 (Agent Guidelines)
1. **유튜브 관련 리서치 요청 시**: 사용자가 "유튜브에서 특정 주제를 찾아줘" 또는 "이 영상 정보 가져와줘" 라고 할 때 이 스킬의 Python 스크립트를 호출하세요.
2. **에러 처리**: API 호출 중 일일 쿼리 한도 초과(Quota Exceeded) 등 에러가 발생하면, 사용자에게 "YouTube API 호출 한도 초과 등의 오류"임을 명확히 안내하세요.
3. **요약 및 보고**: 스크립트 실행 결과를 그대로 주지 말고, 대표님이 읽기 편하도록 마크다운으로 깔끔하게 포맷팅(제목, URL, 조회수 요약 등)하여 보고하세요.
