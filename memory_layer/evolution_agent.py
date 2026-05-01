import os
import time
import requests
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EvolutionAgent] %(message)s")
log = logging.getLogger("evolution-agent")

class EvolutionAgent:
    def __init__(self):
        self.neo4j_uri = "bolt://localhost:7687"
        self.ingest_url = "http://localhost:5050/ingest"
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client() if self.gemini_key else None
        
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.neo4j_uri, auth=("neo4j", "password"))
            self.driver.verify_connectivity()
            log.info("Neo4j Connected for Evolution Agent.")
        except Exception as e:
            log.warning(f"Neo4j not reachable, Evolution Agent paused: {e}")

    def find_knowledge_gap(self):
        """World Best Practice: Find two disconnected but highly central entities (Link Prediction)."""
        if not self.driver:
            return None
        
        link_prediction_query = """
        MATCH (a:Entity), (b:Entity)
        WHERE id(a) < id(b) AND NOT (a)-[]-(b)
        OPTIONAL MATCH (a)-[r1]-()
        OPTIONAL MATCH (b)-[r2]-()
        WITH a, b, count(r1) AS degreeA, count(r2) AS degreeB
        WHERE degreeA > 0 AND degreeB > 0
        WITH a, b, degreeA, degreeB
        ORDER BY (degreeA + degreeB) DESC, rand()
        LIMIT 1
        RETURN a.name AS entityA, b.name AS entityB
        """
        
        fallback_query = """
        MATCH (n:Entity)
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) AS degree
        ORDER BY degree ASC, rand()
        LIMIT 1
        RETURN n.name AS entity
        """
        
        try:
            with self.driver.session() as session:
                record = session.run(link_prediction_query).single()
                if record:
                    return f"{record['entityA']} and {record['entityB']}"
                
                # Fallback if graph is too sparse
                record = session.run(fallback_query).single()
                if record:
                    return record["entity"]
        except Exception as e:
            log.warning(f"Failed to find gap: {e}")
        return None

    @retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(3))
    def research_perplexity(self, query: str) -> str:
        """Use Perplexity API (sonar-reasoning) with Exponential Backoff."""
        log.info(f"Using Perplexity API for deep analysis on: {query}")
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-reasoning",
            "messages": [
                {"role": "system", "content": "You are a deep-research AI agent. Provide a detailed, highly structured, and insightful analysis on the topic."},
                {"role": "user", "content": query}
            ]
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    @retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(3))
    def research_gemini_search(self, query: str) -> str:
        """Fallback to Gemini Native Google Search Grounding with Exponential Backoff."""
        log.info(f"Using Gemini Google Search for research on: {query}")
        if not self.client:
            return "No Gemini API key available."
        
        response = self.client.models.generate_content(
            model='gemini-2.5-pro',
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction="You are a deep-research AI agent. Provide a detailed analysis based on search results."
            )
        )
        return response.text

    def verify_and_clean_insight(self, insight: str, entity: str) -> str:
        """Self-Correction (Critic): Verify knowledge to prevent hallucinations."""
        log.info("Running Self-Correction & Verification on the insight...")
        if not self.client:
            return insight # Skip if no Gemini
            
        prompt = f"""
        You are a strict Logic Critic AI. Review the following research insight about '{entity}'.
        Task:
        1. Remove any conversational fluff or filler words.
        2. If the text contains obvious hallucinations or contradictory statements, remove them.
        3. Restructure the text into clear, definitive facts and structural relationships.
        
        Original Insight:
        {insight}
        
        Return ONLY the cleaned, verified facts:
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            log.warning(f"Self-Correction failed: {e}. Using original insight.")
            return insight

    def perform_evolution_step(self, force_deep_analysis=False):
        log.info("Starting Evolution Step...")
        entity = self.find_knowledge_gap()
        if not entity:
            log.info("No knowledge gaps found or Neo4j is empty.")
            # Default fallback topic if DB is empty
            entity = "Autonomous AI Agents Architecture"
            
        # Decide if deep analysis is needed (e.g., force flag or random 10% chance)
        import random
        needs_deep_analysis = force_deep_analysis or (random.random() < 0.1)
        
        insight = ""
        if needs_deep_analysis and self.perplexity_key and len(self.perplexity_key) > 10:
            research_question = f"Perform a highly critical and deep reasoning analysis on the hidden relationship between or concepts within '{entity}'. Uncover hidden patterns and advanced architectures."
            log.info(f"Generated Deep Question: {research_question}")
            try:
                insight = self.research_perplexity(research_question)
            except Exception as e:
                log.error(f"Perplexity API failed: {e}. Falling back to Gemini Search.")
                
        if not insight:
            research_question = f"What are the most important concepts and relationships related to '{entity}'? Provide a comprehensive overview."
            log.info(f"Generated Standard Question: {research_question}")
            try:
                insight = self.research_gemini_search(research_question)
            except Exception as e:
                log.error(f"Gemini Search failed: {e}")
                return

        # World Best Practice: Self-Correction
        verified_insight = self.verify_and_clean_insight(insight, entity)

        # Prepare memory for ingestion
        source_label = "Perplexity Deep Analysis" if needs_deep_analysis and insight else "Gemini Grounded Search"
        summary_text = f"[Autonomous Research ({source_label}): {entity}]\n\n{verified_insight}"
        try:
            resp = requests.post(self.ingest_url, json={
                "text": summary_text,
                "agent_id": "EvolutionAgent"
            }, timeout=60)
            if resp.status_code == 200:
                log.info(f"Successfully ingested new knowledge about '{entity}' into the collective memory.")
            else:
                log.error(f"Failed to ingest knowledge: {resp.text}")
        except Exception as e:
            log.error(f"Ingest POST failed: {e}")

    def run_loop(self, interval_seconds=1800):
        log.info(f"Evolution Agent started. Loop interval: {interval_seconds} seconds.")
        loop_count = 0
        while True:
            try:
                # Trigger deep analysis every 10th loop
                self.perform_evolution_step(force_deep_analysis=(loop_count % 10 == 0))
                loop_count += 1
            except Exception as e:
                log.error(f"Evolution loop error: {e}")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    agent = EvolutionAgent()
    # Run once immediately for testing if executed directly (standard search)
    agent.perform_evolution_step(force_deep_analysis=False)
