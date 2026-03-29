---
name: Local SQLite Database Manager
description: 에이전트가 단독으로 사용하는 초경량 로컬 임시 데이터베이스(SQLite) 구축 및 활용 스킬
---

# 🗄️ Local SQLite DB Manager Skill

이 스킬은 Luca가 무거운 클라우드 DB(Supabase)나 글로벌 공유 메모리 서버(Port 5050)를 거치지 않고, **특정 작업 전용으로 가볍고 빠른 로컬 파일형 데이터베이스**를 스스로 구축해야 할 때 사용하는 지침서입니다.

## 💡 SQLite란 무엇인가요?
SQLite는 별도의 복잡한 서버 설치나 로그인 계정 없이, **단순한 `.db` 파일 하나**가 데이터베이스 전체 역할을 하는 초경량 DB 엔진입니다.
- 파이썬에 기본으로 내장되어 있어 별도 설치(`pip install` 등)가 필요 없습니다.
- 웹 크롤링 중간 데이터, 일회성 분석 결과, 혹은 에이전트 혼자만 기억하면 되는 임시 상태(Local State)를 저장할 때 가장 완벽합니다.

## 💡 언제 사용하나요?
- "크롤링한 임시 데이터를 로컬 DB에 가볍게 저장해둬"
- "이번 분석 작업만 쓸 일회성 DB(`temp_research.db`)를 하나 만들어"
- Port 5050(장기 공유 메모리)에 넣기에는 너무 지저분한 중간/로그성 데이터를 보관할 때

## 🛠️ Python 연동 레퍼런스 가이드

에이전트가 단독 로컬 DB를 작성해야 할 때는 아래의 기본 내장 `sqlite3` 라이브러리를 활용합니다.

```python
import sqlite3
import os

# 1. 특정 작업을 위한 임시 SQLite DB 파일 생성 (실행 폴더 내에 생성됨)
DB_PATH = "temp_agent_work.db"

def init_local_db():
    # 연결 시 파일이 없으면 자동으로 새로 생성됩니다.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. 테이블 생성 (예: 크롤링 뉴스 임시 보관함)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# 3. 데이터 삽입 및 조회 예시
def save_temp_data(title: str, link: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO temp_news (title, link) VALUES (?, ?)", (title, link))
    conn.commit()
    conn.close()

def get_temp_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_news ORDER BY extracted_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
```

## 🚨 에이전트 주의사항
1. **공유 메모리와의 분리:** 이 스킬은 철저히 '단일 에이전트의 임시/로컬 작업'에만 사용하십시오. 모든 에이전트가 공유해야 하는 핵심 지식은 여전히 5050 포트를 사용하는 장기 메모리(Memory Layer)나 클라우드(Supabase)로 전송해야 합니다.
2. **파일 경로 관리:** 임시 `.db` 파일은 충돌 방지를 위해 고유한 작업명 기반으로 생성하고, 작업이 끝난 후 더 이상 필요 없는 DB 파일은 삭제하거나 정리하도록 설계하세요.
