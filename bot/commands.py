import discord
from discord import app_commands
from utils.logger import get_logger
from utils.helpers import parse_time_range, extract_user_mention, truncate_text, extract_time_keywords
from utils.conversation_context import conversation_context
from utils.analytics import analytics
from utils.embed_builder import embed_builder
from utils.pagination import PaginationView
from utils.suggestions import smart_suggestions
from utils.export_handler import export_handler
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
        self.excluded_channels = Config.get_excluded_channel_ids()
    
    async def ask_command(
        self, 
        interaction: discord.Interaction, 
        query: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None,
        min_length: int = None
    ):
        if not rate_limiter.check_rate_limit(interaction.user.id):
            await interaction.response.send_message(
                "You're sending too many requests. Please wait a moment and try again.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
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
                'min_length': min_length,
                'limit': 20
            }
            
            messages = await search_with_context(
                query_embedding=query_embedding,
                server_id=guild.id,
                filters=filters
            )
            
            if not messages or len(messages) == 0:
                # Send no results embed
                no_results_embed = embed_builder.create_no_results_embed(query, interaction.user)
                await interaction.followup.send(embed=no_results_embed)
                return
            
            logger.info(f"Found {len(messages)} relevant messages")
            
            persona = await server_settings_client.get_bot_persona(guild.id)
            user_name = mentioned_user.name if mentioned_user else "users"
            requester_name = interaction.user.display_name
            
            # Build prompt with conversation context
            base_prompt = get_prompt_for_query(
                query=query,
                messages=messages,
                user_name=user_name,
                requester_name=requester_name,
                persona=persona
            )
            
            # Add conversation context if available
            if context_str:
                prompt = f"{context_str}\n\n{base_prompt}\n\nNote: Consider the previous conversation when answering."
            else:
                prompt = base_prompt
            
            response = await gemini_client.generate_response(prompt)
            
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
            
            # Add message count and filters to first embed
            if embeds:
                sources_text = f"{len(messages)} messages analyzed"
                embeds[0].add_field(
                    name="📊 Sources",
                    value=sources_text,
                    inline=True
                )
                
                # Add active filters info
                active_filters = []
                if in_channel:
                    active_filters.append(f"Channel: {in_channel.mention}")
                if in_thread:
                    active_filters.append(f"Thread: {in_thread.mention}")
                if from_date or to_date:
                    date_range = f"{from_date or '...'} to {to_date or '...'}"
                    active_filters.append(f"Dates: {date_range}")
                if min_length:
                    active_filters.append(f"Min length: {min_length} chars")
                
                if active_filters:
                    embeds[0].add_field(
                        name="🔍 Filters",
                        value="\n".join(active_filters),
                        inline=True
                    )
                
                # Generate and add smart suggestions
                try:
                    suggestions = await smart_suggestions.generate_suggestions(
                        query=query,
                        messages=messages,
                        mentioned_user=mentioned_user
                    )
                    
                    if suggestions:
                        suggestions_text = "\n".join([f"• {s}" for s in suggestions[:5]])
                        embeds[-1].add_field(  # Add to last embed
                            name="💡 You might also ask:",
                            value=suggestions_text,
                            inline=False
                        )
                except Exception as e:
                    logger.error(f"Failed to generate suggestions: {e}")
            
            # Send with pagination if multiple embeds
            if len(embeds) > 1:
                view = PaginationView(embeds, interaction.user)
                sent_message = await interaction.followup.send(embed=embeds[0], view=view)
                view.message = sent_message
            else:
                sent_message = await interaction.followup.send(embed=embeds[0])
            
            # Track this response for feedback
            self.bot.events.track_response(sent_message.id, query, response)
            
            # Add reaction options for feedback
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')
            
            logger.info(f"Sent response to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            error_embed = embed_builder.create_error_embed(
                "Something went wrong while processing your query. Please try again in a moment.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
    
    async def recap_command(
        self,
        interaction: discord.Interaction,
        time: str,
        user: discord.User = None,
        channel: discord.TextChannel = None
    ):
        if not rate_limiter.check_rate_limit(interaction.user.id):
            await interaction.response.send_message(
                "You're sending too many requests. Please wait a moment and try again.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command can only be used in a server.")
                return
            
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
                messages = await supabase_client.get_messages_by_timerange(
                    server_id=guild.id,
                    channel_id=interaction.channel.id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=100
                )
            
            if not messages or len(messages) < 5:
                embed = discord.Embed(
                    title="📅 Recap",
                    description="Not much activity in this timeframe.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            logger.info(f"Found {len(messages)} messages for recap")
            
            persona = await server_settings_client.get_bot_persona(guild.id)
            requester_name = interaction.user.display_name
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
            else:
                location = f" in this channel"
            
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

def setup_commands(bot):
    commands = BotCommands(bot)
    
    @bot.tree.command(name="ask", description="Ask a natural language question about server messages")
    @app_commands.describe(
        query="Your question (e.g., 'what did @user talk about yesterday?')",
        in_channel="Optional: Search only in this channel",
        in_thread="Optional: Search only in this thread",
        from_date="Optional: Start date (YYYY-MM-DD)",
        to_date="Optional: End date (YYYY-MM-DD)",
        min_length="Optional: Minimum message length in characters"
    )
    async def ask(
        interaction: discord.Interaction, 
        query: str,
        in_channel: discord.TextChannel = None,
        in_thread: discord.Thread = None,
        from_date: str = None,
        to_date: str = None,
        min_length: int = None
    ):
        await commands.ask_command(interaction, query, in_channel, in_thread, from_date, to_date, min_length)
    
    @bot.tree.command(name="recap", description="Get a recap of messages from a specific timeframe")
    @app_commands.describe(
        time="Time range for the recap",
        user="Optional: Specific user to recap",
        channel="Optional: Specific channel to recap"
    )
    @app_commands.choices(time=[
        app_commands.Choice(name="Last 24 hours", value="24h"),
        app_commands.Choice(name="Last 7 days", value="7d"),
        app_commands.Choice(name="Last 30 days", value="30d")
    ])
    async def recap(
        interaction: discord.Interaction,
        time: str,
        user: discord.User = None,
        channel: discord.TextChannel = None
    ):
        await commands.recap_command(interaction, time, user, channel)
    
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
