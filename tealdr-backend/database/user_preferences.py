from database.supabase_client import supabase_client
from utils.logger import get_logger

logger = get_logger(__name__)

class UserPreferencesClient:
    """Manages user preferences for DM summaries and email delivery"""
    
    @staticmethod
    def get_user_preferences(user_id: int) -> dict:
        """Get user preferences"""
        try:
            result = supabase_client.client.table('user_preferences').select('*').eq('user_id', user_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # Return defaults if no preferences exist
            return {
                'user_id': user_id,
                'email': None,
                'dm_summaries_enabled': True,
                'email_summaries_enabled': False,
                'summary_frequency': 'weekly',
                'bug_alerts_enabled': True
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    @staticmethod
    def set_user_preferences(user_id: int, preferences: dict) -> bool:
        """Set or update user preferences"""
        try:
            preferences['user_id'] = user_id
            
            result = supabase_client.client.table('user_preferences').upsert(
                preferences,
                on_conflict='user_id'
            ).execute()
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting user preferences: {e}")
            return False
    
    @staticmethod
    def set_email(user_id: int, email: str) -> bool:
        """Set user email for email summaries"""
        try:
            result = supabase_client.client.table('user_preferences').upsert({
                'user_id': user_id,
                'email': email
            }, on_conflict='user_id').execute()
            
            logger.info(f"Set email for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting email: {e}")
            return False
    
    @staticmethod
    def toggle_dm_summaries(user_id: int, enabled: bool) -> bool:
        """Enable or disable DM summaries"""
        try:
            result = supabase_client.client.table('user_preferences').upsert({
                'user_id': user_id,
                'dm_summaries_enabled': enabled
            }, on_conflict='user_id').execute()
            
            logger.info(f"Set DM summaries to {enabled} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error toggling DM summaries: {e}")
            return False
    
    @staticmethod
    def toggle_email_summaries(user_id: int, enabled: bool) -> bool:
        """Enable or disable email summaries"""
        try:
            result = supabase_client.client.table('user_preferences').upsert({
                'user_id': user_id,
                'email_summaries_enabled': enabled
            }, on_conflict='user_id').execute()
            
            logger.info(f"Set email summaries to {enabled} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error toggling email summaries: {e}")
            return False
    
    @staticmethod
    def set_summary_frequency(user_id: int, frequency: str) -> bool:
        """Set summary frequency (daily, weekly, monthly)"""
        if frequency not in ['daily', 'weekly', 'monthly']:
            logger.error(f"Invalid frequency: {frequency}")
            return False
        
        try:
            result = supabase_client.client.table('user_preferences').upsert({
                'user_id': user_id,
                'summary_frequency': frequency
            }, on_conflict='user_id').execute()
            
            logger.info(f"Set summary frequency to {frequency} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting summary frequency: {e}")
            return False
    
    @staticmethod
    def get_users_for_dm_summaries() -> list:
        """Get all users who have DM summaries enabled"""
        try:
            result = supabase_client.client.table('user_preferences').select('*').eq('dm_summaries_enabled', True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting users for DM summaries: {e}")
            return []
    
    @staticmethod
    def get_users_for_email_summaries() -> list:
        """Get all users who have email summaries enabled"""
        try:
            result = supabase_client.client.table('user_preferences').select('*').eq('email_summaries_enabled', True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting users for email summaries: {e}")
            return []

user_preferences_client = UserPreferencesClient()
