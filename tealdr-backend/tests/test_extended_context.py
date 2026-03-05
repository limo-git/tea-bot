"""
Test suite for P3: Extended Conversation Context + Source Anchoring
Tests the enhanced conversation context system with source tracking and relevance scoring.
"""

import pytest
from utils.conversation_context import ConversationContext


class TestSourceAnchoring:
    """Test source message tracking in conversation context."""
    
    def test_add_query_with_sources(self):
        """Test that source messages are tracked correctly."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is a containerization platform...",
            source_messages=["msg_1", "msg_2", "msg_3"]
        )
        
        history = context.get_context(123)
        assert len(history) == 1
        assert history[0]['source_messages'] == ["msg_1", "msg_2", "msg_3"]
    
    def test_get_source_messages(self):
        """Test retrieving all source messages from context."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            source_messages=["msg_1", "msg_2"]
        )
        
        context.add_query(
            user_id=123,
            query="Tell me more",
            response="Docker containers...",
            source_messages=["msg_3", "msg_4"]
        )
        
        sources = context.get_source_messages(123)
        assert len(sources) == 4
        assert set(sources) == {"msg_1", "msg_2", "msg_3", "msg_4"}
    
    def test_source_deduplication(self):
        """Test that duplicate source messages are deduplicated."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="Query 1",
            response="Response 1",
            source_messages=["msg_1", "msg_2"]
        )
        
        context.add_query(
            user_id=123,
            query="Query 2",
            response="Response 2",
            source_messages=["msg_2", "msg_3"]  # msg_2 is duplicate
        )
        
        sources = context.get_source_messages(123)
        assert len(sources) == 3  # Deduplicated
        assert set(sources) == {"msg_1", "msg_2", "msg_3"}


class TestEntityTracking:
    """Test entity tracking across conversation turns."""
    
    def test_add_query_with_entities(self):
        """Test that entities are tracked correctly."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="Tell me about Docker",
            response="Docker is...",
            entities=["docker", "containers"]
        )
        
        history = context.get_context(123)
        assert history[0]['entities'] == ["docker", "containers"]
    
    def test_get_relevant_entities(self):
        """Test retrieving all entities from conversation context."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            entities=["docker", "containers"]
        )
        
        context.add_query(
            user_id=123,
            query="How about Kubernetes?",
            response="Kubernetes is...",
            entities=["kubernetes", "orchestration"]
        )
        
        entities = context.get_relevant_entities(123)
        assert len(entities) == 4
        assert set(entities) == {"docker", "containers", "kubernetes", "orchestration"}
    
    def test_entity_deduplication(self):
        """Test that duplicate entities are deduplicated."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="Query 1",
            response="Response 1",
            entities=["docker", "containers"]
        )
        
        context.add_query(
            user_id=123,
            query="Query 2",
            response="Response 2",
            entities=["docker", "kubernetes"]  # docker is duplicate
        )
        
        entities = context.get_relevant_entities(123)
        assert len(entities) == 3  # Deduplicated
        assert set(entities) == {"docker", "containers", "kubernetes"}


class TestContextRelevance:
    """Test context relevance scoring."""
    
    def test_relevance_with_pronouns(self):
        """Test that pronoun references increase relevance."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is a containerization platform",
            entities=["docker"]
        )
        
        # Query with pronoun reference
        relevance = context.calculate_context_relevance(123, "Tell me more about it")
        assert relevance > 0.3  # Should be relevant
    
    def test_relevance_with_continuation_phrases(self):
        """Test that continuation phrases increase relevance."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            entities=["docker"]
        )
        
        # Query with continuation phrase
        relevance = context.calculate_context_relevance(123, "What about Kubernetes?")
        assert relevance > 0.3
    
    def test_relevance_with_entity_overlap(self):
        """Test that entity overlap increases relevance."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            entities=["docker", "containers"]
        )
        
        # Query mentioning same entity
        relevance = context.calculate_context_relevance(123, "How do Docker containers work?")
        assert relevance >= 0.5  # High relevance due to entity overlap
    
    def test_relevance_with_short_query(self):
        """Test that short queries are considered follow-ups."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            entities=["docker"]
        )
        
        # Very short query (likely a follow-up)
        relevance = context.calculate_context_relevance(123, "Why?")
        assert relevance > 0.0  # Should have some relevance
    
    def test_relevance_with_unrelated_query(self):
        """Test that unrelated queries have low relevance."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            entities=["docker"]
        )
        
        # Completely unrelated query
        relevance = context.calculate_context_relevance(123, "What's the weather like?")
        assert relevance < 0.5  # Should have low relevance
    
    def test_no_context_returns_zero_relevance(self):
        """Test that no context returns 0 relevance."""
        context = ConversationContext()
        
        relevance = context.calculate_context_relevance(123, "Any query")
        assert relevance == 0.0


class TestEnhancedFormatting:
    """Test enhanced context formatting with source anchoring."""
    
    def test_format_with_sources(self):
        """Test that source counts are included in formatted context."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is a containerization platform",
            source_messages=["msg_1", "msg_2", "msg_3"]
        )
        
        formatted = context.format_context_for_prompt(123, include_sources=True)
        
        assert "Turn 1:" in formatted
        assert "What is Docker?" in formatted
        assert "Sources: 3 messages referenced" in formatted
    
    def test_format_with_entities(self):
        """Test that entities are included in formatted context."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="Tell me about Docker",
            response="Docker is...",
            entities=["docker", "containers", "images"]
        )
        
        formatted = context.format_context_for_prompt(123)
        
        assert "Entities:" in formatted
        assert "docker" in formatted
    
    def test_format_without_sources(self):
        """Test formatting without source information."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is...",
            source_messages=["msg_1", "msg_2"]
        )
        
        formatted = context.format_context_for_prompt(123, include_sources=False)
        
        assert "Sources:" not in formatted
    
    def test_format_multiple_turns(self):
        """Test formatting with multiple conversation turns."""
        context = ConversationContext()
        
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is a containerization platform",
            entities=["docker"],
            source_messages=["msg_1"]
        )
        
        context.add_query(
            user_id=123,
            query="How does it work?",
            response="Docker uses containers to package applications",
            entities=["containers"],
            source_messages=["msg_2", "msg_3"]
        )
        
        formatted = context.format_context_for_prompt(123)
        
        assert "Turn 1:" in formatted
        assert "Turn 2:" in formatted
        assert "What is Docker?" in formatted
        assert "How does it work?" in formatted
        assert "Sources: 1 messages referenced" in formatted
        assert "Sources: 2 messages referenced" in formatted
    
    def test_format_truncates_long_responses(self):
        """Test that long responses are truncated."""
        context = ConversationContext()
        
        long_response = "A" * 500  # Very long response
        
        context.add_query(
            user_id=123,
            query="Tell me everything",
            response=long_response
        )
        
        formatted = context.format_context_for_prompt(123)
        
        # Should be truncated to 300 chars + "..."
        assert len(formatted) < len(long_response)
        assert "..." in formatted


class TestTurnTracking:
    """Test conversation turn numbering."""
    
    def test_turn_numbers_increment(self):
        """Test that turn numbers increment correctly."""
        context = ConversationContext()
        
        context.add_query(123, "Query 1", "Response 1")
        context.add_query(123, "Query 2", "Response 2")
        context.add_query(123, "Query 3", "Response 3")
        
        history = context.get_context(123)
        
        assert history[0]['turn_number'] == 1
        assert history[1]['turn_number'] == 2
        assert history[2]['turn_number'] == 3
    
    def test_turn_numbers_after_clear(self):
        """Test that turn numbers reset after context is cleared."""
        context = ConversationContext()
        
        context.add_query(123, "Query 1", "Response 1")
        context.add_query(123, "Query 2", "Response 2")
        
        context.clear_context(123)
        
        context.add_query(123, "Query 3", "Response 3")
        
        history = context.get_context(123)
        assert len(history) == 1
        assert history[0]['turn_number'] == 1  # Reset to 1


class TestBackwardCompatibility:
    """Test that enhanced context is backward compatible."""
    
    def test_add_query_without_new_params(self):
        """Test that add_query works without new P3 parameters."""
        context = ConversationContext()
        
        # Old-style call without source_messages or entities
        context.add_query(
            user_id=123,
            query="What is Docker?",
            response="Docker is..."
        )
        
        history = context.get_context(123)
        assert len(history) == 1
        assert history[0]['source_messages'] == []
        assert history[0]['entities'] == []
    
    def test_get_source_messages_empty(self):
        """Test get_source_messages with no sources."""
        context = ConversationContext()
        
        context.add_query(123, "Query", "Response")
        
        sources = context.get_source_messages(123)
        assert sources == []
    
    def test_get_relevant_entities_empty(self):
        """Test get_relevant_entities with no entities."""
        context = ConversationContext()
        
        context.add_query(123, "Query", "Response")
        
        entities = context.get_relevant_entities(123)
        assert entities == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
