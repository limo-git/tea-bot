"""
Context compression for reducing token usage while preserving relevance.
Implements various compression strategies to keep only the most important information.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def compress_context(
    query: str,
    results: List[Dict[str, Any]],
    max_tokens: int = 4000,
    strategy: str = "relevance"
) -> List[Dict[str, Any]]:
    """
    Compress context to fit within token budget while preserving relevance.
    
    Args:
        query: Original search query
        results: Search results to compress
        max_tokens: Maximum token budget
        strategy: Compression strategy ('relevance', 'extractive', 'hybrid')
    
    Returns:
        Compressed results
    """
    if not results:
        return []
    
    logger.info(f"Compressing {len(results)} results with strategy '{strategy}', max_tokens={max_tokens}")
    
    if strategy == "relevance":
        compressed = _relevance_based_compression(query, results, max_tokens)
    elif strategy == "extractive":
        compressed = _extractive_compression(query, results, max_tokens)
    elif strategy == "hybrid":
        compressed = _hybrid_compression(query, results, max_tokens)
    else:
        logger.warning(f"Unknown compression strategy '{strategy}', using relevance")
        compressed = _relevance_based_compression(query, results, max_tokens)
    
    logger.info(f"Compression complete: {len(results)} -> {len(compressed)} results")
    
    return compressed


def _relevance_based_compression(
    query: str,
    results: List[Dict[str, Any]],
    max_tokens: int
) -> List[Dict[str, Any]]:
    """
    Keep top results by relevance score until token budget is reached.
    
    Simple but effective: assumes results are already ranked by relevance.
    """
    compressed = []
    total_tokens = 0
    
    for result in results:
        # Estimate tokens (rough: ~4 chars per token)
        content = result.get('content', '')
        estimated_tokens = len(content) // 4
        
        if total_tokens + estimated_tokens > max_tokens:
            logger.info(f"Token budget reached: {total_tokens}/{max_tokens}")
            break
        
        compressed.append(result)
        total_tokens += estimated_tokens
    
    return compressed


def _extractive_compression(
    query: str,
    results: List[Dict[str, Any]],
    max_tokens: int
) -> List[Dict[str, Any]]:
    """
    Extract only the most relevant sentences from each document.
    
    Keeps documents but compresses their content to key sentences.
    """
    query_terms = set(query.lower().split())
    compressed = []
    total_tokens = 0
    
    for result in results:
        content = result.get('content', '')
        
        # Split into sentences (simple split on . ! ?)
        sentences = [s.strip() for s in content.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        if not sentences:
            continue
        
        # Score each sentence by query term overlap
        sentence_scores = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for term in query_terms if term in sentence_lower)
            sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Build compressed content
        compressed_content = []
        sentence_tokens = 0
        
        for sentence, score in sentence_scores:
            sentence_token_est = len(sentence) // 4
            
            if total_tokens + sentence_tokens + sentence_token_est > max_tokens:
                break
            
            if score > 0:  # Only include sentences with query terms
                compressed_content.append(sentence)
                sentence_tokens += sentence_token_est
        
        if compressed_content:
            compressed_result = result.copy()
            compressed_result['content'] = '. '.join(compressed_content) + '.'
            compressed_result['compressed'] = True
            compressed_result['original_length'] = len(content)
            compressed.append(compressed_result)
            total_tokens += sentence_tokens
    
    logger.info(f"Extractive compression: {total_tokens} tokens used")
    
    return compressed


def _hybrid_compression(
    query: str,
    results: List[Dict[str, Any]],
    max_tokens: int
) -> List[Dict[str, Any]]:
    """
    Hybrid approach: keep top results fully, compress lower-ranked results.
    
    Strategy:
    - Top 5 results: keep full content
    - Next 10 results: extractive compression
    - Rest: discard
    """
    if not results:
        return []
    
    compressed = []
    total_tokens = 0
    
    # Keep top 5 results fully
    top_results = results[:5]
    for result in top_results:
        content = result.get('content', '')
        estimated_tokens = len(content) // 4
        
        if total_tokens + estimated_tokens > max_tokens:
            break
        
        compressed.append(result)
        total_tokens += estimated_tokens
    
    # Compress next 10 results
    remaining_budget = max_tokens - total_tokens
    if remaining_budget > 0 and len(results) > 5:
        middle_results = results[5:15]
        compressed_middle = _extractive_compression(
            query,
            middle_results,
            remaining_budget
        )
        compressed.extend(compressed_middle)
    
    logger.info(f"Hybrid compression: {len(compressed)} results, ~{total_tokens} tokens")
    
    return compressed


def remove_redundant_content(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate or highly similar content.
    
    Args:
        results: Search results
    
    Returns:
        Deduplicated results
    """
    if not results:
        return []
    
    unique_results = []
    seen_content = set()
    
    for result in results:
        content = result.get('content', '').strip().lower()
        
        # Skip empty content
        if not content:
            continue
        
        # Check for exact duplicates
        if content in seen_content:
            logger.debug(f"Skipping duplicate content: {content[:50]}")
            continue
        
        # Check for high similarity (simple: 80% word overlap)
        is_similar = False
        content_words = set(content.split())
        
        for seen in seen_content:
            seen_words = set(seen.split())
            
            if not content_words or not seen_words:
                continue
            
            intersection = content_words & seen_words
            union = content_words | seen_words
            
            similarity = len(intersection) / len(union) if union else 0
            
            if similarity > 0.8:
                logger.debug(f"Skipping similar content (sim={similarity:.2f}): {content[:50]}")
                is_similar = True
                break
        
        if not is_similar:
            seen_content.add(content)
            unique_results.append(result)
    
    logger.info(f"Deduplication: {len(results)} -> {len(unique_results)} results")
    
    return unique_results


def estimate_token_count(results: List[Dict[str, Any]]) -> int:
    """
    Estimate total token count for results.
    
    Args:
        results: Search results
    
    Returns:
        Estimated token count
    """
    total_chars = sum(len(r.get('content', '')) for r in results)
    # Rough estimate: 4 characters per token
    return total_chars // 4


def compress_to_budget(
    query: str,
    results: List[Dict[str, Any]],
    token_budget: int
) -> List[Dict[str, Any]]:
    """
    Compress results to fit exactly within token budget.
    
    Uses multiple strategies in sequence:
    1. Remove redundant content
    2. Hybrid compression
    3. Final truncation if needed
    
    Args:
        query: Search query
        results: Search results
        token_budget: Maximum tokens allowed
    
    Returns:
        Compressed results within budget
    """
    logger.info(f"Compressing to budget: {token_budget} tokens")
    
    # Step 1: Remove redundancy
    unique_results = remove_redundant_content(results)
    current_tokens = estimate_token_count(unique_results)
    logger.info(f"After deduplication: {current_tokens} tokens")
    
    if current_tokens <= token_budget:
        return unique_results
    
    # Step 2: Hybrid compression
    compressed = _hybrid_compression(query, unique_results, token_budget)
    current_tokens = estimate_token_count(compressed)
    logger.info(f"After hybrid compression: {current_tokens} tokens")
    
    if current_tokens <= token_budget:
        return compressed
    
    # Step 3: Final truncation (keep top results only)
    final_results = []
    total_tokens = 0
    
    for result in compressed:
        content = result.get('content', '')
        estimated_tokens = len(content) // 4
        
        if total_tokens + estimated_tokens > token_budget:
            break
        
        final_results.append(result)
        total_tokens += estimated_tokens
    
    logger.info(f"Final compression: {len(final_results)} results, {total_tokens} tokens")
    
    return final_results
