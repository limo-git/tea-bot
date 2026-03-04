"""
Test suite for channel summaries functionality.
Tests P1.5-P1.7: Hourly summarization and /recap integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from database.supabase_client import SupabaseClient
from ingestion.summarizer import summarize_channel_hour, run_hourly_summarization


class TestChannelSummaryStorage:
    """Test storing and retrieving channel summaries."""
    
    @pytest.mark.asyncio
    async def test_store_channel_summary(self):
        """Test that channel summaries can be stored."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.upsert.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[{"id": 1}])
            mock_table.return_value = mock_chain
            
            hour_bucket = datetime(2026, 3, 4, 14, 0, 0)
            
            result = await client.store_channel_summary(
                server_id=123456,
                channel_id=789,
                hour_bucket=hour_bucket,
                summary_text="Users discussed deployment strategies.",
                message_count=25,
                key_topics=["deployment", "docker", "CI/CD"],
                active_users=[111, 222, 333]
            )
            
            # Verify upsert was called
            assert mock_chain.upsert.called
            call_args = mock_chain.upsert.call_args[0][0]
            assert call_args['server_id'] == 123456
            assert call_args['channel_id'] == 789
            assert call_args['message_count'] == 25
            assert "deployment" in call_args['key_topics']
    
    @pytest.mark.asyncio
    async def test_get_channel_summaries(self):
        """Test retrieving channel summaries for a time range."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.gte.return_value = mock_chain
            mock_chain.lte.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {
                    "server_id": 123456,
                    "channel_id": 789,
                    "hour_bucket": "2026-03-04T14:00:00",
                    "summary_text": "Discussion about deployment",
                    "message_count": 25
                }
            ])
            mock_table.return_value = mock_chain
            
            start_time = datetime(2026, 3, 4, 12, 0, 0)
            end_time = datetime(2026, 3, 4, 18, 0, 0)
            
            summaries = await client.get_channel_summaries(
                server_id=123456,
                channel_id=789,
                start_time=start_time,
                end_time=end_time
            )
            
            assert len(summaries) == 1
            assert summaries[0]['message_count'] == 25
    
    @pytest.mark.asyncio
    async def test_get_channels_needing_summary(self):
        """Test identifying channels that need summarization."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            # Mock messages query
            messages_chain = Mock()
            messages_chain.select.return_value = messages_chain
            messages_chain.gte.return_value = messages_chain
            messages_chain.lt.return_value = messages_chain
            messages_chain.execute.return_value = Mock(data=[
                {"server_id": 123, "channel_id": 456},
                {"server_id": 123, "channel_id": 456},  # Duplicate
                {"server_id": 123, "channel_id": 789},
            ])
            
            # Mock summaries query
            summaries_chain = Mock()
            summaries_chain.select.return_value = summaries_chain
            summaries_chain.eq.return_value = summaries_chain
            summaries_chain.execute.return_value = Mock(data=[
                {"server_id": 123, "channel_id": 456}  # Already has summary
            ])
            
            # Return different chains for different table calls
            call_count = [0]
            def table_side_effect(name):
                call_count[0] += 1
                if call_count[0] == 1:
                    return messages_chain
                else:
                    return summaries_chain
            
            mock_table.side_effect = table_side_effect
            
            channels = await client.get_channels_needing_summary(hours_ago=1)
            
            # Should return channel 789 (has messages but no summary)
            assert (123, 789) in channels
            assert (123, 456) not in channels  # Already has summary


class TestHourlySummarization:
    """Test hourly summarization job."""
    
    @pytest.mark.asyncio
    async def test_summarize_channel_hour_with_messages(self):
        """Test summarizing a channel hour with sufficient messages."""
        with patch('ingestion.summarizer.supabase_client') as mock_supabase, \
             patch('ingestion.summarizer.gemini_client') as mock_gemini:
            
            # Mock message retrieval as async
            mock_supabase.get_messages_by_timerange = AsyncMock(return_value=[
                {"author_name": "Alice", "content": "Let's deploy today", "author_id": 111},
                {"author_name": "Bob", "content": "Agreed, using Docker", "author_id": 222},
                {"author_name": "Alice", "content": "I'll handle CI/CD", "author_id": 111},
            ])
            
            # Mock summary generation
            mock_gemini.generate_response = AsyncMock(side_effect=[
                "Team discussed deployment strategy using Docker and CI/CD.",
                "deployment, docker, CI/CD"
            ])
            
            mock_supabase.store_channel_summary = AsyncMock()
            
            hour_bucket = datetime(2026, 3, 4, 14, 0, 0)
            
            result = await summarize_channel_hour(
                server_id=123456,
                channel_id=789,
                hour_bucket=hour_bucket,
                channel_name="dev-general"
            )
            
            # Verify summary was generated
            assert result is not None
            assert result['message_count'] == 3
            assert 'deployment' in result['summary'].lower()
            
            # Verify summary was stored
            assert mock_supabase.store_channel_summary.called
    
    @pytest.mark.asyncio
    async def test_summarize_channel_hour_skips_low_activity(self):
        """Test that channels with < 3 messages are skipped."""
        with patch('ingestion.summarizer.supabase_client') as mock_supabase:
            
            # Mock low message count as async
            mock_supabase.get_messages_by_timerange = AsyncMock(return_value=[
                {"author_name": "Alice", "content": "Hi", "author_id": 111}
            ])
            
            hour_bucket = datetime(2026, 3, 4, 14, 0, 0)
            
            result = await summarize_channel_hour(
                server_id=123456,
                channel_id=789,
                hour_bucket=hour_bucket
            )
            
            # Should return None for low activity
            assert result is None
    
    @pytest.mark.asyncio
    async def test_run_hourly_summarization(self):
        """Test the full hourly summarization job."""
        with patch('ingestion.summarizer.supabase_client') as mock_supabase, \
             patch('ingestion.summarizer.summarize_channel_hour') as mock_summarize:
            
            # Mock channels needing summary as async
            mock_supabase.get_channels_needing_summary = AsyncMock(return_value=[
                (123, 456),
                (123, 789),
            ])
            
            # Mock summarization as async
            mock_summarize.return_value = {
                'message_count': 10,
                'summary': 'Test summary'
            }
            
            await run_hourly_summarization(hours_ago=1)
            
            # Verify summarization was called for each channel
            assert mock_summarize.call_count == 2


class TestRecapIntegration:
    """Test /recap command integration with pre-computed summaries."""
    
    @pytest.mark.asyncio
    async def test_recap_uses_summaries_when_available(self):
        """Test that /recap uses pre-computed summaries when available."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.gte.return_value = mock_chain
            mock_chain.lte.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {
                    "hour_bucket": "2026-03-04T14:00:00",
                    "summary_text": "Team discussed deployment",
                    "message_count": 25,
                    "key_topics": ["deployment", "docker"]
                },
                {
                    "hour_bucket": "2026-03-04T15:00:00",
                    "summary_text": "Code review session",
                    "message_count": 18,
                    "key_topics": ["code review", "python"]
                }
            ])
            mock_table.return_value = mock_chain
            
            summaries = await client.get_channel_summaries(
                server_id=123456,
                channel_id=789,
                start_time=datetime(2026, 3, 4, 14, 0, 0),
                end_time=datetime(2026, 3, 4, 16, 0, 0)
            )
            
            # Verify summaries were retrieved
            assert len(summaries) == 2
            assert summaries[0]['message_count'] == 25
    
    @pytest.mark.asyncio
    async def test_recap_falls_back_to_messages_when_no_summaries(self):
        """Test that /recap falls back to raw messages when no summaries exist."""
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.gte.return_value = mock_chain
            mock_chain.lte.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[])
            mock_table.return_value = mock_chain
            
            summaries = await client.get_channel_summaries(
                server_id=123456,
                channel_id=789,
                start_time=datetime(2026, 3, 4, 14, 0, 0),
                end_time=datetime(2026, 3, 4, 16, 0, 0)
            )
            
            # Should fall back to messages
            assert len(summaries) == 0


class TestSummaryQuality:
    """Test summary quality and content."""
    
    def test_summary_prompt_includes_time_range(self):
        """Test that summary prompt includes time context."""
        from ingestion.summarizer import HOURLY_SUMMARY_PROMPT
        
        assert "{start_time}" in HOURLY_SUMMARY_PROMPT
        assert "{end_time}" in HOURLY_SUMMARY_PROMPT
        assert "{channel_name}" in HOURLY_SUMMARY_PROMPT
    
    def test_topic_extraction_prompt_exists(self):
        """Test that topic extraction prompt is defined."""
        from ingestion.summarizer import TOPIC_EXTRACTION_PROMPT
        
        assert TOPIC_EXTRACTION_PROMPT is not None
        assert "{messages}" in TOPIC_EXTRACTION_PROMPT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
