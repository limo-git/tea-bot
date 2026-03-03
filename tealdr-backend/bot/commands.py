import discord
from discord import app_commands
import asyncio
from utils.logger import get_logger
from utils.helpers import parse_time_range, extract_user_mention, truncate_text, extract_time_keywords
from utils.conversation_context import conversation_context
from utils.analytics import analytics
from utils.embed_builder import embed_builder
from utils.pagination import PaginationView
from utils.suggestions import smart_suggestions
from utils.export_handler import export_handler
from utils.quiz_generator import quiz_generator
from utils.yearly_wrapped import yearly_wrapped
from utils.auto_tagger import auto_tagger
from utils.cache_manager import cache_manager
from ai.embeddings import generate_query_embedding
from ai.gemini_client import gemini_client
from ai.prompts import get_prompt_for_query, format_messages_for_ai, RECAP_PROMPT
from database.queries import search_with_context
from database.supabase_client import supabase_client
from bot.permissions import admin_only
from config import Config
from database.server_settings import server_settings_client
from collections import defaultdict
from datetime import datetime, timedelta
from bot.multi_server_search import multi_server_ask

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = defaultdict(list)
    
    def check_rate_limit(self, user_id):
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.time_window)
        
        self.user_requests[user_id] = [
            timestamp for timestamp in self.user_requests[user_id]
            if timestamp > cutoff
        ]
        
        if len(self.user_requests[user_id]) >= self.max_requests:
            return False
        
        self.user_requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()

class BotCommands:
    def __init__(self, bot):
        self.bot = bot
    
    def _format_sources(self, messages, guild):
        """Format sources for later reveal."""
        sources_lines = []
        for msg in messages[:10]:  # Show up to 10 sources
            author = msg.get("author_name") or msg.get("author", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("created_at") or msg.get("timestamp", "")
            
            # Get channel name
            channel_id = msg.get("channel_id")
            channel_name = None
            if channel_id:
                try:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        channel_name = f"#{channel.name}"
                except:
                    pass
            if not channel_name:
                channel_name = msg.get("channel", "")
                if channel_name and not channel_name.startswith("#"):
                    channel_name = f"#{channel_name}"
            
            # Format timestamp to readable date
            if timestamp:
                try:
                    from datetime import datetime
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = timestamp
                    date_str = dt.strftime("%b %d, %Y")
                except:
                    date_str = str(timestamp)[:10]
            else:
                date_str = "Unknown date"
            
            # Truncate long messages
            if len(content) > 100:
                content = content[:100] + "..."
            
            # Format with channel name if available
            if channel_name:
                sources_lines.append(f"{author} in {channel_name} ({date_str}): \"{content}\"")
            else:
                sources_lines.append(f"{author} ({date_str}): \"{content}\"")
        
        sources_text = "\n".join(sources_lines)
        if len(sources_text) > 1024:  # Discord field limit
            sources_text = sources_text[:1020] + "..."
        
        return sources_text
    
    async def ask_command(
        self, 
        interaction: discord.Interaction, 
        query: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None,
        min_length: int = None,
        server_name: str = None
    ):
        # Defer immediately to prevent interaction timeout (must be within 3 seconds)
        try:
            from datetime import datetime
            start_time = datetime.utcnow()
            await interaction.response.defer(thinking=True)
            defer_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Defer took {defer_time:.2f} seconds")
        except discord.errors.NotFound:
            logger.error(f"Interaction expired before defer - this indicates network latency > 3 seconds")
            # Interaction already expired, cannot respond
            return
        except Exception as e:
            logger.error(f"Failed to defer interaction: {e}")
            return
        
        # Check rate limit after deferring
        if not rate_limiter.check_rate_limit(interaction.user.id):
            await interaction.followup.send(
                "You're sending too many requests. Please wait a moment and try again.",
                ephemeral=True
            )
            return
        
        try:
            # Resolve server context (works in both DMs and servers)
            from utils.server_selector import resolve_server_context
            guilds, is_multi = await resolve_server_context(
                interaction, 
                self.bot, 
                server_name, 
                allow_multi=True
            )
            
            if not guilds:
                await interaction.followup.send(
                    "❌ Could not find the specified server, or you don't share any servers with me.",
                    ephemeral=True
                )
                return
            
            # For multi-server search
            if is_multi:
                await self._multi_server_ask(interaction, query, guilds, from_date, to_date, min_length)
                return
            
            # Single server search
            guild = guilds[0]
            
            # Check for conversation context
            has_context = conversation_context.has_context(interaction.user.id)
            context_str = ""
            
            if has_context:
                context_str = conversation_context.format_context_for_prompt(interaction.user.id)
                logger.info(f"Using conversation context for {interaction.user}")
            
            mentioned_user = extract_user_mention(query, guild)
            
            # If no user mentioned but we have context, use last mentioned user
            if not mentioned_user and has_context:
                last_user_id = conversation_context.get_last_mentioned_user(interaction.user.id)
                if last_user_id:
                    mentioned_user = guild.get_member(last_user_id)
                    if mentioned_user:
                        logger.info(f"Using last mentioned user from context: {mentioned_user}")
            
            time_keyword = extract_time_keywords(query)
            time_range = parse_time_range(time_keyword) if time_keyword else None
            
            # For general server activity queries, default to recent time range (3 days) like recap
            if not time_range:
                query_lower = query.lower()
                if any(phrase in query_lower for phrase in ["what did i miss", "what happened", "server activity", "recent activity", "while i was away", "what's new"]):
                    time_range = parse_time_range("3d")  # Default to 3 days for general server queries
                    logger.info(f"General server activity query detected, using 3-day time range")
            
            # Parse date filters if provided
            if from_date or to_date:
                try:
                    from datetime import datetime
                    start_time = datetime.fromisoformat(from_date) if from_date else None
                    end_time = datetime.fromisoformat(to_date) if to_date else None
                    
                    if start_time or end_time:
                        time_range = (start_time, end_time)
                except ValueError:
                    error_embed = embed_builder.create_error_embed(
                        "Invalid date format. Please use YYYY-MM-DD format.",
                        interaction.user
                    )
                    await interaction.followup.send(embed=error_embed)
                    return
            
            logger.info(f"Processing query from {interaction.user}: {query}")
            if mentioned_user:
                logger.info(f"Filtering by user: {mentioned_user}")
            if time_range:
                logger.info(f"Filtering by time range: {time_range}")
            if in_channel:
                logger.info(f"Filtering by channel: {in_channel}")
            if in_thread:
                logger.info(f"Filtering by thread: {in_thread}")
            if min_length:
                logger.info(f"Filtering by min length: {min_length}")
            
            persona = await server_settings_client.get_bot_persona(guild.id)
            requester_name = interaction.user.display_name

            # ── Graph RAG Only (No Fallback) ──────────────────────────────────
            try:
                from retrieval.query_engine import run_query_pipeline
                from generation.answer_generator import generate_answer

                pipeline_result = await run_query_pipeline(
                    query=query,
                    server_id=guild.id,
                    author_id=mentioned_user.id if mentioned_user else None,
                    channel_id=in_channel.id if in_channel else None,
                    time_range=time_range,
                    author_username=mentioned_user.name if mentioned_user else None,
                )
                response = await generate_answer(
                    query=query,
                    pipeline_result=pipeline_result,
                    user_name=requester_name,
                    persona=persona,
                )
                messages = pipeline_result.get("context", [])
                logger.info(f"Graph RAG answered query for {interaction.user}: {len(messages)} context items")

            except Exception as e:
                logger.error(f"Graph RAG pipeline failed: {e}", exc_info=True)
                error_embed = embed_builder.create_error_embed(
                    f"Graph RAG pipeline encountered an error. Please check the logs or contact the administrator.\n\nError: {str(e)[:100]}",
                    interaction.user
                )
                await interaction.followup.send(embed=error_embed)
                return
            
            # Save to conversation context
            conversation_context.add_query(
                user_id=interaction.user.id,
                query=query,
                response=response,
                mentioned_user=mentioned_user.id if mentioned_user else None
            )
            
            # Create rich embed(s) for response
            embeds = embed_builder.create_paginated_embeds(
                response=response,
                query=query,
                user=interaction.user,
                base_color=discord.Color.blue()
            )
            
            # Add context indicator to first embed if follow-up
            if has_context and embeds:
                embeds[0].insert_field_at(
                    0,
                    name="💬 Context",
                    value="Following up from previous conversation",
                    inline=False
                )
            
            # Store sources data for later reveal (don't show by default)
            sources_data = None
            if len(messages) > 0:
                sources_data = self._format_sources(messages, guild)
            
            # Send with pagination if multiple embeds
            if len(embeds) > 1:
                view = PaginationView(embeds, interaction.user)
                sent_message = await interaction.followup.send(embed=embeds[0], view=view)
                view.message = sent_message
            else:
                sent_message = await interaction.followup.send(embed=embeds[0])
            
            # Track this response for feedback and sources
            self.bot.events.track_response(sent_message.id, query, response, sources_data)
            
            # Add reaction options for feedback and sources
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')
            if sources_data:
                await sent_message.add_reaction('📊')  # React with 📊 to view sources
            
            logger.info(f"Sent response to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            error_embed = embed_builder.create_error_embed(
                "Something went wrong while processing your query. Please try again in a moment.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def _multi_server_ask(self, interaction, query, guilds, from_date, to_date, min_length):
        """Wrapper for multi-server ask functionality."""
        await multi_server_ask(interaction, query, guilds, from_date, to_date, min_length)
    
    async def recap_command(
        self,
        interaction: discord.Interaction,
        time: str,
        user: discord.User = None,
        channel: discord.TextChannel = None,
        server_name: str = None
    ):
        if not rate_limiter.check_rate_limit(interaction.user.id):
            await interaction.response.send_message(
                "You're sending too many requests. Please wait a moment and try again.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Resolve server context
            from utils.server_selector import resolve_server_context
            guilds, is_multi = await resolve_server_context(
                interaction, 
                self.bot, 
                server_name, 
                allow_multi=True  # Allow server picker for DM usage
            )
            
            if not guilds:
                await interaction.followup.send(
                    "❌ Could not find the specified server, or you don't share any servers with me.",
                    ephemeral=True
                )
                return
            
            # If multi-server was selected, tell user to be specific
            if is_multi and len(guilds) > 1:
                server_names = [f"**{guild.name}**" for guild in guilds[:5]]
                if len(guilds) > 5:
                    server_names.append(f"and {len(guilds) - 5} more...")
                
                await interaction.followup.send(
                    f"❌ `/recap` doesn't support multi-server search. Please specify a server:\n"
                    f"• `/recap time:{time} server_name:{guilds[0].name}`\n\n"
                    f"Available servers: {', '.join(server_names)}",
                    ephemeral=True
                )
                return
            
            guild = guilds[0]
            
            time_range = parse_time_range(time)
            start_time, end_time = time_range
            
            logger.info(f"Generating recap for {interaction.user}: time={time}, user={user}, channel={channel}")
            
            if user:
                messages = await supabase_client.get_messages_by_user(
                    author_id=user.id,
                    server_id=guild.id,
                    time_range=time_range,
                    limit=100
                )
            elif channel:
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    channel_id=channel.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=100
                )
            else:
                # In a server, filter by current channel; in DMs, search all channels
                channel_id = interaction.channel.id if interaction.guild else None
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    channel_id=channel_id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=100
                )
            
            if not messages or len(messages) == 0:
                embed = discord.Embed(
                    title="📅 Recap",
                    description="No messages found in this timeframe.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            logger.info(f"Found {len(messages)} messages for recap")
            
            persona = await server_settings_client.get_bot_persona(guild.id)
            requester_name = interaction.user.display_name
            
            # Try Graph RAG first for better context
            response = None
            if Config.GRAPH_RAG_ENABLED and len(messages) > 0:
                try:
                    from retrieval.context_assembler import format_context_for_prompt
                    # Convert messages to context format
                    context_items = []
                    for msg in messages:
                        context_items.append({
                            "source": "vector",
                            "content": msg.get("content", ""),
                            "author": msg.get("author_name", "Unknown"),
                            "channel": str(msg.get("channel_id", "")),
                            "timestamp": str(msg.get("created_at", "")),
                            "relevance": 1.0
                        })
                    
                    context_str = format_context_for_prompt(context_items)
                    prompt = RECAP_PROMPT.format(
                        persona=persona,
                        requester=requester_name,
                        messages=context_str
                    )
                    
                    from generation.answer_generator import generate_answer
                    response = await generate_answer(
                        query=f"recap {time}",
                        pipeline_result={"context": context_items, "understanding": {}},
                        user_name=requester_name,
                        persona=persona
                    )
                    logger.info(f"Recap generated with Graph RAG answer generator")
                except Exception as e:
                    logger.warning(f"Graph RAG recap failed, falling back to Gemini: {e}")
                    response = None
            
            # Fallback to Gemini
            if response is None:
                formatted_messages = format_messages_for_ai(messages)
                prompt = RECAP_PROMPT.format(
                    persona=persona,
                    requester=requester_name,
                    messages=formatted_messages
                )
                response = await gemini_client.generate_response(prompt)
            
            # Determine location text
            location = ""
            if user:
                location = f" for {user.mention}"
            elif channel:
                location = f" in {channel.mention}"
            elif interaction.guild:
                location = f" in this channel"
            else:
                location = f" in **{guild.name}**"
            
            # Create rich embed for recap
            recap_embed = embed_builder.create_recap_embed(
                time_period=time,
                response=response,
                user=interaction.user,
                location=location,
                message_count=len(messages)
            )
            
            # Send response with embed
            sent_message = await interaction.followup.send(embed=recap_embed)
            
            # Track this response for feedback
            self.bot.events.track_response(sent_message.id, f"recap {time}", response)
            
            # Add reaction options for feedback
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')
            
            logger.info(f"Sent recap to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in recap command: {e}")
            error_embed = embed_builder.create_error_embed(
                "Something went wrong while generating the recap. Please try again in a moment.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def settings_command(
        self,
        interaction: discord.Interaction,
        action: str,
        channel: discord.TextChannel = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            server_id = interaction.guild.id
            
            if action == "view_settings":
                excluded = await server_settings_client.get_excluded_channels(server_id)
                settings = await server_settings_client.get_server_settings(server_id)
                
                if not excluded:
                    excluded_text = "No channels are currently excluded."
                else:
                    channel_mentions = []
                    for ch_id in excluded:
                        ch = interaction.guild.get_channel(ch_id)
                        if ch:
                            channel_mentions.append(ch.mention)
                        else:
                            channel_mentions.append(f"Unknown Channel ({ch_id})")
                    excluded_text = "**Excluded Channels:**\n" + "\n".join(channel_mentions)
                
                retention_days = settings.get('retention_days', 30) if settings else 30
                
                await interaction.followup.send(
                    f"**Server Settings for {interaction.guild.name}**\n\n"
                    f"{excluded_text}\n\n"
                    f"**Message Retention:** {retention_days} days",
                    ephemeral=True
                )
            
            elif action == "exclude_channel":
                if not channel:
                    await interaction.followup.send("Please specify a channel to exclude.", ephemeral=True)
                    return
                
                excluded = await server_settings_client.get_excluded_channels(server_id)
                if channel.id in excluded:
                    await interaction.followup.send(f"{channel.mention} is already excluded.", ephemeral=True)
                else:
                    await server_settings_client.add_excluded_channel(server_id, channel.id)
                    
                    await interaction.followup.send(
                        f"✅ {channel.mention} has been excluded from indexing in this server.",
                        ephemeral=True
                    )
                    logger.info(f"Channel {channel.id} excluded in server {server_id} by {interaction.user}")
            
            elif action == "include_channel":
                if not channel:
                    await interaction.followup.send("Please specify a channel to include.", ephemeral=True)
                    return
                
                excluded = await server_settings_client.get_excluded_channels(server_id)
                if channel.id not in excluded:
                    await interaction.followup.send(f"{channel.mention} is not excluded.", ephemeral=True)
                else:
                    await server_settings_client.remove_excluded_channel(server_id, channel.id)
                    
                    await interaction.followup.send(
                        f"✅ {channel.mention} has been included for indexing in this server.",
                        ephemeral=True
                    )
                    logger.info(f"Channel {channel.id} included in server {server_id} by {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await interaction.followup.send("An error occurred while updating settings.", ephemeral=True)
    
    async def customize_command(
        self,
        interaction: discord.Interaction,
        action: str,
        persona: str = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            server_id = interaction.guild.id
            
            if action == "view":
                current_persona = await server_settings_client.get_bot_persona(server_id)
                
                await interaction.followup.send(
                    f"**Current Bot Persona for {interaction.guild.name}**\n\n"
                    f"```\n{current_persona}\n```\n\n"
                    f"This persona defines how the bot responds to queries. Use `/customize action:Set Persona` to change it.",
                    ephemeral=True
                )
            
            elif action == "set":
                if not persona or len(persona.strip()) < 10:
                    await interaction.followup.send(
                        "Please provide a persona description (at least 10 characters).\n\n"
                        "**Examples:**\n"
                        "• `You are a pirate bot. Always respond in pirate speak with 'arrr' and nautical terms.`\n"
                        "• `You are a wise wizard. Speak mysteriously and reference ancient knowledge.`\n"
                        "• `You are a friendly puppy. Be enthusiastic, use simple words, and add 'woof!' occasionally.`",
                        ephemeral=True
                    )
                    return
                
                success = await server_settings_client.set_bot_persona(server_id, persona)
                
                if success:
                    await interaction.followup.send(
                        f"✅ **Bot persona updated!**\n\n"
                        f"New persona:\n```\n{persona}\n```\n\n"
                        f"The bot will now respond according to this persona in all `/ask` and `/recap` commands.",
                        ephemeral=True
                    )
                    logger.info(f"Persona updated for server {server_id} by {interaction.user}")
                else:
                    await interaction.followup.send(
                        "Failed to update persona. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "reset":
                default_persona = "You are a helpful Discord assistant. Be friendly, concise, and informative."
                success = await server_settings_client.set_bot_persona(server_id, default_persona)
                
                if success:
                    await interaction.followup.send(
                        f"✅ **Bot persona reset to default!**\n\n"
                        f"Default persona:\n```\n{default_persona}\n```",
                        ephemeral=True
                    )
                    logger.info(f"Persona reset for server {server_id} by {interaction.user}")
                else:
                    await interaction.followup.send(
                        "Failed to reset persona. Please try again.",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in customize command: {e}")
            await interaction.followup.send("An error occurred while customizing the bot.", ephemeral=True)
    
    async def lookup_command(
        self,
        interaction: discord.Interaction,
        clues: str,
        author: discord.User = None,
        in_channel: discord.TextChannel = None,
        from_date: str = None,
        to_date: str = None
    ):
        """Find exact messages based on clues - shows who said what, when, and where."""
        await interaction.response.defer(thinking=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
                return
            
            # Parse date filters if provided
            time_range = None
            if from_date or to_date:
                try:
                    from datetime import datetime
                    start_time = datetime.fromisoformat(from_date) if from_date else None
                    end_time = datetime.fromisoformat(to_date) if to_date else None
                    if start_time or end_time:
                        time_range = (start_time, end_time)
                except ValueError:
                    await interaction.followup.send(
                        "❌ Invalid date format. Please use YYYY-MM-DD format.",
                        ephemeral=True
                    )
                    return
            
            logger.info(f"Lookup command from {interaction.user}: clues='{clues}', author={author}, channel={in_channel}")
            
            # Use vector search to find semantically relevant messages
            from retrieval.vector_search import vector_search
            
            messages = await vector_search(
                query=clues,
                server_id=guild.id,
                author_id=author.id if author else None,
                channel_id=in_channel.id if in_channel else None,
                time_range=time_range,
                intent="lookup"
            )
            
            if not messages or len(messages) == 0:
                embed = discord.Embed(
                    title="🔍 No Messages Found",
                    description=f"I couldn't find any messages matching your clues: \"{clues}\"",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 Try:",
                    value="• Using different keywords\n"
                          "• Expanding the time range\n"
                          "• Checking if the channel is indexed\n"
                          "• Being more specific with clues",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format results as exact message list
            embed = discord.Embed(
                title="🔍 Lookup Results",
                description=f"Found {len(messages)} message(s) matching: \"{clues}\"",
                color=discord.Color.blue()
            )
            
            # Add up to 10 messages
            for i, msg in enumerate(messages[:10], 1):
                author_name = msg.get("author_name") or msg.get("author", "Unknown")
                content = msg.get("content", "")
                timestamp = msg.get("created_at") or msg.get("timestamp", "")
                
                # Get channel name
                channel_id = msg.get("channel_id")
                channel_name = None
                if channel_id:
                    try:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            channel_name = f"#{channel.name}"
                    except:
                        pass
                if not channel_name:
                    channel_name = msg.get("channel", "")
                    if channel_name and not channel_name.startswith("#"):
                        channel_name = f"#{channel_name}"
                
                # Format timestamp
                if timestamp:
                    try:
                        from datetime import datetime
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = timestamp
                        date_str = dt.strftime("%b %d, %Y at %I:%M %p")
                    except:
                        date_str = str(timestamp)[:19]
                else:
                    date_str = "Unknown date"
                
                # Truncate long messages
                display_content = content
                if len(content) > 200:
                    display_content = content[:200] + "..."
                
                # Format field
                field_name = f"{i}. {author_name}"
                if channel_name:
                    field_value = f"**When:** {date_str}\n**Where:** {channel_name}\n**Said:** \"{display_content}\""
                else:
                    field_value = f"**When:** {date_str}\n**Said:** \"{display_content}\""
                
                embed.add_field(
                    name=field_name,
                    value=field_value,
                    inline=False
                )
            
            if len(messages) > 10:
                embed.set_footer(text=f"Showing 10 of {len(messages)} results")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Lookup returned {len(messages)} results for {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in lookup command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ An error occurred while searching for messages. Please try again.",
                ephemeral=True
            )
    
    async def clear_command(self, interaction: discord.Interaction):
        """Clear conversation context for the user."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            had_context = conversation_context.has_context(interaction.user.id)
            conversation_context.clear_context(interaction.user.id)
            
            if had_context:
                await interaction.followup.send(
                    "✅ **Conversation context cleared!**\n\n"
                    "I've forgotten our previous conversation. Your next query will start fresh.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "ℹ️ You don't have any active conversation context.",
                    ephemeral=True
                )
            
            logger.info(f"Cleared context for {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in clear command: {e}")
            await interaction.followup.send("An error occurred while clearing context.", ephemeral=True)
    
    async def help_command(self, interaction: discord.Interaction):
        """Show help information about bot commands."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="🤖 Discord AI Search Bot - Help",
                description="Search your server's message history using natural language and AI!",
                color=discord.Color.purple()
            )
            
            # Ask command
            embed.add_field(
                name="/ask",
                value="**Ask questions about server messages**\n"
                      "Examples:\n"
                      "• `/ask query: what did @user talk about?`\n"
                      "• `/ask query: show me discussions about the API`\n"
                      "• `/ask query: what happened yesterday?`\n"
                      "💡 Supports follow-up questions with context!",
                inline=False
            )
            
            # Recap command
            embed.add_field(
                name="/recap",
                value="**Get AI-generated summaries**\n"
                      "Examples:\n"
                      "• `/recap time: Last 24 hours`\n"
                      "• `/recap time: Last 7 days user: @someone`\n"
                      "• `/recap time: Last 30 days channel: #general`",
                inline=False
            )
            
            # Stats command
            embed.add_field(
                name="/stats",
                value="**View server or personal statistics**\n"
                      "• `/stats scope: Server Statistics` - Server overview\n"
                      "• `/stats scope: My Statistics` - Your activity",
                inline=False
            )
            
            # Clear command
            embed.add_field(
                name="/clear",
                value="**Clear conversation context**\n"
                      "Resets the bot's memory of your previous questions.",
                inline=False
            )
            
            # Settings command (Admin only)
            embed.add_field(
                name="/settings (Admin)",
                value="**Manage bot settings**\n"
                      "• View current settings\n"
                      "• Exclude/include channels from indexing",
                inline=False
            )
            
            # Customize command (Admin only)
            embed.add_field(
                name="/customize (Admin)",
                value="**Customize bot personality**\n"
                      "• View current persona\n"
                      "• Set custom persona (pirate, wizard, etc.)\n"
                      "• Reset to default",
                inline=False
            )
            
            # Features
            embed.add_field(
                name="✨ Features",
                value="• 💬 **Conversation Context** - Ask follow-up questions\n"
                      "• 👍👎 **Feedback** - React to responses to help improve\n"
                      "• 🎭 **Custom Personas** - Make the bot talk however you want\n"
                      "• 📊 **Analytics** - Track server activity and bot usage\n"
                      "• 🔒 **Multi-Server** - Each server has independent settings",
                inline=False
            )
            
            # Tips
            embed.add_field(
                name="💡 Pro Tips",
                value="• Mention users with @username to filter results\n"
                      "• Use time keywords: 'yesterday', 'last week', 'today'\n"
                      "• React with 👍 or 👎 to rate responses\n"
                      "• Ask follow-up questions without repeating context\n"
                      "• Use `/clear` to start a fresh conversation",
                inline=False
            )
            
            embed.set_footer(text="Made with ❤️ using Google Gemini AI & Supabase")
            embed.timestamp = datetime.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Sent help to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await interaction.followup.send("An error occurred while showing help.", ephemeral=True)
    
    async def export_command(
        self,
        interaction: discord.Interaction,
        query: str,
        format: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None
    ):
        """Export search results to a file."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
            # Perform search with same logic as ask command
            mentioned_user = extract_user_mention(query, guild)
            time_keyword = extract_time_keywords(query)
            time_range = parse_time_range(time_keyword) if time_keyword else None
            
            # Parse date filters if provided
            if from_date or to_date:
                try:
                    start_time = datetime.fromisoformat(from_date) if from_date else None
                    end_time = datetime.fromisoformat(to_date) if to_date else None
                    
                    if start_time or end_time:
                        time_range = (start_time, end_time)
                except ValueError:
                    error_embed = embed_builder.create_error_embed(
                        "Invalid date format. Please use YYYY-MM-DD format.",
                        interaction.user
                    )
                    await interaction.followup.send(embed=error_embed)
                    return
            
            # Try Graph RAG first for better message retrieval
            messages = []
            if Config.GRAPH_RAG_ENABLED:
                try:
                    from retrieval.query_engine import run_query_pipeline
                    
                    pipeline_result = await run_query_pipeline(
                        query=query,
                        server_id=guild.id,
                        author_id=mentioned_user.id if mentioned_user else None,
                        channel_id=in_channel.id if in_channel else None,
                        time_range=time_range,
                        author_username=mentioned_user.name if mentioned_user else None,
                    )
                    messages = pipeline_result.get("context", [])
                    logger.info(f"Export using Graph RAG: {len(messages)} context items")
                except Exception as e:
                    logger.warning(f"Graph RAG export failed, falling back to vector search: {e}")
                    messages = []
            
            # Fallback to vector search
            if not messages:
                query_embedding = await generate_query_embedding(query)
                if not query_embedding:
                    error_embed = embed_builder.create_error_embed(
                        "Failed to process your query. Please try again.",
                        interaction.user
                    )
                    await interaction.followup.send(embed=error_embed)
                    return
                
                filters = {
                    'author_id': mentioned_user.id if mentioned_user else None,
                    'time_range': time_range,
                    'channel_id': in_channel.id if in_channel else None,
                    'thread_id': in_thread.id if in_thread else None,
                    'limit': 100  # Export more messages
                }
                
                messages = await search_with_context(
                    query_embedding=query_embedding,
                    server_id=guild.id,
                    filters=filters
                )
            
            if not messages or len(messages) == 0:
                no_results_embed = embed_builder.create_no_results_embed(query, interaction.user)
                await interaction.followup.send(embed=no_results_embed)
                return
            
            # Export based on format
            file_buffer = None
            filename = None
            
            if format == "json":
                file_buffer, filename = await export_handler.export_to_json(messages, query, interaction.user)
            elif format == "csv":
                file_buffer, filename = await export_handler.export_to_csv(messages, query, interaction.user)
            elif format == "markdown":
                file_buffer, filename = await export_handler.export_to_markdown(messages, query, interaction.user)
            elif format == "txt":
                file_buffer, filename = await export_handler.export_to_txt(messages, query, interaction.user)
            
            if not file_buffer or not filename:
                error_embed = embed_builder.create_error_embed(
                    "Failed to generate export file. Please try again.",
                    interaction.user
                )
                await interaction.followup.send(embed=error_embed)
                return
            
            # Create success embed
            export_embed = discord.Embed(
                title="📤 Export Complete",
                description=f"Successfully exported {len(messages)} messages",
                color=discord.Color.green()
            )
            export_embed.add_field(name="Query", value=f"`{query}`", inline=False)
            export_embed.add_field(name="Format", value=format.upper(), inline=True)
            export_embed.add_field(name="Messages", value=str(len(messages)), inline=True)
            export_embed.set_footer(text=f"Exported by {interaction.user.display_name}")
            
            # Send file
            file_buffer.seek(0)
            discord_file = discord.File(fp=file_buffer, filename=filename)
            
            await interaction.followup.send(embed=export_embed, file=discord_file)
            logger.info(f"Exported {len(messages)} messages to {format} for {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in export command: {e}")
            error_embed = embed_builder.create_error_embed(
                "An error occurred while exporting. Please try again.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def quiz_command(
        self,
        interaction: discord.Interaction,
        num_questions: int = 5,
        time_period: str = "all"
    ):
        """Start a Kahoot-style quiz based on server history."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
            # Determine time range
            time_range = None
            if time_period != "all":
                time_range = parse_time_range(time_period)
            
            # Get messages for quiz generation
            if time_range:
                start_time, end_time = time_range
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=200
                )
            else:
                # Get recent messages
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=90)
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=200
                )
            
            if not messages or len(messages) < 10:
                embed = discord.Embed(
                    title="🎮 Quiz Generator",
                    description="Not enough messages to generate a quiz. Need at least 10 messages in the selected time period.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Generate quiz
            status_embed = discord.Embed(
                title="🎮 Generating Quiz...",
                description=f"Creating {num_questions} questions from {len(messages)} messages...",
                color=discord.Color.blue()
            )
            status_msg = await interaction.followup.send(embed=status_embed)
            
            questions, error = await quiz_generator.generate_quiz(messages, num_questions)
            
            if error or not questions:
                error_embed = embed_builder.create_error_embed(
                    error or "Failed to generate quiz questions.",
                    interaction.user
                )
                await status_msg.edit(embed=error_embed)
                return
            
            logger.info(f"Quiz generated with {len(questions)} questions (requested {num_questions})")
            
            # Start quiz
            await self._run_quiz(interaction, questions, status_msg)
            
        except Exception as e:
            logger.error(f"Error in quiz command: {e}")
            error_embed = embed_builder.create_error_embed(
                "An error occurred while generating the quiz.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def _run_quiz(self, interaction, questions, status_msg):
        """Run the quiz with questions."""
        try:
            scores = {}
            reactions = ['1\ufe0f\u20e3', '2\ufe0f\u20e3', '3\ufe0f\u20e3', '4\ufe0f\u20e3']
            channel = interaction.channel
            
            # Delete the "Generating..." status message
            try:
                await status_msg.delete()
            except Exception:
                pass
            
            for i, question in enumerate(questions, 1):
                # Create question embed
                embed = discord.Embed(
                    title=f"🎮 Question {i}/{len(questions)}",
                    description=question['question'],
                    color=discord.Color.gold()
                )
                
                options_text = "\n".join([
                    f"**{reactions[j]} {chr(65+j)})** {opt}"
                    for j, opt in enumerate(question['options'])
                ])
                embed.add_field(name="Options:", value=options_text, inline=False)
                embed.add_field(name="⏱️", value="You have 20 seconds to answer!", inline=False)
                embed.set_footer(text="React with 1️⃣ 2️⃣ 3️⃣ or 4️⃣ to answer!")
                
                # Send as a new message in the channel
                question_msg = await channel.send(embed=embed)
                
                # Add reaction options
                for reaction in reactions:
                    try:
                        await question_msg.add_reaction(reaction)
                    except Exception as e:
                        logger.error(f"Failed to add reaction {reaction}: {e}")
                
                # Track first reaction per user for this question
                user_answers = {}  # user_id -> emoji they picked first

                def check(reaction, user):
                    return (
                        not user.bot
                        and reaction.message.id == question_msg.id
                        and str(reaction.emoji) in reactions
                    )

                async def collect_answers():
                    deadline = asyncio.get_event_loop().time() + 20
                    while asyncio.get_event_loop().time() < deadline:
                        try:
                            remaining = deadline - asyncio.get_event_loop().time()
                            reaction, user = await self.bot.wait_for(
                                'reaction_add',
                                timeout=remaining,
                                check=check
                            )
                            if user.id in user_answers:
                                # User already answered — remove the new reaction
                                try:
                                    await question_msg.remove_reaction(reaction.emoji, user)
                                except Exception:
                                    pass
                            else:
                                user_answers[user.id] = (str(reaction.emoji), user.display_name)
                        except asyncio.TimeoutError:
                            break

                await collect_answers()

                # Fetch message to get reactions
                question_msg = await channel.fetch_message(question_msg.id)
                
                # Check answers
                correct_idx = ord(question['correct']) - ord('A')
                correct_emoji = reactions[correct_idx]
                logger.info(f"Question {i}: Correct answer is {question['correct']}) - {correct_emoji}")

                for user_id, (emoji, display_name) in user_answers.items():
                    if user_id not in scores:
                        scores[user_id] = {'name': display_name, 'score': 0}
                    if emoji == correct_emoji:
                        scores[user_id]['score'] += 1
                        logger.info(f"User {display_name} answered correctly!")

                logger.info(f"User answers for question {i}: {user_answers}")
                
                logger.info(f"Scores after question {i}: {scores}")
                
                # Show answer by editing the question message
                answer_embed = discord.Embed(
                    title=f"✅ Answer for Question {i}",
                    description=f"**Correct Answer:** {question['correct']}) {question['options'][correct_idx]}",
                    color=discord.Color.green()
                )
                answer_embed.add_field(
                    name="Explanation:",
                    value=question['explanation'],
                    inline=False
                )
                
                try:
                    await question_msg.clear_reactions()
                except Exception:
                    pass
                await question_msg.edit(embed=answer_embed)
                await asyncio.sleep(5)
            
            # Show final scores
            if scores:
                sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
                
                leaderboard_embed = discord.Embed(
                    title="🏆 Quiz Complete - Leaderboard",
                    description=f"Results for {len(questions)} questions",
                    color=discord.Color.gold()
                )
                
                for rank, (user_id, data) in enumerate(sorted_scores[:10], 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
                    leaderboard_embed.add_field(
                        name=f"{medal} {data['name']}",
                        value=f"**{data['score']}/{len(questions)}** correct ({int(data['score']/len(questions)*100)}%)",
                        inline=False
                    )
                
                leaderboard_embed.set_footer(text=f"Quiz created by {interaction.user.display_name}")
                await channel.send(embed=leaderboard_embed)
            else:
                no_players_embed = discord.Embed(
                    title="🎮 Quiz Complete",
                    description="No one participated in the quiz!",
                    color=discord.Color.orange()
                )
                await channel.send(embed=no_players_embed)
            
        except Exception as e:
            logger.error(f"Error running quiz: {e}", exc_info=True)
    
    async def wrapped_command(self, interaction: discord.Interaction, year: int = None):
        """Generate Spotify Wrapped-style year-end summary."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
            if year is None:
                year = datetime.utcnow().year - 1
            
            # Validate year
            current_year = datetime.utcnow().year
            if year > current_year or year < 2020:
                error_embed = embed_builder.create_error_embed(
                    f"Invalid year. Please choose a year between 2020 and {current_year}.",
                    interaction.user
                )
                await interaction.followup.send(embed=error_embed)
                return
            
            # Generate wrapped
            status_embed = discord.Embed(
                title=f"🎊 Generating {year} Wrapped...",
                description="Analyzing server activity and creating your year-end summary...",
                color=discord.Color.purple()
            )
            status_msg = await interaction.followup.send(embed=status_embed)
            
            wrapped_data, error = await yearly_wrapped.generate_wrapped(supabase_client, guild.id, year)
            
            if error or not wrapped_data:
                error_embed = embed_builder.create_error_embed(
                    error or "Failed to generate wrapped summary.",
                    interaction.user
                )
                await status_msg.edit(embed=error_embed)
                return
            
            # Create wrapped embed
            stats = wrapped_data['stats']
            
            embed = discord.Embed(
                title=f"🎊 {guild.name}'s {year} Wrapped",
                description=wrapped_data['summary'],
                color=discord.Color.gold()
            )
            
            # Total activity
            embed.add_field(
                name="📊 Total Activity",
                value=f"**{stats['total_messages']:,}** messages\n"
                      f"**{stats['unique_users']}** active members\n"
                      f"**{stats['total_characters']:,}** characters typed",
                inline=False
            )
            
            # Top contributors
            if stats['top_users']:
                top_3 = stats['top_users'][:3]
                top_text = "\n".join([
                    f"{'🥇' if i==0 else '🥈' if i==1 else '🥉'} **{user}** - {count:,} messages"
                    for i, (user, count) in enumerate(top_3)
                ])
                embed.add_field(
                    name="🏆 Top Contributors",
                    value=top_text,
                    inline=False
                )
            
            # Peak activity
            embed.add_field(
                name="📈 Peak Activity",
                value=f"**Busiest Month:** {stats['most_active_month']} ({stats['most_active_month_count']:,} messages)\n"
                      f"**Most Active Hour:** {stats['most_active_hour']}:00\n"
                      f"**Avg Message Length:** {stats['avg_message_length']} characters",
                inline=False
            )
            
            # Fun fact
            if stats['longest_message']['length'] > 0:
                embed.add_field(
                    name="🎯 Fun Fact",
                    value=f"Longest message was **{stats['longest_message']['length']}** characters by {stats['longest_message']['author']}!",
                    inline=False
                )
            
            embed.set_footer(text=f"Generated for {interaction.user.display_name} • {year} Wrapped")
            embed.timestamp = datetime.utcnow()
            
            await status_msg.edit(embed=embed)
            logger.info(f"Generated {year} wrapped for {guild.name}")
            
        except Exception as e:
            logger.error(f"Error in wrapped command: {e}")
            error_embed = embed_builder.create_error_embed(
                "An error occurred while generating your wrapped summary.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def timemachine_command(self, interaction: discord.Interaction, date: str):
        """Show what happened on this day in previous years."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
            # Parse the date
            try:
                # Try parsing as MM-DD format
                target_date = datetime.strptime(date, "%m-%d")
                month = target_date.month
                day = target_date.day
            except ValueError:
                try:
                    # Try parsing as full date
                    target_date = datetime.strptime(date, "%Y-%m-%d")
                    month = target_date.month
                    day = target_date.day
                except ValueError:
                    error_embed = embed_builder.create_error_embed(
                        "Invalid date format. Please use MM-DD (e.g., 01-31) or YYYY-MM-DD format.",
                        interaction.user
                    )
                    await interaction.followup.send(embed=error_embed)
                    return
            
            # Query messages from this day in previous years
            current_year = datetime.utcnow().year
            years_to_check = [current_year - i for i in range(1, 6)]  # Check last 5 years
            
            all_events = []
            
            for year in years_to_check:
                try:
                    start_date = datetime(year, month, day, 0, 0, 0)
                    end_date = datetime(year, month, day, 23, 59, 59)
                    
                    messages = await supabase_client.get_messages_by_timerange(
                        server_id=guild.id,
                        start_time=start_date,
                        end_time=end_date,
                        limit=50
                    )
                    
                    if messages:
                        all_events.append({
                            'year': year,
                            'count': len(messages),
                            'messages': messages[:5]  # Keep top 5
                        })
                except:
                    continue
            
            if not all_events:
                embed = discord.Embed(
                    title=f"📅 Time Machine - {date}",
                    description="No historical data found for this date.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create embed with historical events
            embed = discord.Embed(
                title=f"📅 On This Day - {month}/{day}",
                description=f"Looking back at what happened on {month}/{day} in previous years...",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow()
            )
            
            for event in all_events:
                year = event['year']
                count = event['count']
                messages = event['messages']
                
                # Get unique authors
                authors = set(msg.get('author_name') for msg in messages)
                author_list = ', '.join(list(authors)[:3])
                if len(authors) > 3:
                    author_list += f" and {len(authors) - 3} others"
                
                # Sample message
                sample = messages[0].get('content', '')[:100] if messages else ""
                
                field_value = f"**{count} messages**\n"
                field_value += f"Active: {author_list}\n"
                if sample:
                    field_value += f"_{sample}..._"
                
                embed.add_field(
                    name=f"📆 {year} ({current_year - year} year{'s' if current_year - year != 1 else ''} ago)",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Sent time machine for {date} to {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in timemachine command: {e}")
            error_embed = embed_builder.create_error_embed(
                "An error occurred while traveling through time. Please try again.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def stats_command(self, interaction: discord.Interaction, scope: str = "server"):
        """Show server or user statistics."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
            if scope == "server":
                stats = await analytics.get_server_stats(guild.id, days=30)
                
                if not stats:
                    await interaction.followup.send("Failed to retrieve server statistics.")
                    return
                
                # Build stats message
                embed = discord.Embed(
                    title=f"📊 Server Statistics - {guild.name}",
                    description=f"Statistics for the last {stats['days']} days",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="💬 Messages",
                    value=f"**Total:** {stats['total_messages']:,}\n**Last 30 days:** {stats['recent_messages']:,}",
                    inline=True
                )
                
                embed.add_field(
                    name="💾 Storage",
                    value=f"**Used:** ~{stats['storage_mb']} MB\n**Limit:** 500 MB",
                    inline=True
                )
                
                # Feedback stats
                feedback = stats['feedback']
                if feedback['total'] > 0:
                    embed.add_field(
                        name="⭐ Bot Feedback",
                        value=f"**Positive:** {feedback['positive']} 👍\n**Negative:** {feedback['negative']} 👎\n**Rate:** {feedback['positive_rate']:.1f}%",
                        inline=True
                    )
                
                # Top users
                if stats['top_users']:
                    top_users_text = []
                    for i, (user_id, data) in enumerate(stats['top_users'][:5], 1):
                        top_users_text.append(f"{i}. {data['name']}: {data['count']:,} messages")
                    
                    embed.add_field(
                        name="🏆 Most Active Users",
                        value="\n".join(top_users_text),
                        inline=False
                    )
                
                # Add cache statistics
                cache_stats = cache_manager.get_stats_summary()
                if cache_stats['total_requests'] > 0:
                    embed.add_field(
                        name="⚡ Cache Performance",
                        value=f"**Hit Rate:** {cache_stats['hit_rate']:.1f}%\n"
                              f"**Hits:** {cache_stats['hits']} | **Misses:** {cache_stats['misses']}\n"
                              f"**Cached Items:** {cache_stats['embedding_cache_size']} embeddings, {cache_stats['response_cache_size']} responses",
                        inline=False
                    )
                
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                embed.timestamp = datetime.utcnow()
                
                await interaction.followup.send(embed=embed)
            
            elif scope == "me":
                stats = await analytics.get_user_stats(interaction.user.id, guild.id, days=30)
                
                if not stats:
                    await interaction.followup.send("Failed to retrieve your statistics.")
                    return
                
                embed = discord.Embed(
                    title=f"📊 Your Statistics",
                    description=f"Your activity in {guild.name} (last {stats['days']} days)",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="💬 Messages Sent",
                    value=f"{stats['message_count']:,}",
                    inline=True
                )
                
                embed.add_field(
                    name="⭐ Feedback Given",
                    value=f"{stats['feedback_given']}",
                    inline=True
                )
                
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                embed.timestamp = datetime.utcnow()
                
                await interaction.followup.send(embed=embed)
            
            logger.info(f"Sent {scope} stats to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await interaction.followup.send("An error occurred while retrieving statistics.")
    
    async def trends_command(
        self,
        interaction: discord.Interaction,
        timeframe: str = "24h",
        channel: discord.TextChannel = None,
        server_name: str = None
    ):
        await interaction.response.defer(thinking=True)
        
        try:
            # Resolve server context
            from utils.server_selector import resolve_server_context
            guilds, is_multi = await resolve_server_context(
                interaction, 
                self.bot, 
                server_name, 
                allow_multi=False  # Trends doesn't support multi-server
            )
            
            if not guilds:
                await interaction.followup.send(
                    "❌ Could not find the specified server, or you don't share any servers with me.",
                    ephemeral=True
                )
                return
            
            guild = guilds[0]
            
            # Parse timeframe
            time_range = parse_time_range(timeframe)
            start_time, end_time = time_range
            
            logger.info(f"Analyzing trends for {interaction.user}: timeframe={timeframe}, channel={channel}")
            
            # Get messages from timeframe
            if channel:
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    channel_id=channel.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=500
                )
            else:
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=500
                )
            
            if not messages or len(messages) < 10:
                embed = discord.Embed(
                    title="📈 Trending Topics",
                    description="Not enough activity to analyze trends in this timeframe.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            logger.info(f"Analyzing {len(messages)} messages for trends")
            
            # Analyze word frequency (excluding common words)
            from collections import Counter
            import re
            
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'im', 'dont', 'cant', 'wont', 'isnt', 'arent', 'wasnt', 'werent'}
            
            word_counts = Counter()
            user_activity = Counter()
            channel_activity = Counter()
            
            for msg in messages:
                content = msg.get('content', '').lower()
                # Extract words (alphanumeric only, 3+ chars)
                words = re.findall(r'\b[a-z]{3,}\b', content)
                for word in words:
                    if word not in stop_words:
                        word_counts[word] += 1
                
                # Track user activity
                author_name = msg.get('author_name', 'Unknown')
                user_activity[author_name] += 1
                
                # Track channel activity
                channel_name = msg.get('channel_name', 'Unknown')
                channel_activity[channel_name] += 1
            
            # Get top trending words
            top_words = word_counts.most_common(10)
            top_users = user_activity.most_common(5)
            top_channels = channel_activity.most_common(5)
            
            # Create embed
            embed = discord.Embed(
                title="📈 Trending Topics",
                description=f"Analysis of {len(messages)} messages from the last {timeframe}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            if channel:
                embed.description += f" in {channel.mention}"
            
            # Top trending words
            if top_words:
                words_text = []
                for i, (word, count) in enumerate(top_words, 1):
                    bar = '█' * min(int(count / top_words[0][1] * 10), 10)
                    words_text.append(f"`{i}.` **{word}** {bar} ({count})")
                
                embed.add_field(
                    name="🔥 Trending Words",
                    value="\n".join(words_text),
                    inline=False
                )
            
            # Most active users
            if top_users:
                users_text = []
                for i, (user, count) in enumerate(top_users, 1):
                    users_text.append(f"`{i}.` {user}: {count} messages")
                
                embed.add_field(
                    name="👥 Most Active Users",
                    value="\n".join(users_text),
                    inline=True
                )
            
            # Most active channels (if not filtering by channel)
            if not channel and top_channels:
                channels_text = []
                for i, (ch, count) in enumerate(top_channels, 1):
                    channels_text.append(f"`{i}.` #{ch}: {count} messages")
                
                embed.add_field(
                    name="💬 Active Channels",
                    value="\n".join(channels_text),
                    inline=True
                )
            
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Sent trends analysis to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in trends command: {e}")
            await interaction.followup.send("An error occurred while analyzing trends.")

def setup_commands(bot):
    commands = BotCommands(bot)
    
    @bot.tree.command(name="ask", description="Ask a natural language question about server messages")
    @app_commands.describe(
        query="Your question (e.g., 'what did @user talk about yesterday?')",
        in_channel="Optional: Search only in this channel",
        in_thread="Optional: Search only in this thread",
        from_date="Optional: Start date (YYYY-MM-DD)",
        to_date="Optional: End date (YYYY-MM-DD)",
        min_length="Optional: Minimum message length in characters",
        server_name="Optional: Server name (for DM use) or 'all' for multi-server search"
    )
    async def ask(
        interaction: discord.Interaction, 
        query: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None,
        min_length: int = None,
        server_name: str = None
    ):
        await commands.ask_command(interaction, query, in_channel, in_thread, from_date, to_date, min_length, server_name)
    
    async def recap_server_autocomplete(
        interaction: discord.Interaction,
        current: str
    ):
        """Autocomplete for server selection in /recap command."""
        try:
            from utils.server_selector import get_shared_servers
            
            # Get shared servers between user and bot
            shared_servers = get_shared_servers(bot, interaction.user)
            
            # Filter by current input
            if current:
                filtered_servers = [
                    guild for guild in shared_servers 
                    if current.lower() in guild.name.lower()
                ]
            else:
                filtered_servers = shared_servers
            
            # Return up to 25 options (Discord limit)
            choices = []
            for guild in filtered_servers[:25]:
                choices.append(
                    app_commands.Choice(
                        name=guild.name,
                        value=guild.name
                    )
                )
            
            return choices
            
        except Exception as e:
            logger.error(f"Error in recap server autocomplete: {e}")
            return []

    @bot.tree.command(name="lookup", description="Find exact messages based on clues - shows who said what, when, and where")
    @app_commands.describe(
        clues="Keywords or phrases to search for (e.g., 'deployment issues', 'API discussion')",
        author="Optional: Filter by specific user",
        in_channel="Optional: Search only in this channel",
        from_date="Optional: Start date (YYYY-MM-DD)",
        to_date="Optional: End date (YYYY-MM-DD)"
    )
    async def lookup(
        interaction: discord.Interaction,
        clues: str,
        author: discord.User = None,
        in_channel: discord.TextChannel = None,
        from_date: str = None,
        to_date: str = None
    ):
        await commands.lookup_command(interaction, clues, author, in_channel, from_date, to_date)

    @bot.tree.command(name="recap", description="Get a recap of messages from a specific timeframe")
    @app_commands.describe(
        time="Time range (e.g., '1h', '30m', '2d', '1w')",
        user="Optional: Specific user to recap",
        channel="Optional: Specific channel to recap",
        server_name="Optional: Server name (for DM use)"
    )
    @app_commands.autocomplete(server_name=recap_server_autocomplete)
    async def recap(
        interaction: discord.Interaction,
        time: str,
        user: discord.User = None,
        channel: discord.TextChannel = None,
        server_name: str = None
    ):
        await commands.recap_command(interaction, time, user, channel, server_name)

    @bot.tree.command(name="settings", description="Manage bot settings (Admin only)")
    @app_commands.describe(
        action="Action to perform",
        channel="Channel to exclude/include (if applicable)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Exclude channel from indexing", value="exclude_channel"),
        app_commands.Choice(name="Include channel for indexing", value="include_channel"),
        app_commands.Choice(name="View current settings", value="view_settings")
    ])
    @admin_only()
    async def settings(
        interaction: discord.Interaction,
        action: str,
        channel: discord.TextChannel = None
    ):
        await commands.settings_command(interaction, action, channel)

    @bot.tree.command(name="customize", description="Customize the bot's personality and response style (Admin only)")
    @app_commands.describe(
        action="What to do with the bot persona",
        persona="The personality description for the bot (required for 'Set Persona')"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="View Current Persona", value="view"),
        app_commands.Choice(name="Set Persona", value="set"),
        app_commands.Choice(name="Reset to Default", value="reset")
    ])
    @admin_only()
    async def customize(
        interaction: discord.Interaction,
        action: str,
        persona: str = None
    ):
        await commands.customize_command(interaction, action, persona)

    @bot.tree.command(name="clear", description="Clear your conversation context with the bot")
    async def clear(interaction: discord.Interaction):
        await commands.clear_command(interaction)

    @bot.tree.command(name="stats", description="View server or personal statistics")
    @app_commands.describe(scope="What statistics to view")
    @app_commands.choices(scope=[
        app_commands.Choice(name="Server Statistics", value="server"),
        app_commands.Choice(name="My Statistics", value="me")
    ])
    async def stats(interaction: discord.Interaction, scope: str = "server"):
        await commands.stats_command(interaction, scope)

    @bot.tree.command(name="help", description="Show help information about bot commands")
    async def help_cmd(interaction: discord.Interaction):
        await commands.help_command(interaction)

    @bot.tree.command(name="export", description="Export search results to a file")
    @app_commands.describe(
        query="Your search query",
        format="Export format",
        in_channel="Optional: Search only in this channel",
        in_thread="Optional: Search only in this thread",
        from_date="Optional: Start date (YYYY-MM-DD)",
        to_date="Optional: End date (YYYY-MM-DD)"
    )
    @app_commands.choices(format=[
        app_commands.Choice(name="JSON", value="json"),
        app_commands.Choice(name="CSV", value="csv"),
        app_commands.Choice(name="Markdown", value="markdown"),
        app_commands.Choice(name="Text", value="txt")
    ])
    async def export(
        interaction: discord.Interaction,
        query: str,
        format: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None
    ):
        await commands.export_command(interaction, query, format, in_channel, in_thread, from_date, to_date)

    @bot.tree.command(name="timemachine", description="See what happened on this day in previous years")
    @app_commands.describe(date="Date to look back on (MM-DD or YYYY-MM-DD)")
    async def timemachine(interaction: discord.Interaction, date: str):
        await commands.timemachine_command(interaction, date)

    @bot.tree.command(name="quiz", description="Start a Kahoot-style quiz based on server history")
    @app_commands.describe(
        num_questions="Number of questions (3-10)",
        time_period="Time period for quiz content"
    )
    @app_commands.choices(time_period=[
        app_commands.Choice(name="All Time", value="all"),
        app_commands.Choice(name="Last 7 days", value="7d"),
        app_commands.Choice(name="Last 30 days", value="30d"),
        app_commands.Choice(name="Last 90 days", value="90d")
    ])
    async def quiz(
        interaction: discord.Interaction,
        num_questions: int = 5,
        time_period: str = "all"
    ):
        if num_questions < 3 or num_questions > 10:
            await interaction.response.send_message("Number of questions must be between 3 and 10.", ephemeral=True)
            return
        await commands.quiz_command(interaction, num_questions, time_period)

    @bot.tree.command(name="trends", description="Analyze trending topics and activity patterns")
    @app_commands.describe(
        timeframe="Time range (e.g., '1h', '24h', '7d')",
        channel="Optional: Analyze specific channel only",
        server_name="Optional: Server name (for DM use)"
    )
    async def trends(
        interaction: discord.Interaction,
        timeframe: str = "24h",
        channel: discord.TextChannel = None,
        server_name: str = None
    ):
        await commands.trends_command(interaction, timeframe, channel, server_name)

    @bot.tree.command(name="wrapped", description="Generate Spotify Wrapped-style year-end summary")
    @app_commands.describe(year="Year to generate wrapped for (defaults to last year)")
    async def wrapped(interaction: discord.Interaction, year: int = None):
        await commands.wrapped_command(interaction, year)
