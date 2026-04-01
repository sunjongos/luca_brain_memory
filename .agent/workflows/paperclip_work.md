---
description: paperclip 작업하자 - AI agent 기반의 회사 조직(Company) 메타포로 업무 오케스트레이션을 수행합니다.
---

# Paperclip 기반 에이전트 회사 시스템 가동

본 워크플로우는 사용자가 "루카야. paperclip 작업하자"라고 지시할 시 구동되며, Paperclip의 대시보드 서버를 띄워 자율형 AI 에이전트 회사 시스템을 실행합니다.

> 🛠️ **로그인 기반 인증 사용 (Login Auth Mode)**
> 저희는 Claude Max, Google Ultra, ChatGPT Pro 등 프리미엄 계정을 이미 구독하고 있으므로, 별도의 API Key를 연동하지 않고 "로그인 세션(OAuth / Cookie Session 등)"을 공유하는 로컬 Agent 어댑터(예: Claude Code 로그인 세션, 브라우저 자동화 봇)만 Paperclip에 연결(Hire)하여 운용하도록 설정됩니다. 이렇게 하여 추가적인 API 토큰 과금을 방지합니다.

## 1. Paperclip 오케스트레이션 서버 실행
아래 스크립트를 통해 백그라운드에서 Paperclip 서버(데이터베이스, Node.js API, React UI)를 기동합니다.

// turbo
```powershell
Write-Host "[로딩중] Paperclip 오케스트레이션 서버 환경을 시작합니다..."
$dir = "c:\Users\sunjo\Desktop\luca 연구자동화에이전트\paperclip"
Set-Location -Path $dir

# 서버가 이미 떠있는지 확인 (기본 포트 3100)
$port = 3100
$connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue

if ($connection.TcpTestSucceeded) {
    Write-Host "[완료] 이미 Paperclip 대시보드가 구동 중입니다. (포트: $port)"
} else {
    Write-Host "[시작] pnpm dev 실행을 통해 Paperclip API 및 UI 서버를 실행합니다..."
    Start-Process -NoNewWindow -FilePath "pnpm" -ArgumentList "dev"
    Start-Sleep -Seconds 10
    Write-Host "[완료] Paperclip 서버 구동이 완료되었습니다."
}
```

## 2. 대시보드 열기 및 CEO 모드 전환
Paperclip UI를 브라우저로 띄워서, 대표님(사용자)이 CEO 단에서 직접 회사의 목표(Goal)를 정의하고 조직도를 구성하게끔 안내합니다.

// turbo
```powershell
Write-Host "[로딩중] Paperclip 화면을 브라우저에 띄웁니다..."
Start-Process "http://localhost:3100"
Write-Host "[완료] Paperclip 접속 완료! 이제부터 '루카'도 Paperclip의 등록 직원(agent)으로서 지시에 대기하겠습니다."
```

## 3. 루카의 동작 모드
이제 화면을 보면서 대표님이 **새로운 Company 및 Project를 생성**하고, 구글/클로드 로그인 세션을 갖춘 로컬 에이전트들을 배정하여 작업을 지시해주시면 됩니다!
과금 없이 에이전트끼리 자율협업하는 과정을 지켜보실 수 있습니다.
