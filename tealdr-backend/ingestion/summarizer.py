"""
Hourly channel summarization job for pre-computing /recap summaries.
Runs every hour to summarize the previous hour's messages per channel.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from database.supabase_client import supabase_client
from ai.gemini_client import gemini_client
from config import Config

logger = logging.getLogger(__name__)

# Minimum thresholds for summarization to save compute and API calls
MIN_MESSAGES_FOR_SUMMARY = 5
MIN_CHARACTERS_FOR_SUMMARY = 150

# Summarization prompt for hourly channel summaries
HOURLY_SUMMARY_PROMPT = """You are summarizing Discord channel activity for the past hour.

Messages from {channel_name} ({start_time} to {end_time}):
{messages}

Create a concise summary (2-3 sentences) covering:
1. Main topics discussed
2. Key decisions or announcements
3. Notable activity or events

If there are fewer than 3 messages, just briefly describe what was discussed.
Keep it factual and concise.

Summary:"""

# Topic extraction prompt
TOPIC_EXTRACTION_PROMPT = """Extract 3-5 main topics from these Discord messages.

Messages:
{messages}

Return ONLY a comma-separated list of topics (e.g., "deployment, bug fixes, API design").
Topics:"""


async def summarize_channel_hour(server_id: int, channel_id: int, hour_bucket: datetime, 
                                 channel_name: str = None) -> Dict:
    """
    Summarize one hour of messages for a specific channel.
    
    Args:
        server_id: Discord server ID
        channel_id: Discord channel ID
        hour_bucket: Start of the hour to summarize
        channel_name: Optional channel name for better prompts
        
    Returns:
        Dict with summary data or None if failed
    """
    try:
        # Get messages for this hour
        next_hour = hour_bucket + timedelta(hours=1)
        messages = await supabase_client.get_messages_by_timerange(
            server_id=server_id,
            channel_id=channel_id,
            start_time=hour_bucket,
            end_time=next_hour,
            limit=500
        )
        
        if not messages:
            logger.info(f"Skipping summary for channel {channel_id} - 0 messages")
            return None
        
        # Format messages for summarization
        total_characters = 0
        message_texts = []
        active_users = set()
        for msg in messages:
            author = msg.get('author_name', 'Unknown')
            content = msg.get('content', '')
            total_characters += len(content)
            active_users.add(msg.get('author_id'))
            message_texts.append(f"{author}: {content}")
            
        # Check information density before calling LLM
        if len(messages) < MIN_MESSAGES_FOR_SUMMARY or total_characters < MIN_CHARACTERS_FOR_SUMMARY:
            logger.info(f"Skipping summary for channel {channel_id} - low information density ({len(messages)} msgs, {total_characters} chars)")
            
            summary_text = "Minimal chat activity."
            key_topics = ["casual chat"]
            
            await supabase_client.store_channel_summary(
                server_id=server_id,
                channel_id=channel_id,
                hour_bucket=hour_bucket,
                summary_text=summary_text,
                message_count=len(messages),
                key_topics=key_topics,
                active_users=list(active_users)
            )
            return {
                'server_id': server_id,
                'channel_id': channel_id,
                'hour_bucket': hour_bucket,
                'message_count': len(messages),
                'summary': summary_text,
                'topics': key_topics
            }
        
        messages_str = "\n".join(message_texts[:100])  # Limit to 100 messages for context
        
        # Generate summary
        prompt = HOURLY_SUMMARY_PROMPT.format(
            channel_name=channel_name or f"Channel {channel_id}",
            start_time=hour_bucket.strftime("%Y-%m-%d %H:%M"),
            end_time=next_hour.strftime("%Y-%m-%d %H:%M"),
            messages=messages_str
        )
        
        summary_text = await gemini_client.generate_response(
            prompt=prompt,
            use_cache=False,
            apply_anti_hallucination=False  # Not a RAG query
        )
        
        # Extract key topics
        topic_prompt = TOPIC_EXTRACTION_PROMPT.format(messages=messages_str[:2000])
        topics_response = await gemini_client.generate_response(
            prompt=topic_prompt,
            use_cache=False,
            apply_anti_hallucination=False
        )
        
        # Parse topics
        key_topics = [t.strip() for t in topics_response.split(',') if t.strip()][:5]
        
        # Store summary
        await supabase_client.store_channel_summary(
            server_id=server_id,
            channel_id=channel_id,
            hour_bucket=hour_bucket,
            summary_text=summary_text,
            message_count=len(messages),
            key_topics=key_topics,
            active_users=list(active_users)
        )
        
        logger.info(f"Summarized {len(messages)} messages for channel {channel_id} at {hour_bucket}")
        
        return {
            'server_id': server_id,
            'channel_id': channel_id,
            'hour_bucket': hour_bucket,
            'message_count': len(messages),
            'summary': summary_text,
            'topics': key_topics
        }
        
    except Exception as e:
        logger.error(f"Error summarizing channel {channel_id} at {hour_bucket}: {e}")
        return None


async def run_hourly_summarization(hours_ago: int = 1):
    """
    Run hourly summarization for all channels that need it.
    
    Args:
        hours_ago: How many hours back to summarize (default: 1 for last hour)
    """
    try:
        logger.info(f"Starting hourly summarization for {hours_ago} hour(s) ago")
        
        # Get channels that need summarization
        channels_needing_summary = await supabase_client.get_channels_needing_summary(hours_ago)
        
        if not channels_needing_summary:
            logger.info("No channels need summarization")
            return
        
        logger.info(f"Found {len(channels_needing_summary)} channels to summarize")
        
        # Calculate hour bucket
        now = datetime.utcnow()
        hour_bucket = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=hours_ago)
        
        # Summarize each channel
        successful = 0
        failed = 0
        
        for server_id, channel_id in channels_needing_summary:
            try:
                result = await summarize_channel_hour(
                    server_id=server_id,
                    channel_id=channel_id,
                    hour_bucket=hour_bucket
                )
                
                if result:
                    successful += 1
                else:
                    failed += 1
                
                # Rate limiting - don't overwhelm Gemini API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to summarize channel {channel_id}: {e}")
                failed += 1
        
        logger.info(f"Hourly summarization complete: {successful} successful, {failed} failed")
        
    except Exception as e:
        logger.error(f"Error in hourly summarization: {e}")


async def backfill_summaries(server_id: int, channel_id: int, days_back: int = 7):
    """
    Backfill summaries for a channel for the past N days.
    Useful for new channels or re-summarizing after improvements.
    
    Args:
        server_id: Discord server ID
        channel_id: Discord channel ID
        days_back: How many days to backfill
    """
    try:
        logger.info(f"Backfilling summaries for channel {channel_id} - {days_back} days")
        
        now = datetime.utcnow()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # Generate summaries for each hour going back
        for hours_ago in range(1, days_back * 24 + 1):
            hour_bucket = current_hour - timedelta(hours=hours_ago)
            
            # Check if summary already exists
            existing = await supabase_client.get_channel_summaries(
                server_id=server_id,
                channel_id=channel_id,
                start_time=hour_bucket,
                end_time=hour_bucket + timedelta(minutes=1),
                limit=1
            )
            
            if existing:
                logger.debug(f"Summary already exists for {hour_bucket}, skipping")
                continue
            
            # Summarize this hour
            result = await summarize_channel_hour(
                server_id=server_id,
                channel_id=channel_id,
                hour_bucket=hour_bucket
            )
            
            if result:
                logger.info(f"Backfilled summary for {hour_bucket}")
            
            # Rate limiting
            await asyncio.sleep(2)
        
        logger.info(f"Backfill complete for channel {channel_id}")
        
    except Exception as e:
        logger.error(f"Error in backfill: {e}")


if __name__ == "__main__":
    # For testing
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1 and sys.argv[1] == "backfill":
        # Backfill mode
        server_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        channel_id = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        days = int(sys.argv[4]) if len(sys.argv) > 4 else 7
        
        asyncio.run(backfill_summaries(server_id, channel_id, days))
    else:
        # Normal hourly summarization
        asyncio.run(run_hourly_summarization(hours_ago=1))
