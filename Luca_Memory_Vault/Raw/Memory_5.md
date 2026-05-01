---
id: 5
source: luca_chat
date: 2026-03-11T14:44:14.158127+00:00
importance: 0.95
tags: [raw, memory, luca_chat]
---

# Memory 5: User directed that all end-of-day summaries be stored in the ADK persistent memory server (port 5050) as the authoritative source of truth, moving away from local files like MEMORY.md or LanceDB. Several core integrations (Perplexity, Google Workspace, ACP) were successfully updated or repaired to align with this unified memory architecture.

**Date**: 2026-03-11T14:44:14.158127+00:00
**Importance**: 0.95
**Tags**: #Operational_Policy #Infrastructure #System_Architecture

## Linked Concepts
[[ADK persistent memory server]], [[Perplexity]], [[Google Workspace]], [[ACP]], [[Codex]], [[Claude Code]], [[OpenClaw]], [[antigravity]], [[Operational Policy]], [[Infrastructure]], [[System Architecture]]

## 🔗 Causal Links (인과관계)
현재 기록된 인과관계가 없습니다.

## Raw Context
[2026-03-11 day-end summary] User preference: at end of day, store an AutoMemory-style progress summary into the ADK persistent memory server on port 5050 instead of local files. Important completed work today: Perplexity deep-search path configured and tested; Google Workspace moved from MCP-style usage to CLI and basic tests passed; ACP repaired and verified end-to-end for both Codex and Claude Code, including actual file/code edits and execution checks; OpenClaw, Claude Code, and antigravity are intended to share memory through the ADK persistent memory layer on port 5050 as the single source of truth. Operational rule: do not treat MEMORY.md or LanceDB as the authoritative long-term memory when ADK memory_layer is available.
