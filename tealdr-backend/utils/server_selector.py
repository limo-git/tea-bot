"""
Server selection utilities for DM-based commands
"""
import discord
from typing import List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

def get_shared_servers(bot, user: discord.User) -> List[discord.Guild]:
    """Get all servers that both the bot and user are in."""
    shared_servers = []
    
    for guild in bot.guilds:
        member = guild.get_member(user.id)
        if member:
            shared_servers.append(guild)
    
    return shared_servers

def find_server_by_name(bot, user: discord.User, server_name: str) -> Optional[discord.Guild]:
    """Find a specific server by name that both bot and user are in."""
    shared_servers = get_shared_servers(bot, user)
    
    # Try exact match first
    for guild in shared_servers:
        if guild.name.lower() == server_name.lower():
            return guild
    
    # Try partial match
    for guild in shared_servers:
        if server_name.lower() in guild.name.lower():
            return guild
    
    return None

async def resolve_server_context(
    interaction: discord.Interaction,
    bot,
    server_name: Optional[str] = None,
    allow_multi: bool = True
) -> tuple[List[discord.Guild], bool]:
    """
    Resolve which server(s) to use for a command.
    
    Returns:
        tuple: (list of guilds, is_multi_server)
    """
    # If used in a server, use that server
    if interaction.guild:
        return [interaction.guild], False
    
    # If in DM with server_name specified
    if server_name:
        if server_name.lower() in ["all", "all servers", "*"]:
            if not allow_multi:
                return [], False
            servers = get_shared_servers(bot, interaction.user)
            return servers, True
        else:
            # Find specific server
            guild = find_server_by_name(bot, interaction.user, server_name)
            if guild:
                return [guild], False
            else:
                # Server not found
                return [], False
    
    # If in DM without server_name, default to all shared servers
    servers = get_shared_servers(bot, interaction.user)
    
    if not servers:
        return [], False
    
    if len(servers) == 1:
        return servers, False
    
    # Multiple servers — search across all of them
    if allow_multi:
        return servers, True
    else:
        return [servers[0]], False
