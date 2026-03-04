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
    
    async def bm25_search(self, query: str, server_id: int, limit: int = 50):
        """
        Perform BM25 full-text search using PostgreSQL tsvector.
        
        Args:
            query: Search query string
            server_id: Server ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of messages with BM25 rank scores
        """
        try:
            # Convert query to tsquery format
            # Handle multi-word queries by joining with &
            query_terms = query.strip().split()
            tsquery = ' & '.join(query_terms)
            
            # Perform full-text search with ts_rank scoring
            result = self.client.table('messages')\
                .select('*')\
                .eq('server_id', server_id)\
                .text_search('content_tsv', tsquery, config='english')\
                .limit(limit)\
                .execute()
            
            # Add rank scores (Supabase doesn't return ts_rank directly, so we assign based on order)
            messages = result.data
            for i, msg in enumerate(messages):
                # Assign descending rank scores (higher is better)
                msg['bm25_rank'] = 1.0 - (i / max(len(messages), 1))
            
            logger.info(f"BM25 search returned {len(messages)} results for query: {query[:60]}")
            return messages
            
        except Exception as e:
            logger.error(f"Error in BM25 search: {e}")
            return []
    
    async def hybrid_search(self, query: str, embedding: list, server_id: int, limit: int = 20):
        """
        Perform hybrid search combining dense vector similarity (pgvector) and sparse BM25 search.
        Uses Reciprocal Rank Fusion (RRF) to combine results.
        
        Args:
            query: Search query string
            embedding: Query embedding vector
            server_id: Server ID to filter by
            limit: Maximum number of final results
            
        Returns:
            List of messages sorted by fused relevance score
        """
        try:
            # Run both searches in parallel
            vector_results = await self.semantic_search(embedding, server_id, limit=50)
            bm25_results = await self.bm25_search(query, server_id, limit=50)
            
            logger.info(f"Hybrid search: {len(vector_results)} vector results, {len(bm25_results)} BM25 results")
            
            # Reciprocal Rank Fusion (RRF) with k=60
            k = 60
            fused_scores = {}
            
            # Add scores from vector search
            for rank, msg in enumerate(vector_results):
                msg_id = msg.get('message_id')
                if msg_id:
                    fused_scores[msg_id] = fused_scores.get(msg_id, 0) + 1 / (k + rank + 1)
            
            # Add scores from BM25 search
            for rank, msg in enumerate(bm25_results):
                msg_id = msg.get('message_id')
                if msg_id:
                    fused_scores[msg_id] = fused_scores.get(msg_id, 0) + 1 / (k + rank + 1)
            
            # Combine all unique messages
            all_messages = {}
            for msg in vector_results + bm25_results:
                msg_id = msg.get('message_id')
                if msg_id and msg_id not in all_messages:
                    all_messages[msg_id] = msg
            
            # Sort by fused score and add similarity field
            sorted_messages = []
            for msg_id, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True):
                if msg_id in all_messages:
                    msg = all_messages[msg_id]
                    msg['similarity'] = score  # Use fused score as similarity
                    sorted_messages.append(msg)
            
            # Return top results
            final_results = sorted_messages[:limit]
            logger.info(f"Hybrid search fused to {len(final_results)} results")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            # Fallback to vector search only
            return await self.semantic_search(embedding, server_id, limit)
    
    async def semantic_search_filtered(self, embedding, server_id, author_id=None, time_range=None, channel_id=None, thread_id=None, limit=20):
        try:
            # Select messages without channel join (no foreign key relationship exists)
            query = self.client.table('messages').select('*').eq('server_id', server_id)
            
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
            
            # Order by created_at DESC to get most recent messages first
            messages = query.order('created_at', desc=True).limit(200).execute().data
            
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
