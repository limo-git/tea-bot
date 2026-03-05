"""
Test suite for P3: CRAG Refinement Loop
Tests the Corrective RAG system for handling low-confidence queries.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from retrieval.crag_refiner import (
    calculate_retrieval_confidence,
    should_refine_query,
    generate_refined_queries,
    refine_and_retrieve,
    assess_answer_quality
)


class TestConfidenceCalculation:
    """Test retrieval confidence scoring."""
    
    def test_calculate_confidence_with_results(self):
        """Test confidence calculation with valid results."""
        results = [
            {'similarity': 0.8},
            {'similarity': 0.6},
            {'similarity': 0.4}
        ]
        
        confidence = calculate_retrieval_confidence(results)
        assert confidence == pytest.approx(0.6, rel=0.01)
    
    def test_calculate_confidence_empty_results(self):
        """Test confidence with no results."""
        confidence = calculate_retrieval_confidence([])
        assert confidence == 0.0
    
    def test_calculate_confidence_missing_similarity(self):
        """Test confidence when some results lack similarity scores."""
        results = [
            {'similarity': 0.8},
            {'content': 'no similarity'},
            {'similarity': 0.6}
        ]
        
        confidence = calculate_retrieval_confidence(results)
        # Should use 0.0 for missing scores: (0.8 + 0.0 + 0.6) / 3
        assert confidence == pytest.approx(0.467, rel=0.01)


class TestRefinementDecision:
    """Test when to trigger query refinement."""
    
    def test_should_refine_low_confidence(self):
        """Test refinement triggers for low confidence results."""
        results = [
            {'similarity': 0.3},
            {'similarity': 0.2},
            {'similarity': 0.35}
        ]
        
        should_refine = should_refine_query(results, "lookup")
        assert should_refine is True
    
    def test_should_not_refine_high_confidence(self):
        """Test refinement doesn't trigger for high confidence."""
        results = [
            {'similarity': 0.8},
            {'similarity': 0.7},
            {'similarity': 0.75}
        ]
        
        should_refine = should_refine_query(results, "lookup")
        assert should_refine is False
    
    def test_should_not_refine_summarization(self):
        """Test refinement skipped for summarization queries."""
        results = [
            {'similarity': 0.2},
            {'similarity': 0.1},
            {'similarity': 0.15}
        ]
        
        # Even with low confidence, don't refine summarization
        should_refine = should_refine_query(results, "summarization")
        assert should_refine is False
    
    def test_should_not_refine_user_messages(self):
        """Test refinement skipped for user_messages queries."""
        results = [
            {'similarity': 0.2},
            {'similarity': 0.1},
            {'similarity': 0.15}
        ]
        
        # Don't refine user_messages (already filtered by author)
        should_refine = should_refine_query(results, "user_messages")
        assert should_refine is False
    
    def test_should_not_refine_too_few_results(self):
        """Test refinement skipped when too few results to assess."""
        results = [
            {'similarity': 0.2},
            {'similarity': 0.1}
        ]
        
        # Only 2 results, need at least 3
        should_refine = should_refine_query(results, "lookup")
        assert should_refine is False


class TestQueryRefinement:
    """Test refined query generation."""
    
    @pytest.mark.asyncio
    async def test_generate_refined_queries_success(self):
        """Test successful generation of refined queries."""
        with patch('retrieval.crag_refiner._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = '["what is docker", "docker containerization", "docker platform"]'
            
            mock_client_instance = Mock()
            mock_client_instance.models.generate_content.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            refined = await generate_refined_queries(
                "tell me about docker",
                "lookup",
                0.3
            )
            
            assert len(refined) == 3
            assert "docker" in refined[0].lower()
    
    @pytest.mark.asyncio
    async def test_generate_refined_queries_json_error(self):
        """Test handling of invalid JSON response."""
        with patch('retrieval.crag_refiner._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'not valid json'
            
            mock_client_instance = Mock()
            mock_client_instance.models.generate_content.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            refined = await generate_refined_queries("query", "lookup", 0.3)
            
            assert refined == []
    
    @pytest.mark.asyncio
    async def test_generate_refined_queries_limits_count(self):
        """Test that refined queries are limited to 3."""
        with patch('retrieval.crag_refiner._get_client') as mock_client:
            mock_response = Mock()
            # Return 5 queries
            mock_response.text = '["q1", "q2", "q3", "q4", "q5"]'
            
            mock_client_instance = Mock()
            mock_client_instance.models.generate_content.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            refined = await generate_refined_queries("query", "lookup", 0.3)
            
            # Should be limited to 3
            assert len(refined) == 3


class TestCRAGRefinementLoop:
    """Test the full CRAG refinement loop."""
    
    @pytest.mark.asyncio
    async def test_refine_and_retrieve_low_confidence(self):
        """Test refinement loop activates for low confidence."""
        original_results = [
            {'message_id': '1', 'similarity': 0.3, 'content': 'msg1'},
            {'message_id': '2', 'similarity': 0.2, 'content': 'msg2'},
            {'message_id': '3', 'similarity': 0.25, 'content': 'msg3'}
        ]
        
        with patch('retrieval.crag_refiner.generate_refined_queries') as mock_gen, \
             patch('retrieval.vector_search.vector_search') as mock_search:
            
            # Mock refined query generation
            mock_gen.return_value = ["refined query 1", "refined query 2"]
            
            # Mock vector search for refined queries
            mock_search.return_value = [
                {'message_id': '4', 'similarity': 0.7, 'content': 'msg4'},
                {'message_id': '5', 'similarity': 0.65, 'content': 'msg5'}
            ]
            
            results = await refine_and_retrieve(
                original_query="test query",
                original_results=original_results,
                intent="lookup",
                server_id=123
            )
            
            # Should have original + refined results
            assert len(results) > len(original_results)
            assert mock_gen.called
            assert mock_search.call_count == 2  # Called for each refined query
    
    @pytest.mark.asyncio
    async def test_refine_and_retrieve_high_confidence(self):
        """Test refinement skipped for high confidence."""
        original_results = [
            {'message_id': '1', 'similarity': 0.8, 'content': 'msg1'},
            {'message_id': '2', 'similarity': 0.75, 'content': 'msg2'},
            {'message_id': '3', 'similarity': 0.7, 'content': 'msg3'}
        ]
        
        with patch('retrieval.crag_refiner.generate_refined_queries') as mock_gen:
            results = await refine_and_retrieve(
                original_query="test query",
                original_results=original_results,
                intent="lookup",
                server_id=123
            )
            
            # Should return original results unchanged
            assert results == original_results
            assert not mock_gen.called
    
    @pytest.mark.asyncio
    async def test_refine_and_retrieve_deduplicates(self):
        """Test that refined results are deduplicated."""
        original_results = [
            {'message_id': '1', 'similarity': 0.3, 'content': 'msg1'},
            {'message_id': '2', 'similarity': 0.2, 'content': 'msg2'},
            {'message_id': '3', 'similarity': 0.25, 'content': 'msg3'}
        ]
        
        with patch('retrieval.crag_refiner.generate_refined_queries') as mock_gen, \
             patch('retrieval.vector_search.vector_search') as mock_search:
            
            mock_gen.return_value = ["refined query"]
            
            # Return some duplicate message_ids
            mock_search.return_value = [
                {'message_id': '1', 'similarity': 0.8, 'content': 'msg1'},  # Duplicate
                {'message_id': '4', 'similarity': 0.7, 'content': 'msg4'}   # New
            ]
            
            results = await refine_and_retrieve(
                original_query="test query",
                original_results=original_results,
                intent="lookup",
                server_id=123
            )
            
            # Should have 4 unique messages (3 original + 1 new)
            message_ids = [r['message_id'] for r in results]
            assert len(message_ids) == len(set(message_ids))  # All unique
            assert '4' in message_ids  # New message included
    
    @pytest.mark.asyncio
    async def test_refine_and_retrieve_sorts_by_similarity(self):
        """Test that final results are sorted by similarity."""
        original_results = [
            {'message_id': '1', 'similarity': 0.3, 'content': 'msg1'},
            {'message_id': '2', 'similarity': 0.2, 'content': 'msg2'},
            {'message_id': '3', 'similarity': 0.25, 'content': 'msg3'}
        ]
        
        with patch('retrieval.crag_refiner.generate_refined_queries') as mock_gen, \
             patch('retrieval.vector_search.vector_search') as mock_search:
            
            mock_gen.return_value = ["refined query"]
            mock_search.return_value = [
                {'message_id': '4', 'similarity': 0.9, 'content': 'msg4'},
                {'message_id': '5', 'similarity': 0.85, 'content': 'msg5'}
            ]
            
            results = await refine_and_retrieve(
                original_query="test query",
                original_results=original_results,
                intent="lookup",
                server_id=123
            )
            
            # Should be sorted by similarity descending
            similarities = [r['similarity'] for r in results]
            assert similarities == sorted(similarities, reverse=True)
            assert results[0]['message_id'] == '4'  # Highest similarity first


class TestAnswerQualityAssessment:
    """Test answer quality assessment."""
    
    @pytest.mark.asyncio
    async def test_assess_high_quality_answer(self):
        """Test assessment of high-quality answer."""
        context = [
            {'message_id': '1', 'content': 'msg1'},
            {'message_id': '2', 'content': 'msg2'}
        ]
        
        quality = await assess_answer_quality(
            query="What is Docker?",
            answer="Docker is a containerization platform that allows developers to package applications with their dependencies into containers.",
            context=context
        )
        
        assert quality['has_context'] is True
        assert quality['is_substantive'] is True
        assert quality['not_fallback'] is True
        assert quality['is_high_quality'] is True
        assert quality['overall_score'] >= 0.7
    
    @pytest.mark.asyncio
    async def test_assess_low_quality_answer(self):
        """Test assessment of low-quality answer."""
        quality = await assess_answer_quality(
            query="What is Docker?",
            answer="I don't know about Docker.",
            context=[]
        )
        
        assert quality['has_context'] is False
        assert quality['not_fallback'] is False
        assert quality['is_high_quality'] is False
        assert quality['overall_score'] < 0.7
    
    @pytest.mark.asyncio
    async def test_assess_answer_with_context_but_short(self):
        """Test assessment of answer with context but too short."""
        context = [{'message_id': '1', 'content': 'msg1'}]
        
        quality = await assess_answer_quality(
            query="What is Docker?",
            answer="It's a tool.",  # Too short
            context=context
        )
        
        assert quality['has_context'] is True
        assert quality['is_substantive'] is False
        assert quality['overall_score'] <= 0.7


class TestCRAGIntegration:
    """Test CRAG integration with query pipeline."""
    
    @pytest.mark.asyncio
    async def test_crag_preserves_filters(self):
        """Test that CRAG refinement preserves filters (author, channel, etc)."""
        original_results = [
            {'message_id': '1', 'similarity': 0.3},
            {'message_id': '2', 'similarity': 0.2},
            {'message_id': '3', 'similarity': 0.25}
        ]
        
        with patch('retrieval.crag_refiner.generate_refined_queries') as mock_gen, \
             patch('retrieval.vector_search.vector_search') as mock_search:
            
            mock_gen.return_value = ["refined query"]
            mock_search.return_value = []
            
            await refine_and_retrieve(
                original_query="test",
                original_results=original_results,
                intent="lookup",
                server_id=123,
                author_id=456,
                channel_id=789,
                mentions_user_id=999
            )
            
            # Verify filters were passed to vector_search
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs['server_id'] == 123
            assert call_kwargs['author_id'] == 456
            assert call_kwargs['channel_id'] == 789
            assert call_kwargs['mentions_user_id'] == 999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
