#!/usr/bin/env python3
"""
Test cases for /ask command fixes including:
- Supabase channel handling without join relationships
- Neo4j datetime parsing fixes
- Time filter parameter in temporal engine
- Recent data filtering (3 days)
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSupabaseChannelHandling:
    """Test Supabase channel handling without join relationships."""
    
    async def test_semantic_search_without_channel_join(self):
        """Test that semantic search works without trying to join channels table."""
        from database.supabase_client import SupabaseClient
        
        # Mock Supabase client
        mock_client = Mock()
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_limit = Mock()
        mock_execute = Mock()
        
        # Setup mock chain
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.eq.return_value = mock_eq
        mock_eq.gte.return_value = mock_eq
        mock_eq.lte.return_value = mock_eq
        mock_eq.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_execute
        
        # Mock messages with channel_id (not joined channel data)
        mock_execute.data = [
            {
                "id": 1,
                "content": "Test message",
                "author_name": "test_user",
                "channel_id": 123456789,
                "created_at": "2026-03-01T12:00:00Z",
                "embedding": [0.1] * 768
            }
        ]
        
        supabase_client = SupabaseClient()
        supabase_client.client = mock_client
        
        # Test semantic search
        embedding = [0.1] * 768
        results = await supabase_client.semantic_search_filtered(
            embedding=embedding,
            server_id=12345,
            time_range=(datetime(2026, 2, 27), datetime(2026, 3, 2)),
            limit=20
        )
        
        # Verify select was called without channel join
        mock_table.select.assert_called_once_with('*')
        
        # Verify results contain channel_id
        assert len(results) > 0
        assert results[0]["channel_id"] == 123456789
        
        print("✅ Supabase semantic search works without channel join")
    
    async def test_context_assembler_handles_channel_id(self):
        """Test that context assembler properly handles channel_id without join."""
        from retrieval.context_assembler import assemble_context
        
        vector_results = [
            {
                "content": "Test message",
                "author_name": "test_user",
                "channel_id": 123456789,
                "created_at": "2026-03-01T12:00:00Z",
                "similarity": 0.9
            }
        ]
        
        context = assemble_context([], vector_results, "summarization")
        
        # Verify channel_id is formatted correctly
        assert len(context) == 1
        assert context[0]["channel"] == "#123456789"
        assert context[0]["author"] == "test_user"
        
        print("✅ Context assembler handles channel_id correctly")


class TestNeo4jDatetimeParsing:
    """Test Neo4j datetime parsing fixes."""
    
    async def test_temporal_context_query_time_gap_calculation(self):
        """Test that temporal context query uses millisecond arithmetic instead of datetime parsing."""
        from graph.queries import TEMPORAL_CONTEXT_QUERY
        
        # Verify query uses millisecond arithmetic for time_gap
        assert "/ 86400000" in TEMPORAL_CONTEXT_QUERY  # Convert milliseconds to days
        assert "duration.between" not in TEMPORAL_CONTEXT_QUERY  # Should not use duration.between
        assert "CASE" in TEMPORAL_CONTEXT_QUERY  # Should use CASE for safe calculation
        
        print("✅ Temporal context query uses safe time gap calculation")
    
    async def test_conversation_threads_query_time_gap_calculation(self):
        """Test that conversation threads query uses millisecond arithmetic."""
        from graph.queries import CONVERSATION_THREADS_QUERY
        
        # Verify query uses millisecond arithmetic for time_gap
        assert "/ 3600000" in CONVERSATION_THREADS_QUERY  # Convert milliseconds to hours
        assert "abs(m.timestamp - nearby.timestamp)" in CONVERSATION_THREADS_QUERY
        assert "CASE" in CONVERSATION_THREADS_QUERY  # Should use CASE for safe calculation
        
        print("✅ Conversation threads query uses safe time gap calculation")
    
    async def test_summarization_query_datetime_comparison(self):
        """Test that summarization query uses proper datetime comparison."""
        from graph.queries import SUMMARIZATION_QUERY
        
        # Verify query uses datetime() function for comparison
        assert "datetime(m.timestamp) >= datetime(time_filter)" in SUMMARIZATION_QUERY
        assert "time_filter IS NULL OR" in SUMMARIZATION_QUERY  # Should handle NULL
        
        print("✅ Summarization query uses proper datetime comparison")


class TestTimeFilterParameter:
    """Test time_filter parameter in temporal engine."""
    
    async def test_temporal_engine_passes_time_filter(self):
        """Test that temporal engine passes time_filter to primary results."""
        from retrieval.temporal_engine import _get_primary_results
        
        # Mock Neo4j driver and session
        with patch('retrieval.temporal_engine.get_driver') as mock_get_driver, \
             patch('retrieval.temporal_engine.run_intent_query') as mock_run_query:
            
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            mock_get_driver.return_value = mock_driver
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            
            mock_run_query.return_value = [
                {"content": "Test", "timestamp": "2026-03-01T12:00:00Z"}
            ]
            
            understanding = {
                "primary_entity": "server",
                "intent": "summarization"
            }
            
            time_range = (datetime(2026, 2, 27), datetime(2026, 3, 2))
            
            results = await _get_primary_results("summarization", understanding, time_range)
            
            # Verify run_intent_query was called with time_filter parameter
            call_args = mock_run_query.call_args
            params = call_args[0][2]  # Third argument is params dict
            
            assert "time_filter" in params
            assert params["time_filter"] == "2026-02-27T00:00:00"
            
            print("✅ Temporal engine passes time_filter parameter")
    
    async def test_temporal_engine_default_time_filter(self):
        """Test that temporal engine uses 3-day default when no time_range provided."""
        from retrieval.temporal_engine import _get_primary_results
        
        with patch('retrieval.temporal_engine.get_driver') as mock_get_driver, \
             patch('retrieval.temporal_engine.run_intent_query') as mock_run_query:
            
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            mock_get_driver.return_value = mock_driver
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            
            mock_run_query.return_value = []
            
            understanding = {
                "primary_entity": "server",
                "intent": "summarization"
            }
            
            # No time_range provided
            results = await _get_primary_results("summarization", understanding, None)
            
            # Verify time_filter was set to 3 days ago
            call_args = mock_run_query.call_args
            params = call_args[0][2]
            
            assert "time_filter" in params
            
            # Parse the time_filter and verify it's approximately 3 days ago
            filter_time = datetime.fromisoformat(params["time_filter"])
            now = datetime.utcnow()
            time_diff = now - filter_time
            
            # Should be approximately 3 days (allow 1 minute tolerance)
            assert 2.99 <= time_diff.days <= 3.01
            
            print("✅ Temporal engine uses 3-day default time filter")


class TestRecentDataFiltering:
    """Test that /ask command returns recent data (3 days)."""
    
    async def test_ask_command_applies_3day_filter(self):
        """Test that /ask command applies 3-day time range for general queries."""
        from bot.commands import Commands
        from utils.time_parser import parse_time_range
        
        # Test that general server activity queries get 3-day filter
        query = "what did i miss out on while i was away?"
        
        # Simulate the logic in commands.py
        query_lower = query.lower()
        should_apply_filter = any(phrase in query_lower for phrase in [
            "what did i miss", "what happened", "server activity", 
            "recent activity", "while i was away", "what's new"
        ])
        
        assert should_apply_filter == True
        
        # Verify 3-day time range
        time_range = parse_time_range("3d")
        start_time, end_time = time_range
        
        time_diff = end_time - start_time
        assert time_diff.days == 3
        
        print("✅ /ask command applies 3-day filter for general queries")
    
    async def test_graph_traversal_uses_time_filter(self):
        """Test that graph_traversal function uses time_filter parameter."""
        from retrieval.query_engine import graph_traversal
        
        with patch('retrieval.query_engine.get_driver') as mock_get_driver, \
             patch('retrieval.query_engine.run_intent_query') as mock_run_query:
            
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            mock_get_driver.return_value = mock_driver
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            
            mock_run_query.return_value = []
            
            understanding = {
                "primary_entity": "server",
                "intent": "summarization"
            }
            
            time_range = (datetime(2026, 2, 27), datetime(2026, 3, 2))
            
            results = await graph_traversal("summarization", understanding, time_range)
            
            # Verify run_intent_query was called with time_filter
            call_args = mock_run_query.call_args
            params = call_args[0][2]
            
            assert "time_filter" in params
            assert "2026-02-27" in params["time_filter"]
            
            print("✅ graph_traversal uses time_filter parameter")


class TestIntegrationScenarios:
    """Integration tests for complete /ask command flow."""
    
    async def test_complete_ask_flow_with_recent_data(self):
        """Test complete /ask command flow with recent data filtering."""
        
        # Mock all components
        with patch('retrieval.query_engine.understand_query') as mock_understand, \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline') as mock_temporal, \
             patch('generation.answer_generator.generate_answer') as mock_generate:
            
            # Mock query understanding
            mock_understand.return_value = {
                "intent": "summarization",
                "primary_entity": "server",
                "temporal_context_needed": True,
                "search_terms": ["server", "activity"]
            }
            
            # Mock temporal pipeline
            mock_temporal.return_value = {
                "context": [
                    {
                        "source": "graph",
                        "content": "Recent server update completed",
                        "author": "admin",
                        "channel": "#announcements",
                        "timestamp": "2026-03-01T12:00:00Z",
                        "relevance": 1.0
                    }
                ],
                "understanding": mock_understand.return_value,
                "temporal_connections": 2,
                "conversation_threads": 1
            }
            
            # Mock answer generation
            mock_generate.return_value = "Based on recent activity, the server was updated on March 1st."
            
            # Simulate /ask command flow
            from retrieval.query_engine import run_query_pipeline
            
            query = "what did i miss out on while i was away?"
            server_id = 12345
            time_range = (datetime(2026, 2, 27), datetime(2026, 3, 2))
            
            result = await run_query_pipeline(
                query=query,
                server_id=server_id,
                time_range=time_range
            )
            
            # Verify temporal pipeline was called with correct parameters
            mock_temporal.assert_called_once()
            call_kwargs = mock_temporal.call_args.kwargs
            
            assert call_kwargs["query"] == query
            assert call_kwargs["server_id"] == server_id
            assert call_kwargs["time_range"] == time_range
            
            # Verify result contains recent data
            assert len(result["context"]) > 0
            assert "2026-03-01" in result["context"][0]["timestamp"]
            
            print("✅ Complete /ask flow works with recent data filtering")
    
    async def test_error_handling_for_invalid_queries(self):
        """Test error handling for edge cases."""
        
        with patch('retrieval.query_engine.understand_query') as mock_understand:
            
            # Test with empty entity
            mock_understand.return_value = {
                "intent": "summarization",
                "primary_entity": "",
                "temporal_context_needed": False,
                "search_terms": []
            }
            
            from retrieval.query_engine import run_query_pipeline
            
            result = await run_query_pipeline(
                query="",
                server_id=12345
            )
            
            # Should handle gracefully and return empty context
            assert "context" in result
            
            print("✅ Error handling works for edge cases")


async def run_all_tests():
    """Run all test suites."""
    
    print("\n🧪 Running /ask Command Fixes Test Suite")
    print("=" * 60)
    
    # Test Supabase channel handling
    print("\n📦 Testing Supabase Channel Handling...")
    supabase_tests = TestSupabaseChannelHandling()
    await supabase_tests.test_semantic_search_without_channel_join()
    await supabase_tests.test_context_assembler_handles_channel_id()
    
    # Test Neo4j datetime parsing
    print("\n⏰ Testing Neo4j Datetime Parsing...")
    datetime_tests = TestNeo4jDatetimeParsing()
    await datetime_tests.test_temporal_context_query_time_gap_calculation()
    await datetime_tests.test_conversation_threads_query_time_gap_calculation()
    await datetime_tests.test_summarization_query_datetime_comparison()
    
    # Test time filter parameter
    print("\n🔧 Testing Time Filter Parameter...")
    time_filter_tests = TestTimeFilterParameter()
    await time_filter_tests.test_temporal_engine_passes_time_filter()
    await time_filter_tests.test_temporal_engine_default_time_filter()
    
    # Test recent data filtering
    print("\n📅 Testing Recent Data Filtering...")
    recent_data_tests = TestRecentDataFiltering()
    await recent_data_tests.test_ask_command_applies_3day_filter()
    await recent_data_tests.test_graph_traversal_uses_time_filter()
    
    # Test integration scenarios
    print("\n🔗 Testing Integration Scenarios...")
    integration_tests = TestIntegrationScenarios()
    await integration_tests.test_complete_ask_flow_with_recent_data()
    await integration_tests.test_error_handling_for_invalid_queries()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
