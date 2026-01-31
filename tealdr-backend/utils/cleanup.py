from datetime import datetime, timedelta
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

async def cleanup_old_messages(supabase_client):
    try:
        retention_days = Config.MESSAGE_RETENTION_DAYS
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        logger.info(f"Starting cleanup of messages older than {retention_days} days (before {cutoff_date.isoformat()})")
        
        result = supabase_client.client.table('messages').delete().lt('created_at', cutoff_date.isoformat()).execute()
        
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Cleanup complete: Deleted {deleted_count} old messages")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 0

async def get_storage_stats(supabase_client):
    try:
        total_result = supabase_client.client.table('messages').select('id', count='exact').execute()
        total_count = total_result.count
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_result = supabase_client.client.table('messages').select('id', count='exact').gte('created_at', thirty_days_ago.isoformat()).execute()
        recent_count = recent_result.count
        
        logger.info(f"Storage stats - Total messages: {total_count}, Last 30 days: {recent_count}")
        
        return {
            'total_messages': total_count,
            'recent_messages': recent_count,
            'retention_days': Config.MESSAGE_RETENTION_DAYS
        }
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        return None
