"""
Reciprocal Rank Fusion (RRF) for combining multiple retrieval results.
Implements the RRF algorithm to merge BM25, vector, and graph search results.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# RRF constant - controls the influence of rank position
# Higher k = less emphasis on rank differences
RRF_K = 60  # Standard value from literature


def reciprocal_rank_fusion(
    bm25_results: List[Dict[str, Any]],
    vector_results: List[Dict[str, Any]],
    graph_results: List[Dict[str, Any]],
    k: int = RRF_K
) -> List[Dict[str, Any]]:
    """
    Combine results from multiple retrievers using Reciprocal Rank Fusion.
    
    RRF Formula: score(d) = Σ(1 / (k + rank_i(d)))
    where rank_i(d) is the rank of document d in retriever i
    
    Args:
        bm25_results: Results from BM25 keyword search
        vector_results: Results from semantic vector search
        graph_results: Results from knowledge graph traversal
        k: RRF constant (default: 60)
    
    Returns:
        Fused and ranked results
    """
    logger.info(f"RRF fusion: {len(bm25_results)} BM25, {len(vector_results)} vector, {len(graph_results)} graph results")
    
    # Track all unique documents and their RRF scores
    doc_scores = {}  # message_id -> {score, data}
    
    # Process BM25 results
    for rank, result in enumerate(bm25_results, start=1):
        message_id = result.get('message_id') or result.get('id')
        if not message_id:
            continue
        
        rrf_score = 1.0 / (k + rank)
        
        if message_id not in doc_scores:
            doc_scores[message_id] = {
                'rrf_score': 0.0,
                'data': result,
                'sources': []
            }
        
        doc_scores[message_id]['rrf_score'] += rrf_score
        doc_scores[message_id]['sources'].append(f'bm25_rank_{rank}')
    
    # Process vector results
    for rank, result in enumerate(vector_results, start=1):
        message_id = result.get('message_id') or result.get('id')
        if not message_id:
            continue
        
        rrf_score = 1.0 / (k + rank)
        
        if message_id not in doc_scores:
            doc_scores[message_id] = {
                'rrf_score': 0.0,
                'data': result,
                'sources': []
            }
        
        doc_scores[message_id]['rrf_score'] += rrf_score
        doc_scores[message_id]['sources'].append(f'vector_rank_{rank}')
        
        # Preserve similarity score from vector search
        if 'similarity' in result:
            doc_scores[message_id]['data']['similarity'] = result['similarity']
    
    # Process graph results
    for rank, result in enumerate(graph_results, start=1):
        # Graph results may have nested messages
        messages = result.get('messages', [result])
        
        for msg in messages if isinstance(messages, list) else [messages]:
            message_id = msg.get('message_id') or msg.get('id')
            if not message_id:
                continue
            
            rrf_score = 1.0 / (k + rank)
            
            if message_id not in doc_scores:
                doc_scores[message_id] = {
                    'rrf_score': 0.0,
                    'data': msg,
                    'sources': []
                }
            
            doc_scores[message_id]['rrf_score'] += rrf_score
            doc_scores[message_id]['sources'].append(f'graph_rank_{rank}')
    
    # Convert to list and sort by RRF score
    fused_results = []
    for message_id, score_data in doc_scores.items():
        result = score_data['data'].copy()
        result['rrf_score'] = score_data['rrf_score']
        result['retrieval_sources'] = score_data['sources']
        result['num_retrievers'] = len(score_data['sources'])
        fused_results.append(result)
    
    # Sort by RRF score (descending)
    fused_results.sort(key=lambda x: x['rrf_score'], reverse=True)
    
    logger.info(f"RRF fusion complete: {len(fused_results)} unique documents")
    
    # Log top results for debugging
    if fused_results:
        top_3 = fused_results[:3]
        for i, result in enumerate(top_3, 1):
            logger.info(f"  Top {i}: RRF={result['rrf_score']:.4f}, sources={result['retrieval_sources']}")
    
    return fused_results


def hybrid_search_with_rrf(
    query: str,
    bm25_results: List[Dict[str, Any]],
    vector_results: List[Dict[str, Any]],
    graph_results: List[Dict[str, Any]] = None,
    top_k: int = 30
) -> List[Dict[str, Any]]:
    """
    Perform hybrid search with RRF fusion.
    
    Args:
        query: Search query
        bm25_results: BM25 keyword search results
        vector_results: Semantic vector search results
        graph_results: Optional graph traversal results
        top_k: Number of top results to return
    
    Returns:
        Top-k fused results
    """
    if graph_results is None:
        graph_results = []
    
    # Apply RRF fusion
    fused_results = reciprocal_rank_fusion(
        bm25_results=bm25_results,
        vector_results=vector_results,
        graph_results=graph_results
    )
    
    # Return top-k results
    return fused_results[:top_k]


def calculate_fusion_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics about the fusion results.
    
    Args:
        results: Fused results from RRF
    
    Returns:
        Dictionary of metrics
    """
    if not results:
        return {
            'total_results': 0,
            'avg_rrf_score': 0.0,
            'multi_retriever_count': 0,
            'single_retriever_count': 0
        }
    
    total = len(results)
    avg_score = sum(r['rrf_score'] for r in results) / total
    multi_retriever = sum(1 for r in results if r['num_retrievers'] > 1)
    single_retriever = sum(1 for r in results if r['num_retrievers'] == 1)
    
    return {
        'total_results': total,
        'avg_rrf_score': avg_score,
        'multi_retriever_count': multi_retriever,
        'single_retriever_count': single_retriever,
        'multi_retriever_percentage': (multi_retriever / total * 100) if total > 0 else 0
    }
