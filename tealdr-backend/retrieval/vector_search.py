import logging
from database.supabase_client import supabase_client
from ai.embeddings import generate_query_embedding
from config import Config

logger = logging.getLogger(__name__)


async def vector_search(query: str, server_id: int, author_id: int = None,
                        channel_id: int = None, time_range: tuple = None, 
                        intent: str = None) -> list[dict]:
    """
    Run pgvector semantic search against existing Supabase messages table.
    Reuses the existing embedding + supabase infrastructure.
    
    For summarization queries (e.g., "what did I miss"), prioritizes recency over semantic similarity.
    """
    try:
        # If no explicit time range, default to last 3 days for "recently" queries (matching /recap)
        if time_range is None:
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=3)
            time_range = (start_time, end_time)
            logger.info(f"No time range specified, defaulting to last 3 days for recency")

        # For summarization queries, get all recent messages without semantic filtering
        if intent == "summarization":
            logger.info(f"Summarization query detected - fetching all recent messages by timestamp")
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
        
        # For other query types, use semantic search
        embedding = await generate_query_embedding(query)
        if not embedding:
            logger.warning("Failed to generate query embedding for vector search")
            return []

        results = await supabase_client.semantic_search_filtered(
            embedding=embedding,
            server_id=server_id,
            author_id=author_id,
            channel_id=channel_id,
            time_range=time_range,
            limit=Config.VECTOR_TOP_K,
        )

        logger.info(f"Vector search returned {len(results)} results for query: {query[:60]}")
        return results

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []
