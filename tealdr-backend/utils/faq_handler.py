"""
FAQ Handler for TeaL;DR Bot
Handles common questions and greetings with static responses before hitting the RAG pipeline.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

FAQ_RESPONSES = {
    "greeting": {
        "patterns": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
        "response": """👋 Hey there! I'm TeaL;DR, your Discord search assistant.

I can help you:
• **Search messages** - `/ask what did john say about the API?`
• **Find exact messages** - `/lookup clues: deployment issues`
• **Get summaries** - `/recap period: last 7 days`
• **View stats** - `/stats`

Try asking me something about your server's message history!"""
    },
    
    "help": {
        "patterns": ["help", "how do i use", "how to use", "what can you do", "commands", "how does this work"],
        "response": """🤖 **TeaL;DR Help**

**Main Commands:**
• `/ask [query]` - Ask me anything about your server's history
• `/lookup [clues]` - Find exact messages with specific keywords
• `/recap [period]` - Get a summary of conversations
• `/stats` - View server analytics
• `/help` - Show all available commands

**Example Queries:**
• "What did @user say about the new feature?"
• "Who was discussing Python yesterday?"
• "Summarize the last week's announcements"

**Filters Available:**
You can filter by user, channel, date range, and more!

For detailed documentation, visit: [Your Docs URL]"""
    },
    
    "what_is": {
        "patterns": ["what is tealdr", "what are you", "who are you", "what do you do"],
        "response": """🔍 **I'm TeaL;DR** - A semantic search bot for Discord!

I index your server's messages and let you search them using natural language. Think of me as Ctrl+F on steroids.

**Key Features:**
• 🧠 Semantic search (understands meaning, not just keywords)
• 📊 7 different retrieval pipelines for different query types
• 🎯 Hybrid BM25 + vector search
• 🚫 Zero hallucinations (confidence gating)
• ⚡ Fast results from 3000+ indexed messages

Try: `/ask what was discussed about [topic]?`"""
    },
    
    "how_search": {
        "patterns": ["how to search", "how do i search", "search for", "find messages"],
        "response": """🔍 **How to Search with TeaL;DR**

**Use `/ask` for natural language queries:**
```
/ask what did @john say about the API?
/ask who was discussing Python yesterday?
/ask what happened while I was away?
```

**Use `/lookup` for exact message search:**
```
/lookup clues: deployment error
/lookup clues: meeting notes from: @user
```

**Tips:**
• Be specific with your questions
• Mention users with @username
• Use time keywords like "yesterday", "last week"
• Add filters: from_user, in_channel, from_date, to_date

The bot searches your entire message history (last 30 days)!"""
    },
    
    "recap_help": {
        "patterns": ["how to recap", "how do recaps work", "summary", "summarize"],
        "response": """📊 **Recap Command Help**

**Get conversation summaries:**
```
/recap period: last 7 days
/recap period: yesterday
/recap period: 2w
```

**Time formats:**
• `1h`, `2h` - hours
• `1d`, `7d` - days  
• `1w`, `4w` - weeks
• `yesterday`, `today`, `this week`

**Features:**
• Main topics discussed
• Key participants
• Important decisions
• Action items

You can also set up **daily DM recaps** with `/request-summary`!"""
    },
    
    "privacy": {
        "patterns": ["privacy", "data", "what do you store", "is it safe", "security"],
        "response": """🔒 **Privacy & Data**

**What I store:**
• Message content, author, timestamp, channel
• Embeddings for semantic search
• No DMs (unless you explicitly use DM commands)

**What I don't store:**
• Deleted messages (removed within 24h)
• Messages older than 30 days (auto-cleanup)
• Private/hidden channels (unless bot has access)

**Admin Controls:**
• `/settings` - Configure indexing
• `/private_session` - Temporary indexing pause
• Messages can be excluded from indexing

Your data stays in your server's database. I don't share it with anyone."""
    },
    
    "thanks": {
        "patterns": ["thank", "thanks", "appreciate", "awesome", "great job"],
        "response": "You're welcome! Happy to help. Let me know if you need anything else! 🎉"
    }
}


def check_faq(query: str) -> Optional[str]:
    """
    Check if the query matches any FAQ patterns.
    Returns the static response if matched, None otherwise.
    """
    query_lower = query.lower().strip()
    
    # Remove common punctuation for matching
    query_clean = query_lower.rstrip('?!.')
    
    # Check each FAQ category
    for category, faq_data in FAQ_RESPONSES.items():
        patterns = faq_data["patterns"]
        response = faq_data["response"]
        
        # Check if any pattern matches
        for pattern in patterns:
            if pattern in query_clean:
                logger.info(f"FAQ match found: category={category}, pattern='{pattern}'")
                return response
    
    # No FAQ match found
    return None


def is_general_greeting(query: str) -> bool:
    """
    Check if the query is just a greeting without a real question.
    """
    query_lower = query.lower().strip()
    
    # Single word greetings
    if query_lower in ["hi", "hello", "hey", "yo", "sup", "greetings"]:
        return True
    
    # Short greetings with bot name
    greeting_patterns = [
        "hi tealdr",
        "hello tealdr", 
        "hey tealdr",
        "hi bot",
        "hello bot"
    ]
    
    return any(pattern in query_lower for pattern in greeting_patterns)
