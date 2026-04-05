# luca연구에이전트 - 프로젝트 지침

## ASMR 메모리 시스템 통합 (Antigravity Integration)

### 개요
이 프로젝트는 Antigravity 에이전트 생태계의 **ASMR(Agentic Search and Memory Retrieval)** 메모리 시스템과 통합되어 있다.
Port 5050 공유 메모리 서버를 통해 장기 기억을 저장/조회하고, ASMR 3인방 병렬 에이전트로 심층 분석을 수행한다.

### 브릿지 CLI 사용법

```bash
# 1. 헬스체크 (서버 + API키 상태)
python shared/claude_memory_bridge.py health

# 2. 빠른 조회 (Port 5050 직접, ASMR 없이)
python shared/claude_memory_bridge.py raw-query "최근 프로젝트 현황"

# 3. ASMR 딥 분석 (Fact + Context + Causal + Arbiter 교차검증)
python shared/claude_memory_bridge.py query "환자 혈당과 식단 관계 분석"

# 4. 메모리 저장
python shared/claude_memory_bridge.py ingest "중요한 발견/결정사항 #태그"

# 5. 세션 로그 관찰 (자동 분석 + ingest)
python shared/claude_memory_bridge.py observe "이번 세션에서 수행한 작업 요약..."

# 6. 온톨로지 탐색 (지식그래프 Edge + Pathfinder)
python shared/claude_memory_bridge.py ontology "Metformin과 신장기능 관계"
```

### Claude Code 행동 규칙

1. **딥 리서치 필요 시**: raw-query로 먼저 빠르게 확인 -> 복잡하면 query로 ASMR 3인방 분석
2. **작업 완료 시**: 중요 결과/발견을 ingest로 공유 메모리에 저장
3. **세션 종료 전**: 주요 작업 내용을 observe로 자동 요약 + 저장
4. **메모리 서버 장애 시**: 즉시 사용자에게 보고, 로컬 auto-memory에 백업 저장
5. **태그 규칙**: ingest 시 #ClaudeCode 태그를 반드시 포함하여 에이전트 식별

### 인프라 정보
- **Port 5050 서버**: PM2 관리 (pm2 start luca-memory-layer)
- **ASMR 코드**: .agents/skills/asmr_memory_system/
- **브릿지**: shared/claude_memory_bridge.py
- **DB**: AIagent_antigravity/services/memory_layer/luca_memory.db (SQLite)
- **LLM**: Gemini 2.5 Flash (ASMR 에이전트용), 환경변수 GEMINI_API_KEY 필요
