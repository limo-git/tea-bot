import json
import logging
import asyncio
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from config import Config
from db.neo4j import get_driver
from graph.queries import run_intent_query, ENTITY_SEARCH_QUERY
from retrieval.vector_search import vector_search
from retrieval.context_assembler import assemble_context

logger = logging.getLogger(__name__)

_client: genai.Client | None = None

INTENT_TYPES = ["lookup", "relational", "evolutionary", "expert_finding", "summarization", "temporal_context", "conversation_threads"]

QUERY_UNDERSTANDING_PROMPT = """Analyze this Discord server query and extract structured information.

Query: "{query}"

Return:
{{
  "intent": "lookup | relational | evolutionary | expert_finding | summarization | temporal_context | conversation_threads",
  "primary_entity": "main entity (lowercase)",
  "primary_entity_type": "person | topic | technology | null",
  "search_terms": ["keywords"],
  "temporal_context_needed": true/false,
  "time_scope": "recent | days | weeks | months | all_time"
}}

Intent guide:
- "what did X say about Y" → summarization
- "who knows X" → expert_finding  
- "how are X and Y related" → relational
- "tell me about X" → lookup
- "what happened with X over time" → temporal_context
- "continue the discussion about X" → conversation_threads
- Questions asking for context/background → temporal_context
- Follow-up questions → conversation_threads

Temporal context indicators:
- "context", "background", "what happened before", "continuation", "follow-up"
- "over time", "previously", "earlier", "later", "then", "after that"
- "connect", "relate", "link", "sequence", "thread"

JSON only:"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
async def understand_query(query: str) -> dict:
    """Step 1: Use Gemini to extract intent and entities from the user's question."""
    client = _get_client()
    prompt = QUERY_UNDERSTANDING_PROMPT.format(query=query)

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=1024),
            )
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        # Try to parse JSON, with recovery for truncated responses
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"Query understanding JSON parse failed, attempting recovery: {e}")
            # Try to close incomplete JSON
            fixed = raw.rstrip()
            if not fixed.endswith("}"):
                # Add missing closing braces
                open_braces = fixed.count("{") - fixed.count("}")
                open_brackets = fixed.count("[") - fixed.count("]")
                fixed += "]" * open_brackets
                fixed += "}" * open_braces
            try:
                result = json.loads(fixed)
                logger.info("Recovered partial JSON from query understanding")
            except:
                logger.error("Could not recover query understanding JSON, using defaults")
                result = {}
        
        result.setdefault("intent", "summarization")
        result.setdefault("primary_entity", "")
        result.setdefault("primary_entity_type", None)
        result.setdefault("secondary_entity", None)
        result.setdefault("secondary_entity_type", None)
        result.setdefault("search_terms", [query])
        result.setdefault("temporal_context_needed", False)
        result.setdefault("time_scope", "recent")

        logger.info(f"Query understood: intent={result['intent']}, entity={result['primary_entity']}")
        return result

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Query understanding failed: {e}")
        return {
            "intent": "summarization",
            "primary_entity": query,
            "primary_entity_type": None,
            "secondary_entity": None,
            "secondary_entity_type": None,
            "search_terms": [query],
        }


async def graph_traversal(intent: str, understanding: dict) -> list[dict]:
    """Step 2: Run the appropriate Cypher query based on intent."""
    driver = await get_driver()
    primary = understanding.get("primary_entity", "")
    secondary = understanding.get("secondary_entity")

    if not primary:
        return []

    # Build params based on intent
    params = {}
    if intent == "relational" and secondary:
        params = {"entity_a": primary, "entity_b": secondary}
    else:
        params = {"entity_name": primary}

    try:
        async with driver.session() as session:
            # First try exact match
            results = await run_intent_query(session, intent, params)

            # If no results, try fuzzy entity search
            if not results and primary:
                fuzzy = await session.run(ENTITY_SEARCH_QUERY, search_term=primary)
                candidates = [dict(r) async for r in fuzzy]
                if candidates:
                    best = candidates[0]["name"]
                    logger.info(f"Fuzzy match: '{primary}' → '{best}'")
                    if intent == "relational" and secondary:
                        params = {"entity_a": best, "entity_b": secondary}
                    else:
                        params = {"entity_name": best}
                    results = await run_intent_query(session, intent, params)

        logger.info(f"Graph traversal ({intent}): {len(results)} records")
        return results

    except Exception as e:
        logger.error(f"Graph traversal failed: {e}")
        return []


async def run_query_pipeline(
    query: str,
    server_id: int,
    author_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    time_range: Optional[tuple] = None,
    author_username: Optional[str] = None,
) -> dict:
    """
    Full 5-step Graph RAG query pipeline.

    Returns:
        {
            "understanding": dict,
            "context": list[dict],
            "graph_results": list[dict],
            "vector_results": list[dict],
        }
    """
    # Step 1 — Query understanding
    understanding = await understand_query(query)
    intent = understanding["intent"]
    temporal_context_needed = understanding.get("temporal_context_needed", False)
    
    # Override entity with actual username if provided (fixes Discord mention parsing)
    if author_username and understanding.get("primary_entity", "").startswith("<@"):
        understanding["primary_entity"] = author_username
        logger.info(f"Overriding entity from mention to username: {author_username}")

    # Step 2 — Check if temporal context is needed
    if temporal_context_needed or intent in ["temporal_context", "conversation_threads"]:
        # Use enhanced temporal pipeline for cross-time connections
        from retrieval.temporal_engine import run_temporal_query_pipeline
        return await run_temporal_query_pipeline(
            query=query,
            understanding=understanding,
            server_id=server_id,
            author_id=author_id,
            channel_id=channel_id,
            time_range=time_range,
        )

    # Step 2 — Standard Graph traversal (for non-temporal queries)
    graph_results = await graph_traversal(intent, understanding)

    # Step 3 — Vector search (always runs in parallel for semantic coverage)
    search_query = " ".join(understanding.get("search_terms", [query]))
    vector_results = await vector_search(
        query=search_query,
        server_id=server_id,
        author_id=author_id,
        channel_id=channel_id,
        time_range=time_range,
    )

    # Step 4 — Context assembly
    context = assemble_context(graph_results, vector_results, intent)

    return {
        "understanding": understanding,
        "context": context,
        "graph_results": graph_results,
        "vector_results": vector_results,
    }
