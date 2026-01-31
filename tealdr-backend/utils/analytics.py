from database.supabase_client import supabase_client
from database.feedback_client import feedback_client
from utils.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

class Analytics:
    @staticmethod
    async def get_server_stats(server_id, days=30):
        """Get comprehensive server statistics."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Total messages
            total_result = supabase_client.client.table('messages')\
                .select('id', count='exact')\
                .eq('server_id', server_id)\
                .execute()
            total_messages = total_result.count if hasattr(total_result, 'count') else 0
            
            # Recent messages
            recent_result = supabase_client.client.table('messages')\
                .select('id', count='exact')\
                .eq('server_id', server_id)\
                .gte('created_at', cutoff.isoformat())\
                .execute()
            recent_messages = recent_result.count if hasattr(recent_result, 'count') else 0
            
            # Most active users
            user_result = supabase_client.client.table('messages')\
                .select('author_id, author_name')\
                .eq('server_id', server_id)\
                .gte('created_at', cutoff.isoformat())\
                .execute()
            
            user_counts = {}
            for msg in user_result.data:
                author_id = msg['author_id']
                author_name = msg['author_name']
                if author_id not in user_counts:
                    user_counts[author_id] = {'name': author_name, 'count': 0}
                user_counts[author_id]['count'] += 1
            
            top_users = sorted(user_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
            
            # Feedback stats
            feedback_stats = await feedback_client.get_feedback_stats(server_id, days)
            
            # Storage estimate (rough)
            avg_message_size = 1000  # bytes
            storage_mb = (total_messages * avg_message_size) / (1024 * 1024)
            
            return {
                'total_messages': total_messages,
                'recent_messages': recent_messages,
                'top_users': top_users,
                'feedback': feedback_stats,
                'storage_mb': round(storage_mb, 2),
                'days': days
            }
        
        except Exception as e:
            logger.error(f"Error getting server stats: {e}")
            return None
    
    @staticmethod
    async def get_user_stats(user_id, server_id, days=30):
        """Get statistics for a specific user."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # User's message count
            result = supabase_client.client.table('messages')\
                .select('id', count='exact')\
                .eq('server_id', server_id)\
                .eq('author_id', user_id)\
                .gte('created_at', cutoff.isoformat())\
                .execute()
            
            message_count = result.count if hasattr(result, 'count') else 0
            
            # User's feedback given
            feedback_result = feedback_client.client.table('response_feedback')\
                .select('feedback_type', count='exact')\
                .eq('server_id', server_id)\
                .eq('user_id', user_id)\
                .gte('created_at', cutoff.isoformat())\
                .execute()
            
            feedback_count = feedback_result.count if hasattr(feedback_result, 'count') else 0
            
            return {
                'message_count': message_count,
                'feedback_given': feedback_count,
                'days': days
            }
        
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None

analytics = Analytics()
