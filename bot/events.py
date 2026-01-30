import discord
from discord.ext import tasks
from utils.logger import get_logger
from config import Config
from database.queries import store_message_with_embedding
from ai.embeddings import generate_embedding
from utils.cleanup import cleanup_old_messages, get_storage_stats
from database.server_settings import server_settings_client

logger = get_logger(__name__)

class BotEvents:
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task_started = False
    
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
            message_data = {
                'message_id': message.id,
                'server_id': message.guild.id,
                'channel_id': message.channel.id,
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

def setup_events(bot):
    events = BotEvents(bot)
    
    @bot.event
    async def on_ready():
        await events.on_ready()
    
    @bot.event
    async def on_message(message):
        await events.on_message(message)
