from utils.logger import get_logger
from ai.gemini_client import gemini_client
import re

logger = get_logger(__name__)

class AutoTagger:
    """Automatically tag and categorize messages."""
    
    # Predefined tag categories
    CATEGORIES = {
        'technical': ['api', 'bug', 'code', 'error', 'fix', 'feature', 'deploy', 'database', 'server'],
        'discussion': ['idea', 'thought', 'opinion', 'discuss', 'debate', 'question'],
        'announcement': ['announce', 'news', 'update', 'release', 'important', 'notice'],
        'social': ['hello', 'hi', 'thanks', 'lol', 'haha', 'congrats', 'welcome'],
        'help': ['help', 'how', 'what', 'why', 'when', 'where', 'can someone', 'need'],
        'action': ['todo', 'task', 'must', 'should', 'need to', 'have to', 'deadline']
    }
    
    @staticmethod
    async def tag_message(content, author_name=None):
        """Generate tags for a message."""
        try:
            tags = []
            content_lower = content.lower()
            
            # Rule-based tagging
            for category, keywords in AutoTagger.CATEGORIES.items():
                if any(keyword in content_lower for keyword in keywords):
                    tags.append(category)
            
            # Detect questions
            if '?' in content or content_lower.startswith(('how', 'what', 'why', 'when', 'where', 'who')):
                tags.append('question')
            
            # Detect urgency
            urgent_words = ['urgent', 'asap', 'emergency', 'critical', 'important', 'now']
            if any(word in content_lower for word in urgent_words):
                tags.append('urgent')
            
            # Detect links
            if 'http://' in content or 'https://' in content:
                tags.append('has_link')
            
            # Detect code
            if '```' in content or '`' in content:
                tags.append('has_code')
            
            # Length-based tags
            if len(content) > 500:
                tags.append('long_form')
            elif len(content) < 50:
                tags.append('short')
            
            # Remove duplicates
            tags = list(set(tags))
            
            # Use AI for more nuanced tagging if message is substantial
            if len(content) > 100 and len(tags) < 3:
                ai_tags = await AutoTagger._ai_tag_message(content)
                tags.extend(ai_tags)
            
            return list(set(tags))[:5]  # Limit to 5 tags
            
        except Exception as e:
            logger.error(f"Error tagging message: {e}")
            return ['general']
    
    @staticmethod
    async def _ai_tag_message(content):
        """Use AI to generate contextual tags."""
        try:
            prompt = f"""Analyze this Discord message and provide 1-3 relevant tags.

Message: "{content[:300]}"

Choose from these categories or suggest similar ones:
- technical, bug_report, feature_request
- discussion, opinion, debate
- announcement, update, news
- question, help_needed
- social, casual, humor
- action_item, task, decision

Respond with ONLY the tags, comma-separated, no explanation:"""

            response = await gemini_client.generate_response(prompt)
            
            # Parse tags from response
            tags = [tag.strip().lower().replace(' ', '_') 
                   for tag in response.split(',')[:3]]
            
            return [tag for tag in tags if tag and len(tag) < 20]
            
        except Exception as e:
            logger.error(f"Error in AI tagging: {e}")
            return []
    
    @staticmethod
    def get_tag_emoji(tag):
        """Get emoji representation for a tag."""
        emoji_map = {
            'technical': '💻',
            'bug': '🐛',
            'discussion': '💬',
            'announcement': '📢',
            'social': '🎉',
            'help': '❓',
            'question': '❓',
            'action': '✅',
            'urgent': '🚨',
            'has_link': '🔗',
            'has_code': '📝',
            'long_form': '📄',
            'short': '💭'
        }
        return emoji_map.get(tag, '🏷️')

auto_tagger = AutoTagger()
