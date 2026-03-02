import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from db.neo4j import get_driver
from graph.queries import run_intent_query
from retrieval.vector_search import vector_search
from retrieval.context_assembler import assemble_context

logger = logging.getLogger(__name__)


async def run_temporal_query_pipeline(
    query: str,
    understanding: dict,
    server_id: int,
    author_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    time_range: Optional[tuple] = None,
) -> dict:
    """
    Enhanced query pipeline that connects related discussions across time periods.
    
    This implements your requirement to connect discussions that happened at different times,
    like something from a week ago that gets continued 2 days ago.
    """
    
    intent = understanding.get("intent", "summarization")
    primary_entity = understanding.get("primary_entity", "")
    temporal_context_needed = understanding.get("temporal_context_needed", False)
    time_scope = understanding.get("time_scope", "recent")
    
    logger.info(f"Temporal pipeline: intent={intent}, entity={primary_entity}, temporal={temporal_context_needed}")
    
    # Step 1: Get primary results based on intent
    primary_results = await _get_primary_results(intent, understanding, time_range)
    
    # Step 2: If temporal context is needed, get related discussions across time
    temporal_results = []
    if temporal_context_needed or intent in ["temporal_context", "conversation_threads"]:
        temporal_results = await _get_temporal_context(primary_entity, time_scope)
    
    # Step 3: Get conversation threads for continuity
    thread_results = []
    if intent in ["conversation_threads", "summarization"] or temporal_context_needed:
        thread_results = await _get_conversation_threads(primary_entity)
    
    # Step 4: Combine all graph results
    all_graph_results = []
    all_graph_results.extend(primary_results)
    all_graph_results.extend(temporal_results)
    all_graph_results.extend(thread_results)
    
    logger.info(f"Graph results: {len(primary_results)} primary, {len(temporal_results)} temporal, {len(thread_results)} threads")
    
    # Step 5: Get vector search for semantic gaps
    vector_results = []
    if understanding.get("search_terms"):
        search_query = " ".join(understanding["search_terms"])
        vector_results = await vector_search(
            query=search_query,
            server_id=server_id,
            author_id=author_id,
            channel_id=channel_id,
            time_range=time_range,
            intent=intent,  # Pass intent to prioritize recency for summarization queries
        )
    
    # Step 6: Assemble comprehensive context
    context = assemble_context(all_graph_results, vector_results, intent)
    
    # Step 7: Add temporal metadata for answer generation
    context_with_temporal = _add_temporal_metadata(context, all_graph_results)
    
    return {
        "context": context_with_temporal,
        "understanding": understanding,
        "temporal_connections": len(temporal_results),
        "conversation_threads": len(thread_results),
        "total_sources": len(context_with_temporal)
    }


async def _get_primary_results(intent: str, understanding: dict, time_range: tuple = None) -> List[dict]:
    """Get primary results based on the main intent."""
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
    
    # Add time filter for recent data (default to last 3 days for general queries)
    if time_range:
        # Use provided time range
        start_time, end_time = time_range
        if start_time:
            params["time_filter"] = start_time.isoformat()
    else:
        # Default to last 3 days for recency
        from datetime import datetime, timedelta
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        params["time_filter"] = three_days_ago.isoformat()
        logger.info(f"No time range specified, filtering to last 3 days for recency")
    
    try:
        async with driver.session() as session:
            records = await run_intent_query(session, intent, params)
            logger.info(f"Primary graph traversal ({intent}): {len(records)} records")
            return records
    except Exception as e:
        logger.error(f"Primary graph traversal failed: {e}")
        return []


async def _get_temporal_context(entity_name: str, time_scope: str) -> List[dict]:
    """Get related discussions across different time periods."""
    if not entity_name:
        return []
    
    driver = await get_driver()
    params = {"entity_name": entity_name}
    
    try:
        async with driver.session() as session:
            records = await run_intent_query(session, "temporal_context", params)
            logger.info(f"Temporal context: {len(records)} records across time periods")
            return records
    except Exception as e:
        logger.error(f"Temporal context query failed: {e}")
        return []


async def _get_conversation_threads(entity_name: str) -> List[dict]:
    """Get conversation threads and message sequences."""
    if not entity_name:
        return []
    
    driver = await get_driver()
    params = {"entity_name": entity_name}
    
    try:
        async with driver.session() as session:
            records = await run_intent_query(session, "conversation_threads", params)
            logger.info(f"Conversation threads: {len(records)} thread records")
            return records
    except Exception as e:
        logger.error(f"Conversation threads query failed: {e}")
        return []


def _add_temporal_metadata(context: List[dict], graph_results: List[dict]) -> List[dict]:
    """Add temporal relationship metadata to context items."""
    
    # Group messages by entity and time
    entity_timeline = {}
    for result in graph_results:
        if "related_discussions" in result:
            primary_entity = result.get("related_entity", "unknown")
            primary_time = result.get("timestamp")
            
            if primary_entity not in entity_timeline:
                entity_timeline[primary_entity] = []
            
            entity_timeline[primary_entity].append({
                "content": result.get("content", ""),
                "timestamp": primary_time,
                "context_type": "primary"
            })
            
            # Add related discussions
            for related in result.get("related_discussions", []):
                if related.get("content"):
                    entity_timeline[primary_entity].append({
                        "content": related["content"],
                        "timestamp": related.get("timestamp"),
                        "context_type": "related",
                        "time_gap_days": related.get("time_gap", 0)
                    })
    
    # Add temporal metadata to context items
    enhanced_context = []
    for item in context:
        enhanced_item = item.copy()
        
        # Find temporal connections for this item
        content = item.get("content", "")
        temporal_connections = []
        
        for entity, timeline in entity_timeline.items():
            for event in timeline:
                if event["content"] != content and _are_related(content, event["content"]):
                    temporal_connections.append({
                        "entity": entity,
                        "related_content": event["content"][:100] + "...",
                        "time_gap": event.get("time_gap_days", 0),
                        "context_type": event["context_type"]
                    })
        
        if temporal_connections:
            enhanced_item["temporal_connections"] = temporal_connections
            enhanced_item["has_temporal_context"] = True
        
        enhanced_context.append(enhanced_item)
    
    return enhanced_context


def _are_related(content1: str, content2: str) -> bool:
    """Simple heuristic to check if two messages are related."""
    if not content1 or not content2:
        return False
    
    # Convert to lowercase for comparison
    c1, c2 = content1.lower(), content2.lower()
    
    # Check for common words (excluding very common ones)
    words1 = set(c1.split()) - {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    words2 = set(c2.split()) - {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    
    if len(words1) == 0 or len(words2) == 0:
        return False
    
    # Calculate overlap ratio
    overlap = len(words1.intersection(words2))
    total_unique = len(words1.union(words2))
    
    return overlap / total_unique > 0.2  # 20% word overlap threshold
