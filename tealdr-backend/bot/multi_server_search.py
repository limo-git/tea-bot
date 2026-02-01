"""
Multi-server search functionality for DM commands
"""
import discord
from typing import List
from utils.logger import get_logger
from ai.embeddings import generate_query_embedding
from database.queries import search_with_context
from ai.gemini_client import gemini_client
from ai.prompts import get_prompt_for_query
from utils.embed_builder import embed_builder
from utils.pagination import PaginationView

logger = get_logger(__name__)

async def multi_server_ask(
    interaction: discord.Interaction,
    query: str,
    guilds: List[discord.Guild],
    from_date: str = None,
    to_date: str = None,
    min_length: int = None
) -> None:
    """
    Perform an /ask search across multiple servers and aggregate results.
    """
    try:
        # Generate query embedding once
        query_embedding = await generate_query_embedding(query)
        if not query_embedding:
            error_embed = embed_builder.create_error_embed(
                "Failed to process your query. Please try again.",
                interaction.user
            )
            await interaction.followup.send(embed=error_embed)
            return
        
        # Parse date filters if provided
        time_range = None
        if from_date or to_date:
            try:
                from datetime import datetime
                start_time = datetime.fromisoformat(from_date) if from_date else None
                end_time = datetime.fromisoformat(to_date) if to_date else None
                
                if start_time or end_time:
                    time_range = (start_time, end_time)
            except ValueError:
                error_embed = embed_builder.create_error_embed(
                    "Invalid date format. Please use YYYY-MM-DD format.",
                    interaction.user
                )
                await interaction.followup.send(embed=error_embed)
                return
        
        # Search each server
        all_results = []
        server_names = []
        
        for guild in guilds:
            filters = {
                'time_range': time_range,
                'min_length': min_length,
                'limit': 10  # Limit per server to avoid overwhelming results
            }
            
            messages = await search_with_context(
                query_embedding=query_embedding,
                server_id=guild.id,
                filters=filters
            )
            
            if messages:
                # Tag each message with server name
                for msg in messages:
                    msg['_server_name'] = guild.name
                    msg['_server_id'] = guild.id
                
                all_results.extend(messages)
                server_names.append(guild.name)
        
        if not all_results:
            no_results_embed = embed_builder.create_no_results_embed(query, interaction.user)
            no_results_embed.add_field(
                name="🌐 Servers Searched",
                value=f"Searched {len(guilds)} server(s)",
                inline=False
            )
            await interaction.followup.send(embed=no_results_embed)
            return
        
        logger.info(f"Found {len(all_results)} total messages across {len(server_names)} servers")
        
        # Sort by relevance (assuming messages come sorted from each server)
        # Take top results across all servers
        top_results = all_results[:20]
        
        # Generate AI response
        requester_name = interaction.user.display_name
        
        prompt = get_prompt_for_query(
            query=query,
            messages=top_results,
            user_name="users",
            requester_name=requester_name,
            persona="You are a helpful Discord assistant searching across multiple servers. When referencing messages, mention which server they're from."
        )
        
        response = await gemini_client.generate_response(prompt)
        
        # Create embeds with multi-server indicator
        embeds = embed_builder.create_paginated_embeds(
            response=response,
            query=query,
            user=interaction.user,
            base_color=discord.Color.purple()  # Different color for multi-server
        )
        
        # Add multi-server info to first embed
        if embeds:
            embeds[0].title = "🌐 Multi-Server Search Results"
            embeds[0].add_field(
                name="📊 Sources",
                value=f"{len(all_results)} messages from {len(server_names)} server(s)",
                inline=True
            )
            embeds[0].add_field(
                name="🏢 Servers",
                value=", ".join(server_names[:5]) + (f" (+{len(server_names)-5} more)" if len(server_names) > 5 else ""),
                inline=True
            )
        
        # Send with pagination if multiple embeds
        if len(embeds) > 1:
            view = PaginationView(embeds, interaction.user)
            sent_message = await interaction.followup.send(embed=embeds[0], view=view)
            view.message = sent_message
        else:
            sent_message = await interaction.followup.send(embed=embeds[0])
        
        # Add reaction options for feedback
        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        
        logger.info(f"Sent multi-server response to {interaction.user}")
    
    except Exception as e:
        logger.error(f"Error in multi-server ask: {e}")
        error_embed = embed_builder.create_error_embed(
            "An error occurred while searching across servers.",
            interaction.user
        )
        await interaction.followup.send(embed=error_embed)
