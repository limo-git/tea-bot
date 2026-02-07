from google import genai
from google.genai import types
from config import Config
from utils.logger import get_logger
from utils.cache_manager import cache_manager
import asyncio

logger = get_logger(__name__)

client = genai.Client(api_key=Config.GEMINI_API_KEY)

async def generate_embedding(text):
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        # Check cache first
        cached_embedding = cache_manager.get_embedding(text)
        if cached_embedding is not None:
            logger.debug(f"Using cached embedding for text (length: {len(text)})")
            return cached_embedding
        
        # Generate new embedding
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: client.models.embed_content(
                model="models/embedding-001",
                contents=text,
                config={"task_type": "retrieval_document"}
            )
        )
        
        embedding = result.embeddings[0].values
        
        # Cache the result
        cache_manager.set_embedding(text, embedding)
        
        logger.debug(f"Generated and cached embedding for text (length: {len(text)})")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

async def generate_query_embedding(text):
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for query embedding")
            return None
        
        # Check cache first (use different prefix for query embeddings)
        cache_key = f"query:{text}"
        cached_embedding = cache_manager.get_embedding(cache_key)
        if cached_embedding is not None:
            logger.debug(f"Using cached query embedding for text (length: {len(text)})")
            return cached_embedding
        
        # Generate new embedding
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: client.models.embed_content(
                model="models/embedding-001",
                contents=text,
                config={"task_type": "retrieval_query"}
            )
        )
        
        embedding = result.embeddings[0].values
        
        # Cache the result
        cache_manager.set_embedding(cache_key, embedding)
        
        logger.debug(f"Generated and cached query embedding for text (length: {len(text)})")
        return embedding
    except Exception as e:
        logger.error(f"Error generating query embedding: {e}")
        return None

async def generate_embeddings_batch(texts):
    try:
        embeddings = []
        for text in texts:
            embedding = await generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        return []
