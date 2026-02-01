SUMMARY_PROMPT = """{persona}

The user {requester} asked: "{query}"

Based on these messages from {target_user}, provide a focused answer that specifically addresses the query. Only include information relevant to what was asked. If the messages don't contain relevant information about the specific topic, say so. Keep it concise and conversational. Address {requester} directly.

Messages:
{messages}

Answer for {requester}:"""

EXAMPLES_PROMPT = """{persona}

{requester} asked: '{query}'

From these messages by {target_user}, select and format 5-10 of the most relevant examples for {requester}. Include timestamps and keep each example to 1-2 lines.

Messages:
{messages}

Relevant Examples for {requester}:"""

RECAP_PROMPT = """{persona}

{requester} wants a recap of recent activity. Summarize the key discussions, decisions, and highlights from these messages. Organize by topic if applicable. Keep it clear and actionable. Address {requester} directly.

Messages:
{messages}

Recap for {requester}:"""

GENERAL_QUERY_PROMPT = """{persona}

The user {user_name} is asking: "{query}"

Based on the following messages from this Discord server, provide a helpful answer directly to {user_name}. If the messages don't contain relevant information, let them know.

Messages:
{messages}

Answer (speak directly to {user_name}):"""

def format_messages_for_ai(messages):
    formatted = []
    for msg in messages:
        author = msg.get('author_name', 'Unknown')
        content = msg.get('content', '')
        created_at = msg.get('created_at', '')
        
        formatted.append(f"[{created_at}] {author}: {content}")
    
    return "\n".join(formatted)

def get_prompt_for_query(query, messages, user_name=None, requester_name=None, persona=None):
    formatted_messages = format_messages_for_ai(messages)
    
    if persona is None:
        persona = "You are a helpful Discord assistant. Be friendly, concise, and informative."
    
    if requester_name is None:
        requester_name = "the user"
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['summary', 'summarize', 'what did', 'tell me about']):
        return SUMMARY_PROMPT.format(
            persona=persona,
            requester=requester_name,
            query=query,
            target_user=user_name or "the user",
            messages=formatted_messages
        )
    
    elif any(word in query_lower for word in ['example', 'show me', 'find']):
        return EXAMPLES_PROMPT.format(
            persona=persona,
            requester=requester_name,
            query=query,
            target_user=user_name or "the user",
            messages=formatted_messages
        )
    
    else:
        return GENERAL_QUERY_PROMPT.format(
            persona=persona,
            user_name=requester_name,
            query=query,
            messages=formatted_messages
        )
