from datetime import datetime, timedelta
import re
import discord

def parse_time_range(time_string):
    now = datetime.utcnow()
    time_string = time_string.lower().strip()
    
    if time_string == "24h" or time_string == "today":
        start = now - timedelta(hours=24)
        return (start, now)
    
    elif time_string == "7d" or time_string == "this week":
        start = now - timedelta(days=7)
        return (start, now)
    
    elif time_string == "30d" or time_string == "this month":
        start = now - timedelta(days=30)
        return (start, now)
    
    elif time_string == "yesterday":
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)
        return (yesterday_start, yesterday_end)
    
    else:
        start = now - timedelta(days=7)
        return (start, now)

def extract_user_mention(query, guild):
    mention_pattern = r'<@!?(\d+)>|@(\w+)'
    matches = re.findall(mention_pattern, query)
    
    if not matches:
        return None
    
    for match in matches:
        user_id = match[0] if match[0] else None
        username = match[1] if match[1] else None
        
        if user_id:
            try:
                return guild.get_member(int(user_id))
            except:
                continue
        
        if username:
            member = discord.utils.find(lambda m: m.name.lower() == username.lower() or 
                                       (m.nick and m.nick.lower() == username.lower()), 
                                       guild.members)
            if member:
                return member
    
    return None

def truncate_text(text, max_length=2000):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_timestamp(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:R>"

def extract_time_keywords(query):
    query_lower = query.lower()
    
    time_keywords = {
        'yesterday': 'yesterday',
        'today': '24h',
        'this week': '7d',
        'last week': '7d',
        'this month': '30d',
        'last month': '30d'
    }
    
    for keyword, time_range in time_keywords.items():
        if keyword in query_lower:
            return time_range
    
    return None
