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

class ServerSelectorView(discord.ui.View):
    """Interactive view for selecting a server in DMs."""
    
    def __init__(self, servers: List[discord.Guild], allow_all: bool = True, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.selected_server = None
        self.selected_all = False
        
        # Create dropdown options
        options = []
        
        if allow_all:
            options.append(
                discord.SelectOption(
                    label="🌐 All Servers (Multi-Search)",
                    value="__all__",
                    description="Search across all your servers",
                    emoji="🔍"
                )
            )
        
        for guild in servers[:24]:  # Discord limit is 25 options, we used 1 for "All"
            # Truncate long server names
            name = guild.name[:100] if len(guild.name) > 100 else guild.name
            options.append(
                discord.SelectOption(
                    label=name,
                    value=str(guild.id),
                    description=f"{guild.member_count} members" if guild.member_count else "Server",
                    emoji="📁"
                )
            )
        
        # Add the select menu
        select = discord.ui.Select(
            placeholder="Choose a server to search...",
            options=options,
            min_values=1,
            max_values=1
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """Handle server selection."""
        selected_value = interaction.data['values'][0]
        
        if selected_value == "__all__":
            self.selected_all = True
            await interaction.response.send_message(
                "🌐 Searching across all your servers...",
                ephemeral=True
            )
        else:
            self.selected_server = int(selected_value)
            guild = interaction.client.get_guild(self.selected_server)
            await interaction.response.send_message(
                f"📁 Searching in **{guild.name}**...",
                ephemeral=True
            )
        
        self.stop()
    
    async def on_timeout(self):
        """Handle timeout."""
        # Disable all items
        for item in self.children:
            item.disabled = True

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
    
    # If in DM without server_name, show picker
    servers = get_shared_servers(bot, interaction.user)
    
    if not servers:
        return [], False
    
    if len(servers) == 1:
        # Only one shared server, use it automatically
        return servers, False
    
    # Show interactive picker
    view = ServerSelectorView(servers, allow_all=allow_multi)
    
    embed = discord.Embed(
        title="🔍 Select Server",
        description="Which server would you like to search?",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Your Servers",
        value=f"You share **{len(servers)}** server(s) with me.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    # Wait for selection
    await view.wait()
    
    if view.selected_all:
        return servers, True
    elif view.selected_server:
        guild = bot.get_guild(view.selected_server)
        return [guild] if guild else [], False
    else:
        # Timeout or no selection
        return [], False
