# 🗄️ Supabase Database Manager Skill (for AI Agents)

AI 에이전트(Luca)가 클라우드 데이터베이스(Supabase)를 자율적으로 연동, 제어 및 관리할 수 있도록 설계된 스킬 지침서(Skill Document)입니다. 

이 스킬을 장착한 AI 에이전트는 다음 능력을 갖게 됩니다.
1. 사용자의 자연어 지시("우리 작업 내용 DB 만들어서 관리할까?")에 따라 즉각적인 **Supabase 연동 코드(Python 등) 및 스키마 설계**
2. RAG(검색 증강 생성) 또는 에이전트 다중 협업 처리를 위한 **pgvector 기반 클라우드 DB 연동**
3. CRM 로그(`crm_logs`) 등 핵심 데이터의 **실시간(Real-time) 저장 및 호출 아키텍처 구축**

## 🚀 적용 방법 (Setup)

1. 본 레지스토리의 파일들을 에이전트 스킬 디렉토리(`.agent/skills/supabase_integration/`)로 복사합니다.
2. 로컬(또는 프로덕션) 시스템 최상단에 `.env` 파일을 만들고 아래 코드를 기재합니다 (실제 발급받은 API 키 사용. **보안 유지 필수**).
   ```env
   # .env
   SUPABASE_URL=https://<your-project-id>.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SECRET_KEY=your-service-role-secret-key
   ```
3. 에이전트에게 "Supabase에 새로운 테이블 연동해줘" 등의 관련 명령을 내립니다.
4. 에이전트가 알아서 `.env`를 파싱하여 환경 변수(`os.environ`)에 기반한 접속 코드를 작성해 줍니다.

## ⚠️ 보안 주의 (Security Warning)
- 이 레포지토리에 코드를 커밋/푸시할 때 **절대 `SKILL.md`나 스크립트 내부에 실제 API 키를 하드코딩하지 마십시오.** 
- `SUPABASE_SECRET_KEY` (Service Role Key)는 RLS(Row Level Security)를 포함한 데이터베이스의 모든 규칙을 우회할 수 있는 최고 관리자 권한을 지닙니다. 따라서 사용자가 볼 수 있는 프론트엔드 코드(React 등)에 절대 노출시켜서는 안 되며 백엔드 연동 전용으로만 사용해야 합니다.

## 📄 라이선스
MIT License
