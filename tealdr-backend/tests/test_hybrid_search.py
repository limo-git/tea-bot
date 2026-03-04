"""
Test suite for BM25 hybrid search functionality.
Tests P1.2: Hybrid dense + sparse search with Reciprocal Rank Fusion.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from database.supabase_client import SupabaseClient


class TestBM25Search:
    """Test BM25 full-text search functionality."""
    
    @pytest.mark.asyncio
    async def test_bm25_search_returns_results(self):
        """Test that BM25 search returns results for matching queries."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.text_search.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {"message_id": 1, "content": "Docker deployment"},
                {"message_id": 2, "content": "Docker container"},
            ])
            mock_table.return_value = mock_chain
            
            results = await client.bm25_search("docker", server_id=123456, limit=50)
            
            assert len(results) == 2
            assert all('bm25_rank' in msg for msg in results)
            assert results[0]['bm25_rank'] > results[1]['bm25_rank']  # Descending order
    
    @pytest.mark.asyncio
    async def test_bm25_search_handles_multi_word_queries(self):
        """Test that BM25 search handles multi-word queries correctly."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.text_search.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {"message_id": 1, "content": "Docker deployment issues"},
            ])
            mock_table.return_value = mock_chain
            
            results = await client.bm25_search("docker deployment", server_id=123456)
            
            # Verify text_search was called with correct tsquery
            assert mock_chain.text_search.called
            call_args = mock_chain.text_search.call_args
            assert 'docker & deployment' in str(call_args)
    
    @pytest.mark.asyncio
    async def test_bm25_search_filters_by_server_id(self):
        """Test that BM25 search filters by server_id."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.text_search.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[])
            mock_table.return_value = mock_chain
            
            await client.bm25_search("test", server_id=999)
            
            # Verify eq was called with server_id
            assert mock_chain.eq.called
            call_args = mock_chain.eq.call_args
            assert call_args[0] == ('server_id', 999)
    
    @pytest.mark.asyncio
    async def test_bm25_search_returns_empty_on_error(self):
        """Test that BM25 search returns empty list on error."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_table.side_effect = Exception("Database error")
            
            results = await client.bm25_search("test", server_id=123456)
            
            assert results == []


class TestHybridSearch:
    """Test hybrid search with Reciprocal Rank Fusion."""
    
    @pytest.mark.asyncio
    async def test_hybrid_search_combines_vector_and_bm25(self):
        """Test that hybrid search combines vector and BM25 results."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            # Mock vector search results
            mock_vector.return_value = [
                {"message_id": 1, "content": "Python programming", "similarity": 0.9},
                {"message_id": 2, "content": "Python tutorial", "similarity": 0.8},
            ]
            
            # Mock BM25 search results
            mock_bm25.return_value = [
                {"message_id": 2, "content": "Python tutorial", "bm25_rank": 0.95},
                {"message_id": 3, "content": "Python basics", "bm25_rank": 0.85},
            ]
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("python", embedding, server_id=123456)
            
            # Should combine unique messages from both searches
            assert len(results) >= 2
            assert all('similarity' in msg for msg in results)
    
    @pytest.mark.asyncio
    async def test_hybrid_search_rrf_scoring(self):
        """Test that Reciprocal Rank Fusion scoring works correctly."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            # Message appears in both results (should get higher fused score)
            mock_vector.return_value = [
                {"message_id": 1, "content": "Docker deployment"},
            ]
            
            mock_bm25.return_value = [
                {"message_id": 1, "content": "Docker deployment"},
                {"message_id": 2, "content": "Docker container"},
            ]
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("docker", embedding, server_id=123456)
            
            # Message 1 should rank higher (appears in both)
            assert results[0]['message_id'] == 1
            assert results[0]['similarity'] > results[1]['similarity']
    
    @pytest.mark.asyncio
    async def test_hybrid_search_respects_limit(self):
        """Test that hybrid search respects the limit parameter."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            # Return many results
            mock_vector.return_value = [
                {"message_id": i, "content": f"Message {i}"} for i in range(30)
            ]
            mock_bm25.return_value = [
                {"message_id": i+30, "content": f"Message {i+30}"} for i in range(30)
            ]
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("test", embedding, server_id=123456, limit=10)
            
            # Should return exactly 10 results
            assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_hybrid_search_handles_empty_vector_results(self):
        """Test that hybrid search handles empty vector search results."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            mock_vector.return_value = []
            mock_bm25.return_value = [
                {"message_id": 1, "content": "Docker deployment"},
            ]
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("docker", embedding, server_id=123456)
            
            # Should still return BM25 results
            assert len(results) >= 1
    
    @pytest.mark.asyncio
    async def test_hybrid_search_handles_empty_bm25_results(self):
        """Test that hybrid search handles empty BM25 results."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            mock_vector.return_value = [
                {"message_id": 1, "content": "Python programming"},
            ]
            mock_bm25.return_value = []
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("python", embedding, server_id=123456)
            
            # Should still return vector results
            assert len(results) >= 1
    
    @pytest.mark.asyncio
    async def test_hybrid_search_fallback_on_error(self):
        """Test that hybrid search falls back to vector search on error."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            mock_vector.return_value = [
                {"message_id": 1, "content": "Fallback result"},
            ]
            mock_bm25.side_effect = Exception("BM25 error")
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("test", embedding, server_id=123456)
            
            # Should return vector search results as fallback
            assert len(results) >= 1


class TestReciprocalRankFusion:
    """Test Reciprocal Rank Fusion algorithm."""
    
    @pytest.mark.asyncio
    async def test_rrf_formula_k_equals_60(self):
        """Test that RRF uses k=60 as specified in research."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            # Single result at rank 0
            mock_vector.return_value = [
                {"message_id": 1, "content": "Test"},
            ]
            mock_bm25.return_value = []
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("test", embedding, server_id=123456)
            
            # RRF score should be 1/(60+0+1) = 1/61 ≈ 0.0164
            expected_score = 1 / 61
            assert abs(results[0]['similarity'] - expected_score) < 0.001
    
    @pytest.mark.asyncio
    async def test_rrf_boosts_messages_in_both_results(self):
        """Test that messages appearing in both searches get boosted scores."""
        client = SupabaseClient()
        
        with patch.object(client, 'semantic_search') as mock_vector, \
             patch.object(client, 'bm25_search') as mock_bm25:
            
            # Message 1 appears in both (rank 0 in both)
            # Message 2 only in vector (rank 1)
            mock_vector.return_value = [
                {"message_id": 1, "content": "Both"},
                {"message_id": 2, "content": "Vector only"},
            ]
            mock_bm25.return_value = [
                {"message_id": 1, "content": "Both"},
            ]
            
            embedding = [0.1] * 768
            results = await client.hybrid_search("test", embedding, server_id=123456)
            
            # Message 1 should have higher score (appears in both)
            msg1 = next(r for r in results if r['message_id'] == 1)
            msg2 = next(r for r in results if r['message_id'] == 2)
            assert msg1['similarity'] > msg2['similarity']


class TestHybridSearchIntegration:
    """Integration tests for hybrid search in /lookup command."""
    
    def test_hybrid_search_method_exists(self):
        """Test that hybrid_search method exists on SupabaseClient."""
        client = SupabaseClient()
        assert hasattr(client, 'hybrid_search')
        assert callable(client.hybrid_search)
    
    def test_bm25_search_method_exists(self):
        """Test that bm25_search method exists on SupabaseClient."""
        client = SupabaseClient()
        assert hasattr(client, 'bm25_search')
        assert callable(client.bm25_search)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
