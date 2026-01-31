from supabase import create_client, Client
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class FeedbackClient:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_PROJECT_URL, Config.SUPABASE_SECRET_KEY)
        logger.info("Feedback client initialized")
    
    async def store_feedback(self, server_id, user_id, message_id, query, response, feedback_type):
        """Store user feedback for a bot response."""
        try:
            data = {
                'server_id': server_id,
                'user_id': user_id,
                'message_id': message_id,
                'query': query,
                'response': response,
                'feedback_type': feedback_type
            }
            
            result = self.client.table('response_feedback').insert(data).execute()
            logger.info(f"Stored {feedback_type} feedback from user {user_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
            return None
    
    async def get_feedback_stats(self, server_id, days=30):
        """Get feedback statistics for a server."""
        try:
            from datetime import datetime, timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            result = self.client.table('response_feedback')\
                .select('feedback_type')\
                .eq('server_id', server_id)\
                .gte('created_at', cutoff.isoformat())\
                .execute()
            
            if not result.data:
                return {'positive': 0, 'negative': 0, 'total': 0}
            
            positive = sum(1 for f in result.data if f['feedback_type'] == 'positive')
            negative = sum(1 for f in result.data if f['feedback_type'] == 'negative')
            
            return {
                'positive': positive,
                'negative': negative,
                'total': positive + negative,
                'positive_rate': (positive / (positive + negative) * 100) if (positive + negative) > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {'positive': 0, 'negative': 0, 'total': 0}
    
    async def get_user_feedback_history(self, user_id, limit=10):
        """Get recent feedback from a user."""
        try:
            result = self.client.table('response_feedback')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting user feedback history: {e}")
            return []

feedback_client = FeedbackClient()
