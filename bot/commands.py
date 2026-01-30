import discord
from discord import app_commands
from utils.logger import get_logger
from utils.helpers import parse_time_range, extract_user_mention, truncate_text, extract_time_keywords
from ai.embeddings import generate_query_embedding
from ai.gemini_client import gemini_client
from ai.prompts import get_prompt_for_query, format_messages_for_ai, RECAP_PROMPT
from database.queries import search_with_context
from database.supabase_client import supabase_client
from bot.permissions import admin_only
from config import Config
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
            
            mentioned_user = extract_user_mention(query, guild)
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
            
            user_name = mentioned_user.name if mentioned_user else "users"
            prompt = get_prompt_for_query(query, messages, user_name)
            
            response = await gemini_client.generate_response(prompt)
            
            response = truncate_text(response, 2000)
            
            await interaction.followup.send(response)
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
            
            formatted_messages = format_messages_for_ai(messages)
            prompt = RECAP_PROMPT.format(messages=formatted_messages)
            
            response = await gemini_client.generate_response(prompt)
            
            response = truncate_text(response, 2000)
            
            location = ""
            if user:
                location = f" for {user.mention}"
            elif channel:
                location = f" in {channel.mention}"
            else:
                location = f" in {interaction.channel.mention}"
            
            await interaction.followup.send(f"**Recap{location} ({time}):**\n\n{response}")
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
            if action == "view_settings":
                excluded = Config.get_excluded_channel_ids()
                if not excluded:
                    await interaction.followup.send("No channels are currently excluded.", ephemeral=True)
                else:
                    channel_mentions = []
                    for ch_id in excluded:
                        ch = interaction.guild.get_channel(ch_id)
                        if ch:
                            channel_mentions.append(ch.mention)
                        else:
                            channel_mentions.append(f"Unknown Channel ({ch_id})")
                    
                    await interaction.followup.send(
                        f"**Excluded Channels:**\n" + "\n".join(channel_mentions),
                        ephemeral=True
                    )
            
            elif action == "exclude_channel":
                if not channel:
                    await interaction.followup.send("Please specify a channel to exclude.", ephemeral=True)
                    return
                
                excluded = Config.get_excluded_channel_ids()
                if channel.id in excluded:
                    await interaction.followup.send(f"{channel.mention} is already excluded.", ephemeral=True)
                else:
                    excluded.append(channel.id)
                    Config.EXCLUDED_CHANNELS = [str(ch_id) for ch_id in excluded]
                    
                    await interaction.followup.send(
                        f"✅ {channel.mention} has been excluded from indexing.",
                        ephemeral=True
                    )
                    logger.info(f"Channel {channel.id} excluded by {interaction.user}")
            
            elif action == "include_channel":
                if not channel:
                    await interaction.followup.send("Please specify a channel to include.", ephemeral=True)
                    return
                
                excluded = Config.get_excluded_channel_ids()
                if channel.id not in excluded:
                    await interaction.followup.send(f"{channel.mention} is not excluded.", ephemeral=True)
                else:
                    excluded.remove(channel.id)
                    Config.EXCLUDED_CHANNELS = [str(ch_id) for ch_id in excluded]
                    
                    await interaction.followup.send(
                        f"✅ {channel.mention} has been included for indexing.",
                        ephemeral=True
                    )
                    logger.info(f"Channel {channel.id} included by {interaction.user}")
        
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await interaction.followup.send("An error occurred while updating settings.", ephemeral=True)

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
