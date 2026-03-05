from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class ConversationContext:
    def __init__(self, timeout_minutes=10, max_history=5):
        self.timeout_minutes = timeout_minutes
        self.max_history = max_history
        self.user_contexts = defaultdict(list)
        self.last_activity = {}
    
    def add_query(self, user_id, query, response, mentioned_user=None, source_messages=None, entities=None):
        """
        Add a query-response pair to user's conversation history with source anchoring.
        
        Args:
            user_id: Discord user ID
            query: User's query text
            response: Bot's response text
            mentioned_user: User mentioned in the query (if any)
            source_messages: List of message IDs used as sources for the response
            entities: List of entities extracted from the query
        """
        now = datetime.utcnow()
        
        if self._is_expired(user_id):
            self.clear_context(user_id)
        
        context_entry = {
            'query': query,
            'response': response,
            'mentioned_user': mentioned_user,
            'timestamp': now,
            'source_messages': source_messages or [],  # P3: Source anchoring
            'entities': entities or [],  # P3: Track entities for context continuity
            'turn_number': len(self.user_contexts[user_id]) + 1
        }
        
        self.user_contexts[user_id].append(context_entry)
        self.last_activity[user_id] = now
        
        if len(self.user_contexts[user_id]) > self.max_history:
            self.user_contexts[user_id].pop(0)
        
        logger.debug(f"Added context for user {user_id}: turn {context_entry['turn_number']}, {len(source_messages or [])} sources")
    
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
    
    def get_relevant_entities(self, user_id) -> List[str]:
        """Get all entities mentioned in recent conversation context."""
        context = self.get_context(user_id)
        if not context:
            return []
        
        entities = set()
        for entry in context:
            entities.update(entry.get('entities', []))
        
        return list(entities)
    
    def get_source_messages(self, user_id) -> List[str]:
        """Get all source message IDs from recent context."""
        context = self.get_context(user_id)
        if not context:
            return []
        
        sources = set()
        for entry in context:
            sources.update(entry.get('source_messages', []))
        
        return list(sources)
    
    def calculate_context_relevance(self, user_id, current_query: str) -> float:
        """
        Calculate how relevant the conversation context is to the current query.
        Returns a score between 0.0 (not relevant) and 1.0 (highly relevant).
        """
        context = self.get_context(user_id)
        if not context:
            return 0.0
        
        # Simple heuristic: check for pronoun references or continuation phrases
        continuation_indicators = [
            'it', 'that', 'this', 'they', 'them', 'their',
            'also', 'and', 'but', 'however', 'additionally',
            'what about', 'how about', 'tell me more',
            'continue', 'go on', 'elaborate'
        ]
        
        query_lower = current_query.lower()
        relevance_score = 0.0
        
        # Check for continuation indicators
        for indicator in continuation_indicators:
            if indicator in query_lower:
                relevance_score += 0.3
                break
        
        # Check if query is short (likely a follow-up)
        if len(current_query.split()) <= 5:
            relevance_score += 0.2
        
        # Check for entity overlap
        recent_entities = self.get_relevant_entities(user_id)
        if recent_entities:
            for entity in recent_entities:
                if entity.lower() in query_lower:
                    relevance_score += 0.5
                    break
        
        return min(relevance_score, 1.0)
    
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
    
    def format_context_for_prompt(self, user_id, include_sources: bool = True):
        """
        Format conversation history for AI prompt with source anchoring.
        
        Args:
            user_id: Discord user ID
            include_sources: Whether to include source message references
        """
        context = self.get_context(user_id)
        if not context:
            return ""
        
        formatted = ["Previous conversation context:"]
        for i, entry in enumerate(context, 1):
            formatted.append(f"\nTurn {entry.get('turn_number', i)}:")
            formatted.append(f"  User: {entry['query']}")
            
            # Truncate response but keep it informative
            response = entry['response']
            if len(response) > 300:
                response = response[:300] + "..."
            formatted.append(f"  Bot: {response}")
            
            # P3: Add source anchoring
            if include_sources and entry.get('source_messages'):
                source_count = len(entry['source_messages'])
                formatted.append(f"  Sources: {source_count} messages referenced")
            
            # P3: Add entity tracking
            if entry.get('entities'):
                entities_str = ", ".join(entry['entities'][:3])  # Show first 3
                formatted.append(f"  Entities: {entities_str}")
        
        formatted.append("\nCurrent query should build on this context if relevant.")
        return "\n".join(formatted)
    
    def has_context(self, user_id):
        """Check if user has active conversation context."""
        return bool(self.get_context(user_id))

conversation_context = ConversationContext()
