# 🪐 Luca Research Automation Agent (루카 연구자동화에이전트)

Luca는 사용자의 백그라운드 환경에서 24시간 자율적으로 동작하며, 다양한 연구, 탐색, 웹 크롤링 및 데이터베이스 연동 자동화를 수행하는 **다목적 AI 에이전트 시스템**입니다. 내부적으로 강력한 LLM과 다양한 스킬(Skill)들이 결합되어 있어, 반복적이고 복잡한 데이터 작업을 인간의 개입 없이 스스로 해결합니다.

## ✨ 주요 특징 (Key Features)
- **자율형 에이전트 아키텍처:** OpenClaw 및 자체 개발 시스템(Dr. Claw 등)을 포크/확장하여 설계된 Zero-Trust 다중 에이전트 체계
- **슈퍼 확장성 (스킬 시스템):** `Skill.md` 형태의 지침서를 기반으로 Supabase, Perplexity, Google Workspace, GitHub, Telegram 등 지속적인 서드파티 확장 지원
- **장기 기억 (Long-term Memory):** 로컬 SQLite 에이전트 기억망 및 Supabase 클라우드(pgvector)를 연계한 RAG 및 온톨로지 학습/추론 기능 탑재
- **텔레그램 기반 모니터링:** 24/7 백그라운드 구동 중 발생하는 로그 및 보고서를 텔레그램 등을 통해 사용자의 모바일로 즉각 전송

## 📁 디렉토리 구조 및 핵심 모듈
- `.agent/skills/` : Luca 에이전트가 직접 참고하고 실행할 수 있는 확정 배포 스킬(Supabase DB 매니저 등) 세트
- `memory_layer/` : 텍스트 기억, 메타데이터 연산 및 벡터 스토어가 결합된 고속 검색 모듈
- `ontology/` : Dr. NDB, Dr. Eye 등 도메인 특화 지식 그래프(Knowledge Graph) 처리 시스템
- `luca_brain.py` / `luca_watchdog.py` : 에이전트 코어 판단 및 백그라운드 데몬 프로세스
- `telegram_bot.py` : 사용자와의 자연어 소통 및 명령어 처리 봇 인터페이스

## 🚀 빠른 시작 (Getting Started)

### 1. 환경 변수 세팅
프로젝트 최상단에 `.env` 파일을 생성하고, 실행에 필요한 각 API 키들을 구성합니다. (절대 Git에 커밋하지 마세요.)
```env
# Example .env config
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_SECRET_KEY=your-secret...
TELEGRAM_BOT_TOKEN=your-token...
```

### 2. 구동 및 데몬 실행
Windows 환경에서 백그라운드 감시 및 에이전트를 가동하려면 루트 폴더의 통합 시작 스크립트를 사용합니다.
```powershell
./start_all_services.bat
# 또는
cscript ./start_unified_hidden.vbs
```

## 🔒 보안 정책
- `.env` 및 `.git` 등 민감 데이터가 포함된 구역은 반드시 로컬 환경에 격리해야 합니다. (`.gitignore` 설정 권장)
- Supabase 등의 Cloud DB 연동 시 반드시 로컬 환경변수의 Key를 로드하여 사용하도록 코드를 설계하십시오.

## 📄 라이선스
해당 프로젝트 내 커스텀 에이전트 스크립트의 권리는 개발자에게 있으며, 결합된 오픈소스 라이브러리는 각각의 라이선스 정책을 따릅니다.
