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
  "intent": "lookup | relational | evolutionary | expert_finding | summarization | temporal_context | conversation_threads | user_messages",
  "primary_entity": "main entity (lowercase)",
  "primary_entity_type": "person | topic | technology | null",
  "search_terms": ["keywords"],
  "temporal_context_needed": true/false,
  "time_scope": "recent | days | weeks | months | all_time"
}}

Intent guide (choose the MOST SPECIFIC intent):
- "what did @user say" / "what is @user trying to convey" / "@user's messages" / "messages from @user" → user_messages (find messages FROM a specific user)
- "who talked about X" / "who mentioned X" / "who was discussing X" → lookup (find messages about X)
- "who knows X" / "who is expert in X" → expert_finding  
- "what did X say about Y" → user_messages (X is person, Y is topic - filter by user AND topic)
- "how are X and Y related" → relational
- "tell me about X" / "what is X" / "explain X" → lookup
- "what happened with X over time" / "how did X evolve" → temporal_context
- "continue the discussion about X" → conversation_threads
- "what did i miss" / "what happened" / "server activity" / "recent activity" (NO specific entity) → summarization 

IMPORTANT: 
- If query asks about messages FROM a specific user (e.g., "what @user said", "@user's messages"), use "user_messages" intent
- If query asks about a SPECIFIC topic/person/thing, use "lookup" NOT "summarization"
- Only use "summarization" for general server activity with NO specific entity
- Extract the actual entity name from the query (e.g., "geopolitics" from "who talked about geopolitics")
- For user mentions like @username or <@123456>, extract the username as the entity and set type to "person"

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
        
        # Smart defaults based on query content
        query_lower = query.lower()
        import re
        has_user_mention = bool(re.search(r'<@!?\d+>|@\w+', query))
        is_user_query = any(phrase in query_lower for phrase in ["what is", "what's", "what do", "what does", "know about", "upto", "up to", "doing", "said", "messages from", "tell me about"])
        
        # Determine default intent based on query type
        if has_user_mention and is_user_query:
            default_intent = "user_messages"
            logger.info("Detected user-specific query in defaults, using user_messages intent")
        elif any(phrase in query_lower for phrase in ["what did i miss", "what happened", "server activity", "recent activity", "while i was away", "what's new"]):
            default_intent = "summarization"
        else:
            default_intent = "lookup"
        
        result.setdefault("intent", default_intent)
        result.setdefault("primary_entity", query if has_user_mention else "")
        result.setdefault("primary_entity_type", None)
        result.setdefault("secondary_entity", None)
        result.setdefault("secondary_entity_type", None)
        result.setdefault("search_terms", [query])
        result.setdefault("temporal_context_needed", False)
        result.setdefault("time_scope", "recent")
        
        # Fix for general server activity queries
        if not result["primary_entity"] or result["primary_entity"] in ["", "**", "*"]:
            # Check if this is a general server activity query
            if any(phrase in query_lower for phrase in ["what did i miss", "what happened", "server activity", "recent activity", "while i was away", "what's new"]):
                result["primary_entity"] = "server"
                result["intent"] = "summarization"
                logger.info(f"Detected general server activity query, setting entity to 'server'")

        logger.info(f"Query understood: intent={result['intent']}, entity={result['primary_entity']}")
        return result

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Query understanding failed: {e}")
        # Fallback for failed query understanding
        query_lower = query.lower()
        
        # Check if this is a user-specific query (mentions or "what is @user doing")
        import re
        has_user_mention = bool(re.search(r'<@!?\d+>|@\w+', query))
        is_user_query = any(phrase in query_lower for phrase in ["what is", "what's", "what do", "what does", "know about", "upto", "up to", "doing", "said", "messages from", "tell me about"])
        
        if has_user_mention and is_user_query:
            # User-specific query - use lookup intent to search entire history
            fallback_intent = "user_messages"
            fallback_entity = query
            logger.info(f"Fallback: Detected user-specific query, using user_messages intent")
        elif any(phrase in query_lower for phrase in ["what did i miss", "what happened", "server activity", "recent activity", "while i was away", "what's new"]):
            # General server activity query
            fallback_intent = "summarization"
            fallback_entity = "server"
            logger.info(f"Fallback: Detected general server activity query")
        else:
            # Default to lookup for specific queries
            fallback_intent = "lookup"
            fallback_entity = query
            logger.info(f"Fallback: Using lookup intent for specific query")
            
        return {
            "intent": fallback_intent,
            "primary_entity": fallback_entity,
            "primary_entity_type": None,
            "secondary_entity": None,
            "secondary_entity_type": None,
            "search_terms": [query],
            "temporal_context_needed": False,
            "time_scope": "recent",
        }


async def graph_traversal(intent: str, understanding: dict, server_id: int, time_range: tuple = None) -> list[dict]:
    """Step 2: Run the appropriate Cypher query based on intent."""
    driver = await get_driver()
    primary = understanding.get("primary_entity", "")
    secondary = understanding.get("secondary_entity")

    if not primary:
        return []

    # Build params based on intent
    params = {"server_id": server_id}  # CRITICAL: Always filter by server
    if intent == "relational" and secondary:
        params.update({"entity_a": primary, "entity_b": secondary})
    else:
        params.update({"entity_name": primary})
    
    # Add time filter for recent data
    # For summarization queries, default to last 3 days
    # For lookup queries, search entire database (no default time filter)
    if time_range:
        # Use provided time range
        start_time, end_time = time_range
        if start_time:
            params["time_filter"] = start_time.isoformat()
    elif intent == "summarization":
        # Only default to 3 days for summarization queries
        from datetime import datetime, timedelta
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        params["time_filter"] = three_days_ago.isoformat()
        logger.info(f"Summarization query - filtering to last 3 days for recency")
    else:
        # For lookup/expert_finding/etc, don't apply time filter by default
        # This allows searching the entire database semantically
        params["time_filter"] = None
        logger.info(f"Lookup query - searching entire database (no time filter)")

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
                    # Keep the time filter for fuzzy search
                    if "time_filter" not in params:
                        if time_range:
                            start_time, end_time = time_range
                            if start_time:
                                params["time_filter"] = start_time.isoformat()
                        else:
                            from datetime import datetime, timedelta
                            seven_days_ago = datetime.utcnow() - timedelta(days=7)
                            params["time_filter"] = seven_days_ago.isoformat()
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
    mentions_user_id: Optional[int] = None,
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

    # Step 2 — Handle user_messages intent (messages FROM a specific user)
    if intent == "user_messages":
        # For user-specific queries, we ONLY want messages from that user
        # Skip graph traversal and rely entirely on vector search with author filter
        logger.info(f"User messages query detected - filtering by author_id: {author_id}")
        
        # Use the original query for semantic search
        # For user queries, use a more generic search to avoid low similarity scores
        search_query = query
        
        vector_results = await vector_search(
            query=search_query,
            server_id=server_id,
            author_id=author_id,  # CRITICAL: Filter by author
            channel_id=channel_id,
            time_range=time_range,
            intent="user_messages",  # Use user_messages intent to skip confidence threshold
            mentions_user_id=mentions_user_id,
        )
        
        # No graph traversal for user_messages - we only want messages FROM the user
        graph_results = []
        
        # Context is just the vector results (all from the specified user)
        context = vector_results
        
        return {
            "understanding": understanding,
            "context": context,
            "graph_results": graph_results,
            "vector_results": vector_results,
        }
    
    # Step 2 — Standard Graph traversal (for non-temporal queries)
    graph_results = await graph_traversal(intent, understanding, server_id, time_range)

    # Step 3 — Vector search (always runs in parallel for semantic coverage)
    # For lookup queries, use the entity name + search terms for better semantic matching
    if intent == "lookup" and understanding.get("primary_entity"):
        search_query = f"{understanding['primary_entity']} {' '.join(understanding.get('search_terms', []))}"
    else:
        search_query = " ".join(understanding.get("search_terms", [query]))
    
    logger.info(f"Vector search query: '{search_query[:100]}'")
    
    vector_results = await vector_search(
        query=search_query,
        server_id=server_id,
        author_id=author_id,
        channel_id=channel_id,
        time_range=time_range,
        intent=intent,  # Pass intent to prioritize recency for summarization queries
        mentions_user_id=mentions_user_id,
    )

    # P3: CRAG refinement loop for low-confidence queries
    from retrieval.crag_refiner import refine_and_retrieve
    
    vector_results = await refine_and_retrieve(
        original_query=query,
        original_results=vector_results,
        intent=intent,
        server_id=server_id,
        author_id=author_id,
        channel_id=channel_id,
        time_range=time_range,
        mentions_user_id=mentions_user_id
    )

    # Step 4 — Context assembly
    context = assemble_context(graph_results, vector_results, intent)

    return {
        "understanding": understanding,
        "context": context,
        "graph_results": graph_results,
        "vector_results": vector_results,
    }
