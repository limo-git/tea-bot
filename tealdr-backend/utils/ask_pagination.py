"""
Pagination view for /ask command with arrow navigation, sources toggle, and feedback buttons.
"""

import discord
from discord.ui import View, Button
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class AskPaginationView(View):
    """Pagination view for /ask responses with sources toggle and feedback."""
    
    def __init__(
        self, 
        answer: str, 
        context_items: List[Dict], 
        user: discord.User,
        guild: discord.Guild,
        query: str,
        chars_per_page: int = 1800,
        timeout: int = 300
    ):
        super().__init__(timeout=timeout)
        self.answer = answer
        self.context_items = context_items
        self.user = user
        self.guild = guild
        self.query = query
        self.chars_per_page = chars_per_page
        self.current_page = 0
        self.showing_sources = False
        self.message = None
        self.feedback_given = None  # Track if user gave feedback
        
        # Split answer into pages if needed
        self.answer_pages = self._split_into_pages(answer, chars_per_page)
        self.total_pages = len(self.answer_pages)
        
        # Update button states
        self.update_buttons()
    
    def _split_into_pages(self, text: str, max_chars: int) -> List[str]:
        """Split long text into pages, trying to break at paragraph boundaries."""
        if len(text) <= max_chars:
            return [text]
        
        pages = []
        current_page = ""
        
        # Split by paragraphs (double newline)
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            # If adding this paragraph exceeds limit, save current page and start new one
            if len(current_page) + len(para) + 2 > max_chars and current_page:
                pages.append(current_page.strip())
                current_page = para
            else:
                if current_page:
                    current_page += '\n\n' + para
                else:
                    current_page = para
            
            # If single paragraph is too long, split it by sentences
            if len(current_page) > max_chars:
                sentences = current_page.split('. ')
                temp_page = ""
                for sentence in sentences:
                    if len(temp_page) + len(sentence) + 2 > max_chars and temp_page:
                        pages.append(temp_page.strip() + '.')
                        temp_page = sentence
                    else:
                        if temp_page:
                            temp_page += '. ' + sentence
                        else:
                            temp_page = sentence
                current_page = temp_page
        
        # Add remaining content
        if current_page:
            pages.append(current_page.strip())
        
        return pages if pages else [text]
    
    def update_buttons(self):
        """Update button enabled/disabled states."""
        # Calculate max pages based on current view
        if self.showing_sources:
            # For sources, calculate max pages based on 10 sources per page
            max_pages = max(1, (len(self.context_items) + 9) // 10)
        else:
            max_pages = self.total_pages
        
        # Previous button (index 0)
        self.children[0].disabled = self.current_page == 0
        
        # Next button (index 1)
        self.children[1].disabled = self.current_page >= max_pages - 1
        
        # Sources button (index 2) - update label based on state
        if self.showing_sources:
            self.children[2].label = "📋 Show Answer"
            self.children[2].style = discord.ButtonStyle.secondary
        else:
            self.children[2].label = "📊 Show Sources"
            self.children[2].style = discord.ButtonStyle.primary
        
        # Feedback buttons (index 3, 4) - disable if feedback already given
        if self.feedback_given is not None:
            self.children[3].disabled = True
            self.children[4].disabled = True
            # Update style to show which was selected
            if self.feedback_given == 'positive':
                self.children[3].style = discord.ButtonStyle.success
                self.children[4].style = discord.ButtonStyle.secondary
            else:
                self.children[3].style = discord.ButtonStyle.secondary
                self.children[4].style = discord.ButtonStyle.danger
    
    def create_answer_embed(self) -> discord.Embed:
        """Create embed showing the answer for current page."""
        embed = discord.Embed(
            title="💬 Answer",
            description=self.answer_pages[self.current_page],
            color=discord.Color.blue()
        )
        
        # Add query as field
        query_display = self.query if len(self.query) <= 100 else self.query[:97] + "..."
        embed.add_field(
            name="❓ Your Question",
            value=query_display,
            inline=False
        )
        
        # Footer with page info and source count
        if self.total_pages > 1:
            footer_text = f"Page {self.current_page + 1}/{self.total_pages} • {len(self.context_items)} sources used"
        else:
            footer_text = f"{len(self.context_items)} sources used"
        
        embed.set_footer(text=footer_text)
        
        return embed
    
    def create_sources_embed(self) -> discord.Embed:
        """Create embed showing source information."""
        embed = discord.Embed(
            title="📊 Sources",
            description=f"Sources used to answer your question",
            color=discord.Color.green()
        )
        
        # Show up to 10 sources per page
        start_idx = self.current_page * 10
        end_idx = min(start_idx + 10, len(self.context_items))
        page_sources = self.context_items[start_idx:end_idx]
        
        for i, item in enumerate(page_sources, start=start_idx + 1):
            author_name = item.get("author_name") or item.get("author", "Unknown")
            content = item.get("content", "")
            channel_name = item.get("channel", "")
            timestamp = item.get("timestamp") or item.get("created_at", "")
            
            # Get channel mention if possible
            channel_id = item.get("channel_id")
            if channel_id:
                try:
                    channel = self.guild.get_channel(int(channel_id))
                    if channel:
                        channel_name = channel.mention
                except:
                    pass
            
            if channel_name and not channel_name.startswith("#") and not channel_name.startswith("<#"):
                channel_name = f"#{channel_name}"
            
            # Format timestamp
            time_str = ""
            if timestamp:
                try:
                    from datetime import datetime as dt
                    if isinstance(timestamp, str):
                        timestamp_dt = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        timestamp_dt = timestamp
                    unix_timestamp = int(timestamp_dt.timestamp())
                    time_str = f"<t:{unix_timestamp}:R>"
                except:
                    time_str = str(timestamp)[:19]
            
            # Truncate content
            content_preview = content[:150] + "..." if len(content) > 150 else content
            
            field_value = f"**Author:** {author_name}\n"
            if channel_name:
                field_value += f"**Channel:** {channel_name}\n"
            if time_str:
                field_value += f"**When:** {time_str}\n"
            field_value += f"**Content:** {content_preview}"
            
            embed.add_field(
                name=f"Source {i}",
                value=field_value,
                inline=False
            )
        
        # Calculate total pages for sources (10 per page)
        total_source_pages = (len(self.context_items) + 9) // 10
        
        if total_source_pages > 1:
            footer_text = f"Page {self.current_page + 1}/{total_source_pages} • Showing {start_idx + 1}-{end_idx} of {len(self.context_items)} sources"
        else:
            footer_text = f"Showing {len(self.context_items)} source(s)"
        
        embed.set_footer(text=footer_text)
        
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to use the buttons."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "These buttons are not for you! Use `/ask` to make your own query.",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_answer_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        """Go to next page."""
        if self.showing_sources:
            # For sources, calculate max pages based on 10 sources per page
            max_pages = (len(self.context_items) + 9) // 10
        else:
            max_pages = self.total_pages
        
        self.current_page = min(max_pages - 1, self.current_page + 1)
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_answer_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📊 Show Sources", style=discord.ButtonStyle.primary)
    async def sources_button(self, interaction: discord.Interaction, button: Button):
        """Toggle between answer and sources view."""
        self.showing_sources = not self.showing_sources
        self.current_page = 0  # Reset to first page when switching views
        self.update_buttons()
        
        if self.showing_sources:
            embed = self.create_sources_embed()
        else:
            embed = self.create_answer_embed()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="👍", style=discord.ButtonStyle.success)
    async def thumbs_up_button(self, interaction: discord.Interaction, button: Button):
        """Positive feedback."""
        if self.feedback_given is not None:
            await interaction.response.send_message(
                "You've already provided feedback for this answer.",
                ephemeral=True
            )
            return
        
        self.feedback_given = 'positive'
        self.update_buttons()
        
        # Log feedback
        logger.info(f"Positive feedback from {interaction.user} for query: '{self.query[:50]}...'")
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            "✅ Thanks for the positive feedback!",
            ephemeral=True
        )
    
    @discord.ui.button(emoji="👎", style=discord.ButtonStyle.danger)
    async def thumbs_down_button(self, interaction: discord.Interaction, button: Button):
        """Negative feedback."""
        if self.feedback_given is not None:
            await interaction.response.send_message(
                "You've already provided feedback for this answer.",
                ephemeral=True
            )
            return
        
        self.feedback_given = 'negative'
        self.update_buttons()
        
        # Log feedback
        logger.info(f"Negative feedback from {interaction.user} for query: '{self.query[:50]}...'")
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            "📝 Thanks for the feedback! We'll work on improving the answers.",
            ephemeral=True
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
