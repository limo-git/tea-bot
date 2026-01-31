from supabase import create_client, Client
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class ServerSettingsClient:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_PROJECT_URL, Config.SUPABASE_SECRET_KEY)
        logger.info("Server settings client initialized")
    
    async def get_server_settings(self, server_id):
        try:
            result = self.client.table('server_settings').select('*').eq('server_id', server_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting server settings: {e}")
            return None
    
    async def update_server_settings(self, server_id, settings):
        try:
            existing = await self.get_server_settings(server_id)
            
            if existing:
                result = self.client.table('server_settings').update(settings).eq('server_id', server_id).execute()
            else:
                settings['server_id'] = server_id
                result = self.client.table('server_settings').insert(settings).execute()
            
            logger.info(f"Updated settings for server {server_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating server settings: {e}")
            return None
    
    async def get_excluded_channels(self, server_id):
        try:
            settings = await self.get_server_settings(server_id)
            if settings and 'excluded_channels' in settings:
                return settings['excluded_channels']
            return []
        except Exception as e:
            logger.error(f"Error getting excluded channels: {e}")
            return []
    
    async def add_excluded_channel(self, server_id, channel_id):
        try:
            excluded = await self.get_excluded_channels(server_id)
            if channel_id not in excluded:
                excluded.append(channel_id)
                await self.update_server_settings(server_id, {'excluded_channels': excluded})
            return excluded
        except Exception as e:
            logger.error(f"Error adding excluded channel: {e}")
            return []
    
    async def remove_excluded_channel(self, server_id, channel_id):
        try:
            excluded = await self.get_excluded_channels(server_id)
            if channel_id in excluded:
                excluded.remove(channel_id)
                await self.update_server_settings(server_id, {'excluded_channels': excluded})
            return excluded
        except Exception as e:
            logger.error(f"Error removing excluded channel: {e}")
            return []
    
    async def get_bot_persona(self, server_id):
        try:
            settings = await self.get_server_settings(server_id)
            if settings and 'bot_persona' in settings:
                return settings['bot_persona']
            return 'You are a helpful Discord assistant. Be friendly, concise, and informative.'
        except Exception as e:
            logger.error(f"Error getting bot persona: {e}")
            return 'You are a helpful Discord assistant. Be friendly, concise, and informative.'
    
    async def set_bot_persona(self, server_id, persona):
        try:
            await self.update_server_settings(server_id, {'bot_persona': persona})
            logger.info(f"Updated bot persona for server {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting bot persona: {e}")
            return False

server_settings_client = ServerSettingsClient()
