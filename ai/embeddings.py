from google import genai
from google.genai import types
from config import Config
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

client = genai.Client(api_key=Config.GEMINI_API_KEY)

async def generate_embedding(text):
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
        )
        
        embedding = result.embeddings[0].values
        logger.debug(f"Generated embedding for text (length: {len(text)})")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

async def generate_query_embedding(text):
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for query embedding")
            return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
        )
        
        embedding = result.embeddings[0].values
        logger.debug(f"Generated query embedding for text (length: {len(text)})")
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
