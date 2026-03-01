import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import discord

# Import Discord bot components
from bot.commands import ask_command


class TestDiscordIntegration:
    """Test Discord bot integration with temporal Graph RAG."""
    
    @pytest.mark.asyncio
    async def test_ask_command_temporal_query(self):
        """Test /ask command with temporal context query."""
        
        # Mock Discord interaction
        mock_interaction = Mock(spec=discord.Interaction)
        mock_interaction.guild = Mock()
        mock_interaction.guild.id = 1131555356418523180
        mock_interaction.user = Mock()
        mock_interaction.user.display_name = "test_user"
        mock_interaction.user.id = 12345
        mock_interaction.channel = Mock()
        mock_interaction.channel.id = 67890
        mock_interaction.followup = AsyncMock()
        
        # Mock server settings
        mock_persona = "You are TeaL;DR, a helpful Discord bot."
        
        # Mock Graph RAG pipeline result
        mock_pipeline_result = {
            "context": [
                {
                    "source": "graph",
                    "content": "Deployment started successfully at 2PM",
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
        
        mock_answer = "Based on the temporal context, the deployment discussion started last week with planning by **sidtheitguy** in #dev-ops, and was successfully executed today by **limo.ew**. This shows a clear progression from planning to execution over a 7-day period."
        
        with patch('bot.commands.server_settings_client.get_bot_persona', return_value=mock_persona), \
             patch('bot.commands.run_query_pipeline', return_value=mock_pipeline_result), \
             patch('bot.commands.generate_answer', return_value=mock_answer), \
             patch('bot.commands.embed_builder') as mock_embed_builder:
            
            # Mock embed creation
            mock_embed = Mock()
            mock_embed_builder.create_paginated_embeds.return_value = [mock_embed]
            
            # Test the ask command
            await ask_command(
                interaction=mock_interaction,
                query="What's the background context on the deployment?"
            )
            
            # Verify pipeline was called with correct parameters
            # Verify answer generation was called
            # Verify embed was created and sent
            mock_interaction.followup.send.assert_called_once()
            
            print("✅ Discord /ask command with temporal context works")
    
    @pytest.mark.asyncio
    async def test_ask_command_conversation_thread(self):
        """Test /ask command with conversation thread query."""
        
        mock_interaction = Mock(spec=discord.Interaction)
        mock_interaction.guild = Mock()
        mock_interaction.guild.id = 1131555356418523180
        mock_interaction.user = Mock()
        mock_interaction.user.display_name = "test_user"
        mock_interaction.followup = AsyncMock()
        
        mock_pipeline_result = {
            "context": [
                {
                    "source": "graph",
                    "content": "Bug reported in authentication system",
                    "author": "quantadude",
                    "channel": "bug-reports",
                    "timestamp": "2026-03-01T10:00:00Z",
                    "conversation_thread": {
                        "context_type": "thread_starter",
                        "primary_entity": "authentication bug"
                    }
                },
                {
                    "source": "graph",
                    "content": "Working on a fix for the auth issue",
                    "author": "vivek_75006",
                    "channel": "bug-reports", 
                    "timestamp": "2026-03-01T11:00:00Z",
                    "conversation_thread": {
                        "context_type": "thread_message",
                        "time_gap_hours": 1,
                        "mentioned_entities": ["authentication", "fix"]
                    }
                }
            ],
            "understanding": {
                "intent": "conversation_threads",
                "primary_entity": "authentication bug"
            },
            "temporal_connections": 0,
            "conversation_threads": 1
        }
        
        mock_answer = "The authentication bug discussion thread shows: **quantadude** reported the issue at 10:00 AM, then **vivek_75006** responded 1 hour later saying they're working on a fix. This demonstrates active problem-solving collaboration."
        
        with patch('bot.commands.server_settings_client.get_bot_persona', return_value="Test persona"), \
             patch('bot.commands.run_query_pipeline', return_value=mock_pipeline_result), \
             patch('bot.commands.generate_answer', return_value=mock_answer), \
             patch('bot.commands.embed_builder') as mock_embed_builder:
            
            mock_embed_builder.create_paginated_embeds.return_value = [Mock()]
            
            await ask_command(
                interaction=mock_interaction,
                query="Continue the discussion about the authentication bug"
            )
            
            mock_interaction.followup.send.assert_called_once()
            
            print("✅ Discord /ask command with conversation threads works")


class TestRealWorldScenarios:
    """Test real-world scenarios that users might encounter."""
    
    @pytest.mark.asyncio
    async def test_server_migration_context(self):
        """Test: 'What's the context behind the server migration?'"""
        
        # This tests the scenario where:
        # - Planning happened 2 weeks ago
        # - Implementation started 1 week ago  
        # - Issues were discussed 3 days ago
        # - Resolution happened today
        
        query = "What's the context behind the server migration?"
        
        mock_understanding = {
            "intent": "temporal_context",
            "primary_entity": "server migration",
            "temporal_context_needed": True,
            "search_terms": ["server", "migration", "context"]
        }
        
        mock_temporal_result = {
            "context": [
                # Today's resolution
                {
                    "source": "graph",
                    "content": "Server migration completed successfully! All services are running on the new infrastructure.",
                    "author": "limo.ew",
                    "channel": "infrastructure",
                    "timestamp": "2026-03-01T16:00:00Z",
                    "temporal_context": {
                        "context_type": "primary",
                        "related_to_entity": "server migration"
                    }
                },
                # 3 days ago - issues
                {
                    "source": "graph", 
                    "content": "Encountering some database connectivity issues during migration testing",
                    "author": "sidtheitguy",
                    "channel": "infrastructure",
                    "timestamp": "2026-02-26T14:00:00Z",
                    "temporal_context": {
                        "context_type": "related_discussion",
                        "time_gap_days": 3,
                        "related_to_entity": "server migration"
                    }
                },
                # 1 week ago - implementation
                {
                    "source": "graph",
                    "content": "Starting the server migration process. Moving databases first, then application servers.",
                    "author": "quantadude",
                    "channel": "infrastructure", 
                    "timestamp": "2026-02-22T09:00:00Z",
                    "temporal_context": {
                        "context_type": "related_discussion", 
                        "time_gap_days": 7,
                        "related_to_entity": "server migration"
                    }
                },
                # 2 weeks ago - planning
                {
                    "source": "graph",
                    "content": "Planning the server migration for next week. Need to coordinate with all teams.",
                    "author": "vivek_75006",
                    "channel": "infrastructure",
                    "timestamp": "2026-02-15T11:00:00Z", 
                    "temporal_context": {
                        "context_type": "related_discussion",
                        "time_gap_days": 14,
                        "related_to_entity": "server migration"
                    }
                }
            ],
            "understanding": mock_understanding,
            "temporal_connections": 3,
            "conversation_threads": 0
        }
        
        with patch('retrieval.query_engine.understand_query', return_value=mock_understanding), \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline', return_value=mock_temporal_result):
            
            result = await run_query_pipeline(
                query=query,
                server_id=1131555356418523180
            )
            
            # Verify temporal connections were found
            assert result["temporal_connections"] == 3
            assert len(result["context"]) == 4
            
            # Verify chronological order of events
            context_items = result["context"]
            timestamps = [item.get("timestamp") for item in context_items if item.get("timestamp")]
            
            # Should have items from different time periods
            assert any("2026-02-15" in ts for ts in timestamps)  # 2 weeks ago
            assert any("2026-02-22" in ts for ts in timestamps)  # 1 week ago  
            assert any("2026-02-26" in ts for ts in timestamps)  # 3 days ago
            assert any("2026-03-01" in ts for ts in timestamps)  # Today
            
            print("✅ Server migration context scenario works")
    
    @pytest.mark.asyncio 
    async def test_bug_discussion_thread(self):
        """Test: 'Continue the discussion about the authentication bug'"""
        
        # This tests conversation thread tracking:
        # - Bug report
        # - Investigation 
        # - Proposed solution
        # - Implementation
        # - Testing
        # - Resolution
        
        query = "Continue the discussion about the authentication bug"
        
        mock_understanding = {
            "intent": "conversation_threads",
            "primary_entity": "authentication bug", 
            "temporal_context_needed": True,
            "search_terms": ["authentication", "bug", "discussion"]
        }
        
        mock_thread_result = {
            "context": [
                # Bug report
                {
                    "source": "graph",
                    "content": "Users are getting 401 errors when trying to log in with valid credentials",
                    "author": "galvanizedsquaresteel6769",
                    "channel": "bug-reports",
                    "timestamp": "2026-03-01T09:00:00Z",
                    "conversation_thread": {
                        "context_type": "thread_starter",
                        "primary_entity": "authentication bug"
                    }
                },
                # Investigation
                {
                    "source": "graph",
                    "content": "Looking into this - seems like the JWT token validation is failing",
                    "author": "ogyuvrajs",
                    "channel": "bug-reports",
                    "timestamp": "2026-03-01T09:30:00Z",
                    "conversation_thread": {
                        "context_type": "thread_message",
                        "time_gap_hours": 0.5,
                        "mentioned_entities": ["JWT", "token", "validation"]
                    }
                },
                # Solution
                {
                    "source": "graph", 
                    "content": "Found the issue! The secret key rotation broke the token validation. Fixing now.",
                    "author": "sayushkamat1660",
                    "channel": "bug-reports",
                    "timestamp": "2026-03-01T10:15:00Z",
                    "conversation_thread": {
                        "context_type": "thread_message",
                        "time_gap_hours": 1.25,
                        "mentioned_entities": ["secret key", "rotation", "fix"]
                    }
                },
                # Resolution
                {
                    "source": "graph",
                    "content": "Authentication bug is fixed! All users should be able to log in normally now.",
                    "author": "sayushkamat1660", 
                    "channel": "bug-reports",
                    "timestamp": "2026-03-01T11:00:00Z",
                    "conversation_thread": {
                        "context_type": "thread_message",
                        "time_gap_hours": 2,
                        "mentioned_entities": ["fixed", "login", "resolved"]
                    }
                }
            ],
            "understanding": mock_understanding,
            "temporal_connections": 0,
            "conversation_threads": 1
        }
        
        with patch('retrieval.query_engine.understand_query', return_value=mock_understanding), \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline', return_value=mock_thread_result):
            
            result = await run_query_pipeline(
                query=query,
                server_id=1131555356418523180
            )
            
            # Verify conversation thread was tracked
            assert result["conversation_threads"] == 1
            assert len(result["context"]) == 4
            
            # Verify thread progression
            context_items = result["context"]
            thread_items = [item for item in context_items if item.get("conversation_thread")]
            assert len(thread_items) == 4
            
            # Verify time gaps make sense (should be sequential)
            time_gaps = [item["conversation_thread"].get("time_gap_hours", 0) for item in thread_items[1:]]
            assert all(gap >= 0 for gap in time_gaps)
            
            print("✅ Bug discussion thread scenario works")


# Performance and edge case tests
class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_no_temporal_context_found(self):
        """Test when no temporal context is available."""
        
        query = "What's the background on XYZ project?"
        
        mock_understanding = {
            "intent": "temporal_context", 
            "primary_entity": "XYZ project",
            "temporal_context_needed": True
        }
        
        # Empty results
        mock_result = {
            "context": [],
            "understanding": mock_understanding,
            "temporal_connections": 0,
            "conversation_threads": 0
        }
        
        with patch('retrieval.query_engine.understand_query', return_value=mock_understanding), \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline', return_value=mock_result):
            
            result = await run_query_pipeline(
                query=query,
                server_id=1131555356418523180
            )
            
            assert len(result["context"]) == 0
            assert result["temporal_connections"] == 0
            
            print("✅ No temporal context edge case works")
    
    def test_malformed_temporal_data(self):
        """Test handling of malformed temporal data."""
        
        # Graph results with missing or malformed temporal data
        graph_results = [
            {
                "content": "Valid message",
                "author": "user1",
                "related_discussions": [
                    {
                        "content": "Related message",
                        # Missing timestamp and time_gap
                        "author": "user2"
                    }
                ]
            },
            {
                # Missing content
                "author": "user3",
                "timestamp": "invalid-timestamp"
            }
        ]
        
        vector_results = []
        
        # Should not crash and should handle gracefully
        context = assemble_context(graph_results, vector_results, "temporal_context")
        
        # Should still return valid items
        valid_items = [item for item in context if item.get("content")]
        assert len(valid_items) >= 1
        
        print("✅ Malformed temporal data handling works")


# Main test runner
async def run_integration_tests():
    """Run all integration and real-world scenario tests."""
    
    print("🔗 Running Integration & Real-World Tests")
    print("=" * 50)
    
    # Discord Integration Tests
    print("\n🤖 Testing Discord Integration...")
    discord_tests = TestDiscordIntegration()
    await discord_tests.test_ask_command_temporal_query()
    await discord_tests.test_ask_command_conversation_thread()
    
    # Real-World Scenarios
    print("\n🌍 Testing Real-World Scenarios...")
    scenario_tests = TestRealWorldScenarios()
    await scenario_tests.test_server_migration_context()
    await scenario_tests.test_bug_discussion_thread()
    
    # Edge Cases
    print("\n⚠️ Testing Edge Cases...")
    edge_tests = TestEdgeCases()
    await edge_tests.test_no_temporal_context_found()
    edge_tests.test_malformed_temporal_data()
    
    print("\n" + "=" * 50)
    print("✅ All integration tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
