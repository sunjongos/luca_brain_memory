---
description: [AI 콜센터] 닥터NDB CRM 통화 기록 듀얼 데이터베이스(Supabase & Google Sheets) 자동화 구축
---

# 🚀 남양주백병원 AI 콜센터 듀얼 DB 자동화 워크플로우

본 워크플로우는 `luca_voice_crm.py` 발신 종료 후 로컬 엑셀(CSV)에만 저장되던 통화 기록(AI 요약본 및 녹음)을 **1단계: 구글 시트(실무자용)**와 **2단계: Supabase(웹서버 클라우드 DB, 정통 SaaS 방식)** 양쪽에 실시간 자동 동기화(Auto-Sync)하는 전산팀 실무 매뉴얼입니다. 최선종 병원장님의 결재 하에 '가장 폼나고 강력한 사내 클라우드 형태'로 시스템을 격상시키기 위해 고안되었습니다.

## 1단계: Google Sheets API 연동 (실무자 즉시 확인용 뷰어)
구글 시트는 원무과 직원들이 즉각적으로 통화 결과를 모니터링할 수 있는 가벼운 프론트엔드 역할을 합니다.

1. **GCP(Google Cloud Platform) 설정:**
   - GCP 콘솔에서 새 프로젝트 생성.
   - `Google Sheets API` 및 `Google Drive API` 사용 설정.
   - **서비스 계정(Service Account)** 생성 후 JSON 키 (`credentials.json`) 발급.
2. **파이썬 라이브러리 설치:**
   ```bash
   pip install gspread oauth2client
   ```
3. **스프레드시트 공유:**
   - 엑셀 열람을 원하는 구글 시트를 만들고, 우측 상단 '공유' 버튼을 눌러 발급된 서비스 계정 이메일(예: `crm-bot@project.iam.gserviceaccount.com`)에 **'편집자'** 권한 부여.
4. **코드 연동:**
   - 파이썬 파일 내에 `gspread`를 활용하여 통화 종료 콜백(Webhook) 콜이 들어오면 새로 생성된 row(전화번호, 요약본 등)를 `.append_row()`로 즉시 삽입.

## 2단계: Supabase (PostgreSQL) 클라우드 DB 연동 (정통 웹앱용)
가장 진보된 오픈소스 클라우드 DB(Firebase의 SQL 버전)인 **Supabase**를 활용하여, 보안 수준을 최상으로 끌어올리고 병원 자체 웹 대시보드 화면(HTML)에 실시간 통계를 쏴주는 코어 백엔드를 구축합니다.

1. **Supabase 프로젝트 생성:**
   - [Supabase.com](https://supabase.com/) 가입 후 `Namyangju Baek Hospital CRM` 신규 프로젝트 생성.
   - 대시보드 ➡️ **Project Settings ➡️ API** 탭에서 `Project URL`과 `anon public API Key` 획득.
2. **DB 테이블(Table) 설계:**
   - SQL Editor에서 아래 명령어로 `crm_logs` 통화 기록 테이블 생성:
     ```sql
     create table public.crm_logs (
       id uuid default gen_random_uuid() primary key,
       call_id text,
       patient_name text,
       phone_number text,
       ai_summary text,
       transcript text,
       recording_url text,
       call_status text,
       created_at timestamp with time zone default timezone('utc'::text, now()) not null
     );
     ```
3. **파이썬 SDK 설치:**
   ```bash
   pip install supabase
   ```
4. **코드 연동 및 보안(`.env`):**
   - 앞서 만든 로컬 `.env` 파일에 <code>SUPABASE_URL="자신의URL"</code>, <code>SUPABASE_KEY="자신의키"</code> 추가.
   - `luca_voice_crm.py` 실행 시 통화가 끝날 때마다 Supabase 테이블에 원격으로 `insert` 함수를 날리도록 백엔드 코딩 구현.

// turbo-all
## 3단계: 즉시 적용 테스트 (실행 명령어)
전산팀은 위 세팅을 마친 뒤 터미널에서 아래 명령을 즉시 실행하여 실전 콜 및 듀얼 DB 적재 테스트를 진행하십시오.

```bash
# 1. 필요 패키지 일괄 설치
pip install gspread oauth2client supabase

# 2. 업데이트된 CRM 듀얼 파이썬 엔진 구동
python luca_voice_crm.py
```
