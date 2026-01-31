from database.supabase_client import supabase_client
from utils.logger import get_logger

logger = get_logger(__name__)

async def store_message_with_embedding(message, embedding):
    try:
        message_data = {
            'message_id': message['message_id'],
            'server_id': message['server_id'],
            'channel_id': message['channel_id'],
            'author_id': message['author_id'],
            'author_name': message['author_name'],
            'content': message['content'],
            'embedding': embedding,
            'created_at': message['created_at'].isoformat()
        }
        
        exists = await supabase_client.message_exists(message['message_id'])
        if exists:
            logger.debug(f"Message {message['message_id']} already exists, skipping")
            return None
        
        result = await supabase_client.insert_message(message_data)
        logger.info(f"Stored message {message['message_id']} with embedding")
        return result
    except Exception as e:
        logger.error(f"Error storing message with embedding: {e}")
        raise

async def search_with_context(query_embedding, server_id, filters=None):
    try:
        author_id = filters.get('author_id') if filters else None
        time_range = filters.get('time_range') if filters else None
        channel_id = filters.get('channel_id') if filters else None
        thread_id = filters.get('thread_id') if filters else None
        min_length = filters.get('min_length') if filters else None
        limit = filters.get('limit', 20) if filters else 20
        
        messages = await supabase_client.semantic_search_filtered(
            embedding=query_embedding,
            server_id=server_id,
            author_id=author_id,
            time_range=time_range,
            channel_id=channel_id,
            thread_id=thread_id,
            limit=limit
        )
        
        # Apply min_length filter if specified
        if min_length and messages:
            messages = [msg for msg in messages if len(msg.get('content', '')) >= min_length]
        
        return messages
    except Exception as e:
        logger.error(f"Error in search with context: {e}")
        return []
