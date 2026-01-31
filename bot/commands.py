import discord
from discord import app_commands
from utils.logger import get_logger
from utils.helpers import parse_time_range, extract_user_mention, truncate_text, extract_time_keywords
from utils.conversation_context import conversation_context
from utils.analytics import analytics
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
    
    async def ask_command(self, interaction: discord.Interaction, query: str):
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
            
            logger.info(f"Processing query from {interaction.user}: {query}")
            if mentioned_user:
                logger.info(f"Filtering by user: {mentioned_user}")
            if time_range:
                logger.info(f"Filtering by time range: {time_range}")
            
            query_embedding = await generate_query_embedding(query)
            if not query_embedding:
                await interaction.followup.send("Failed to process your query. Please try again.")
                return
            
            filters = {
                'author_id': mentioned_user.id if mentioned_user else None,
                'time_range': time_range,
                'limit': 20
            }
            
            messages = await search_with_context(
                query_embedding=query_embedding,
                server_id=guild.id,
                filters=filters
            )
            
            if not messages or len(messages) == 0:
                await interaction.followup.send("No messages found matching your query. Try a different time range or user.")
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
            
            response = truncate_text(response, 2000)
            
            # Save to conversation context
            conversation_context.add_query(
                user_id=interaction.user.id,
                query=query,
                response=response,
                mentioned_user=mentioned_user.id if mentioned_user else None
            )
            
            # Add context indicator if this is a follow-up
            if has_context:
                response = f"💬 *Following up from our conversation...*\n\n{response}"
            
            # Send response and add feedback reactions
            sent_message = await interaction.followup.send(response)
            
            # Track this response for feedback
            self.bot.events.track_response(sent_message.id, query, response)
            
            # Add reaction options for feedback
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')
            
            logger.info(f"Sent response to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            await interaction.followup.send("Something went wrong on my end. Please try again in a moment.")
    
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
                await interaction.followup.send("Not much activity in this timeframe.")
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
            
            response = truncate_text(response, 2000)
            
            location = ""
            if user:
                location = f" for {user.mention}"
            elif channel:
                location = f" in {channel.mention}"
            else:
                location = f" in this channel"
            
            # Send response and add feedback reactions
            sent_message = await interaction.followup.send(f"**Recap{location} ({time}):**\n\n{response}")
            
            # Track this response for feedback
            self.bot.events.track_response(sent_message.id, f"recap {time}", response)
            
            # Add reaction options for feedback
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')
            
            logger.info(f"Sent recap to {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in recap command: {e}")
            await interaction.followup.send("Something went wrong on my end. Please try again in a moment.")
    
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
    @app_commands.describe(query="Your question (e.g., 'what did @user talk about yesterday?')")
    async def ask(interaction: discord.Interaction, query: str):
        await commands.ask_command(interaction, query)
    
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
