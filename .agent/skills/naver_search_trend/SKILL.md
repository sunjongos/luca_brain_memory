---
name: Naver Search & Trend 스킬
description: 네이버 검색 API와 데이터랩 API를 활용하여 연관 키워드 콘텐츠와 검색어 트렌드를 분석하는 기술 (마케팅 최적화 지원용)
---

# Naver Search & Trend 스킬

이 스킬은 Luca가 네이버 검색 결과(블로그, 뉴스, 웹문서, 지식iN)와 데이터랩 트렌드 데이터를 조회하여, 마케팅 효율(ROAS) 최적화에 필요한 인사이트를 대표님께 제공하기 위해 사용됩니다.

## 🛠 사용 방법 (Use Cases)

### 1. 네이버 검색 결과 조회 (Search API)
특정 키워드(예: 남양주 백병원)에 대한 실시간 블로그, 뉴스, 지식iN 반응을 수집합니다. 검색 노출 상태나 경쟁사 현황 파악에 유용합니다.

```powershell
# 블로그 검색 (기본값)
python .agent\skills\naver_search_trend\naver_api.py search --query "남양주 백병원"
# 조회 결과 수 늘리기
python .agent\skills\naver_search_trend\naver_api.py search --query "남양주 백병원 관절" --display 20
# 뉴스 카테고리 검색
python .agent\skills\naver_search_trend\naver_api.py search --query "백병원" --target news
# 카페 침투 (카페 게시글 검색) - 신규 지원
python .agent\skills\naver_search_trend\naver_api.py search --query "남양주 백병원" --target cafearticle
```

### 2. 네이버 검색어 트렌드 조회 (Datalab API)
특정 키워드의 상대적 검색량 변화 추이(최대 100을 기준으로 환산)를 분석하여 시기별 관심도를 파악합니다.

```powershell
# 한 개의 키워드 기본 조회 (최근 30일)
python .agent\skills\naver_search_trend\naver_api.py trend --keywords "남양주 백병원"

# 여러 키워드 비교 (쉼표로 구분) - 최대 5개 그룹
python .agent\skills\naver_search_trend\naver_api.py trend --keywords "남양주 백병원,구리 백병원,다산 정형외과"

# 특정 기간 지정
python .agent\skills\naver_search_trend\naver_api.py trend --keywords "관절 수술" --start "2023-01-01" --end "2023-12-31"
```

## 🧠 에이전트 가이드 (Prompting Guidelines)
*   **분석 모드:** 대표님이 `데이터랩(검색어트렌드)` 조회를 요청했을 때, 단순한 JSON 수치를 반환하지 말고, "가장 검색량이 튀는 날짜", "평균 대비 관심도(ratio) 차이", "키워드 간 상대적 비교 결과"를 정리해서 브리핑하세요.
*   **광고 최적화 조언:** 키워드 조회를 마친 뒤, "A 키워드는 검색량이 높지만 단가 경쟁이 치열할 수 있으므로, B 형태의 세부 키워드로 콘텐츠를 배포하는 것도 제안 드립니다"처럼 통찰력 있는 분석을 제시하세요.
*   **파일 위치:** 이 스크립트는 항상 `.agent\skills\naver_search_trend\naver_api.py` 에 존재합니다.
