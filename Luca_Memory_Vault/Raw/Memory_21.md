---
id: 21
source: luca_chat
date: 2026-03-24T13:42:24.768438+00:00
importance: 0.8
tags: [raw, memory, luca_chat]
---

# Memory 21: Unified auto-start configuration for the memory server and Telegram bot was implemented using a batch file and VBS script, including a fix for a character encoding bug.

**Date**: 2026-03-24T13:42:24.768438+00:00
**Importance**: 0.8
**Tags**: #Development #Infrastructure #Automation

## Linked Concepts
[[memory server]], [[Telegram bot]], [[memory_server.py]], [[start_all_services.bat]], [[Luca_AllServices_AutoStart.vbs]], [[Development]], [[Infrastructure]], [[Automation]]

## 🔗 Causal Links (인과관계)
현재 기록된 인과관계가 없습니다.

## Raw Context
[2026-03-24] Memory server(5050) + Telegram bot unified auto-start built. Fixed memory_server.py cp949 encoding bug. Created start_all_services.bat launcher (memory server -> wait 5050 -> watchdog+bot). Registered Luca_AllServices_AutoStart.vbs in startup folder. Removed old duplicate startup entries.
