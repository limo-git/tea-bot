"""
True Hybrid Search implementation combining BM25 keyword search and dense vector search.
Uses Reciprocal Rank Fusion (RRF) to merge results.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


async def hybrid_search(
    query: str,
    server_id: int,
    author_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Perform hybrid search combining BM25 keyword search and semantic vector search.
    
    Args:
        query: Search query
        server_id: Server ID to search in
        author_id: Optional author filter
        channel_id: Optional channel filter
        time_range: Optional time range filter
        limit: Number of results per retriever
    
    Returns:
        Fused results using RRF
    """
    from database.supabase_client import supabase_client
    from ai.embeddings import generate_query_embedding
    from retrieval.rrf_fusion import reciprocal_rank_fusion
    
    logger.info(f"Hybrid search: query='{query[:60]}', server={server_id}")
    
    # Run BM25 and vector search in parallel
    import asyncio
    
    # 1. BM25 keyword search
    async def bm25_search_task():
        try:
            results = await supabase_client.bm25_search(
                query=query,
                server_id=server_id,
                limit=limit
            )
            
            # Apply filters
            if author_id:
                results = [r for r in results if r.get('author_id') == author_id]
            if channel_id:
                results = [r for r in results if r.get('channel_id') == channel_id]
            if time_range:
                start_time, end_time = time_range
                filtered = []
                for r in results:
                    created_at = r.get('created_at')
                    if created_at:
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_time <= created_at <= end_time:
                            filtered.append(r)
                results = filtered
            
            logger.info(f"BM25 search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    # 2. Semantic vector search
    async def vector_search_task():
        try:
            embedding = await generate_query_embedding(query)
            if not embedding:
                return []
            
            results = await supabase_client.semantic_search_filtered(
                embedding=embedding,
                server_id=server_id,
                author_id=author_id,
                channel_id=channel_id,
                time_range=time_range,
                limit=limit
            )
            
            logger.info(f"Vector search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    # Execute both searches in parallel
    bm25_results, vector_results = await asyncio.gather(
        bm25_search_task(),
        vector_search_task()
    )
    
    # Apply RRF fusion
    fused_results = reciprocal_rank_fusion(
        bm25_results=bm25_results,
        vector_results=vector_results,
        graph_results=[]  # Graph results added separately in query_engine
    )
    
    logger.info(f"Hybrid search complete: {len(fused_results)} fused results")
    
    return fused_results


async def hybrid_search_with_graph(
    query: str,
    server_id: int,
    graph_results: List[Dict[str, Any]],
    author_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Perform hybrid search and fuse with graph results.
    
    Args:
        query: Search query
        server_id: Server ID
        graph_results: Results from graph traversal
        author_id: Optional author filter
        channel_id: Optional channel filter
        time_range: Optional time range filter
        limit: Number of results per retriever
    
    Returns:
        Fused results from all three retrievers
    """
    from database.supabase_client import supabase_client
    from ai.embeddings import generate_query_embedding
    from retrieval.rrf_fusion import reciprocal_rank_fusion
    
    logger.info(f"Hybrid search with graph: query='{query[:60]}', {len(graph_results)} graph results")
    
    # Run BM25 and vector search
    import asyncio
    
    async def bm25_task():
        try:
            results = await supabase_client.bm25_search(query, server_id, limit)
            if author_id:
                results = [r for r in results if r.get('author_id') == author_id]
            if channel_id:
                results = [r for r in results if r.get('channel_id') == channel_id]
            return results
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    async def vector_task():
        try:
            embedding = await generate_query_embedding(query)
            if not embedding:
                return []
            return await supabase_client.semantic_search_filtered(
                embedding=embedding,
                server_id=server_id,
                author_id=author_id,
                channel_id=channel_id,
                time_range=time_range,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    bm25_results, vector_results = await asyncio.gather(bm25_task(), vector_task())
    
    # Fuse all three: BM25 + Vector + Graph
    fused_results = reciprocal_rank_fusion(
        bm25_results=bm25_results,
        vector_results=vector_results,
        graph_results=graph_results
    )
    
    logger.info(f"Hybrid search with graph complete: {len(fused_results)} total results")
    
    return fused_results


def explain_hybrid_results(results: List[Dict[str, Any]], top_n: int = 5) -> str:
    """
    Generate explanation of hybrid search results for debugging.
    
    Args:
        results: Fused results
        top_n: Number of top results to explain
    
    Returns:
        Human-readable explanation
    """
    if not results:
        return "No results found"
    
    explanation = [f"Hybrid Search Results (Top {top_n}):"]
    
    for i, result in enumerate(results[:top_n], 1):
        rrf_score = result.get('rrf_score', 0)
        sources = result.get('retrieval_sources', [])
        num_retrievers = result.get('num_retrievers', 0)
        content_preview = result.get('content', '')[:60]
        
        explanation.append(
            f"\n{i}. RRF Score: {rrf_score:.4f} | "
            f"Retrievers: {num_retrievers} | "
            f"Sources: {', '.join(sources)}"
        )
        explanation.append(f"   Content: {content_preview}...")
    
    return '\n'.join(explanation)
