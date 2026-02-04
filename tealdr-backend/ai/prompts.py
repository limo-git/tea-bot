SUMMARY_PROMPT = """{persona}

The user {requester} asked: "{query}"

Based on the following messages, provide a helpful and comprehensive answer. If the query is specific, focus on that topic. If the query is broad or general, provide a well-organized overview of the relevant information.

Messages from {target_user}:
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

Based on the following messages from this Discord server, provide a helpful and comprehensive answer. For broad questions, give an organized overview. For specific questions, focus on the relevant details. Be conversational and helpful.

Messages:
{messages}

Answer for {user_name}:"""

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
    
    # Use EXAMPLES_PROMPT only for explicit example requests
    if any(word in query_lower for word in ['example', 'examples', 'show me examples', 'give me examples']):
        return EXAMPLES_PROMPT.format(
            persona=persona,
            requester=requester_name,
            query=query,
            target_user=user_name or "the user",
            messages=formatted_messages
        )
    
    # Use SUMMARY_PROMPT for user-specific queries
    elif user_name and user_name != "users":
        return SUMMARY_PROMPT.format(
            persona=persona,
            requester=requester_name,
            query=query,
            target_user=user_name,
            messages=formatted_messages
        )
    
    # Use GENERAL_QUERY_PROMPT for all other queries (handles both broad and specific)
    else:
        return GENERAL_QUERY_PROMPT.format(
            persona=persona,
            user_name=requester_name,
            query=query,
            messages=formatted_messages
        )
