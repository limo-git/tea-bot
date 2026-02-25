from google import genai
from google.genai import types
from config import Config
from utils.logger import get_logger
from utils.cache_manager import cache_manager
import asyncio

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.generation_config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=8192,
        )
        logger.info("Gemini client initialized")
    
    async def generate_response(self, prompt, context_messages=None, use_cache=True):
        try:
            if context_messages:
                full_prompt = prompt
            else:
                full_prompt = prompt
            
            # Check cache first (if enabled)
            if use_cache:
                cached_response = cache_manager.get_response(full_prompt)
                if cached_response is not None:
                    logger.debug("Using cached AI response")
                    return cached_response
            
            # Generate new response
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=full_prompt,
                    config=self.generation_config
                )
            )
            
            response_text = response.text
            
            # Cache the result (if enabled)
            if use_cache:
                cache_manager.set_response(full_prompt, response_text)
            
            if response_text:
                logger.debug(f"Generated response (length: {len(response_text)})")
                return response_text
            else:
                logger.warning("Empty response from Gemini")
                return "I couldn't generate a response. Please try again."
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating response: {e}")
            
            # Check for specific error types
            if "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg:
                return "🔴 **Service Temporarily Unavailable**\n\nThe AI service is experiencing high demand right now. Please try again in a few moments."
            elif "429" in error_msg or "quota" in error_msg.lower():
                return "⚠️ **Rate Limit Reached**\n\nToo many requests. Please wait a moment and try again."
            elif "404" in error_msg or "NOT_FOUND" in error_msg:
                return "❌ **Model Not Available**\n\nThe AI model is not available. Please contact the bot administrator."
            else:
                return "I encountered an error while processing your request. Please try again."

gemini_client = GeminiClient()
