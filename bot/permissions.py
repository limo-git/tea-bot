import discord
from utils.logger import get_logger

logger = get_logger(__name__)

def is_admin(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        logger.warning(f"User {interaction.user} attempted admin action without permissions")
        return False
    return True

def can_access_channel(user: discord.Member, channel: discord.TextChannel):
    permissions = channel.permissions_for(user)
    return permissions.read_messages

def admin_only():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return False
        return True
    return discord.app_commands.check(predicate)
