import discord
from utils.logger import get_logger
from config import Config
from database.queries import store_message_with_embedding
from ai.embeddings import generate_embedding

logger = get_logger(__name__)

class BotEvents:
    def __init__(self, bot):
        self.bot = bot
        self.excluded_channels = Config.get_excluded_channel_ids()
    
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
    
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        if message.channel.id in self.excluded_channels:
            logger.debug(f"Skipping message from excluded channel {message.channel.id}")
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
