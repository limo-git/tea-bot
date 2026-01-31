import discord
from discord.ext import tasks
from utils.logger import get_logger
from config import Config
from database.queries import store_message_with_embedding
from ai.embeddings import generate_embedding
from utils.cleanup import cleanup_old_messages, get_storage_stats
from database.server_settings import server_settings_client
from database.feedback_client import feedback_client

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
            
            message_data = {
                'message_id': message.id,
                'server_id': message.guild.id,
                'channel_id': parent_channel_id,
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
            else:
                logger.warning(f"Failed to generate embedding for message {message.id}")
        
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reactions to bot messages for feedback."""
        if user.bot:
            return
        
        # Check if this is a reaction to a bot message
        if reaction.message.author.id != self.bot.user.id:
            return
        
        # Check if this is a feedback reaction
        if str(reaction.emoji) not in ['👍', '👎']:
            return
        
        try:
            # Get the response data if we tracked it
            response_data = self.bot_responses.get(reaction.message.id)
            
            if not response_data:
                logger.debug(f"No tracked response data for message {reaction.message.id}")
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
            logger.error(f"Error handling reaction feedback: {e}")
    
    def track_response(self, message_id, query, response):
        """Track a bot response for feedback collection."""
        self.bot_responses[message_id] = {
            'query': query,
            'response': response
        }
        
        # Clean up old tracked responses (keep last 100)
        if len(self.bot_responses) > 100:
            oldest_keys = list(self.bot_responses.keys())[:50]
            for key in oldest_keys:
                del self.bot_responses[key]

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
    
    # Make events accessible for tracking responses
    bot.events = events
