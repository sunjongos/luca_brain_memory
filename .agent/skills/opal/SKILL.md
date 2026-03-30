---
name: Opal Security MCP — AI 에이전트 권한 관리
description: Opal Security의 MCP 서버를 활용하여 AI 에이전트의 접근 권한을 자동 관리하고, 보안 컴플라이언스를 유지하는 스킬입니다.
---

# 🔐 Opal Security MCP — AI 에이전트 권한 관리

AI 에이전트의 **접근 권한(Access)을 중앙 통제**하는 보안 스킬.
누가 어디에 접근할 수 있는지를 Luca가 자동으로 관리합니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| **JIT 권한 요청** | 필요한 순간에만 접근 권한 자동 부여 |
| **사용자 관리** | 리소스/그룹 접근 추가·제거·수정 |
| **감사 로그** | 접근 이력 조회 및 이상 감지 |
| **자동 권한 회수** | 미사용 권한 자동 정리 |

## Claude MCP 설정

`claude.json`에 추가:
```json
{
  "mcpServers": {
    "opal": {
      "command": "npx",
      "args": ["-y", "@opal-security/mcp-server"],
      "env": { "OPAL_API_TOKEN": "your_opal_token" }
    }
  }
}
```

`.env`에 추가:
```
OPAL_API_TOKEN=your_opal_api_token
```

API 토큰 발급: https://app.opal.dev → Settings → API Tokens

## Luca 활용 (Human-in-the-Loop 필수)

```
대표님: "A 직원 Drive 접근 제거해줘"
Luca:   "✅ 확인해 주시면 Opal MCP로 즉시 처리하겠습니다!"
대표님: "응"
Luca:   → 권한 제거 실행 → 감사 로그 자동 저장
```

🔗 공식 문서: https://docs.opal.dev/reference/mcp
