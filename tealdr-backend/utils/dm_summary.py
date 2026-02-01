import discord
from utils.logger import get_logger
from ai.gemini_client import gemini_client
from database.supabase_client import supabase_client
from database.topic_preferences import topic_preferences_client
from datetime import datetime

logger = get_logger(__name__)

class DMSummaryHandler:
    """Handles sending personalized summaries to users via DM"""
    
    @staticmethod
    def filter_messages_by_topics(messages: list, topics: list) -> list:
        """
        Filter messages to only include those matching user's topic preferences
        
        Args:
            messages: List of message dictionaries
            topics: List of topic keywords to filter by
            
        Returns:
            Filtered list of messages
        """
        if not topics or len(topics) == 0:
            return messages
        
        filtered = []
        for msg in messages:
            content = msg.get('content', '').lower()
            # Check if any topic keyword appears in the message
            if any(topic.lower() in content for topic in topics):
                filtered.append(msg)
        
        return filtered
    
    @staticmethod
    async def send_dm_summary(user: discord.User, summary_data: dict):
        """
        Send a personalized summary to a user's DMs
        
        Args:
            user: Discord user to send DM to
            summary_data: Dict containing summary information
        """
        try:
            embed = discord.Embed(
                title="📬 Your Personalized Summary",
                description=summary_data.get('content', ''),
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            if summary_data.get('server_name'):
                embed.add_field(
                    name="🏠 Server",
                    value=summary_data['server_name'],
                    inline=True
                )
            
            if summary_data.get('time_period'):
                embed.add_field(
                    name="📅 Period",
                    value=summary_data['time_period'],
                    inline=True
                )
            
            if summary_data.get('topics'):
                topics_text = "\n".join([f"• {topic}" for topic in summary_data['topics'][:5]])
                embed.add_field(
                    name="🔖 Key Topics",
                    value=topics_text,
                    inline=False
                )
            
            embed.set_footer(text="💡 Tip: Use /dm-settings to manage your summary preferences")
            
            await user.send(embed=embed)
            logger.info(f"Sent DM summary to {user.name}")
            return True
            
        except discord.Forbidden:
            logger.warning(f"Cannot send DM to {user.name} - DMs disabled")
            return False
        except Exception as e:
            logger.error(f"Error sending DM summary: {e}")
            return False
    
    @staticmethod
    async def send_bug_summary(user: discord.User, bug_data: dict):
        """
        Send a summary about bugs/dependency updates to user's DMs
        
        Args:
            user: Discord user to send DM to
            bug_data: Dict containing bug/dependency information
        """
        try:
            embed = discord.Embed(
                title="🐛 Bug & Dependency Update Summary",
                description=bug_data.get('summary', ''),
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            if bug_data.get('dependency'):
                embed.add_field(
                    name="📦 Dependency",
                    value=bug_data['dependency'],
                    inline=True
                )
            
            if bug_data.get('severity'):
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }
                emoji = severity_emoji.get(bug_data['severity'].lower(), '⚪')
                embed.add_field(
                    name="⚠️ Severity",
                    value=f"{emoji} {bug_data['severity'].title()}",
                    inline=True
                )
            
            if bug_data.get('resolution'):
                embed.add_field(
                    name="✅ Resolution",
                    value=bug_data['resolution'],
                    inline=False
                )
            
            if bug_data.get('discussion_link'):
                embed.add_field(
                    name="🔗 Discussion",
                    value=f"[View full discussion]({bug_data['discussion_link']})",
                    inline=False
                )
            
            embed.set_footer(text="Stay updated with the latest bug fixes and dependency updates")
            
            await user.send(embed=embed)
            logger.info(f"Sent bug summary to {user.name}")
            return True
            
        except discord.Forbidden:
            logger.warning(f"Cannot send DM to {user.name} - DMs disabled")
            return False
        except Exception as e:
            logger.error(f"Error sending bug summary: {e}")
            return False

dm_summary_handler = DMSummaryHandler()
