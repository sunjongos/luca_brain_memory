---
id: 6
source: luca_chat
date: 2026-03-11T14:45:00.692116+00:00
importance: 0.95
tags: [raw, memory, luca_chat]
---

# Memory 6: User mandates ADK persistent memory server (port 5050) as the authoritative source of truth for all tools, replacing MEMORY.md/LanceDB, and confirming successful tests for Perplexity, Google Workspace CLI, and ACP.

**Date**: 2026-03-11T14:45:00.692116+00:00
**Importance**: 0.95
**Tags**: #Infrastructure #Memory_Management #System_Configuration

## Linked Concepts
[[ADK persistent memory server]], [[Perplexity]], [[Google Workspace]], [[ACP]], [[Codex]], [[Claude Code]], [[OpenClaw]], [[antigravity]], [[Infrastructure]], [[Memory Management]], [[System Configuration]]

## 🔗 Causal Links (인과관계)
현재 기록된 인과관계가 없습니다.

## Raw Context
2026-03-11 day-end summary: User preference is to store an AutoMemory-style progress summary at the end of each day into the ADK persistent memory server on port 5050 instead of local files. Important completed work today: Perplexity deep-search path configured and tested; Google Workspace moved to CLI flow and basic tests passed; ACP repaired and verified end-to-end for both Codex and Claude Code, including actual file/code edits and execution checks; OpenClaw, Claude Code, and antigravity are intended to share memory through the ADK persistent memory layer on port 5050 as the single source of truth. Operational rule: do not treat MEMORY.md or LanceDB as the authoritative long-term memory when ADK memory_layer is available.
