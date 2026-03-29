---
name: Supabase Database Manager
description: Supabase 클라우드 DB 연동 및 확장이 가능하도록 지원하는 베이스 스킬 (API 키는 .env를 통해 주입)
---

# 🗄️ Supabase Database Manager Skill

이 스킬은 Luca가 Supabase 클라우드 데이터베이스 인프라를 이해하고, 사용자가 원할 때 즉각적으로 연동 코드(Python/JS 등)를 작성하여 DB를 구축하거나 관리할 수 있도록 안내하는 지침서입니다.

## 💡 언제 사용하나요?
- "우리 작업 내용 DB 만들어서 관리할까?" 라는 요청이 올 때
- "Supabase에 새로운 테이블 연동해줘"
- CRM 로그 등의 데이터를 클라우드에 적재/조회할 때
- 로컬 DB(SQLite)의 용량/공유 한계를 넘어 클라우드 스토리지 리소스가 필요할 때

## 🔐 인프라 및 보안 정보
**중요:** 이 스킬은 깃허브 등 외부에 공개될 수 있으므로, 실제 접속 정보는 모두 시스템 로컬 환경 변수(`.env`)에 안전하게 격리되어 관리됩니다. 에이전트가 코드를 작성할 땐 **반드시 `os.getenv()` 등을 통해 `.env`에서 키를 불러오도록 스크립트를 작성하세요.**

`.env` 설정 필수 변수명:
- `SUPABASE_URL`: 프로젝트 API Endpoint 주소
- `SUPABASE_ANON_KEY`: 클라이언트 노출 가능 Public 키
- `SUPABASE_SECRET_KEY`: 최고 관리자의 마스터 키 (모든 권한 무시 및 완전 제어)

## 📊 주력 데이터 테이블 (Schema 예시)

### `public.crm_logs`
- 콜 단위별 고유 ID
- 수신자 이름
- AI 1줄 요약
- STT 원문록
- 실제 음성 WAV 재생 링크
- 통화 성공 여부

*상기 테이블 구조처럼, 지정된 규격에 맞춰 데이터를 Supabase에 실시간 보관합니다.*

## 🛠️ Python 연동 레퍼런스 가이드

에이전트가 DB 접근 코드를 작성해야 할 때는 아래의 `supabase-py` 표준 패턴을 준수하세요.

```python
# 필수 패키지 설치: pip install supabase python-dotenv

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# .env 환경 변수 불러오기
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
# 백엔드 스크립트/보안 구역에서는 Secret Key 사용, 웹 프론트에서는 Anon Key 사용
key: str = os.environ.get("SUPABASE_SECRET_KEY") 

if not url or not key:
    raise ValueError("Supabase 환경변수가 .env 파일에 설정되지 않았습니다.")

supabase: Client = create_client(url, key)

# 데이터 삽입 예시 (Insert)
def insert_call_log(data: dict):
    # data 구조: {"receiver_name": "홍길동", "ai_summary": "...", "status": "성공"}
    response = supabase.table("crm_logs").insert(data).execute()
    return response
```

## 🚨 에이전트 주의사항 (보안 가이드라인)
1. Supabase 접속 코드를 짤 때는 **절대 Secret Key를 웹 브라우저(React/Vue 등) 코드나 Git 저장소에 하드코딩해서는 안 됩니다.**
2. 에이전트 전용 백엔드 서버 스크립트나 안전한 클라우드 함수 내에서만 Secret Key를 취급하도록 통제하십시오.
