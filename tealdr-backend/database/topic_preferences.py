from database.supabase_client import supabase_client
from utils.logger import get_logger

logger = get_logger(__name__)

class TopicPreferencesClient:
    """Manages user topic preferences for filtered summaries"""
    
    @staticmethod
    def get_user_topics(user_id: int, server_id: int) -> list:
        """Get user's topic preferences for a specific server"""
        try:
            result = supabase_client.client.table('user_topic_preferences').select('topic_keywords').eq('user_id', user_id).eq('server_id', server_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0].get('topic_keywords', [])
            
            return []
        except Exception as e:
            logger.error(f"Error getting user topics: {e}")
            return []
    
    @staticmethod
    def set_user_topics(user_id: int, server_id: int, topics: list) -> bool:
        """Set or update user's topic preferences for a server"""
        try:
            if not topics or len(topics) == 0:
                # If no topics, delete the preference
                result = supabase_client.client.table('user_topic_preferences').delete().eq('user_id', user_id).eq('server_id', server_id).execute()
                logger.info(f"Removed topic preferences for user {user_id} in server {server_id}")
                return True
            
            data = {
                'user_id': user_id,
                'server_id': server_id,
                'topic_keywords': topics
            }
            
            result = supabase_client.client.table('user_topic_preferences').upsert(
                data,
                on_conflict='user_id,server_id'
            ).execute()
            
            logger.info(f"Set {len(topics)} topics for user {user_id} in server {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting user topics: {e}")
            return False
    
    @staticmethod
    def add_topic(user_id: int, server_id: int, topic: str) -> bool:
        """Add a single topic to user's preferences"""
        try:
            current_topics = TopicPreferencesClient.get_user_topics(user_id, server_id)
            
            # Normalize topic (lowercase, strip whitespace)
            topic = topic.lower().strip()
            
            if topic in current_topics:
                logger.info(f"Topic '{topic}' already exists for user {user_id}")
                return True
            
            current_topics.append(topic)
            return TopicPreferencesClient.set_user_topics(user_id, server_id, current_topics)
        except Exception as e:
            logger.error(f"Error adding topic: {e}")
            return False
    
    @staticmethod
    def remove_topic(user_id: int, server_id: int, topic: str) -> bool:
        """Remove a single topic from user's preferences"""
        try:
            current_topics = TopicPreferencesClient.get_user_topics(user_id, server_id)
            
            topic = topic.lower().strip()
            
            if topic not in current_topics:
                logger.info(f"Topic '{topic}' not found for user {user_id}")
                return True
            
            current_topics.remove(topic)
            return TopicPreferencesClient.set_user_topics(user_id, server_id, current_topics)
        except Exception as e:
            logger.error(f"Error removing topic: {e}")
            return False
    
    @staticmethod
    def get_all_user_topics(user_id: int) -> dict:
        """Get all topic preferences for a user across all servers"""
        try:
            result = supabase_client.client.table('user_topic_preferences').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                return {}
            
            # Return as dict: {server_id: [topics]}
            topics_by_server = {}
            for row in result.data:
                topics_by_server[row['server_id']] = row['topic_keywords']
            
            return topics_by_server
        except Exception as e:
            logger.error(f"Error getting all user topics: {e}")
            return {}

class ServerSummarySettingsClient:
    """Manages user's server-specific summary settings"""
    
    @staticmethod
    def get_server_settings(user_id: int, server_id: int) -> dict:
        """Get user's summary settings for a specific server"""
        try:
            result = supabase_client.client.table('user_server_summary_settings').select('*').eq('user_id', user_id).eq('server_id', server_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # Return defaults
            return {
                'user_id': user_id,
                'server_id': server_id,
                'summaries_enabled': True,
                'include_channels': None,
                'exclude_channels': []
            }
        except Exception as e:
            logger.error(f"Error getting server settings: {e}")
            return None
    
    @staticmethod
    def set_server_enabled(user_id: int, server_id: int, enabled: bool) -> bool:
        """Enable or disable summaries for a specific server"""
        try:
            data = {
                'user_id': user_id,
                'server_id': server_id,
                'summaries_enabled': enabled
            }
            
            result = supabase_client.client.table('user_server_summary_settings').upsert(
                data,
                on_conflict='user_id,server_id'
            ).execute()
            
            logger.info(f"Set summaries to {enabled} for user {user_id} in server {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting server enabled: {e}")
            return False
    
    @staticmethod
    def set_channel_filters(user_id: int, server_id: int, include_channels: list = None, exclude_channels: list = None) -> bool:
        """Set channel filters for summaries"""
        try:
            data = {
                'user_id': user_id,
                'server_id': server_id
            }
            
            if include_channels is not None:
                data['include_channels'] = include_channels
            
            if exclude_channels is not None:
                data['exclude_channels'] = exclude_channels
            
            result = supabase_client.client.table('user_server_summary_settings').upsert(
                data,
                on_conflict='user_id,server_id'
            ).execute()
            
            logger.info(f"Updated channel filters for user {user_id} in server {server_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting channel filters: {e}")
            return False
    
    @staticmethod
    def get_enabled_servers(user_id: int) -> list:
        """Get all servers where user has summaries enabled"""
        try:
            result = supabase_client.client.table('user_server_summary_settings').select('server_id').eq('user_id', user_id).eq('summaries_enabled', True).execute()
            
            if not result.data:
                return []
            
            return [row['server_id'] for row in result.data]
        except Exception as e:
            logger.error(f"Error getting enabled servers: {e}")
            return []

topic_preferences_client = TopicPreferencesClient()
server_summary_settings_client = ServerSummarySettingsClient()
