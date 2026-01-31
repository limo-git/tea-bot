from collections import defaultdict
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

class ConversationContext:
    def __init__(self, timeout_minutes=10, max_history=5):
        self.timeout_minutes = timeout_minutes
        self.max_history = max_history
        self.user_contexts = defaultdict(list)
        self.last_activity = {}
    
    def add_query(self, user_id, query, response, mentioned_user=None):
        """Add a query-response pair to user's conversation history."""
        now = datetime.utcnow()
        
        if self._is_expired(user_id):
            self.clear_context(user_id)
        
        context_entry = {
            'query': query,
            'response': response,
            'mentioned_user': mentioned_user,
            'timestamp': now
        }
        
        self.user_contexts[user_id].append(context_entry)
        self.last_activity[user_id] = now
        
        if len(self.user_contexts[user_id]) > self.max_history:
            self.user_contexts[user_id].pop(0)
        
        logger.debug(f"Added context for user {user_id}: {len(self.user_contexts[user_id])} entries")
    
    def get_context(self, user_id):
        """Get conversation context for a user."""
        if self._is_expired(user_id):
            self.clear_context(user_id)
            return []
        
        return self.user_contexts[user_id]
    
    def get_last_mentioned_user(self, user_id):
        """Get the last mentioned user from context."""
        context = self.get_context(user_id)
        if not context:
            return None
        
        for entry in reversed(context):
            if entry.get('mentioned_user'):
                return entry['mentioned_user']
        
        return None
    
    def clear_context(self, user_id):
        """Clear conversation context for a user."""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
        if user_id in self.last_activity:
            del self.last_activity[user_id]
        logger.debug(f"Cleared context for user {user_id}")
    
    def _is_expired(self, user_id):
        """Check if user's context has expired."""
        if user_id not in self.last_activity:
            return True
        
        last_time = self.last_activity[user_id]
        timeout = timedelta(minutes=self.timeout_minutes)
        
        return datetime.utcnow() - last_time > timeout
    
    def format_context_for_prompt(self, user_id):
        """Format conversation history for AI prompt."""
        context = self.get_context(user_id)
        if not context:
            return ""
        
        formatted = ["Previous conversation:"]
        for entry in context:
            formatted.append(f"User asked: {entry['query']}")
            formatted.append(f"Bot responded: {entry['response'][:200]}...")  # Truncate for brevity
        
        return "\n".join(formatted)
    
    def has_context(self, user_id):
        """Check if user has active conversation context."""
        return bool(self.get_context(user_id))

conversation_context = ConversationContext()
