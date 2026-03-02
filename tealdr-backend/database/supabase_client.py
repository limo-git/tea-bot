from supabase import create_client, Client
from config import Config
from utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_PROJECT_URL, Config.SUPABASE_SECRET_KEY)
        logger.info("Supabase client initialized")
    
    async def insert_message(self, message_data):
        try:
            result = self.client.table('messages').insert(message_data).execute()
            logger.debug(f"Inserted message {message_data.get('message_id')}")
            return result
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            raise
    
    async def message_exists(self, message_id):
        try:
            result = self.client.table('messages').select('id').eq('message_id', message_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking message existence: {e}")
            return False
    
    async def get_messages_by_user(self, author_id, server_id, time_range=None, limit=50):
        try:
            query = self.client.table('messages').select('*').eq('author_id', author_id).eq('server_id', server_id)
            
            if time_range:
                start_time, end_time = time_range
                query = query.gte('created_at', start_time.isoformat()).lte('created_at', end_time.isoformat())
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting messages by user: {e}")
            return []
    
    async def get_messages_by_timerange(self, server_id, channel_id=None, start_time=None, end_time=None, limit=50):
        try:
            query = self.client.table('messages').select('*').eq('server_id', server_id)
            
            if channel_id:
                query = query.eq('channel_id', channel_id)
            
            if start_time:
                query = query.gte('created_at', start_time.isoformat())
            
            if end_time:
                query = query.lte('created_at', end_time.isoformat())
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting messages by timerange: {e}")
            return []
    
    async def semantic_search(self, embedding, server_id, limit=10):
        try:
            result = self.client.rpc(
                'match_messages',
                {
                    'query_embedding': embedding,
                    'match_threshold': 0.5,
                    'match_count': limit,
                    'server_id_filter': server_id
                }
            ).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    async def semantic_search_filtered(self, embedding, server_id, author_id=None, time_range=None, channel_id=None, thread_id=None, limit=20):
        try:
            # Select messages with channel name if available
            query = self.client.table('messages').select('*, channels(name)').eq('server_id', server_id)
            
            if author_id:
                query = query.eq('author_id', author_id)
            
            if channel_id:
                query = query.eq('channel_id', channel_id)
            
            if thread_id:
                query = query.eq('thread_id', thread_id)
            
            if time_range:
                start_time, end_time = time_range
                if start_time:
                    query = query.gte('created_at', start_time.isoformat())
                if end_time:
                    query = query.lte('created_at', end_time.isoformat())
            
            messages = query.limit(200).execute().data
            
            if not messages:
                return []
            
            scored_messages = []
            for msg in messages:
                if msg.get('embedding'):
                    similarity = self._cosine_similarity(embedding, msg['embedding'])
                    msg['similarity'] = similarity
                    scored_messages.append(msg)
            
            scored_messages.sort(key=lambda x: x['similarity'], reverse=True)
            return scored_messages[:limit]
        except Exception as e:
            logger.error(f"Error in filtered semantic search: {e}")
            return []
    
    def _cosine_similarity(self, vec1, vec2):
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except:
            return 0.0
    
    async def get_message_count(self):
        try:
            result = self.client.table('messages').select('id', count='exact').execute()
            return result.count
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0

supabase_client = SupabaseClient()
