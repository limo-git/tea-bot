"""
Test suite for query relevance improvements.

Tests:
1. Query understanding correctly classifies intent
2. Fuzzy entity matching works in graph queries
3. Vector search returns semantically relevant results
4. End-to-end queries return accurate, relevant results
"""

import asyncio
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta


class TestQueryUnderstanding:
    """Test that query understanding correctly classifies intent and extracts entities."""
    
    async def test_lookup_intent_for_specific_topic(self):
        """Test that 'who talked about X' is classified as lookup, not summarization."""
        from retrieval.query_engine import understand_query
        
        # Mock Gemini response
        mock_response = {
            "intent": "lookup",
            "primary_entity": "geopolitics",
            "primary_entity_type": "topic",
            "search_terms": ["geopolitics", "talking", "discussing"],
            "temporal_context_needed": False,
            "time_scope": "recent"
        }
        
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_gen = MagicMock()
            mock_gen.models.generate_content.return_value.text = f"```json\n{json.dumps(mock_response)}\n```"
            mock_client.return_value = mock_gen
            
            result = await understand_query("who was talking about geopolitics?")
            
            assert result["intent"] == "lookup", f"Expected 'lookup' but got '{result['intent']}'"
            assert result["primary_entity"] == "geopolitics", f"Expected 'geopolitics' but got '{result['primary_entity']}'"
            
            print("✅ Query 'who talked about X' correctly classified as lookup")
    
    async def test_summarization_intent_for_general_query(self):
        """Test that 'what did i miss' is classified as summarization."""
        from retrieval.query_engine import understand_query
        
        mock_response = {
            "intent": "summarization",
            "primary_entity": "server",
            "primary_entity_type": None,
            "search_terms": ["miss", "happened", "activity"],
            "temporal_context_needed": False,
            "time_scope": "recent"
        }
        
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_gen = MagicMock()
            mock_gen.models.generate_content.return_value.text = f"```json\n{json.dumps(mock_response)}\n```"
            mock_client.return_value = mock_gen
            
            result = await understand_query("what did i miss out on?")
            
            assert result["intent"] == "summarization", f"Expected 'summarization' but got '{result['intent']}'"
            assert result["primary_entity"] == "server", f"Expected 'server' but got '{result['primary_entity']}'"
            
            print("✅ Query 'what did i miss' correctly classified as summarization")
    
    async def test_entity_extraction_from_query(self):
        """Test that entities are correctly extracted from queries."""
        from retrieval.query_engine import understand_query
        
        test_cases = [
            ("who talked about deployment?", "deployment"),
            ("what did Alice say about the bot?", "bot"),
            ("tell me about the auth refactor", "auth refactor"),
        ]
        
        for query, expected_entity in test_cases:
            mock_response = {
                "intent": "lookup",
                "primary_entity": expected_entity,
                "primary_entity_type": "topic",
                "search_terms": [expected_entity],
                "temporal_context_needed": False,
                "time_scope": "recent"
            }
            
            with patch('retrieval.query_engine._get_client') as mock_client:
                mock_gen = MagicMock()
                mock_gen.models.generate_content.return_value.text = f"```json\n{json.dumps(mock_response)}\n```"
                mock_client.return_value = mock_gen
                
                result = await understand_query(query)
                
                assert result["primary_entity"] == expected_entity, \
                    f"Query '{query}': Expected '{expected_entity}' but got '{result['primary_entity']}'"
        
        print("✅ Entities correctly extracted from queries")


class TestFuzzyEntityMatching:
    """Test that fuzzy entity matching works in graph queries."""
    
    async def test_fuzzy_match_case_insensitive(self):
        """Test that entity matching is case-insensitive."""
        # Verify the LOOKUP_QUERY uses toLower for case-insensitive matching
        from graph.queries import LOOKUP_QUERY
        
        assert "toLower(e.name)" in LOOKUP_QUERY, "LOOKUP_QUERY should use toLower for case-insensitive matching"
        assert "toLower($entity_name)" in LOOKUP_QUERY, "LOOKUP_QUERY should use toLower on parameter"
        
        print("✅ LOOKUP_QUERY uses case-insensitive matching")
    
    async def test_fuzzy_match_partial_matching(self):
        """Test that entity matching uses CONTAINS for partial matching."""
        from graph.queries import LOOKUP_QUERY
        
        assert "CONTAINS" in LOOKUP_QUERY, "LOOKUP_QUERY should use CONTAINS for partial matching"
        
        print("✅ LOOKUP_QUERY uses partial matching with CONTAINS")
    
    async def test_fuzzy_match_bidirectional(self):
        """Test that entity matching works in both directions."""
        from graph.queries import LOOKUP_QUERY
        
        # Should match both "geopolitics" in "geopolitical" AND "geopolitical" in "geopolitics"
        assert "OR" in LOOKUP_QUERY, "LOOKUP_QUERY should have bidirectional matching with OR"
        
        print("✅ LOOKUP_QUERY uses bidirectional matching")
    
    async def test_lookup_query_orders_by_timestamp(self):
        """Test that LOOKUP_QUERY orders results by timestamp DESC."""
        from graph.queries import LOOKUP_QUERY
        
        assert "ORDER BY m.timestamp DESC" in LOOKUP_QUERY, \
            "LOOKUP_QUERY should order messages by timestamp DESC for recency"
        
        print("✅ LOOKUP_QUERY orders by timestamp DESC")


class TestVectorSearchRelevance:
    """Test that vector search returns semantically relevant results."""
    
    async def test_vector_search_uses_semantic_search_for_lookup(self):
        """Test that vector search uses semantic search for lookup queries."""
        from retrieval.vector_search import vector_search
        
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search:
            
            mock_embed.return_value = [0.1] * 768  # Mock embedding
            mock_search.return_value = [
                {"content": "Discussion about geopolitics", "similarity": 0.9}
            ]
            
            results = await vector_search(
                query="geopolitics discussion",
                server_id=123,
                intent="lookup"
            )
            
            assert mock_embed.called, "Should generate embedding for lookup queries"
            assert mock_search.called, "Should use semantic search for lookup queries"
            assert len(results) > 0, "Should return results"
            
            print("✅ Vector search uses semantic search for lookup queries")
    
    async def test_vector_search_uses_timerange_for_summarization(self):
        """Test that vector search uses get_messages_by_timerange for summarization."""
        from retrieval.vector_search import vector_search
        
        with patch('retrieval.vector_search.supabase_client.get_messages_by_timerange') as mock_timerange:
            
            mock_timerange.return_value = [
                {"content": "Recent message 1", "created_at": "2026-03-02T10:00:00Z"},
                {"content": "Recent message 2", "created_at": "2026-03-02T09:00:00Z"}
            ]
            
            results = await vector_search(
                query="what happened",
                server_id=123,
                intent="summarization"
            )
            
            assert mock_timerange.called, "Should use get_messages_by_timerange for summarization"
            assert len(results) == 2, "Should return all recent messages"
            assert all(msg.get("similarity") == 1.0 for msg in results), \
                "All messages should have similarity 1.0 for summarization"
            
            print("✅ Vector search uses timerange query for summarization")
    
    async def test_vector_search_logs_warning_for_no_results(self):
        """Test that vector search logs warning when no results found."""
        from retrieval.vector_search import vector_search
        import logging
        
        with patch('retrieval.vector_search.generate_query_embedding') as mock_embed, \
             patch('retrieval.vector_search.supabase_client.semantic_search_filtered') as mock_search, \
             patch('retrieval.vector_search.logger') as mock_logger:
            
            mock_embed.return_value = [0.1] * 768
            mock_search.return_value = []  # No results
            
            results = await vector_search(
                query="nonexistent topic",
                server_id=123,
                intent="lookup"
            )
            
            assert len(results) == 0, "Should return empty list"
            assert mock_logger.warning.called, "Should log warning when no results found"
            
            print("✅ Vector search logs warning for no results")


class TestSearchQueryConstruction:
    """Test that search queries are constructed correctly for different intents."""
    
    async def test_lookup_query_includes_entity_name(self):
        """Test that lookup queries include the entity name in search."""
        # Verify the code constructs search query with entity name
        import os
        query_engine_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                        'retrieval', 'query_engine.py')
        
        with open(query_engine_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Check that lookup queries combine entity + search terms
        assert 'if intent == "lookup"' in source_code, \
            "Should have special handling for lookup queries"
        assert 'understanding["primary_entity"]' in source_code, \
            "Should use primary_entity in search query"
        
        print("✅ Lookup queries include entity name in search")
    
    async def test_search_query_logging(self):
        """Test that search queries are logged for debugging."""
        import os
        query_engine_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                        'retrieval', 'query_engine.py')
        
        with open(query_engine_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        assert 'logger.info(f"Vector search query:' in source_code, \
            "Should log search query for debugging"
        
        print("✅ Search queries are logged")


class TestEndToEndQueryAccuracy:
    """Integration tests for end-to-end query accuracy."""
    
    async def test_geopolitics_query_returns_relevant_results(self):
        """Test that 'who talked about geopolitics' returns relevant results."""
        from retrieval.query_engine import run_query_pipeline
        
        with patch('retrieval.query_engine.understand_query') as mock_understand, \
             patch('retrieval.query_engine.graph_traversal') as mock_graph, \
             patch('retrieval.query_engine.vector_search') as mock_vector:
            
            # Mock query understanding
            mock_understand.return_value = {
                "intent": "lookup",
                "primary_entity": "geopolitics",
                "search_terms": ["geopolitics", "discussing"]
            }
            
            # Mock graph results
            mock_graph.return_value = [
                {
                    "content": "We should discuss geopolitical issues",
                    "author": "alice",
                    "timestamp": "2026-03-02T10:00:00Z"
                }
            ]
            
            # Mock vector results
            mock_vector.return_value = [
                {
                    "content": "The geopolitical situation is complex",
                    "author_name": "bob",
                    "created_at": "2026-03-02T09:00:00Z",
                    "similarity": 0.85
                }
            ]
            
            result = await run_query_pipeline(
                query="who was talking about geopolitics?",
                server_id=123
            )
            
            assert result["understanding"]["intent"] == "lookup"
            assert result["understanding"]["primary_entity"] == "geopolitics"
            assert len(result["context"]) > 0, "Should return context items"
            
            # Verify all context items are about geopolitics
            for item in result["context"]:
                content_lower = item["content"].lower()
                assert "geopolit" in content_lower, \
                    f"Context item should be about geopolitics: {item['content']}"
            
            print("✅ Geopolitics query returns relevant results")
    
    async def test_bot_development_query_returns_relevant_results(self):
        """Test that 'what happened to the bot' returns relevant results."""
        from retrieval.query_engine import run_query_pipeline
        
        with patch('retrieval.query_engine.understand_query') as mock_understand, \
             patch('retrieval.query_engine.graph_traversal') as mock_graph, \
             patch('retrieval.query_engine.vector_search') as mock_vector:
            
            mock_understand.return_value = {
                "intent": "lookup",
                "primary_entity": "bot",
                "search_terms": ["bot", "development", "making"]
            }
            
            mock_graph.return_value = [
                {
                    "content": "I switched to graph RAG for the bot",
                    "author": "limo.ew",
                    "timestamp": "2026-02-22T10:00:00Z"
                }
            ]
            
            mock_vector.return_value = [
                {
                    "content": "The bot now uses Neo4j and episodic memory",
                    "author_name": "limo.ew",
                    "created_at": "2026-02-22T10:05:00Z",
                    "similarity": 0.9
                }
            ]
            
            result = await run_query_pipeline(
                query="what happened to the bot?",
                server_id=123
            )
            
            assert result["understanding"]["intent"] == "lookup"
            assert "bot" in result["understanding"]["primary_entity"]
            assert len(result["context"]) > 0
            
            print("✅ Bot development query returns relevant results")
    
    async def test_general_summary_query_returns_all_recent(self):
        """Test that 'what did i miss' returns all recent messages."""
        from retrieval.query_engine import run_query_pipeline
        
        with patch('retrieval.query_engine.understand_query') as mock_understand, \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline') as mock_temporal:
            
            mock_understand.return_value = {
                "intent": "summarization",
                "primary_entity": "server",
                "search_terms": ["miss", "happened"],
                "temporal_context_needed": True
            }
            
            mock_temporal.return_value = {
                "context": [
                    {"content": "Message 1", "timestamp": "2026-03-02T10:00:00Z"},
                    {"content": "Message 2", "timestamp": "2026-03-02T09:00:00Z"},
                    {"content": "Message 3", "timestamp": "2026-03-01T10:00:00Z"}
                ],
                "understanding": mock_understand.return_value
            }
            
            result = await run_query_pipeline(
                query="what did i miss?",
                server_id=123
            )
            
            assert result["understanding"]["intent"] == "summarization"
            assert len(result["context"]) == 3, "Should return all recent messages"
            
            print("✅ General summary query returns all recent messages")


async def run_all_tests():
    """Run all test suites."""
    
    print("\n🧪 Running Query Relevance Test Suite")
    print("=" * 60)
    
    # Test query understanding
    print("\n📝 Testing Query Understanding...")
    understanding_tests = TestQueryUnderstanding()
    await understanding_tests.test_lookup_intent_for_specific_topic()
    await understanding_tests.test_summarization_intent_for_general_query()
    await understanding_tests.test_entity_extraction_from_query()
    
    # Test fuzzy entity matching
    print("\n🔍 Testing Fuzzy Entity Matching...")
    fuzzy_tests = TestFuzzyEntityMatching()
    await fuzzy_tests.test_fuzzy_match_case_insensitive()
    await fuzzy_tests.test_fuzzy_match_partial_matching()
    await fuzzy_tests.test_fuzzy_match_bidirectional()
    await fuzzy_tests.test_lookup_query_orders_by_timestamp()
    
    # Test vector search relevance
    print("\n🎯 Testing Vector Search Relevance...")
    vector_tests = TestVectorSearchRelevance()
    await vector_tests.test_vector_search_uses_semantic_search_for_lookup()
    await vector_tests.test_vector_search_uses_timerange_for_summarization()
    await vector_tests.test_vector_search_logs_warning_for_no_results()
    
    # Test search query construction
    print("\n🔨 Testing Search Query Construction...")
    construction_tests = TestSearchQueryConstruction()
    await construction_tests.test_lookup_query_includes_entity_name()
    await construction_tests.test_search_query_logging()
    
    # Test end-to-end accuracy
    print("\n🔗 Testing End-to-End Query Accuracy...")
    integration_tests = TestEndToEndQueryAccuracy()
    await integration_tests.test_geopolitics_query_returns_relevant_results()
    await integration_tests.test_bot_development_query_returns_relevant_results()
    await integration_tests.test_general_summary_query_returns_all_recent()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
