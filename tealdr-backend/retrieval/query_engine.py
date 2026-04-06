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

QUERY_UNDERSTANDING_PROMPT = """Analyze this user query and extract structured information.

Query: "{query}"

Return JSON with these fields:
{{
  "intent": "lookup | expert_finding | relational | evolutionary | summarization | user_messages | temporal_context | conversation_threads",
  "primary_entity": "main topic/person/thing being asked about",
  "primary_entity_type": "person | topic | technology | null",
  "secondary_entity": "second entity if comparing/relating two things",
  "secondary_entity_type": "person | topic | technology | null",
  "search_terms": ["key", "search", "terms"],
  "temporal_context_needed": true/false,
  "time_scope": "recent | days | weeks | months | all_time"
}}

Intent Classification Rules (CRITICAL - follow strictly):

1. **user_messages** - Messages FROM a specific user
   - "what did @user say"
   - "@user's messages" 
   - "messages from @user"
   - "what is @user trying to convey"
   - ANY query with user mention + asking about their messages

2. **lookup** - Find messages ABOUT a specific topic/entity
   - "who talked about X"
   - "who mentioned X"
   - "tell me about X"
   - "what is X"
   - "find messages about X"
   - "discussions about X"
   - ANY query with a SPECIFIC entity/topic

3. **expert_finding** - Find who knows about a topic
   - "who knows X"
   - "who is expert in X"
   - "who can help with X"

4. **relational** - Relationship between entities
   - "how are X and Y related"
   - "connection between X and Y"

5. **temporal_context** - How something evolved
   - "what happened with X over time"
   - "how did X evolve"

6. **conversation_threads** - Continue a discussion
   - "continue the discussion about X"
   - "thread about X"

7. **summarization** - General server activity (NO specific entity)
   - "what did i miss"
   - "what happened"
   - "server activity"
   - "recent activity"
   - ONLY when NO specific topic/entity mentioned

CRITICAL RULES:
- DEFAULT to "lookup" if there's ANY specific entity/topic
- ONLY use "summarization" if query is about general server activity with NO entity
- If user mention present → "user_messages"
- If specific topic present → "lookup"
- Extract actual entity names (e.g., "API" from "who talked about API")
- For @username or <@123456> → entity_type = "person"

Examples:
- "who talked about geopolitics" → intent: lookup, entity: geopolitics
- "what did @john say" → intent: user_messages, entity: john
- "tell me about the API" → intent: lookup, entity: API
- "what happened" → intent: summarization, entity: server
- "who knows Python" → intent: expert_finding, entity: Python

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
        
        # Check for specific entities/topics in query (keywords that indicate a specific topic)
        topic_indicators = ["about", "regarding", "concerning", "related to", "discussed", "mentioned", "talked about"]
        has_topic = any(indicator in query_lower for indicator in topic_indicators)
        
        # Check for question words that indicate lookup
        lookup_patterns = ["who", "what", "where", "when", "how", "why", "which", "tell me", "find", "search", "show me"]
        is_lookup_query = any(pattern in query_lower for pattern in lookup_patterns)
        
        # Determine default intent based on query type (PREFER lookup over summarization)
        if has_user_mention and is_user_query:
            default_intent = "user_messages"
            logger.info("Detected user-specific query in defaults, using user_messages intent")
        elif any(phrase in query_lower for phrase in ["what did i miss", "what happened", "server activity", "recent activity", "while i was away", "what's new"]) and not has_topic:
            # Only use summarization if it's general activity AND no specific topic
            default_intent = "summarization"
            logger.info("Detected general server activity query, using summarization intent")
        elif is_lookup_query or has_topic:
            # Default to lookup if there are question words or topic indicators
            default_intent = "lookup"
            logger.info("Detected specific query, using lookup intent")
        else:
            # Final fallback: lookup (NOT summarization)
            default_intent = "lookup"
            logger.info("Using lookup as default intent")
        
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

    # Step 3 — TRUE HYBRID SEARCH (BM25 + Vector + Graph with RRF Fusion)
    from retrieval.hybrid_search import hybrid_search_with_graph
    
    # For lookup queries, use the entity name + search terms for better semantic matching
    # Avoid duplicating entity if it's already in search terms
    if intent == "lookup" and understanding.get("primary_entity"):
        entity = understanding.get('primary_entity', '')
        search_terms = understanding.get('search_terms', [])
        # Check if entity is already in search terms to avoid duplication
        if entity and entity.lower() not in ' '.join(search_terms).lower():
            search_query = f"{entity} {' '.join(search_terms)}"
        else:
            search_query = ' '.join(search_terms) if search_terms else entity
    else:
        search_query = " ".join(understanding.get("search_terms", [query]))
    
    logger.info(f"Hybrid search query: '{search_query[:100]}'")
    
    # Hybrid search with RRF fusion (BM25 + Vector + Graph)
    fused_results = await hybrid_search_with_graph(
        query=search_query,
        server_id=server_id,
        graph_results=graph_results,
        author_id=author_id,
        channel_id=channel_id,
        time_range=time_range,
        limit=50
    )
    
    logger.info(f"Hybrid search returned {len(fused_results)} fused results")

    # Step 4 — RERANKING (Cross-encoder scoring)
    from retrieval.reranker import rerank_results
    
    reranked_results = await rerank_results(
        query=search_query,
        results=fused_results,
        top_k=30
    )
    
    logger.info(f"Reranking complete: {len(reranked_results)} results")

    # Step 5 — CRAG refinement loop for low-confidence queries
    from retrieval.crag_refiner import refine_and_retrieve
    
    refined_results = await refine_and_retrieve(
        original_query=query,
        original_results=reranked_results,
        intent=intent,
        server_id=server_id,
        author_id=author_id,
        channel_id=channel_id,
        time_range=time_range,
        mentions_user_id=mentions_user_id
    )

    # Step 6 — CONTEXT COMPRESSION (Token budget management)
    from retrieval.compressor import compress_to_budget
    
    compressed_results = compress_to_budget(
        query=search_query,
        results=refined_results,
        token_budget=4000  # Leave room for prompt + answer
    )
    
    logger.info(f"Compression complete: {len(compressed_results)} results within token budget")

    # Step 7 — Context assembly (format for prompt)
    context = assemble_context(graph_results, compressed_results, intent)

    return {
        "understanding": understanding,
        "context": context,
        "graph_results": graph_results,
        "vector_results": compressed_results,  # Use compressed results as vector_results
    }
