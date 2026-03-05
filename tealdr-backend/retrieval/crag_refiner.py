"""
P3: CRAG (Corrective RAG) Refinement Loop
Handles low-confidence queries by refining and re-retrieving.
"""

import logging
from typing import Dict, List, Optional
from google import genai
from config import Config

logger = logging.getLogger(__name__)

_client: genai.Client | None = None

# Confidence thresholds for CRAG activation
LOW_CONFIDENCE_THRESHOLD = 0.4  # Trigger refinement if avg similarity < 0.4
MIN_RESULTS_FOR_CONFIDENCE = 3  # Need at least 3 results to calculate confidence

QUERY_REFINEMENT_PROMPT = """You are a query refinement assistant. Your job is to improve search queries that didn't return good results.

Original query: "{original_query}"
Query intent: {intent}
Search results quality: Low (average similarity: {avg_similarity:.2f})

Generate 2-3 alternative search queries that might find better results. Consider:
1. Using different keywords or synonyms
2. Breaking down complex queries into simpler parts
3. Adding context or specificity
4. Removing ambiguous terms

Return ONLY a JSON array of refined queries:
["refined query 1", "refined query 2", "refined query 3"]

JSON only:"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


def calculate_retrieval_confidence(results: List[Dict]) -> float:
    """
    Calculate confidence score for retrieval results.
    
    Args:
        results: List of retrieved messages with similarity scores
        
    Returns:
        Average similarity score (0.0 to 1.0)
    """
    if not results:
        return 0.0
    
    similarities = [msg.get('similarity', 0.0) for msg in results]
    if not similarities:
        return 0.0
    
    return sum(similarities) / len(similarities)


def should_refine_query(results: List[Dict], intent: str) -> bool:
    """
    Determine if query should be refined based on retrieval quality.
    
    Args:
        results: Retrieved messages
        intent: Query intent type
        
    Returns:
        True if refinement is needed
    """
    # Don't refine for summarization queries (they use time-based retrieval)
    if intent == "summarization":
        return False
    
    # Don't refine for user_messages (already filtered by author)
    if intent == "user_messages":
        return False
    
    # Need minimum results to assess confidence
    if len(results) < MIN_RESULTS_FOR_CONFIDENCE:
        logger.info(f"Too few results ({len(results)}) to assess confidence, skipping refinement")
        return False
    
    # Calculate average confidence
    avg_confidence = calculate_retrieval_confidence(results)
    
    if avg_confidence < LOW_CONFIDENCE_THRESHOLD:
        logger.info(f"Low retrieval confidence ({avg_confidence:.2f}), will refine query")
        return True
    
    return False


async def generate_refined_queries(original_query: str, intent: str, avg_similarity: float) -> List[str]:
    """
    Generate refined search queries using LLM.
    
    Args:
        original_query: The original user query
        intent: Query intent type
        avg_similarity: Average similarity score of original results
        
    Returns:
        List of refined query strings
    """
    try:
        client = _get_client()
        
        prompt = QUERY_REFINEMENT_PROMPT.format(
            original_query=original_query,
            intent=intent,
            avg_similarity=avg_similarity
        )
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={
                'temperature': 0.7,
                'max_output_tokens': 200,
            }
        )
        
        # Parse JSON response
        import json
        refined_queries = json.loads(response.text.strip())
        
        if not isinstance(refined_queries, list):
            logger.warning(f"Refined queries not a list: {refined_queries}")
            return []
        
        logger.info(f"Generated {len(refined_queries)} refined queries")
        return refined_queries[:3]  # Max 3 refinements
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse refined queries JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error generating refined queries: {e}")
        return []


async def refine_and_retrieve(
    original_query: str,
    original_results: List[Dict],
    intent: str,
    server_id: int,
    author_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    time_range: Optional[tuple] = None,
    mentions_user_id: Optional[int] = None
) -> List[Dict]:
    """
    CRAG refinement loop: Generate refined queries and re-retrieve.
    
    Args:
        original_query: Original user query
        original_results: Results from original retrieval
        intent: Query intent
        server_id: Discord server ID
        author_id: Optional author filter
        channel_id: Optional channel filter
        time_range: Optional time range filter
        mentions_user_id: Optional mentions filter
        
    Returns:
        Combined and deduplicated results from original + refined queries
    """
    # Check if refinement is needed
    if not should_refine_query(original_results, intent):
        return original_results
    
    avg_similarity = calculate_retrieval_confidence(original_results)
    
    # Generate refined queries
    refined_queries = await generate_refined_queries(original_query, intent, avg_similarity)
    
    if not refined_queries:
        logger.warning("No refined queries generated, returning original results")
        return original_results
    
    # Re-retrieve with refined queries
    from retrieval.vector_search import vector_search
    
    all_results = list(original_results)  # Start with original results
    seen_message_ids = {msg.get('message_id') for msg in original_results if msg.get('message_id')}
    
    for refined_query in refined_queries:
        logger.info(f"Re-retrieving with refined query: '{refined_query[:60]}...'")
        
        refined_results = await vector_search(
            query=refined_query,
            server_id=server_id,
            author_id=author_id,
            channel_id=channel_id,
            time_range=time_range,
            intent=intent,
            mentions_user_id=mentions_user_id
        )
        
        # Deduplicate by message_id
        for msg in refined_results:
            msg_id = msg.get('message_id')
            if msg_id and msg_id not in seen_message_ids:
                all_results.append(msg)
                seen_message_ids.add(msg_id)
        
        logger.info(f"Refined query returned {len(refined_results)} results, {len(all_results)} total after dedup")
    
    # Re-sort by similarity
    all_results.sort(key=lambda x: x.get('similarity', 0.0), reverse=True)
    
    # Limit to top results
    max_results = Config.VECTOR_TOP_K * 2  # Allow more results from refinement
    final_results = all_results[:max_results]
    
    logger.info(f"CRAG refinement complete: {len(original_results)} -> {len(final_results)} results")
    
    return final_results


async def assess_answer_quality(query: str, answer: str, context: List[Dict]) -> Dict:
    """
    Assess the quality of a generated answer.
    
    Args:
        query: User's query
        answer: Generated answer
        context: Context messages used
        
    Returns:
        Dict with quality metrics
    """
    # Simple heuristics for answer quality
    quality = {
        'has_context': len(context) > 0,
        'answer_length': len(answer),
        'is_substantive': len(answer) > 50,
        'not_fallback': "I don't know" not in answer and "couldn't find" not in answer.lower(),
        'context_count': len(context)
    }
    
    # Calculate overall quality score
    score = 0.0
    if quality['has_context']:
        score += 0.3
    if quality['is_substantive']:
        score += 0.3
    if quality['not_fallback']:
        score += 0.4
    
    quality['overall_score'] = score
    quality['is_high_quality'] = score >= 0.7
    
    return quality
