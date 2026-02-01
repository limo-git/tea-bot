import discord
from discord import app_commands
from utils.logger import get_logger
from utils.dm_summary import dm_summary_handler
from utils.email_handler import email_handler
from utils.bug_tracker import bug_tracker
from database.user_preferences import user_preferences_client
from database.topic_preferences import topic_preferences_client, server_summary_settings_client
from database.queries import search_with_context
from ai.gemini_client import gemini_client
from ai.prompts import RECAP_PROMPT
from datetime import datetime, timedelta
import re

logger = get_logger(__name__)

class DMCommands:
    """Commands for managing DM summaries and email delivery"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def dm_settings_command(
        self,
        interaction: discord.Interaction,
        action: str,
        value: str = None
    ):
        """Manage DM summary and email preferences"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id = interaction.user.id
            
            if action == "view":
                prefs = user_preferences_client.get_user_preferences(user_id)
                
                embed = discord.Embed(
                    title="⚙️ Your Summary Preferences",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="📬 DM Summaries",
                    value="✅ Enabled" if prefs['dm_summaries_enabled'] else "❌ Disabled",
                    inline=True
                )
                
                embed.add_field(
                    name="📧 Email Summaries",
                    value="✅ Enabled" if prefs['email_summaries_enabled'] else "❌ Disabled",
                    inline=True
                )
                
                embed.add_field(
                    name="🔔 Bug Alerts",
                    value="✅ Enabled" if prefs['bug_alerts_enabled'] else "❌ Disabled",
                    inline=True
                )
                
                embed.add_field(
                    name="📅 Frequency",
                    value=prefs['summary_frequency'].title(),
                    inline=True
                )
                
                if prefs['email']:
                    embed.add_field(
                        name="📮 Email",
                        value=prefs['email'],
                        inline=True
                    )
                
                embed.set_footer(text="Use /dm-settings to change your preferences")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            elif action == "toggle_dm":
                current = user_preferences_client.get_user_preferences(user_id)
                new_state = not current['dm_summaries_enabled']
                
                if user_preferences_client.toggle_dm_summaries(user_id, new_state):
                    status = "enabled" if new_state else "disabled"
                    await interaction.followup.send(
                        f"✅ DM summaries have been **{status}**.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to update preferences. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "toggle_email":
                current = user_preferences_client.get_user_preferences(user_id)
                
                if not current['email']:
                    await interaction.followup.send(
                        "❌ Please set your email first using `/dm-settings action: Set Email`",
                        ephemeral=True
                    )
                    return
                
                new_state = not current['email_summaries_enabled']
                
                if user_preferences_client.toggle_email_summaries(user_id, new_state):
                    status = "enabled" if new_state else "disabled"
                    await interaction.followup.send(
                        f"✅ Email summaries have been **{status}**.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to update preferences. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "set_email":
                if not value:
                    await interaction.followup.send(
                        "❌ Please provide an email address.",
                        ephemeral=True
                    )
                    return
                
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    await interaction.followup.send(
                        "❌ Invalid email address format.",
                        ephemeral=True
                    )
                    return
                
                if user_preferences_client.set_email(user_id, value):
                    await interaction.followup.send(
                        f"✅ Email set to **{value}**\n\nYou can now enable email summaries with `/dm-settings action: Toggle Email`",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to set email. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "set_frequency":
                if not value or value not in ['daily', 'weekly', 'monthly']:
                    await interaction.followup.send(
                        "❌ Please provide a valid frequency: daily, weekly, or monthly",
                        ephemeral=True
                    )
                    return
                
                if user_preferences_client.set_summary_frequency(user_id, value):
                    await interaction.followup.send(
                        f"✅ Summary frequency set to **{value}**",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to update frequency. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "toggle_bug_alerts":
                current = user_preferences_client.get_user_preferences(user_id)
                new_state = not current['bug_alerts_enabled']
                
                prefs = {
                    'bug_alerts_enabled': new_state
                }
                
                if user_preferences_client.set_user_preferences(user_id, prefs):
                    status = "enabled" if new_state else "disabled"
                    await interaction.followup.send(
                        f"✅ Bug alerts have been **{status}**.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to update preferences. Please try again.",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in dm_settings command: {e}")
            await interaction.followup.send(
                "❌ An error occurred. Please try again later.",
                ephemeral=True
            )
    
    async def request_summary_command(
        self,
        interaction: discord.Interaction,
        time_period: str,
        delivery: str
    ):
        """Request an on-demand summary via DM or email"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Parse time period
            days_map = {
                '24h': 1,
                '7d': 7,
                '30d': 30
            }
            days = days_map.get(time_period, 7)
            
            # Get messages from the time period
            from_date = datetime.utcnow() - timedelta(days=days)
            
            messages = await search_with_context(
                guild_id=guild.id,
                query="",
                from_date=from_date.isoformat(),
                limit=100
            )
            
            if not messages or len(messages) == 0:
                await interaction.followup.send(
                    "❌ No messages found in this time period.",
                    ephemeral=True
                )
                return
            
            # Generate summary using AI
            prompt = f"{RECAP_PROMPT}\n\nGenerate a comprehensive summary of the following messages from the last {days} days:\n\n"
            for msg in messages[:50]:  # Limit to 50 messages for token management
                prompt += f"[{msg.get('author_name', 'Unknown')}]: {msg.get('content', '')}\n"
            
            summary = await gemini_client.generate_response(prompt)
            
            # Extract topics
            topics = []
            if messages:
                # Simple topic extraction from message content
                common_words = {}
                for msg in messages:
                    words = msg.get('content', '').lower().split()
                    for word in words:
                        if len(word) > 5:  # Only count longer words
                            common_words[word] = common_words.get(word, 0) + 1
                
                # Get top 5 topics
                sorted_topics = sorted(common_words.items(), key=lambda x: x[1], reverse=True)
                topics = [word.title() for word, count in sorted_topics[:5]]
            
            summary_data = {
                'content': summary,
                'server_name': guild.name,
                'time_period': f"Last {days} days",
                'topics': topics
            }
            
            # Deliver based on preference
            if delivery == "dm":
                success = await dm_summary_handler.send_dm_summary(interaction.user, summary_data)
                if success:
                    await interaction.followup.send(
                        "✅ Summary sent to your DMs!",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to send DM. Please make sure you have DMs enabled for this server.",
                        ephemeral=True
                    )
            
            elif delivery == "email":
                prefs = user_preferences_client.get_user_preferences(interaction.user.id)
                
                if not prefs.get('email'):
                    await interaction.followup.send(
                        "❌ No email address set. Use `/dm-settings action: Set Email` first.",
                        ephemeral=True
                    )
                    return
                
                success = email_handler.send_summary_email(prefs['email'], summary_data)
                if success:
                    await interaction.followup.send(
                        f"✅ Summary sent to **{prefs['email']}**!",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to send email. Please try again later.",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in request_summary command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while generating the summary.",
                ephemeral=True
            )
    
    async def bug_summary_command(
        self,
        interaction: discord.Interaction,
        days: int
    ):
        """Get a summary of recent bugs and their resolutions"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            summary = bug_tracker.generate_bug_summary(guild.id, days)
            
            if not summary or summary['total_bugs'] == 0:
                await interaction.followup.send(
                    f"No bug discussions found in the last {days} days.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🐛 Bug Summary - Last {days} Days",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📊 Overview",
                value=f"**Total:** {summary['total_bugs']}\n**Resolved:** {summary['resolved']}\n**Unresolved:** {summary['unresolved']}\n**Critical:** {summary['critical_bugs']}",
                inline=False
            )
            
            if summary['resolved_bugs']:
                resolved_text = ""
                for bug in summary['resolved_bugs'][:3]:
                    dep = bug.get('dependency_name', 'Unknown')
                    resolved_text += f"✅ **{dep}**: {bug.get('resolution', 'Fixed')[:100]}\n"
                
                embed.add_field(
                    name="✅ Recently Resolved",
                    value=resolved_text or "None",
                    inline=False
                )
            
            if summary['unresolved_bugs']:
                unresolved_text = ""
                for bug in summary['unresolved_bugs'][:3]:
                    dep = bug.get('dependency_name', 'Unknown')
                    severity = bug.get('severity', 'medium')
                    unresolved_text += f"⚠️ **{dep}** ({severity})\n"
                
                embed.add_field(
                    name="⚠️ Unresolved Issues",
                    value=unresolved_text or "None",
                    inline=False
                )
            
            embed.set_footer(text="Use /dm-settings to enable automatic bug alerts")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in bug_summary command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while generating the bug summary.",
                ephemeral=True
            )
    
    async def summary_topics_command(
        self,
        interaction: discord.Interaction,
        action: str,
        topic: str = None
    ):
        """Manage topic preferences for summaries"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            user_id = interaction.user.id
            server_id = guild.id
            
            if action == "view":
                topics = topic_preferences_client.get_user_topics(user_id, server_id)
                
                embed = discord.Embed(
                    title=f"📋 Your Topic Preferences - {guild.name}",
                    color=discord.Color.blue()
                )
                
                if topics and len(topics) > 0:
                    topics_text = "\n".join([f"• {t}" for t in topics])
                    embed.add_field(
                        name="Active Topics",
                        value=topics_text,
                        inline=False
                    )
                    embed.description = f"You'll receive summaries about these {len(topics)} topics from this server."
                else:
                    embed.description = "No topic filters set. You'll receive summaries about all discussions."
                
                embed.set_footer(text="Use /summary-topics to add or remove topics")
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            elif action == "add":
                if not topic:
                    await interaction.followup.send(
                        "❌ Please provide a topic to add.",
                        ephemeral=True
                    )
                    return
                
                if topic_preferences_client.add_topic(user_id, server_id, topic):
                    await interaction.followup.send(
                        f"✅ Added topic: **{topic}**\n\nYou'll now receive summaries about this topic from {guild.name}.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to add topic. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "remove":
                if not topic:
                    await interaction.followup.send(
                        "❌ Please provide a topic to remove.",
                        ephemeral=True
                    )
                    return
                
                if topic_preferences_client.remove_topic(user_id, server_id, topic):
                    await interaction.followup.send(
                        f"✅ Removed topic: **{topic}**",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to remove topic. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "clear":
                if topic_preferences_client.set_user_topics(user_id, server_id, []):
                    await interaction.followup.send(
                        f"✅ Cleared all topic filters for {guild.name}\n\nYou'll now receive summaries about all discussions.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to clear topics. Please try again.",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in summary_topics command: {e}")
            await interaction.followup.send(
                "❌ An error occurred. Please try again later.",
                ephemeral=True
            )
    
    async def summary_servers_command(
        self,
        interaction: discord.Interaction,
        action: str
    ):
        """Manage which servers send summaries"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            user_id = interaction.user.id
            
            if action == "view":
                # Get all servers user is in and check which have summaries enabled
                enabled_servers = server_summary_settings_client.get_enabled_servers(user_id)
                
                embed = discord.Embed(
                    title="🌐 Your Summary Servers",
                    color=discord.Color.blue()
                )
                
                # Get all servers the bot is in that the user is also in
                user_servers = []
                for bot_guild in self.bot.guilds:
                    member = bot_guild.get_member(user_id)
                    if member:
                        is_enabled = bot_guild.id in enabled_servers
                        status = "✅ Enabled" if is_enabled else "❌ Disabled"
                        user_servers.append(f"{status} - **{bot_guild.name}**")
                
                if user_servers:
                    embed.description = "\n".join(user_servers)
                else:
                    embed.description = "You're not in any servers with this bot."
                
                embed.set_footer(text="Use /summary-servers to enable/disable servers")
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            elif action == "enable":
                if not guild:
                    await interaction.followup.send(
                        "❌ This command can only be used in a server.",
                        ephemeral=True
                    )
                    return
                
                if server_summary_settings_client.set_server_enabled(user_id, guild.id, True):
                    await interaction.followup.send(
                        f"✅ Enabled summaries from **{guild.name}**\n\nYou'll now receive summaries from this server in your DMs.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to enable server. Please try again.",
                        ephemeral=True
                    )
            
            elif action == "disable":
                if not guild:
                    await interaction.followup.send(
                        "❌ This command can only be used in a server.",
                        ephemeral=True
                    )
                    return
                
                if server_summary_settings_client.set_server_enabled(user_id, guild.id, False):
                    await interaction.followup.send(
                        f"✅ Disabled summaries from **{guild.name}**\n\nYou'll no longer receive summaries from this server.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Failed to disable server. Please try again.",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error in summary_servers command: {e}")
            await interaction.followup.send(
                "❌ An error occurred. Please try again later.",
                ephemeral=True
            )

def register_dm_commands(bot):
    """Register DM-related commands with the bot"""
    dm_commands = DMCommands(bot)
    
    @bot.tree.command(name="dm-settings", description="Manage your DM summary and email preferences")
    @app_commands.describe(
        action="What to do",
        value="Value for the action (email address or frequency)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="View Settings", value="view"),
        app_commands.Choice(name="Toggle DM Summaries", value="toggle_dm"),
        app_commands.Choice(name="Toggle Email Summaries", value="toggle_email"),
        app_commands.Choice(name="Set Email", value="set_email"),
        app_commands.Choice(name="Set Frequency", value="set_frequency"),
        app_commands.Choice(name="Toggle Bug Alerts", value="toggle_bug_alerts")
    ])
    async def dm_settings(
        interaction: discord.Interaction,
        action: str,
        value: str = None
    ):
        await dm_commands.dm_settings_command(interaction, action, value)
    
    @bot.tree.command(name="request-summary", description="Request an on-demand summary via DM or email")
    @app_commands.describe(
        time_period="Time period for the summary",
        delivery="How to receive the summary"
    )
    @app_commands.choices(
        time_period=[
            app_commands.Choice(name="Last 24 hours", value="24h"),
            app_commands.Choice(name="Last 7 days", value="7d"),
            app_commands.Choice(name="Last 30 days", value="30d")
        ],
        delivery=[
            app_commands.Choice(name="Send to DM", value="dm"),
            app_commands.Choice(name="Send to Email", value="email")
        ]
    )
    async def request_summary(
        interaction: discord.Interaction,
        time_period: str,
        delivery: str
    ):
        await dm_commands.request_summary_command(interaction, time_period, delivery)
    
    @bot.tree.command(name="bug-summary", description="Get a summary of recent bugs and dependency issues")
    @app_commands.describe(days="Number of days to look back (1-30)")
    async def bug_summary(
        interaction: discord.Interaction,
        days: int = 7
    ):
        if days < 1 or days > 30:
            await interaction.response.send_message(
                "❌ Days must be between 1 and 30.",
                ephemeral=True
            )
            return
        await dm_commands.bug_summary_command(interaction, days)
    
    @bot.tree.command(name="summary-topics", description="Manage which topics you want in your summaries")
    @app_commands.describe(
        action="What to do with topics",
        topic="Topic keyword to add or remove"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="View Topics", value="view"),
        app_commands.Choice(name="Add Topic", value="add"),
        app_commands.Choice(name="Remove Topic", value="remove"),
        app_commands.Choice(name="Clear All Topics", value="clear")
    ])
    async def summary_topics(
        interaction: discord.Interaction,
        action: str,
        topic: str = None
    ):
        await dm_commands.summary_topics_command(interaction, action, topic)
    
    @bot.tree.command(name="summary-servers", description="Manage which servers send you summaries")
    @app_commands.describe(
        action="What to do"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="View Enabled Servers", value="view"),
        app_commands.Choice(name="Enable This Server", value="enable"),
        app_commands.Choice(name="Disable This Server", value="disable")
    ])
    async def summary_servers(
        interaction: discord.Interaction,
        action: str
    ):
        await dm_commands.summary_servers_command(interaction, action)
    
    logger.info("DM commands registered successfully")
