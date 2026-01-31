from datetime import datetime, timedelta
from utils.logger import get_logger
from ai.gemini_client import gemini_client
from collections import Counter

logger = get_logger(__name__)

class YearlyWrapped:
    """Generate Spotify Wrapped-style year-end summaries."""
    
    @staticmethod
    async def generate_wrapped(supabase_client, server_id, year=None):
        """Generate yearly wrapped summary for a server."""
        try:
            if year is None:
                year = datetime.utcnow().year - 1  # Default to last year
            
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            
            # Get all messages from the year
            messages = await supabase_client.get_messages_by_timerange(
                server_id=server_id,
                start_time=start_date,
                end_time=end_date,
                limit=5000
            )
            
            if not messages or len(messages) < 50:
                return None, f"Not enough data for {year}. Need at least 50 messages."
            
            # Calculate statistics
            stats = YearlyWrapped._calculate_stats(messages, year)
            
            # Generate AI summary
            ai_summary = await YearlyWrapped._generate_ai_summary(messages, year, stats)
            
            return {
                'year': year,
                'stats': stats,
                'summary': ai_summary
            }, None
            
        except Exception as e:
            logger.error(f"Error generating yearly wrapped: {e}")
            return None, f"Failed to generate wrapped: {str(e)}"
    
    @staticmethod
    def _calculate_stats(messages, year):
        """Calculate various statistics from messages."""
        # User activity
        user_messages = Counter()
        user_chars = Counter()
        
        # Monthly activity
        monthly_counts = {i: 0 for i in range(1, 13)}
        
        # Content analysis
        total_chars = 0
        longest_message = {'content': '', 'author': '', 'length': 0}
        
        # Time analysis
        hourly_activity = Counter()
        
        for msg in messages:
            author = msg.get('author_name', 'Unknown')
            content = msg.get('content', '')
            created_at = msg.get('created_at', '')
            
            user_messages[author] += 1
            user_chars[author] += len(content)
            total_chars += len(content)
            
            # Monthly breakdown
            try:
                if isinstance(created_at, str):
                    msg_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    msg_date = created_at
                monthly_counts[msg_date.month] += 1
                hourly_activity[msg_date.hour] += 1
            except:
                pass
            
            # Longest message
            if len(content) > longest_message['length']:
                longest_message = {
                    'content': content[:200],
                    'author': author,
                    'length': len(content)
                }
        
        # Top users
        top_users = user_messages.most_common(10)
        
        # Most active month
        most_active_month = max(monthly_counts.items(), key=lambda x: x[1])
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        # Most active hour
        most_active_hour = hourly_activity.most_common(1)[0] if hourly_activity else (12, 0)
        
        return {
            'total_messages': len(messages),
            'total_characters': total_chars,
            'unique_users': len(user_messages),
            'top_users': top_users,
            'most_active_month': month_names[most_active_month[0]],
            'most_active_month_count': most_active_month[1],
            'most_active_hour': most_active_hour[0],
            'longest_message': longest_message,
            'avg_message_length': total_chars // len(messages) if messages else 0,
            'monthly_breakdown': monthly_counts
        }
    
    @staticmethod
    async def _generate_ai_summary(messages, year, stats):
        """Generate AI-powered highlights and insights."""
        try:
            # Sample interesting messages
            sample_messages = messages[:100] if len(messages) > 100 else messages
            
            message_context = "\n".join([
                f"{msg.get('author_name')}: {msg.get('content')[:150]}"
                for msg in sample_messages[:30]
            ])
            
            prompt = f"""Create a fun, engaging "Year in Review" summary for {year} based on this Discord server's activity.

Statistics:
- Total messages: {stats['total_messages']:,}
- Active users: {stats['unique_users']}
- Most active month: {stats['most_active_month']}
- Top contributor: {stats['top_users'][0][0] if stats['top_users'] else 'Unknown'}

Sample messages:
{message_context}

Generate a brief, exciting summary (3-4 sentences) highlighting:
1. Overall server vibe/theme
2. Most memorable moments or topics
3. Community growth or changes
4. Fun fact or surprise

Keep it upbeat and celebratory like Spotify Wrapped!"""

            summary = await gemini_client.generate_response(prompt)
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return f"What a year it was in {year}! The community came together with amazing conversations and memorable moments."

yearly_wrapped = YearlyWrapped()
