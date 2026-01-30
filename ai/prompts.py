SUMMARY_PROMPT = """You are a Discord conversation summarizer. Given the following messages from {user}, provide a concise summary of their key points, topics discussed, and notable quotes. Keep it under 200 words and conversational.

Messages:
{messages}

Summary:"""

EXAMPLES_PROMPT = """You are a Discord message curator. Given the query '{query}' and these messages from {user}, select and format 5-10 of the most relevant examples. Include timestamps and keep each example to 1-2 lines.

Messages:
{messages}

Relevant Examples:"""

RECAP_PROMPT = """You are a Discord recap assistant. Summarize the key discussions, decisions, and highlights from these messages. Organize by topic if applicable. Keep it clear and actionable.

Messages:
{messages}

Recap:"""

GENERAL_QUERY_PROMPT = """You are a helpful Discord assistant. Based on the following messages, answer the user's question: "{query}"

Provide a clear, concise answer based on the message context. If the messages don't contain relevant information, say so.

Messages:
{messages}

Answer:"""

def format_messages_for_ai(messages):
    formatted = []
    for msg in messages:
        author = msg.get('author_name', 'Unknown')
        content = msg.get('content', '')
        created_at = msg.get('created_at', '')
        
        formatted.append(f"[{created_at}] {author}: {content}")
    
    return "\n".join(formatted)

def get_prompt_for_query(query, messages, user_name=None):
    formatted_messages = format_messages_for_ai(messages)
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['summary', 'summarize', 'what did', 'tell me about']):
        return SUMMARY_PROMPT.format(user=user_name or "the user", messages=formatted_messages)
    
    elif any(word in query_lower for word in ['example', 'show me', 'find']):
        return EXAMPLES_PROMPT.format(query=query, user=user_name or "the user", messages=formatted_messages)
    
    else:
        return GENERAL_QUERY_PROMPT.format(query=query, messages=formatted_messages)
