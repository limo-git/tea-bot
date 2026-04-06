"""
Cross-encoder reranking for improving retrieval quality.
Uses a reranking model to score query-document pairs and reorder results.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 20,
    use_model: bool = False
) -> List[Dict[str, Any]]:
    """
    Rerank search results using cross-encoder scoring.
    
    For now, uses a heuristic-based reranking. Can be upgraded to use
    a cross-encoder model like ms-marco-MiniLM-L-6-v2 in the future.
    
    Args:
        query: Original search query
        results: Search results to rerank
        top_k: Number of top results to return
        use_model: Whether to use ML model (future enhancement)
    
    Returns:
        Reranked results
    """
    if not results:
        return []
    
    logger.info(f"Reranking {len(results)} results for query: '{query[:60]}'")
    
    if use_model:
        # Future: Use cross-encoder model
        # from sentence_transformers import CrossEncoder
        # model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        # pairs = [[query, r['content']] for r in results]
        # scores = model.predict(pairs)
        logger.warning("Model-based reranking not yet implemented, using heuristic")
    
    # Heuristic-based reranking
    reranked = _heuristic_rerank(query, results)
    
    logger.info(f"Reranking complete: returning top {min(top_k, len(reranked))} results")
    
    return reranked[:top_k]


def _heuristic_rerank(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Heuristic-based reranking using multiple signals.
    
    Scoring factors:
    1. RRF score (if present)
    2. Number of retrievers that found this document
    3. Similarity score (if present)
    4. Content length (prefer substantial messages)
    5. Query term coverage
    6. Recency (slight boost for recent messages)
    """
    from datetime import datetime
    
    query_terms = set(query.lower().split())
    now = datetime.utcnow()
    
    for result in results:
        score = 0.0
        
        # 1. RRF score (most important)
        rrf_score = result.get('rrf_score', 0)
        score += rrf_score * 10.0  # Weight: 10x
        
        # 2. Number of retrievers (consensus signal)
        num_retrievers = result.get('num_retrievers', 1)
        score += num_retrievers * 2.0  # Weight: 2x
        
        # 3. Similarity score from vector search
        similarity = result.get('similarity', 0)
        score += similarity * 5.0  # Weight: 5x
        
        # 4. Content length (prefer substantial messages, penalize too short/long)
        content = result.get('content', '')
        content_length = len(content)
        if 50 <= content_length <= 500:
            score += 1.0
        elif content_length > 500:
            score += 0.5
        
        # 5. Query term coverage
        content_lower = content.lower()
        matching_terms = sum(1 for term in query_terms if term in content_lower)
        term_coverage = matching_terms / len(query_terms) if query_terms else 0
        score += term_coverage * 3.0  # Weight: 3x
        
        # 6. Recency boost (slight preference for recent messages)
        created_at = result.get('created_at') or result.get('timestamp')
        if created_at:
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    dt = created_at
                
                # Messages from last 7 days get a small boost
                age_days = (now - dt).days
                if age_days <= 7:
                    score += 0.5
                elif age_days <= 30:
                    score += 0.2
            except:
                pass
        
        # Store rerank score
        result['rerank_score'] = score
    
    # Sort by rerank score (descending)
    results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
    
    return results


def explain_reranking(results: List[Dict[str, Any]], top_n: int = 5) -> str:
    """
    Generate explanation of reranking decisions.
    
    Args:
        results: Reranked results
        top_n: Number of results to explain
    
    Returns:
        Human-readable explanation
    """
    if not results:
        return "No results to explain"
    
    explanation = [f"Reranking Explanation (Top {top_n}):"]
    
    for i, result in enumerate(results[:top_n], 1):
        rerank_score = result.get('rerank_score', 0)
        rrf_score = result.get('rrf_score', 0)
        similarity = result.get('similarity', 0)
        num_retrievers = result.get('num_retrievers', 0)
        content_preview = result.get('content', '')[:50]
        
        explanation.append(
            f"\n{i}. Rerank Score: {rerank_score:.2f}"
        )
        explanation.append(
            f"   - RRF: {rrf_score:.4f} | "
            f"Similarity: {similarity:.2f} | "
            f"Retrievers: {num_retrievers}"
        )
        explanation.append(f"   - Content: {content_preview}...")
    
    return '\n'.join(explanation)


async def rerank_with_diversity(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 20,
    diversity_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Rerank results while promoting diversity.
    
    Uses Maximal Marginal Relevance (MMR) to balance relevance and diversity.
    
    Args:
        query: Search query
        results: Search results
        top_k: Number of results to return
        diversity_weight: Weight for diversity (0-1, higher = more diverse)
    
    Returns:
        Reranked diverse results
    """
    if not results or len(results) <= top_k:
        return await rerank_results(query, results, top_k)
    
    logger.info(f"Reranking with diversity (λ={1-diversity_weight:.2f})")
    
    # First, get base reranking scores
    reranked = await rerank_results(query, results, len(results))
    
    # MMR-based selection
    selected = []
    remaining = reranked.copy()
    
    # Select first result (highest score)
    if remaining:
        selected.append(remaining.pop(0))
    
    # Iteratively select diverse results
    while len(selected) < top_k and remaining:
        best_score = -float('inf')
        best_idx = 0
        
        for i, candidate in enumerate(remaining):
            # Relevance score
            relevance = candidate.get('rerank_score', 0)
            
            # Diversity score (max similarity to already selected)
            max_similarity = 0
            for selected_doc in selected:
                # Simple diversity: check content overlap
                similarity = _content_similarity(
                    candidate.get('content', ''),
                    selected_doc.get('content', '')
                )
                max_similarity = max(max_similarity, similarity)
            
            # MMR score: λ * relevance - (1-λ) * max_similarity
            mmr_score = (1 - diversity_weight) * relevance - diversity_weight * max_similarity
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i
        
        selected.append(remaining.pop(best_idx))
    
    logger.info(f"Diversity reranking complete: {len(selected)} diverse results")
    
    return selected


def _content_similarity(content1: str, content2: str) -> float:
    """
    Simple content similarity based on word overlap.
    
    Args:
        content1: First content string
        content2: Second content string
    
    Returns:
        Similarity score (0-1)
    """
    words1 = set(content1.lower().split())
    words2 = set(content2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0
