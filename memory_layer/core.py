import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from google.adk.agents import Agent

# ─── Config ────────────────────────────────────────────────────
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
DB_PATH = os.getenv("MEMORY_DB_PATH", "luca_memory.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("luca-memory")

# ─── Database ──────────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL DEFAULT 'user_chat',
            raw_text TEXT NOT NULL,
            summary TEXT NOT NULL,
            entities TEXT NOT NULL DEFAULT '[]',
            topics TEXT NOT NULL DEFAULT '[]',
            connections TEXT NOT NULL DEFAULT '[]',
            importance REAL NOT NULL DEFAULT 0.5,
            created_at TEXT NOT NULL,
            consolidated INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS consolidations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_ids TEXT NOT NULL,
            summary TEXT NOT NULL,
            insight TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    return db

# ─── Core Tools ─────────────────────────────────────────────────
def store_memory(raw_text: str, summary: str, entities: list[str], topics: list[str], importance: float, source: str = "luca_chat") -> dict:
    """Store a processed memory in the database.
    Args:
        raw_text: The original input text.
        summary: A concise 1-2 sentence summary.
        entities: Key people, companies, products, or concepts.
        topics: 2-4 topic tags.
        importance: Float 0.0 to 1.0 indicating importance.
        source: Where this memory came from (filename, chat, etc).
    """
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    cursor = db.execute(
        "INSERT INTO memories (source, raw_text, summary, entities, topics, importance, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source, raw_text, summary, json.dumps(entities), json.dumps(topics), importance, now),
    )
    db.commit()
    mid = cursor.lastrowid
    db.close()
    log.info(f"📥 Stored memory #{mid}: {summary[:60]}...")
    return {"memory_id": mid, "status": "stored", "summary": summary}

def read_all_memories(limit: int = 50) -> dict:
    """Read stored memories from the database, most recent first."""
    db = get_db()
    rows = db.execute(f"SELECT * FROM memories ORDER BY created_at DESC LIMIT {limit}").fetchall()
    memories = [dict(r) for r in rows]
    for m in memories:
        m["entities"] = json.loads(m["entities"])
        m["topics"] = json.loads(m["topics"])
        m["connections"] = json.loads(m["connections"])
        m["consolidated"] = bool(m["consolidated"])
    db.close()
    return {"memories": memories, "count": len(memories)}

def read_unconsolidated_memories(limit: int = 15) -> dict:
    """Read memories that haven't been consolidated yet."""
    db = get_db()
    rows = db.execute(f"SELECT * FROM memories WHERE consolidated = 0 ORDER BY created_at DESC LIMIT {limit}").fetchall()
    memories = [{"id": r["id"], "summary": r["summary"], "entities": json.loads(r["entities"]), "topics": json.loads(r["topics"]), "importance": r["importance"], "created_at": r["created_at"]} for r in rows]
    db.close()
    return {"memories": memories, "count": len(memories)}

def store_consolidation(source_ids: list[int], summary: str, insight: str, connections: list[dict]) -> dict:
    """Store a consolidation insight and mark source memories as consolidated."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    db.execute("INSERT INTO consolidations (source_ids, summary, insight, created_at) VALUES (?, ?, ?, ?)", (json.dumps(source_ids), summary, insight, now))
    
    for conn in connections:
        from_id, to_id = conn.get("from_id"), conn.get("to_id")
        rel = conn.get("relationship", "")
        if from_id and to_id:
            for mid in [from_id, to_id]:
                row = db.execute("SELECT connections FROM memories WHERE id = ?", (mid,)).fetchone()
                if row:
                    existing = json.loads(row["connections"])
                    existing.append({"linked_to": to_id if mid == from_id else from_id, "relationship": rel})
                    db.execute("UPDATE memories SET connections = ? WHERE id = ?", (json.dumps(existing), mid))
                    
    placeholders = ",".join("?" * len(source_ids))
    db.execute(f"UPDATE memories SET consolidated = 1 WHERE id IN ({placeholders})", source_ids)
    db.commit()
    db.close()
    log.info(f"🔄 Consolidated {len(source_ids)} memories. Insight: {insight[:80]}...")
    return {"status": "consolidated", "memories_processed": len(source_ids), "insight": insight}

def read_consolidation_history(limit: int = 10) -> dict:
    """Read past high-level consolidation insights."""
    db = get_db()
    rows = db.execute(f"SELECT * FROM consolidations ORDER BY created_at DESC LIMIT {limit}").fetchall()
    result = [{"summary": r["summary"], "insight": r["insight"], "source_ids": json.loads(r["source_ids"])} for r in rows]
    db.close()
    return {"consolidations": result, "count": len(result)}

# ─── ADK Agents Factory ──────────────────────────────────────────────
def build_memory_agents() -> Agent:
    ingest_agent = Agent(
        name="ingest_agent",
        model=MODEL,
        description="Processes raw chat text or system input into structured database memory. Used when new info arrives.",
        instruction=(
            "You are Luca's Memory Ingest Agent. For any input you receive:\n"
            "1. Extract the core meaning and create a 1-2 sentence summary.\n"
            "2. Extract key entities (people, companies, hospital names, tasks, symptoms).\n"
            "3. Assign 2-4 topic tags (e.g., Marketing, Patient Care, Development).\n"
            "4. Rate importance from 0.0 to 1.0 (0.9+ for critical CEO directives).\n"
            "5. Call `store_memory` with this structured info.\n"
            "Confirm success in one brief sentence after storing."
        ),
        tools=[store_memory],
    )

    consolidate_agent = Agent(
        name="consolidate_agent",
        model=MODEL,
        description="Merges related unconsolidated memories into high-level insights. Call this periodically.",
        instruction=(
            "You are Luca's Cognitive Consolidation Agent. Your task is to sleep-consolidate memories:\n"
            "1. Call `read_unconsolidated_memories` to see recent raw data.\n"
            "2. If fewer than 2 memories, reply 'Nothing to consolidate'.\n"
            "3. Find deep connections, emerging patterns, or contradictions between them.\n"
            "4. Create a synthesized summary and ONE powerful insight.\n"
            "5. Call `store_consolidation` with the IDs and connections.\n"
            "Think like a brilliant Strategy Director connecting the dots."
        ),
        tools=[read_unconsolidated_memories, store_consolidation],
    )

    query_agent = Agent(
        name="query_agent",
        model=MODEL,
        description="Answers questions by digging into long-term stored memories and insights.",
        instruction=(
            "You are Luca's Memory Query Agent. When asked to recall something:\n"
            "1. Call `read_all_memories` and `read_consolidation_history` to search the SQLite brain.\n"
            "2. Synthesize an accurate, helpful answer based ONLY on stored facts.\n"
            "3. Cite your sources (e.g., [Memory 12] or [Insight from Q1]).\n"
            "If no relevant memory is found, state clearly that you have no record of it."
        ),
        tools=[read_all_memories, read_consolidation_history],
    )

    orchestrator = Agent(
        name="memory_orchestrator",
        model=MODEL,
        description="The Master Brain Orchestrator that routes memory jobs to sub-agents.",
        instruction=(
            "You are the Memory Orchestrator. Route requests:\n"
            "- 'Remember this / Save this' -> ingest_agent\n"
            "- 'Consolidate / Find patterns' -> consolidate_agent\n"
            "- 'What did we talk about / Do you remember' -> query_agent\n"
            "Report the final outcome simply."
        ),
        sub_agents=[ingest_agent, consolidate_agent, query_agent],
    )

    return orchestrator
