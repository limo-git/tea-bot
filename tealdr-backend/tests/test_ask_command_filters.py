"""
Test suite for /ask command filter parameters.
Tests the new from_user and mentions parameters.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from bot.commands import BotCommands


class TestFromUserParameter:
    """Test the from_user parameter filtering."""
    
    @pytest.mark.asyncio
    async def test_from_user_parameter_filters_by_author(self):
        """Test that from_user parameter correctly filters messages by author."""
        with patch('retrieval.query_engine.run_query_pipeline') as mock_pipeline, \
             patch('generation.answer_generator.generate_answer') as mock_answer:
            
            # Mock the pipeline to verify author_id is passed
            mock_pipeline.return_value = {
                "understanding": {"intent": "lookup"},
                "context": [
                    {"author_id": 12345, "author_name": "alice", "content": "Test message"}
                ],
                "graph_results": [],
                "vector_results": []
            }
            mock_answer.return_value = "Test response"
            
            # Create mock interaction
            mock_interaction = Mock()
            mock_interaction.response.defer = AsyncMock()
            mock_interaction.followup.send = AsyncMock()
            mock_interaction.user.id = 99999
            mock_interaction.user.display_name = "TestUser"
            mock_interaction.guild.id = 123456
            
            # Mock guild and user
            mock_guild = Mock()
            mock_guild.id = 123456
            mock_user = Mock()
            mock_user.id = 12345
            mock_user.name = "alice"
            mock_guild.get_member.return_value = mock_user
            
            mock_interaction.guild = mock_guild
            
            # Mock bot
            mock_bot = Mock()
            commands = BotCommands(mock_bot)
            
            # Call ask_command with from_user parameter
            with patch('utils.server_selector.resolve_server_context') as mock_resolve:
                mock_resolve.return_value = ([mock_guild], False)
                
                with patch('bot.commands.conversation_context') as mock_context:
                    mock_context.has_context.return_value = False
                    
                    with patch('bot.commands.server_settings_client') as mock_settings:
                        mock_settings.get_bot_persona.return_value = "TealDR"
                        
                        await commands.ask_command(
                            interaction=mock_interaction,
                            query="what did alice say",
                            from_user=mock_user
                        )
            
            # Verify pipeline was called with author_id
            assert mock_pipeline.called
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs["author_id"] == 12345
    
    @pytest.mark.asyncio
    async def test_from_user_overrides_query_mention(self):
        """Test that from_user parameter takes priority over @mentions in query."""
        with patch('retrieval.query_engine.run_query_pipeline') as mock_pipeline, \
             patch('generation.answer_generator.generate_answer') as mock_answer:
            
            mock_pipeline.return_value = {
                "understanding": {"intent": "lookup"},
                "context": [],
                "graph_results": [],
                "vector_results": []
            }
            mock_answer.return_value = "Test response"
            
            mock_interaction = Mock()
            mock_interaction.response.defer = AsyncMock()
            mock_interaction.followup.send = AsyncMock()
            mock_interaction.user.id = 99999
            mock_interaction.user.display_name = "TestUser"
            
            # Mock guild with two users
            mock_guild = Mock()
            mock_guild.id = 123456
            
            alice = Mock()
            alice.id = 11111
            alice.name = "alice"
            
            bob = Mock()
            bob.id = 22222
            bob.name = "bob"
            
            def get_member(user_id):
                if user_id == 11111:
                    return alice
                elif user_id == 22222:
                    return bob
                return None
            
            mock_guild.get_member.side_effect = get_member
            mock_guild.members = [alice, bob]
            mock_interaction.guild = mock_guild
            
            mock_bot = Mock()
            commands = BotCommands(mock_bot)
            
            with patch('utils.server_selector.resolve_server_context') as mock_resolve:
                mock_resolve.return_value = ([mock_guild], False)
                
                with patch('bot.commands.conversation_context') as mock_context:
                    mock_context.has_context.return_value = False
                    
                    with patch('bot.commands.server_settings_client') as mock_settings:
                        mock_settings.get_bot_persona.return_value = "TealDR"
                        
                        # Query mentions @bob but from_user is alice
                        await commands.ask_command(
                            interaction=mock_interaction,
                            query="what did @bob say",
                            from_user=alice  # Should override @bob
                        )
            
            # Should use alice's ID (from from_user), not bob's
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs["author_id"] == 11111


class TestMentionsParameter:
    """Test the mentions parameter filtering."""
    
    @pytest.mark.asyncio
    async def test_mentions_parameter_filters_by_mentioned_user(self):
        """Test that mentions parameter filters messages that mention a specific user."""
        with patch('retrieval.query_engine.run_query_pipeline') as mock_pipeline, \
             patch('generation.answer_generator.generate_answer') as mock_answer:
            
            mock_pipeline.return_value = {
                "understanding": {"intent": "lookup"},
                "context": [
                    {"content": "Hey <@12345>, check this out", "author_name": "bob"}
                ],
                "graph_results": [],
                "vector_results": []
            }
            mock_answer.return_value = "Test response"
            
            mock_interaction = Mock()
            mock_interaction.response.defer = AsyncMock()
            mock_interaction.followup.send = AsyncMock()
            mock_interaction.user.id = 99999
            mock_interaction.user.display_name = "TestUser"
            
            mock_guild = Mock()
            mock_guild.id = 123456
            
            alice = Mock()
            alice.id = 12345
            alice.name = "alice"
            
            mock_guild.get_member.return_value = alice
            mock_interaction.guild = mock_guild
            
            mock_bot = Mock()
            commands = BotCommands(mock_bot)
            
            with patch('utils.server_selector.resolve_server_context') as mock_resolve:
                mock_resolve.return_value = ([mock_guild], False)
                
                with patch('bot.commands.conversation_context') as mock_context:
                    mock_context.has_context.return_value = False
                    
                    with patch('bot.commands.server_settings_client') as mock_settings:
                        mock_settings.get_bot_persona.return_value = "TealDR"
                        
                        await commands.ask_command(
                            interaction=mock_interaction,
                            query="who mentioned alice",
                            mentions=alice
                        )
            
            # Verify pipeline was called with mentions_user_id
            assert mock_pipeline.called
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs["mentions_user_id"] == 12345
    
    @pytest.mark.asyncio
    async def test_from_user_and_mentions_can_be_combined(self):
        """Test that from_user and mentions can be used together."""
        with patch('retrieval.query_engine.run_query_pipeline') as mock_pipeline, \
             patch('generation.answer_generator.generate_answer') as mock_answer:
            
            mock_pipeline.return_value = {
                "understanding": {"intent": "lookup"},
                "context": [],
                "graph_results": [],
                "vector_results": []
            }
            mock_answer.return_value = "Test response"
            
            mock_interaction = Mock()
            mock_interaction.response.defer = AsyncMock()
            mock_interaction.followup.send = AsyncMock()
            mock_interaction.user.id = 99999
            mock_interaction.user.display_name = "TestUser"
            
            mock_guild = Mock()
            mock_guild.id = 123456
            
            alice = Mock()
            alice.id = 11111
            alice.name = "alice"
            
            bob = Mock()
            bob.id = 22222
            bob.name = "bob"
            
            def get_member(user_id):
                if user_id == 11111:
                    return alice
                elif user_id == 22222:
                    return bob
                return None
            
            mock_guild.get_member.side_effect = get_member
            mock_interaction.guild = mock_guild
            
            mock_bot = Mock()
            commands = BotCommands(mock_bot)
            
            with patch('utils.server_selector.resolve_server_context') as mock_resolve:
                mock_resolve.return_value = ([mock_guild], False)
                
                with patch('bot.commands.conversation_context') as mock_context:
                    mock_context.has_context.return_value = False
                    
                    with patch('bot.commands.server_settings_client') as mock_settings:
                        mock_settings.get_bot_persona.return_value = "TealDR"
                        
                        # Find messages FROM alice that MENTION bob
                        await commands.ask_command(
                            interaction=mock_interaction,
                            query="what did alice say about bob",
                            from_user=alice,
                            mentions=bob
                        )
            
            # Should have both filters
            call_kwargs = mock_pipeline.call_args[1]
            assert call_kwargs["author_id"] == 11111  # From alice
            assert call_kwargs["mentions_user_id"] == 22222  # Mentioning bob


class TestMentionsFiltering:
    """Test the actual mention filtering logic in database layer."""
    
    @pytest.mark.asyncio
    async def test_semantic_search_filters_mentions(self):
        """Test that semantic_search_filtered correctly filters by mentions."""
        from database.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            # Mock messages with and without mentions
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {
                    "message_id": 1,
                    "content": "Hey <@12345>, check this out",
                    "author_id": 999,
                    "embedding": [0.1] * 768
                },
                {
                    "message_id": 2,
                    "content": "Hello <@!12345>, how are you?",  # Nickname mention
                    "author_id": 888,
                    "embedding": [0.2] * 768
                },
                {
                    "message_id": 3,
                    "content": "This message doesn't mention anyone",
                    "author_id": 777,
                    "embedding": [0.3] * 768
                }
            ])
            mock_table.return_value = mock_chain
            
            # Search with mentions filter
            results = await client.semantic_search_filtered(
                embedding=[0.5] * 768,
                server_id=123456,
                mentions_user_id=12345
            )
            
            # Should only return messages that mention user 12345
            assert len(results) == 2
            assert all("<@12345>" in msg["content"] or "<@!12345>" in msg["content"] for msg in results)
    
    @pytest.mark.asyncio
    async def test_mentions_filter_handles_both_formats(self):
        """Test that mentions filter handles both <@id> and <@!id> formats."""
        from database.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        
        with patch.object(client.client, 'table') as mock_table:
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.order.return_value = mock_chain
            mock_chain.limit.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data=[
                {"message_id": 1, "content": "Standard mention <@99999>", "embedding": [0.1] * 768},
                {"message_id": 2, "content": "Nickname mention <@!99999>", "embedding": [0.2] * 768},
            ])
            mock_table.return_value = mock_chain
            
            results = await client.semantic_search_filtered(
                embedding=[0.5] * 768,
                server_id=123,
                mentions_user_id=99999
            )
            
            # Both formats should be found
            assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
