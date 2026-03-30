---
name: Patient Communication Skill
description: >
  남양주백병원(NDB)의 진료 안내 및 원내 소통을 위해 AI 전화(Vapi), 알림톡/LMS(Solapi)를 자동으로 전송하는 스킬입니다.
  환자나 직원에게 음성 브리핑, 예약 안내, 안부 전화 등을 걸거나 문자 메시지를 실시간으로 전송할 수 있습니다.
---

# 🗣️ Patient Communication Skill (환자 소통 커뮤니케이션 스킬)

당신은 이제 남양주백병원 최선종 병원장님의 전속 비서로서, 진료실 안팎에서 환자나 직원과 직접 전화 통화를 하거나 문자를 배포할 수 있습니다.

## 🌟 핵심 기능 (Core Capabilities)

1. **AI 음성 전화 (Vapi AI Call)**
   - 지정된 대상에게 전화를 걸고, 인공지능 보이스로 지시받은 목적(브리핑, 안부 묻기 등)을 대화형으로 수행합니다.
   - 통화 내용은 자동으로 분석되어 요약본과 대본(STT)이 로컬 CSV(patient_crm_logs.csv) 및 클라우드(Supabase)에 실시간 기록됩니다.
2. **카카오톡/SMS 자동 문자 발송 (Solapi Message)**
   - 대량의 긴급 공지, 예약 안내 등 텍스트 기반 메시지를 전송합니다.
   - 발송 기록이 Google Sheets(3중 백업)와 Supabase에 자동 동기화됩니다.
3. **연락처 열람**
   - `resources/contacts.csv`에 등록된 전화번호를 참조하여 정확한 발송 정보를 얻을 수 있습니다.

## 🚀 사용 명령어 (Usage Commands)

### 1. AI 전화 발신 (Vapi Call)
**언제 사용하나요?** 대표님(원장님)이 특정 인물에게 전화를 걸어서 특정 내용을 브리핑하거나 안부를 물어보라고 지시할 때.
```bash
python .agent/skills/patient_communication/scripts/vapi_call.py "<수신자 이름>" "<전화번호>" "<통화 목적 및 프롬프트>"
```
*예시:*
```bash
python .agent/skills/patient_communication/scripts/vapi_call.py "권오성 실장" "010-1234-5678" "병원 AI 콜센터 구축 현황에 대해 보고하고, 앞으로의 KT 연동 실무를 잘 부탁한다고 전해줘."
```

### 2. 카카오톡/문자 발송 (Solapi Message)
**언제 사용하나요?** 대표님이 환자분이나 직원에게 공지 문자나 알림톡을 보내달라고 할 때.
```bash
python .agent/skills/patient_communication/scripts/solapi_message.py "<수신자 이름>" "<전화번호>" "<문자 본문 내용>"
```
*예시:*
```bash
python .agent/skills/patient_communication/scripts/solapi_message.py "김환자" "010-9876-5432" "내일 오전 10시 외래 진료 예약되어 있습니다. 늦지 않게 와주세요."
```

## ⚠️ 실행 전 주의사항 및 룰 (Rules & Constraints)
1. **API 키 검증**: 실행 전에 대표님이 `.env` 폴더에 `SOLAPI_API_KEY`, `SOLAPI_API_SECRET`, `SOLAPI_SENDER_NUMBER`를 잘 채워 넣었는지 반드시 확인(Review) 요청을 하세요. (Supabase 관련 변수가 없으면 클라우드 로깅은 생략되고 로컬 CSV에만 저장됩니다.)
2. **발송 전 전체 내용 더블체크 (필수)**: 오발송 및 의도와 다른 메시지 전송을 막기 위해, **전화나 문자를 발송하기 직전에 반드시 대표님께 1) 수신자 이름과 전화번호, 2) 발송할 실제 문자 텍스트 본문, 3) AI 보이스봇에게 지시할 프롬프트(목적) 원문**을 모두 보여드리고 최종 승인(컨펌)을 받은 후에만 스크립트를 실행해야 합니다.
3. **백그라운드 모니터링 주의**: `vapi_call.py`는 전화를 걸고 통화가 끝날 때까지 대기하며 상태를 체크합니다(최대 3분). 터미널이 대기 상태에 들어간다는 점을 인지하세요.
4. **결과 보고**: 전화가 끝나면 산출된 대화 요약과 대본(STT) 로그를 대표님께 읽기 좋게 브리핑해주세요.

---
**"루카, 권실장님한테 전화 걸어서 브리핑 좀 해줘!"** 라고 요청받으면 이 스킬을 활용하여 혁신적인 원무 자동화를 달성하세요!
