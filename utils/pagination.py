import discord
from discord.ui import Button, View
from utils.logger import get_logger

logger = get_logger(__name__)

class PaginationView(View):
    """View for paginated embed navigation."""
    
    def __init__(self, embeds, user, timeout=180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.user = user
        self.current_page = 0
        self.message = None
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button enabled/disabled states."""
        # Disable previous button on first page
        self.children[0].disabled = self.current_page == 0
        
        # Disable next button on last page
        self.children[1].disabled = self.current_page >= len(self.embeds) - 1
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to use the buttons."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "These buttons are not for you! Use `/ask` to make your own query.",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        """Go to next page."""
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self.update_buttons()
        
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )
    
    @discord.ui.button(label="🗑️ Delete", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: Button):
        """Delete the message."""
        await interaction.message.delete()
        self.stop()
    
    async def on_timeout(self):
        """Disable buttons when view times out."""
        for child in self.children:
            child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass  # Message might be deleted

class SimplePaginationView(View):
    """Simpler pagination view with just prev/next."""
    
    def __init__(self, embeds, user, timeout=180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.user = user
        self.current_page = 0
        self.message = None
        
        # Only show buttons if multiple pages
        if len(embeds) <= 1:
            self.clear_items()
        else:
            self.update_buttons()
    
    def update_buttons(self):
        """Update button states."""
        if len(self.embeds) <= 1:
            return
        
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= len(self.embeds) - 1
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to use the buttons."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "These buttons are not for you!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        """Go to next page."""
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self.update_buttons()
        
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )
    
    async def on_timeout(self):
        """Disable buttons when view times out."""
        for child in self.children:
            child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass
