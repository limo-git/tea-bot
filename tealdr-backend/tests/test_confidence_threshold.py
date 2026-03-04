"""
Test suite for confidence threshold gating in vector search.
Tests P0.2: Confidence threshold filtering (>= 0.35).
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from retrieval.vector_search import vector_search, CONFIDENCE_THRESHOLD


class TestConfidenceThreshold:
    """Test that confidence threshold filtering works correctly."""
    
    @pytest.mark.asyncio
    async def test_filters_low_confidence_results(self):
        """Test that results below confidence threshold are filtered out."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768  # Mock embedding
            
            # Mock search results with varying similarity scores
            mock_search.return_value = [
                {"content": "High relevance", "similarity": 0.85},
                {"content": "Medium relevance", "similarity": 0.50},
                {"content": "Threshold boundary", "similarity": 0.35},
                {"content": "Below threshold", "similarity": 0.30},
                {"content": "Very low", "similarity": 0.10},
            ]
            
            results = await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Should only return results >= 0.35
            assert len(results) == 3
            assert all(msg['similarity'] >= CONFIDENCE_THRESHOLD for msg in results)
            assert results[0]['similarity'] == 0.85
            assert results[1]['similarity'] == 0.50
            assert results[2]['similarity'] == 0.35
    
    @pytest.mark.asyncio
    async def test_returns_empty_when_all_below_threshold(self):
        """Test that empty list is returned when all results are below threshold."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768
            
            # All results below threshold
            mock_search.return_value = [
                {"content": "Low relevance", "similarity": 0.25},
                {"content": "Very low", "similarity": 0.15},
                {"content": "Extremely low", "similarity": 0.05},
            ]
            
            results = await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Should return empty list
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_preserves_order_after_filtering(self):
        """Test that result order is preserved after confidence filtering."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768
            
            # Results in descending similarity order
            mock_search.return_value = [
                {"content": "First", "similarity": 0.90},
                {"content": "Second", "similarity": 0.70},
                {"content": "Third - below threshold", "similarity": 0.20},
                {"content": "Fourth", "similarity": 0.45},
                {"content": "Fifth - below threshold", "similarity": 0.30},
            ]
            
            results = await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Should maintain order: First, Second, Fourth
            assert len(results) == 3
            assert results[0]['content'] == "First"
            assert results[1]['content'] == "Second"
            assert results[2]['content'] == "Fourth"
    
    @pytest.mark.asyncio
    async def test_handles_missing_similarity_scores(self):
        """Test that messages without similarity scores are filtered out."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768
            
            # Mix of results with and without similarity scores
            mock_search.return_value = [
                {"content": "Has score", "similarity": 0.80},
                {"content": "No score"},  # Missing similarity
                {"content": "Has score", "similarity": 0.40},
            ]
            
            results = await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Should only return results with similarity >= threshold
            assert len(results) == 2
            assert all('similarity' in msg for msg in results)
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_not_applied_to_summarization(self):
        """Test that confidence threshold is NOT applied to summarization queries."""
        with patch('retrieval.vector_search.supabase_client.get_messages_by_timerange') as mock_timerange:
            
            # Mock time-based results (no similarity scores needed)
            mock_timerange.return_value = [
                {"content": "Recent message 1"},
                {"content": "Recent message 2"},
                {"content": "Recent message 3"},
            ]
            
            results = await vector_search(
                query="what did I miss",
                server_id=123456,
                intent="summarization"
            )
            
            # Should return all results (summarization doesn't use confidence threshold)
            assert len(results) == 3
            # All should have similarity = 1.0 (assigned by vector_search)
            assert all(msg['similarity'] == 1.0 for msg in results)
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_value(self):
        """Test that confidence threshold is set to 0.35."""
        assert CONFIDENCE_THRESHOLD == 0.35


class TestConfidenceThresholdIntegration:
    """Integration tests for confidence threshold in query pipeline."""
    
    def test_confidence_threshold_constant_value(self):
        """Test that confidence threshold constant is set to 0.35."""
        from retrieval.vector_search import CONFIDENCE_THRESHOLD
        
        assert CONFIDENCE_THRESHOLD == 0.35
    
    @pytest.mark.asyncio
    async def test_vector_search_filters_by_threshold(self):
        """Test that vector_search function actually filters results by confidence threshold."""
        from retrieval.vector_search import vector_search, CONFIDENCE_THRESHOLD
        
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768
            
            # Return mix of high and low confidence results
            mock_search.return_value = [
                {"content": "High confidence", "similarity": 0.80},
                {"content": "Low confidence", "similarity": 0.20},
                {"content": "Medium confidence", "similarity": 0.50},
            ]
            
            results = await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Should only return results >= threshold
            assert len(results) == 2
            assert all(msg['similarity'] >= CONFIDENCE_THRESHOLD for msg in results)


class TestConfidenceThresholdLogging:
    """Test that confidence threshold filtering is properly logged."""
    
    @pytest.mark.asyncio
    async def test_logs_filtering_statistics(self):
        """Test that filtering statistics are logged."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search, \
             patch('retrieval.vector_search.logger') as mock_logger:
            
            mock_embed.return_value = [0.1] * 768
            
            # 5 results, 2 below threshold
            mock_search.return_value = [
                {"content": "High", "similarity": 0.80},
                {"content": "Medium", "similarity": 0.50},
                {"content": "Low", "similarity": 0.30},
                {"content": "Very low", "similarity": 0.20},
                {"content": "Threshold", "similarity": 0.35},
            ]
            
            await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Verify logging of filtering statistics
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("Confidence threshold filtering" in str(call) for call in log_calls)
            assert any("removed 2 low-confidence results" in str(call) for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_logs_warning_when_no_results_pass_threshold(self):
        """Test that warning is logged when no results pass threshold."""
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search, \
             patch('retrieval.vector_search.logger') as mock_logger:
            
            mock_embed.return_value = [0.1] * 768
            
            # All below threshold
            mock_search.return_value = [
                {"content": "Low", "similarity": 0.25},
                {"content": "Very low", "similarity": 0.15},
            ]
            
            await vector_search(
                query="test query",
                server_id=123456,
                intent="lookup"
            )
            
            # Verify warning was logged
            assert mock_logger.warning.called
            warning_call = str(mock_logger.warning.call_args)
            assert "No results passed confidence threshold" in warning_call


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
