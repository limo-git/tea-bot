import discord
from discord.ext import tasks
from utils.logger import get_logger
from config import Config
from database.queries import store_message_with_embedding
from ai.embeddings import generate_embedding
from utils.cleanup import cleanup_old_messages, get_storage_stats
from database.server_settings import server_settings_client
from database.feedback_client import feedback_client
from utils.bug_tracker import bug_tracker

logger = get_logger(__name__)

class BotEvents:
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task_started = False
        self.bot_responses = {}  # Track bot responses for feedback
    
    async def on_ready(self):
        logger.info(f'Bot logged in as {self.bot.user.name} (ID: {self.bot.user.id})')
        logger.info(f'Connected to {len(self.bot.guilds)} servers')
        
        try:
            synced = await self.bot.tree.sync()
            logger.info(f'Synced {len(synced)} command(s)')
        except Exception as e:
            logger.error(f'Failed to sync commands: {e}')
        
        from database.supabase_client import supabase_client
        try:
            count = await supabase_client.get_message_count()
            logger.info(f'Total messages in database: {count}')
        except Exception as e:
            logger.warning(f'Could not get message count: {e}')
        
        if not self.cleanup_task_started:
            self.start_cleanup_task()
            self.cleanup_task_started = True
    
    def start_cleanup_task(self):
        @tasks.loop(hours=Config.CLEANUP_INTERVAL_HOURS)
        async def cleanup_task():
            logger.info("Running scheduled cleanup task")
            from database.supabase_client import supabase_client
            deleted = await cleanup_old_messages(supabase_client)
            stats = await get_storage_stats(supabase_client)
            if stats:
                logger.info(f"Current storage: {stats['total_messages']} total messages, {stats['recent_messages']} from last 30 days")
        
        @cleanup_task.before_loop
        async def before_cleanup():
            await self.bot.wait_until_ready()
            logger.info(f"Cleanup task initialized - will run every {Config.CLEANUP_INTERVAL_HOURS} hours")
        
        cleanup_task.start()
        logger.info("Cleanup task started")
    
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        excluded_channels = await server_settings_client.get_excluded_channels(message.guild.id)
        if message.channel.id in excluded_channels:
            logger.debug(f"Skipping message from excluded channel {message.channel.id} in server {message.guild.id}")
            return
        
        if not message.content or message.content.strip() == "":
            logger.debug(f"Skipping empty message {message.id}")
            return
        
        try:
            # Check if message is in a thread
            is_thread = isinstance(message.channel, discord.Thread)
            thread_id = message.channel.id if is_thread else None
            parent_channel_id = message.channel.parent_id if is_thread else message.channel.id
            channel_name = message.channel.parent.name if is_thread else message.channel.name
            
            message_data = {
                'message_id': message.id,
                'server_id': message.guild.id,
                'channel_id': parent_channel_id,
                'channel_name': channel_name,
                'thread_id': thread_id,
                'is_thread_message': is_thread,
                'author_id': message.author.id,
                'author_name': str(message.author),
                'content': message.content,
                'created_at': message.created_at
            }
            
            from database.supabase_client import supabase_client
            exists = await supabase_client.message_exists(message.id)
            if exists:
                logger.debug(f"Message {message.id} already indexed")
                return
            
            embedding = await generate_embedding(message.content)
            
            if embedding:
                await store_message_with_embedding(message_data, embedding)
                logger.info(f"Indexed message {message.id} from {message.author}")
                
                # Check if message is about a bug/dependency issue
                if bug_tracker.is_bug_discussion(message.content):
                    bug_tracker.track_bug_discussion(
                        server_id=message.guild.id,
                        channel_id=parent_channel_id,
                        message_id=message.id,
                        message_content=message.content
                    )
                    logger.info(f"Tracked bug discussion in message {message.id}")

                # Graph RAG: queue message for entity extraction (non-blocking)
                if Config.GRAPH_RAG_ENABLED:
                    import asyncio
                    asyncio.create_task(self._extract_graph_entities(message_data))
            else:
                logger.warning(f"Failed to generate embedding for message {message.id}")
        
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
    
    async def _extract_graph_entities(self, message_data: dict):
        """Non-blocking: extract entities from a single message and update the graph."""
        try:
            from extraction.entity_extractor import extract_entities_from_chunk, format_messages_for_extraction
            from graph.builder import build_graph_from_extraction
            chunk_text = format_messages_for_extraction([message_data])
            chunk_metadata = {
                "channel_id": message_data.get("channel_id"),
                "channel_name": message_data.get("channel_name", "unknown"),
                "guild_id": message_data.get("server_id"),
                "start_time": str(message_data.get("created_at", "")),
                "end_time": str(message_data.get("created_at", "")),
            }
            extraction = await extract_entities_from_chunk(chunk_text, chunk_metadata)
            await build_graph_from_extraction(extraction, [message_data])
        except Exception as e:
            logger.error(f"Graph entity extraction failed for message {message_data.get('message_id')}: {e}", exc_info=True)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reactions to bot messages for feedback and sources reveal."""
        if user.bot:
            return
        
        # Check if this is a reaction to a bot message
        if reaction.message.author.id != self.bot.user.id:
            return
        
        # Get the response data if we tracked it
        response_data = self.bot_responses.get(reaction.message.id)
        
        if not response_data:
            logger.debug(f"No tracked response data for message {reaction.message.id}")
            return
        
        try:
            # Handle sources reveal (📊 reaction)
            if str(reaction.emoji) == '📊':
                sources = response_data.get('sources')
                if sources:
                    # Send sources as ephemeral message to the user
                    await reaction.message.channel.send(
                        f"**📊 Sources for {user.mention}:**\n{sources}",
                        delete_after=60  # Auto-delete after 60 seconds
                    )
                    logger.info(f"Revealed sources to {user} for message {reaction.message.id}")
                return
            
            # Handle feedback reactions (👍 👎)
            if str(reaction.emoji) not in ['👍', '👎']:
                return
            
            feedback_type = 'positive' if str(reaction.emoji) == '👍' else 'negative'
            
            await feedback_client.store_feedback(
                server_id=reaction.message.guild.id,
                user_id=user.id,
                message_id=reaction.message.id,
                query=response_data['query'],
                response=response_data['response'],
                feedback_type=feedback_type
            )
            
            logger.info(f"Recorded {feedback_type} feedback from {user} on message {reaction.message.id}")
            
            # Send a thank you message
            if feedback_type == 'positive':
                await reaction.message.channel.send(
                    f"Thanks for the feedback, {user.mention}! Glad I could help! 😊",
                    delete_after=5
                )
            else:
                await reaction.message.channel.send(
                    f"Thanks for the feedback, {user.mention}. I'll try to do better! 🙏",
                    delete_after=5
                )
        
        except Exception as e:
            logger.error(f"Error handling reaction: {e}")
    
    def track_response(self, message_id, query, response, sources=None):
        """Track a bot response for feedback collection and sources reveal."""
        self.bot_responses[message_id] = {
            'query': query,
            'response': response,
            'sources': sources
        }
        
        # Clean up old tracked responses (keep last 100)
        if len(self.bot_responses) > 100:
            oldest_keys = list(self.bot_responses.keys())[:50]
            for key in oldest_keys:
                del self.bot_responses[key]
    
    async def on_guild_join(self, guild: discord.Guild):
        """Auto-index the past 5 days of messages when the bot joins a new server."""
        logger.info(f"Joined new server: {guild.name} (ID: {guild.id}) — starting backfill of past 5 days")
        
        # Run backfill in background so it doesn't block the bot
        import asyncio
        asyncio.create_task(self._backfill_server(guild))
    
    async def _backfill_server(self, guild: discord.Guild):
        """Backfill past 5 days of messages for a server."""
        from datetime import datetime, timedelta, timezone
        from database.supabase_client import supabase_client
        
        after_date = datetime.now(timezone.utc) - timedelta(days=5)
        total_indexed = 0
        total_skipped = 0
        total_errors = 0
        
        excluded_channels = await server_settings_client.get_excluded_channels(guild.id)
        
        for channel in guild.text_channels:
            if channel.id in excluded_channels:
                logger.debug(f"Skipping excluded channel {channel.name} in {guild.name}")
                continue
            
            try:
                permissions = channel.permissions_for(guild.me)
                if not permissions.read_messages or not permissions.read_message_history:
                    logger.debug(f"No read permissions for channel {channel.name} in {guild.name}")
                    continue
                
                async for message in channel.history(after=after_date, limit=None, oldest_first=True):
                    if message.author.bot:
                        continue
                    
                    if not message.content or message.content.strip() == "":
                        continue
                    
                    try:
                        exists = await supabase_client.message_exists(message.id)
                        if exists:
                            total_skipped += 1
                            continue
                        
                        is_thread = isinstance(message.channel, discord.Thread)
                        thread_id = message.channel.id if is_thread else None
                        parent_channel_id = message.channel.parent_id if is_thread else message.channel.id
                        
                        message_data = {
                            'message_id': message.id,
                            'server_id': guild.id,
                            'channel_id': parent_channel_id,
                            'thread_id': thread_id,
                            'is_thread_message': is_thread,
                            'author_id': message.author.id,
                            'author_name': str(message.author),
                            'content': message.content,
                            'created_at': message.created_at
                        }
                        
                        embedding = await generate_embedding(message.content)
                        if embedding:
                            await store_message_with_embedding(message_data, embedding)
                            total_indexed += 1
                        else:
                            total_errors += 1
                        
                        # Rate limit: small delay to avoid API throttling
                        if total_indexed % 50 == 0 and total_indexed > 0:
                            logger.info(f"Backfill progress for {guild.name}: {total_indexed} messages indexed so far...")
                            import asyncio
                            await asyncio.sleep(1)
                    
                    except Exception as e:
                        logger.error(f"Error indexing message {message.id} during backfill: {e}")
                        total_errors += 1
            
            except discord.Forbidden:
                logger.debug(f"Forbidden access to channel {channel.name} in {guild.name}")
            except Exception as e:
                logger.error(f"Error backfilling channel {channel.name} in {guild.name}: {e}")
        
        logger.info(
            f"Backfill complete for {guild.name}: "
            f"{total_indexed} indexed, {total_skipped} already existed, {total_errors} errors"
        )

def setup_events(bot):
    events = BotEvents(bot)
    
    @bot.event
    async def on_ready():
        await events.on_ready()
    
    @bot.event
    async def on_message(message):
        await events.on_message(message)
    
    @bot.event
    async def on_reaction_add(reaction, user):
        await events.on_reaction_add(reaction, user)
    
    @bot.event
    async def on_guild_join(guild):
        await events.on_guild_join(guild)
    
    # Make events accessible for tracking responses
    bot.events = events
