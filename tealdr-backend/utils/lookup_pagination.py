"""
Pagination view for /lookup command with arrow reactions and source viewing.
"""

import discord
from discord.ui import View
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class LookupPaginationView(View):
    """Pagination view for lookup results with source viewing."""
    
    def __init__(self, messages: List[Dict], clues: str, guild: discord.Guild, user: discord.User, items_per_page: int = 10, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.messages = messages
        self.clues = clues
        self.guild = guild
        self.user = user
        self.items_per_page = items_per_page
        self.current_page = 0
        self.showing_sources = False
        self.message = None
        
        # Calculate total pages
        self.total_pages = (len(messages) + items_per_page - 1) // items_per_page
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button enabled/disabled states."""
        # Previous button (index 0)
        self.children[0].disabled = self.current_page == 0
        
        # Next button (index 1)
        self.children[1].disabled = self.current_page >= self.total_pages - 1
        
        # Sources button (index 2) - update label based on state
        if self.showing_sources:
            self.children[2].label = "📋 Show Results"
            self.children[2].style = discord.ButtonStyle.secondary
        else:
            self.children[2].label = "📊 Show Sources"
            self.children[2].style = discord.ButtonStyle.primary
    
    def create_results_embed(self) -> discord.Embed:
        """Create embed showing lookup results for current page."""
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.messages))
        page_messages = self.messages[start_idx:end_idx]
        
        embed = discord.Embed(
            title="🔍 Lookup Results",
            description=f"Found {len(self.messages)} relevant message(s) matching: \"{self.clues}\"\n*Showing messages with >50% relevance*",
            color=discord.Color.blue()
        )
        
        for i, msg in enumerate(page_messages, start=start_idx + 1):
            author_name = msg.get("author_name") or msg.get("author", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("created_at") or msg.get("timestamp", "")
            
            # Get channel name
            channel_id = msg.get("channel_id")
            channel_name = None
            if channel_id:
                try:
                    channel = self.guild.get_channel(int(channel_id))
                    if channel:
                        channel_name = f"#{channel.name}"
                except:
                    pass
            if not channel_name:
                channel_name = msg.get("channel", "")
                if channel_name and not channel_name.startswith("#"):
                    channel_name = f"#{channel_name}"
            
            # Format timestamp
            if timestamp:
                try:
                    from datetime import datetime
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        dt = timestamp
                    unix_timestamp = int(dt.timestamp())
                    date_str = f"<t:{unix_timestamp}:f>"
                except:
                    date_str = str(timestamp)[:19]
            else:
                date_str = "Unknown date"
            
            # Truncate long messages
            display_content = content
            if len(content) > 200:
                display_content = content[:200] + "..."
            
            # Format field
            field_name = f"{i}. {author_name}"
            if channel_name:
                field_value = f"**When:** {date_str}\n**Where:** {channel_name}\n**Said:** \"{display_content}\""
            else:
                field_value = f"**When:** {date_str}\n**Said:** \"{display_content}\""
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )
        
        # Footer with page info
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Showing {start_idx + 1}-{end_idx} of {len(self.messages)} results")
        
        return embed
    
    def create_sources_embed(self) -> discord.Embed:
        """Create embed showing source information for current page."""
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.messages))
        page_messages = self.messages[start_idx:end_idx]
        
        embed = discord.Embed(
            title="📊 Source Information",
            description=f"Detailed source data for page {self.current_page + 1}",
            color=discord.Color.green()
        )
        
        for i, msg in enumerate(page_messages, start=start_idx + 1):
            author_name = msg.get("author_name") or msg.get("author", "Unknown")
            author_id = msg.get("author_id", "Unknown")
            message_id = msg.get("message_id", "Unknown")
            channel_id = msg.get("channel_id", "Unknown")
            similarity = msg.get("similarity", 0)
            
            # Get channel name
            channel_name = "Unknown"
            if channel_id and channel_id != "Unknown":
                try:
                    channel = self.guild.get_channel(int(channel_id))
                    if channel:
                        channel_name = f"#{channel.name}"
                except:
                    pass
            
            field_value = (
                f"**Author:** {author_name} (ID: `{author_id}`)\n"
                f"**Message ID:** `{message_id}`\n"
                f"**Channel:** {channel_name} (ID: `{channel_id}`)\n"
                f"**Relevance:** {similarity:.1%}"
            )
            
            embed.add_field(
                name=f"{i}. Source Details",
                value=field_value,
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages} • Click 'Show Results' to return")
        
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to use the buttons."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "These buttons are not for you! Use `/lookup` to make your own search.",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_results_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page."""
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_results_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📊 Show Sources", style=discord.ButtonStyle.primary)
    async def sources_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle between results and sources view."""
        self.showing_sources = not self.showing_sources
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_results_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Disable buttons when view times out."""
        for child in self.children:
            child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass
