from google import genai
from google.genai import types
from config import Config
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.generation_config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1000,
        )
        logger.info("Gemini client initialized")
    
    async def generate_response(self, prompt, context_messages=None):
        try:
            if context_messages:
                full_prompt = prompt
            else:
                full_prompt = prompt
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=self.generation_config
                )
            )
            
            if response and response.text:
                logger.debug(f"Generated response (length: {len(response.text)})")
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return "I couldn't generate a response. Please try again."
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"An error occurred while generating the response: {str(e)}"

gemini_client = GeminiClient()
