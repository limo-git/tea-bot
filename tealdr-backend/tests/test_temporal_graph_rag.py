import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

# Import modules to test
from retrieval.query_engine import understand_query, run_query_pipeline
from retrieval.temporal_engine import run_temporal_query_pipeline
from retrieval.context_assembler import assemble_context
from generation.answer_generator import generate_answer
from generation.temporal_context_helper import _generate_temporal_context_info, format_context_for_prompt


class TestQueryUnderstanding:
    """Test query understanding with temporal context detection."""
    
    @pytest.mark.asyncio
    async def test_temporal_context_detection(self):
        """Test that temporal context queries are properly detected."""
        
        # Mock Gemini client
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = json.dumps({
                "intent": "temporal_context",
                "primary_entity": "deployment",
                "temporal_context_needed": True,
                "time_scope": "weeks"
            })
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            # Test temporal context query
            result = await understand_query("What's the background context on the deployment issue?")
            
            assert result["intent"] == "temporal_context"
            assert result["temporal_context_needed"] == True
            assert result["primary_entity"] == "deployment"
            print("✅ Temporal context detection works")
    
    @pytest.mark.asyncio
    async def test_conversation_thread_detection(self):
        """Test that conversation thread queries are detected."""
        
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = json.dumps({
                "intent": "conversation_threads",
                "primary_entity": "bug fix",
                "temporal_context_needed": True,
                "time_scope": "recent"
            })
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            result = await understand_query("Continue the discussion about the bug fix")
            
            assert result["intent"] == "conversation_threads"
            assert result["temporal_context_needed"] == True
            print("✅ Conversation thread detection works")
    
    @pytest.mark.asyncio
    async def test_standard_query_detection(self):
        """Test that standard queries don't trigger temporal context."""
        
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = json.dumps({
                "intent": "summarization",
                "primary_entity": "server",
                "temporal_context_needed": False,
                "time_scope": "recent"
            })
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            result = await understand_query("What happened on the server today?")
            
            assert result["intent"] == "summarization"
            assert result["temporal_context_needed"] == False
            print("✅ Standard query detection works")


class TestTemporalEngine:
    """Test the temporal query pipeline."""
    
    @pytest.mark.asyncio
    async def test_temporal_pipeline_execution(self):
        """Test that temporal pipeline runs multiple queries."""
        
        # Mock understanding
        understanding = {
            "intent": "temporal_context",
            "primary_entity": "deployment",
            "temporal_context_needed": True,
            "search_terms": ["deployment", "context"]
        }
        
        # Mock graph results
        mock_primary_results = [
            {
                "content": "Deployment started at 2PM",
                "timestamp": "2026-03-01T14:00:00Z",
                "author": "limo.ew",
                "channel": "dev-ops"
            }
        ]
        
        mock_temporal_results = [
            {
                "content": "Initial deployment planning discussion",
                "timestamp": "2026-02-28T10:00:00Z", 
                "author": "sidtheitguy",
                "channel": "dev-ops",
                "related_discussions": [
                    {
                        "content": "Follow-up on deployment issues",
                        "timestamp": "2026-03-01T16:00:00Z",
                        "author": "quantadude",
                        "channel": "dev-ops",
                        "time_gap": 1
                    }
                ]
            }
        ]
        
        mock_thread_results = [
            {
                "content": "Deployment thread message",
                "timestamp": "2026-03-01T14:30:00Z",
                "author": "vivek_75006",
                "channel": "dev-ops",
                "thread_context": [
                    {
                        "content": "Related thread message",
                        "timestamp": "2026-03-01T15:00:00Z",
                        "author": "galvanizedsquaresteel6769",
                        "time_gap_hours": 0.5,
                        "mentioned_entities": ["deployment", "server"]
                    }
                ]
            }
        ]
        
        # Mock vector search results
        mock_vector_results = [
            {
                "content": "Vector search result about deployment",
                "author_name": "ogyuvrajs",
                "channel_id": "123456",
                "created_at": "2026-03-01T13:00:00Z",
                "similarity": 0.85
            }
        ]
        
        with patch('retrieval.temporal_engine._get_primary_results', return_value=mock_primary_results), \
             patch('retrieval.temporal_engine._get_temporal_context', return_value=mock_temporal_results), \
             patch('retrieval.temporal_engine._get_conversation_threads', return_value=mock_thread_results), \
             patch('retrieval.temporal_engine.vector_search', return_value=mock_vector_results):
            
            result = await run_temporal_query_pipeline(
                query="What's the context behind the deployment?",
                understanding=understanding,
                server_id=12345,
            )
            
            assert "context" in result
            assert result["temporal_connections"] == len(mock_temporal_results)
            assert result["conversation_threads"] == len(mock_thread_results)
            assert len(result["context"]) > 0
            print("✅ Temporal pipeline execution works")


class TestContextAssembler:
    """Test context assembly with temporal metadata."""
    
    def test_temporal_context_assembly(self):
        """Test that temporal context is properly assembled."""
        
        graph_results = [
            {
                "content": "Primary message",
                "timestamp": "2026-03-01T14:00:00Z",
                "author": "limo.ew",
                "channel": "dev-ops",
                "related_discussions": [
                    {
                        "content": "Related message from yesterday",
                        "timestamp": "2026-02-28T14:00:00Z",
                        "author": "sidtheitguy",
                        "channel": "dev-ops",
                        "time_gap": 1
                    }
                ]
            }
        ]
        
        vector_results = [
            {
                "content": "Vector result",
                "author_name": "quantadude",
                "channel_id": "123456",
                "created_at": "2026-03-01T15:00:00Z",
                "similarity": 0.8
            }
        ]
        
        context = assemble_context(graph_results, vector_results, "temporal_context")
        
        # Should have primary message + related discussion + vector result
        assert len(context) >= 3
        
        # Check temporal metadata
        temporal_items = [item for item in context if item.get("temporal_context")]
        assert len(temporal_items) > 0
        
        # Check that related discussion has temporal metadata
        related_item = next((item for item in context 
                           if item.get("temporal_context", {}).get("context_type") == "related_discussion"), None)
        assert related_item is not None
        assert related_item["temporal_context"]["time_gap_days"] == 1
        
        print("✅ Temporal context assembly works")
    
    def test_conversation_thread_assembly(self):
        """Test that conversation threads are properly assembled."""
        
        graph_results = [
            {
                "content": "Thread starter",
                "timestamp": "2026-03-01T14:00:00Z",
                "author": "limo.ew",
                "channel": "general",
                "thread_context": [
                    {
                        "content": "Thread reply",
                        "timestamp": "2026-03-01T14:30:00Z",
                        "author": "sidtheitguy",
                        "time_gap_hours": 0.5,
                        "mentioned_entities": ["deployment"]
                    }
                ]
            }
        ]
        
        context = assemble_context(graph_results, [], "conversation_threads")
        
        # Should have thread starter + thread reply
        assert len(context) >= 2
        
        # Check conversation thread metadata
        thread_items = [item for item in context if item.get("conversation_thread")]
        assert len(thread_items) > 0
        
        print("✅ Conversation thread assembly works")


class TestTemporalContextHelper:
    """Test temporal context helper functions."""
    
    def test_temporal_context_info_generation(self):
        """Test temporal context information generation."""
        
        pipeline_result = {
            "temporal_connections": 2,
            "conversation_threads": 1,
            "understanding": {"intent": "temporal_context"}
        }
        
        context_items = [
            {
                "content": "Primary message",
                "author": "limo.ew",
                "temporal_context": {
                    "context_type": "related_discussion",
                    "time_gap_days": 3,
                    "related_to_entity": "deployment"
                }
            },
            {
                "content": "Thread message",
                "author": "sidtheitguy", 
                "conversation_thread": {
                    "context_type": "thread_message",
                    "time_gap_hours": 2,
                    "mentioned_entities": ["server", "deployment"]
                }
            }
        ]
        
        info = _generate_temporal_context_info(pipeline_result, context_items)
        
        assert "Temporal Context" in info
        assert "Conversation Threads" in info
        assert "Cross-Time Connections" in info
        assert "3 days ago" in info
        
        print("✅ Temporal context info generation works")
    
    def test_enhanced_context_formatting(self):
        """Test enhanced context formatting with temporal indicators."""
        
        context_items = [
            {
                "source": "graph",
                "content": "Primary message about deployment",
                "author": "limo.ew",
                "channel": "dev-ops",
                "timestamp": "2026-03-01T14:00:00Z",
                "temporal_context": {
                    "context_type": "related_discussion",
                    "time_gap_days": 2,
                    "related_to_entity": "deployment"
                }
            },
            {
                "source": "graph",
                "content": "Thread reply message",
                "author": "sidtheitguy",
                "channel": "general",
                "timestamp": "2026-03-01T15:00:00Z",
                "conversation_thread": {
                    "context_type": "thread_message",
                    "time_gap_hours": 1,
                    "mentioned_entities": ["server"]
                }
            }
        ]
        
        formatted = format_context_for_prompt(context_items)
        
        assert "[RELATED: 2d ago]" in formatted
        assert "[ENTITY: deployment]" in formatted
        assert "[THREAD: 1h gap]" in formatted
        assert "[MENTIONS: server]" in formatted
        assert "limo.ew" in formatted
        assert "sidtheitguy" in formatted
        
        print("✅ Enhanced context formatting works")


class TestAnswerGeneration:
    """Test answer generation with temporal context."""
    
    @pytest.mark.asyncio
    async def test_temporal_answer_generation(self):
        """Test that temporal context is used in answer generation."""
        
        pipeline_result = {
            "context": [
                {
                    "source": "graph",
                    "content": "Deployment started successfully",
                    "author": "limo.ew",
                    "channel": "dev-ops",
                    "timestamp": "2026-03-01T14:00:00Z",
                    "temporal_context": {
                        "context_type": "primary",
                        "related_to_entity": "deployment"
                    }
                },
                {
                    "source": "graph", 
                    "content": "Initial deployment planning from last week",
                    "author": "sidtheitguy",
                    "channel": "dev-ops",
                    "timestamp": "2026-02-22T10:00:00Z",
                    "temporal_context": {
                        "context_type": "related_discussion",
                        "time_gap_days": 7,
                        "related_to_entity": "deployment"
                    }
                }
            ],
            "understanding": {
                "intent": "temporal_context",
                "primary_entity": "deployment"
            },
            "temporal_connections": 1,
            "conversation_threads": 0
        }
        
        with patch('generation.answer_generator._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = "Based on the temporal context, the deployment discussion started last week with planning by sidtheitguy, and was successfully executed today by limo.ew in #dev-ops."
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            answer = await generate_answer(
                query="What's the context behind the deployment?",
                pipeline_result=pipeline_result,
                user_name="test_user"
            )
            
            assert "temporal context" in answer.lower()
            assert "sidtheitguy" in answer
            assert "limo.ew" in answer
            
            # Verify the prompt included temporal context info
            call_args = mock_client.return_value.models.generate_content.call_args
            prompt = call_args[1]['contents']
            assert "Temporal Context" in prompt
            assert "[RELATED: 7d ago]" in prompt
            
            print("✅ Temporal answer generation works")


class TestIntegration:
    """Integration tests for the complete temporal Graph RAG system."""
    
    @pytest.mark.asyncio
    async def test_full_temporal_pipeline(self):
        """Test the complete temporal pipeline from query to answer."""
        
        query = "What's the background on the server migration project?"
        
        # Mock query understanding
        understanding = {
            "intent": "temporal_context",
            "primary_entity": "server migration",
            "temporal_context_needed": True,
            "search_terms": ["server", "migration", "project"]
        }
        
        # Mock the complete pipeline
        with patch('retrieval.query_engine.understand_query', return_value=understanding), \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline') as mock_temporal:
            
            mock_temporal.return_value = {
                "context": [
                    {
                        "source": "graph",
                        "content": "Server migration completed successfully",
                        "author": "limo.ew",
                        "timestamp": "2026-03-01T16:00:00Z",
                        "temporal_context": {
                            "context_type": "primary"
                        }
                    }
                ],
                "understanding": understanding,
                "temporal_connections": 2,
                "conversation_threads": 1
            }
            
            result = await run_query_pipeline(
                query=query,
                server_id=12345
            )
            
            assert "context" in result
            assert result["temporal_connections"] == 2
            assert result["conversation_threads"] == 1
            
            # Verify temporal pipeline was called
            mock_temporal.assert_called_once()
            
            print("✅ Full temporal pipeline integration works")


# Test runner function
async def run_all_tests():
    """Run all temporal Graph RAG tests."""
    
    print("🧪 Running Temporal Graph RAG Test Suite")
    print("=" * 50)
    
    # Query Understanding Tests
    print("\n📝 Testing Query Understanding...")
    qu_tests = TestQueryUnderstanding()
    await qu_tests.test_temporal_context_detection()
    await qu_tests.test_conversation_thread_detection() 
    await qu_tests.test_standard_query_detection()
    
    # Temporal Engine Tests
    print("\n⚡ Testing Temporal Engine...")
    te_tests = TestTemporalEngine()
    await te_tests.test_temporal_pipeline_execution()
    
    # Context Assembler Tests
    print("\n🔧 Testing Context Assembler...")
    ca_tests = TestContextAssembler()
    ca_tests.test_temporal_context_assembly()
    ca_tests.test_conversation_thread_assembly()
    
    # Temporal Context Helper Tests
    print("\n🛠️ Testing Temporal Context Helpers...")
    tch_tests = TestTemporalContextHelper()
    tch_tests.test_temporal_context_info_generation()
    tch_tests.test_enhanced_context_formatting()
    
    # Answer Generation Tests
    print("\n💬 Testing Answer Generation...")
    ag_tests = TestAnswerGeneration()
    await ag_tests.test_temporal_answer_generation()
    
    # Integration Tests
    print("\n🔗 Testing Integration...")
    int_tests = TestIntegration()
    await int_tests.test_full_temporal_pipeline()
    
    print("\n" + "=" * 50)
    print("✅ All Temporal Graph RAG tests completed successfully!")
    print("🎉 Your temporal Graph RAG system is working as expected!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
