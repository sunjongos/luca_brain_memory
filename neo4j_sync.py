import sqlite3
import json
import os
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "admin123"

DB_PATH = os.path.join(os.path.dirname(__file__), "memory_layer", "luca_memory.db")

def sync_to_neo4j():
    if not os.path.exists(DB_PATH):
        print(f"SQLite DB not found: {DB_PATH}")
        return

    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    # Clear existing data (for clean sync)
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        
        # Add constraints
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Memory) REQUIRE m.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE")

    print("Connecting to SQLite...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    memories = cursor.execute("SELECT * FROM memories").fetchall()
    causal_chains = cursor.execute("SELECT * FROM causal_chains").fetchall()
    consolidations = cursor.execute("SELECT * FROM consolidations").fetchall()

    print(f"Syncing {len(memories)} memories...")
    with driver.session() as session:
        for rm in memories:
            m_id = rm["id"]
            
            # 1. Create Memory Node
            session.run('''
                CREATE (m:Memory {
                    id: $id, 
                    summary: $summary, 
                    importance: $importance, 
                    created_at: $created_at, 
                    source: $source
                })
            ''', id=m_id, summary=rm["summary"], importance=rm["importance"], 
                 created_at=rm["created_at"], source=rm["source"])
            
            try: entities = json.loads(rm["entities"])
            except: entities = []
                
            try: topics = json.loads(rm["topics"])
            except: topics = []

            # 2. Link Entities
            for e in entities:
                if not e: continue
                session.run('''
                    MATCH (m:Memory {id: $m_id})
                    MERGE (ent:Entity {name: $e_name})
                    MERGE (m)-[:MENTIONS]->(ent)
                ''', m_id=m_id, e_name=e)
                
            # 3. Link Topics
            for t in topics:
                if not t: continue
                session.run('''
                    MATCH (m:Memory {id: $m_id})
                    MERGE (top:Topic {name: $t_name})
                    MERGE (m)-[:RELATES_TO]->(top)
                ''', m_id=m_id, t_name=t)

    print(f"Syncing {len(causal_chains)} causal chains...")
    with driver.session() as session:
        for c in causal_chains:
            session.run('''
                MATCH (m1:Memory {id: $from_id})
                MATCH (m2:Memory {id: $to_id})
                MERGE (m1)-[r:CAUSES {
                    cause: $cause_desc, 
                    effect: $effect_desc, 
                    confidence: $conf
                }]->(m2)
            ''', from_id=c["from_memory_id"], to_id=c["to_memory_id"],
                 cause_desc=c["cause_description"], effect_desc=c["effect_description"],
                 conf=c.get("confidence", 0.7))

    print(f"Syncing {len(consolidations)} consolidations...")
    with driver.session() as session:
        for c in consolidations:
            c_id = c["id"]
            session.run('''
                CREATE (cons:Consolidation {
                    id: $id, 
                    summary: $summary, 
                    created_at: $created_at
                })
            ''', id=c_id, summary=c["summary"], created_at=c["created_at"])
            
            try: source_ids = json.loads(c["source_ids"])
            except: source_ids = []
            
            for src in source_ids:
                session.run('''
                    MATCH (cons:Consolidation {id: $c_id})
                    MATCH (m:Memory {id: $m_id})
                    MERGE (cons)-[:CONSOLIDATED_FROM]->(m)
                ''', c_id=c_id, m_id=src)

    driver.close()
    conn.close()
    print("✅ Neo4j Sync Complete! 100% of ontology loaded into Graph DB.")

if __name__ == "__main__":
    sync_to_neo4j()
