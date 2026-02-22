import logging
from database.supabase_client import supabase_client
from ai.embeddings import generate_query_embedding
from config import Config

logger = logging.getLogger(__name__)


async def vector_search(query: str, server_id: int, author_id: int = None,
                        channel_id: int = None, time_range: tuple = None) -> list[dict]:
    """
    Run pgvector semantic search against existing Supabase messages table.
    Reuses the existing embedding + supabase infrastructure.
    """
    try:
        embedding = await generate_query_embedding(query)
        if not embedding:
            logger.warning("Failed to generate query embedding for vector search")
            return []

        # If no explicit time range, default to last 7 days for "recently" queries
        if time_range is None:
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            time_range = (start_time, end_time)
            logger.info(f"No time range specified, defaulting to last 7 days for recency")

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
