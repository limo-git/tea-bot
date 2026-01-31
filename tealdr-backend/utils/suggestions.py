from utils.logger import get_logger
from ai.gemini_client import gemini_client
import re

logger = get_logger(__name__)

class SmartSuggestions:
    """Generate smart follow-up query suggestions based on search results."""
    
    @staticmethod
    async def generate_suggestions(query, messages, mentioned_user=None):
        """Generate 3-5 related query suggestions based on the search results."""
        try:
            # Extract key topics from messages
            topics = SmartSuggestions._extract_topics(messages)
            
            # Build prompt for AI to generate suggestions
            prompt = f"""Based on this search query: "{query}"

And these topics found in the results: {', '.join(topics[:5])}

Generate 3-5 short, natural follow-up questions a user might want to ask next.
Each question should be on a new line, starting with "•".
Keep questions concise (under 60 characters each).
Make them specific and actionable.

Examples:
• What did others say about this?
• When was this first mentioned?
• Who else was involved?
• What was the outcome?
• Show me more recent discussions

Your suggestions:"""

            response = await gemini_client.generate_response(prompt)
            
            # Parse suggestions from response
            suggestions = SmartSuggestions._parse_suggestions(response)
            
            # Add context-aware suggestions
            if mentioned_user:
                suggestions.insert(0, f"What else did {mentioned_user.name} say?")
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return SmartSuggestions._get_default_suggestions(query, mentioned_user)
    
    @staticmethod
    def _extract_topics(messages):
        """Extract key topics/keywords from messages."""
        topics = set()
        
        for msg in messages[:10]:  # Analyze top 10 messages
            content = msg.get('content', '').lower()
            
            # Extract words longer than 4 characters (likely meaningful)
            words = re.findall(r'\b\w{5,}\b', content)
            topics.update(words[:3])  # Add top 3 words from each message
        
        return list(topics)[:10]
    
    @staticmethod
    def _parse_suggestions(response):
        """Parse AI-generated suggestions from response."""
        suggestions = []
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines starting with bullet points
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                suggestion = line.lstrip('•-* ').strip()
                if suggestion and len(suggestion) < 100:
                    suggestions.append(suggestion)
        
        return suggestions
    
    @staticmethod
    def _get_default_suggestions(query, mentioned_user=None):
        """Return default suggestions if AI generation fails."""
        suggestions = [
            "Show me more recent discussions",
            "What was said about this yesterday?",
            "Who else talked about this?"
        ]
        
        if mentioned_user:
            suggestions.insert(0, f"What else did {mentioned_user.name} say?")
        
        return suggestions

smart_suggestions = SmartSuggestions()
