---
description: 네이버 검색광고 최적화 - 현재 광고 중인 20개 키워드를 진단하고, 전환율 높은 세부 키워드 20개를 추천하여 월 250만원 예산의 ROI를 극대화합니다
---

# 네이버 검색광고 최적화 워크플로우

## 목적
남양주 백병원의 **월 250만 원 네이버 검색광고 예산**의 낭비를 차단하고,  
환자 전환율이 높은 **세부(롱테일) 키워드로 교체**하여 비용 대비 효과(ROI)를 극대화합니다.  
광고 클릭 시 랜딩 URL: **https://www.baekhospital.co.kr**

---

## 필수 입력 정보
워크플로우 실행 전, 사용자로부터 다음 정보를 수집하십시오.
1. **현재 광고 중인 키워드 20개** (쉼표로 구분)
2. **분석 기간** (기본값: 최근 12개월)

입력 예시:
```
남양주정형외과, 남양주신경과, 남양주내과, 남양주백병원, 남양주건강검진, 
남양주디스크, 남양주척추, 남양주도수치료, 남양주재활치료, 남양주두통,
남양주어지럼증, 남양주손발저림, 남양주뇌MRI, 남양주관절, 남양주무릎통증,
남양주허리통증, 남양주목디스크, 남양주체형교정, 남양주야간진료, 남양주종합병원
```

---

## STEP 1: 현재 키워드 성과 분석 (경쟁도 및 가성비 진단)

```powershell
python "C:\Users\USER\.claude\skills\naver-ads-optimizer\scripts\optimize_keywords.py" `
  --client_id "q8Y3EuiGXRYGjemuDFYv" `
  --client_secret "HLddlF0Qc1" `
  --mode analyze `
  --keywords "사용자가_입력한_키워드_20개_쉼표구분" `
  --output_dir "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\naver검색어_광고분석"
```

결과 파일: `analysis_result.json`

### 해석 기준
| 등급 | 가성비 점수 | 의미 | 조치 |
|------|------------|------|------|
| A | 80~100점 | 최우선 추천 (경쟁 낮고 안정적) | 입찰가 상향 |
| B | 60~79점 | 유지 권장 | 현행 유지 |
| C | 40~59점 | 재검토 필요 (경쟁 중간) | 모니터링 |
| D | 0~39점 | 교체 대상 (단가 높고 전환 낮음) | **즉시 교체** |

---

## STEP 2: AI 롱테일 키워드 발굴 및 검증

STEP 1에서 D등급 키워드를 파악한 후, AI가 대체 키워드를 생성하고 DataLab으로 검증합니다.

**롱테일 키워드 발굴 원칙:**
- 증상 중심: "남양주 다리저림", "구리 손목통증", "평내호평 두통병원"
- 치료/시술 중심: "남양주 도수치료 실비", "남양주 하지정맥류 수술"
- 지역 확장: 구리, 하남, 가평, 포천 등 인접 지역 포함
- 계절/이슈: "여름 냉방병 남양주", "환절기 어지럼증 병원"

```powershell
python "C:\Users\USER\.claude\skills\naver-ads-optimizer\scripts\optimize_keywords.py" `
  --client_id "q8Y3EuiGXRYGjemuDFYv" `
  --client_secret "HLddlF0Qc1" `
  --mode recommend `
  --keywords "AI가_발굴한_후보_키워드_20개" `
  --output_dir "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\naver검색어_광고분석"
```

결과 파일: `recommend_result.json`

---

## STEP 3: HTML 최적화 리포트 생성

```powershell
python "C:\Users\USER\.claude\skills\naver-ads-optimizer\scripts\generate_report.py" `
  --analysis_file "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\naver검색어_광고분석\analysis_result.json" `
  --recommend_file "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\naver검색어_광고분석\recommend_result.json" `
  --budget 2500000 `
  --site_url "https://www.baekhospital.co.kr" `
  --output_dir "C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\naver검색어_광고분석"
```

결과 파일: `검색광고_최적화리포트_YYYYMMDD.html`

---

## STEP 4: 최종 보고 (사용자에게 전달)

리포트 파일 경로를 사용자에게 안내하고, 주요 인사이트를 요약 보고합니다.
1. 교체 권장 키워드 목록 및 절감 예상 금액
2. AI 추천 롱테일 키워드 Top 10
3. 다음 최적화 일정 안내 (다음달 1일)
