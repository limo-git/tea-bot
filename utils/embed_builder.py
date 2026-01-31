import discord
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class EmbedBuilder:
    """Helper class for building rich Discord embeds."""
    
    @staticmethod
    def create_search_result_embed(query, response, user, message_count=0, has_context=False):
        """Create an embed for /ask command results."""
        embed = discord.Embed(
            title="🔍 Search Results",
            description=response,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Add query info
        embed.add_field(
            name="📝 Your Query",
            value=f"`{query}`",
            inline=False
        )
        
        # Add context indicator
        if has_context:
            embed.add_field(
                name="💬 Context",
                value="Following up from previous conversation",
                inline=True
            )
        
        # Add message count
        if message_count > 0:
            embed.add_field(
                name="📊 Sources",
                value=f"{message_count} messages analyzed",
                inline=True
            )
        
        embed.set_footer(
            text=f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url
        )
        
        return embed
    
    @staticmethod
    def create_recap_embed(time_period, response, user, location="", message_count=0):
        """Create an embed for /recap command results."""
        embed = discord.Embed(
            title=f"📅 Recap{location}",
            description=response,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⏰ Time Period",
            value=time_period,
            inline=True
        )
        
        if message_count > 0:
            embed.add_field(
                name="💬 Messages",
                value=f"{message_count} analyzed",
                inline=True
            )
        
        embed.set_footer(
            text=f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url
        )
        
        return embed
    
    @staticmethod
    def create_error_embed(error_message, user):
        """Create an embed for error messages."""
        embed = discord.Embed(
            title="❌ Error",
            description=error_message,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(
            text=f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url
        )
        
        return embed
    
    @staticmethod
    def create_no_results_embed(query, user):
        """Create an embed when no results are found."""
        embed = discord.Embed(
            title="🔍 No Results Found",
            description="I couldn't find any messages matching your query.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Your Query",
            value=f"`{query}`",
            inline=False
        )
        
        embed.add_field(
            name="💡 Try:",
            value="• Using different keywords\n"
                  "• Expanding the time range\n"
                  "• Checking if the channel is indexed\n"
                  "• Using `/help` for search tips",
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url
        )
        
        return embed
    
    @staticmethod
    def create_message_list_embed(messages, title="Messages", user=None, page=1, total_pages=1):
        """Create an embed showing a list of messages."""
        embed = discord.Embed(
            title=title,
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        # Add messages
        for i, msg in enumerate(messages[:10], 1):  # Limit to 10 per page
            author = msg.get('author_name', 'Unknown')
            content = msg.get('content', '')[:100]  # Truncate
            timestamp = msg.get('created_at', '')
            
            embed.add_field(
                name=f"{i}. {author}",
                value=f"{content}...\n*{timestamp}*",
                inline=False
            )
        
        # Add pagination info
        if total_pages > 1:
            embed.set_footer(text=f"Page {page}/{total_pages}")
        elif user:
            embed.set_footer(
                text=f"Requested by {user.display_name}",
                icon_url=user.display_avatar.url
            )
        
        return embed
    
    @staticmethod
    def split_long_response(response, max_length=4000):
        """Split a long response into chunks that fit in embeds."""
        if len(response) <= max_length:
            return [response]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs
        paragraphs = response.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def create_paginated_embeds(response, query, user, base_color=discord.Color.blue()):
        """Create multiple embeds for paginated long responses."""
        chunks = EmbedBuilder.split_long_response(response)
        embeds = []
        
        for i, chunk in enumerate(chunks, 1):
            embed = discord.Embed(
                title=f"🔍 Search Results (Part {i}/{len(chunks)})" if len(chunks) > 1 else "🔍 Search Results",
                description=chunk,
                color=base_color,
                timestamp=datetime.utcnow()
            )
            
            if i == 1:  # Only add query on first page
                embed.add_field(
                    name="📝 Your Query",
                    value=f"`{query}`",
                    inline=False
                )
            
            embed.set_footer(
                text=f"Page {i}/{len(chunks)} • Requested by {user.display_name}",
                icon_url=user.display_avatar.url
            )
            
            embeds.append(embed)
        
        return embeds

embed_builder = EmbedBuilder()
