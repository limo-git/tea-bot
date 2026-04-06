import logging
from database.supabase_client import supabase_client
from ai.embeddings import generate_query_embedding
from config import Config

logger = logging.getLogger(__name__)

# Confidence threshold for semantic search results
# Results below this similarity score are considered too weak to use
CONFIDENCE_THRESHOLD = 0.35


async def vector_search(query: str, server_id: int, author_id: int = None,
                        channel_id: int = None, time_range: tuple = None, 
                        intent: str = None, mentions_user_id: int = None) -> list[dict]:
    """
    Run pgvector semantic search against existing Supabase messages table.
    Reuses the existing embedding + supabase infrastructure.
    
    For summarization queries (e.g., "what did I miss"), prioritizes recency over semantic similarity.
    """
    try:
        # SAFETY CHECK: If author_id is provided, this is a user-specific query
        # Don't limit to 3 days even if intent is "summarization"
        if author_id and intent == "summarization":
            logger.info(f"User-specific query detected (author_id={author_id}), overriding summarization intent to search entire history")
            intent = "user_messages"
        
        # For summarization queries (general server activity), get all recent messages
        if intent == "summarization":
            # Default to last 3 days for summarization if no time range specified
            if time_range is None:
                from datetime import datetime, timedelta
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=3)
                time_range = (start_time, end_time)
                logger.info(f"Summarization query - defaulting to last 3 days for recency")
            
            logger.info(f"Fetching all recent messages by timestamp (last 3 days)")
            results = await supabase_client.get_messages_by_timerange(
                server_id=server_id,
                channel_id=channel_id,
                start_time=time_range[0],
                end_time=time_range[1],
                limit=Config.VECTOR_TOP_K,
            )
            # Add similarity score of 1.0 for all messages (they're all equally relevant for summarization)
            for msg in results:
                msg['similarity'] = 1.0
            logger.info(f"Fetched {len(results)} recent messages for summarization")
            return results
        
        # For user_messages queries, skip confidence filtering (already filtered by author)
        if intent == "user_messages":
            logger.info(f"User messages query - will skip confidence threshold filtering")
            skip_confidence_filter = True
        else:
            skip_confidence_filter = False
        
        # For all other query types (lookup, expert_finding, etc.), use semantic search
        # For lookup queries, search the ENTIRE database semantically (no time filter by default)
        # This allows finding relevant messages from any time period
        logger.info(f"Lookup/specific query - using semantic search across entire database")
        
        embedding = await generate_query_embedding(query)
        if not embedding:
            logger.warning("Failed to generate query embedding for vector search")
            return []

        # Only apply time_range if explicitly provided by user
        # For lookup queries without explicit time range, search all messages
        results = await supabase_client.semantic_search_filtered(
            embedding=embedding,
            server_id=server_id,
            author_id=author_id,
            channel_id=channel_id,
            time_range=time_range if time_range else None,  # Don't default to 3 days for lookup
            mentions_user_id=mentions_user_id,
            limit=Config.VECTOR_TOP_K,
        )

        logger.info(f"Vector search returned {len(results)} results before confidence filtering")
        
        # Skip confidence filtering for user_messages queries (already filtered by author)
        if skip_confidence_filter:
            logger.info(f"Skipping confidence threshold for user_messages query - returning all {len(results)} results")
            return results
        
        # Apply confidence threshold - filter out low-relevance results
        filtered_results = [msg for msg in results if msg.get('similarity', 0) >= CONFIDENCE_THRESHOLD]
        
        if len(filtered_results) < len(results):
            logger.info(f"Confidence threshold filtering: {len(results)} -> {len(filtered_results)} results (removed {len(results) - len(filtered_results)} low-confidence results)")
        
        # If no results pass confidence threshold, log warning
        if not filtered_results:
            logger.warning(f"No results passed confidence threshold ({CONFIDENCE_THRESHOLD}) for query: {query[:60]}")
        
        return filtered_results

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []
