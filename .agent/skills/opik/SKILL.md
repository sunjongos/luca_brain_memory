---
name: Opal Security MCP — AI 에이전트 권한 관리
description: Opal Security의 MCP 서버를 활용하여 AI 에이전트의 접근 권한을 자동 관리하고, 보안 컴플라이언스를 유지하는 스킬입니다.
---

# 🔐 Opal Security MCP — AI 에이전트 권한 관리

Luca가 기업 시스템의 **접근 권한(Access)을 자동 관리**하는 보안 스킬입니다.
AI 에이전트가 폭발적으로 늘어나는 시대에, Opal MCP는 **어떤 에이전트가 어디에 접근할 수 있는지**를 중앙 통제합니다.

## 📌 Opal Security란?
- **Non-Human Identity (NHI) 관리** 전문 플랫폼
- AI 에이전트의 권한을 **Just-In-Time (JIT) 방식**으로 제공
- 불필요한 권한을 자동 회수하여 보안 위협 최소화
- MCP 서버를 통해 AI 에이전트가 자신의 권한을 직접 요청/관리

## 🛠️ 주요 기능

| 기능 | 설명 |
|------|------|
| **사용자 접근 관리** | 리소스/그룹에 사용자 추가·삭제·권한 수정 |
| **접근 감사(Audit)** | 이벤트 로그·접근 이력 조회 및 감시 |
| **JIT 접근 요청** | AI 에이전트가 필요한 순간에만 권한 요청 |
| **접근 요청 검토** | 승인 대기 중인 요청 확인 및 처리 |

## 🔧 설치 방법

### Claude Desktop MCP 설정

`claude_desktop_config.json` 또는 `claude.json`에 추가:
```json
{
  "mcpServers": {
    "opal": {
      "command": "npx",
      "args": ["-y", "@opal-security/mcp-server"],
      "env": {
        "OPAL_API_TOKEN": "your_opal_api_token"
      }
    }
  }
}
```

### API 토큰 발급
1. https://app.opal.dev 접속
2. Settings → API Tokens → New Token 생성
3. `.env`에 추가:
```
OPAL_API_TOKEN=your_opal_api_token
```

## 💡 Luca 활용 시나리오

### Human-in-the-Loop 연동 예시
```
대표님: "A 직원의 Google Drive 접근 권한 제거해줘"
Luca:   "다음 작업 진행할까요?
         - 대상: A 직원
         - 작업: Google Drive 접근 권한 제거
         ✅ 확인해 주시면 Opal MCP로 즉시 처리하겠습니다!"
대표님: "응"
Luca:   → Opal MCP API 호출 → 권한 제거 → 감사 로그 저장
```

### 자동 감시 시나리오
- 비정상 접근 패턴 감지 시 대표님께 즉시 알림
- 미사용 권한 주기적 검토 및 정리 보고

## 🔗 참고
- Opal 공식 사이트: https://opal.dev
- MCP 서버 문서: https://docs.opal.dev/reference/mcp
