import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _generate_temporal_context_info(pipeline_result: dict, context_items: List[dict]) -> str:
    """
    Generate temporal context information to help the LLM understand cross-time connections.
    This implements the user's requirement to connect discussions across different time periods.
    """
    
    # Check if we have temporal connections
    temporal_connections = pipeline_result.get("temporal_connections", 0)
    conversation_threads = pipeline_result.get("conversation_threads", 0)
    
    if temporal_connections == 0 and conversation_threads == 0:
        return ""
    
    info_parts = []
    
    # Add temporal context summary
    if temporal_connections > 0:
        info_parts.append(f"**Temporal Context**: Found {temporal_connections} related discussions across different time periods.")
    
    if conversation_threads > 0:
        info_parts.append(f"**Conversation Threads**: Found {conversation_threads} conversation sequences.")
    
    # Analyze temporal patterns in context items
    temporal_items = []
    thread_items = []
    
    for item in context_items:
        if item.get("temporal_context"):
            temporal_items.append(item)
        if item.get("conversation_thread"):
            thread_items.append(item)
    
    # Add temporal relationship details
    if temporal_items:
        info_parts.append("\n**Cross-Time Connections**:")
        
        # Group by time gaps
        time_gaps = {}
        for item in temporal_items:
            tc = item.get("temporal_context", {})
            gap = tc.get("time_gap_days", 0)
            
            if gap > 0:
                gap_key = f"{gap} days ago"
                if gap_key not in time_gaps:
                    time_gaps[gap_key] = []
                time_gaps[gap_key].append({
                    "author": item.get("author_name") or item.get("author", "Unknown"),
                    "content_preview": item.get("content", "")[:50] + "...",
                    "entity": tc.get("related_to_entity", "")
                })
        
        for gap, items in sorted(time_gaps.items()):
            info_parts.append(f"- {gap}: {len(items)} related messages")
    
    # Add conversation thread details
    if thread_items:
        info_parts.append("\n**Conversation Flow**:")
        
        # Group by time proximity
        recent_threads = [item for item in thread_items 
                         if item.get("conversation_thread", {}).get("time_gap_hours", 24) <= 24]
        
        if recent_threads:
            info_parts.append(f"- {len(recent_threads)} messages in recent conversation threads (within 24 hours)")
        
        # Show entities mentioned in threads
        thread_entities = set()
        for item in thread_items:
            ct = item.get("conversation_thread", {})
            entities = ct.get("mentioned_entities", [])
            thread_entities.update(entities)
        
        if thread_entities:
            info_parts.append(f"- Related entities in threads: {', '.join(list(thread_entities)[:5])}")
    
    if info_parts:
        return "\n".join(info_parts) + "\n"
    
    return ""


def format_context_for_prompt(context_items: List[dict]) -> str:
    """
    Format context with structured metadata for RAG best practices.
    Each chunk includes visible metadata: source type, timestamp, author, channel.
    """
    if not context_items:
        return "No relevant context found."
    
    formatted_items = []
    
    for i, item in enumerate(context_items, 1):
        source = item.get("source", "unknown")
        content = item.get("content", "").strip()
        author = item.get("author_name") or item.get("author", "Unknown")
        channel = item.get("channel", "")
        timestamp = item.get("timestamp", "")
        
        # Format timestamp for provenance
        time_str = ""
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = timestamp
                time_str = dt.strftime("%Y-%m-%d %H:%M UTC")
            except:
                time_str = str(timestamp)[:16]
        
        # Structured metadata header - visible to model for provenance reasoning
        metadata_parts = [f"[Doc {i}"]
        
        if time_str:
            metadata_parts.append(f"| {time_str}")
        
        metadata_parts.append(f"| source: {source}")
        
        if author:
            metadata_parts.append(f"| author: {author}")
        
        if channel:
            metadata_parts.append(f"| channel: #{channel}")
        
        metadata_parts.append("]")
        
        metadata_header = " ".join(metadata_parts)
        
        # Add temporal context indicators if present
        temporal_indicators = []
        
        if item.get("temporal_context"):
            tc = item["temporal_context"]
            context_type = tc.get("context_type", "")
            
            if context_type == "related_discussion":
                gap_days = tc.get("time_gap_days", 0)
                if gap_days > 0:
                    temporal_indicators.append(f"[RELATED: {gap_days}d ago]")
                entity = tc.get("related_to_entity", "")
                if entity:
                    temporal_indicators.append(f"[ENTITY: {entity}]")
        
        if item.get("conversation_thread"):
            ct = item["conversation_thread"]
            context_type = ct.get("context_type", "")
            
            if context_type == "thread_message":
                gap_hours = ct.get("time_gap_hours", 0)
                if gap_hours > 0:
                    temporal_indicators.append(f"[THREAD: {gap_hours}h gap]")
                entities = ct.get("mentioned_entities", [])
                if entities:
                    temporal_indicators.append(f"[MENTIONS: {', '.join(entities[:2])}]")
        
        # Combine metadata header with temporal indicators and content
        formatted_item = metadata_header
        
        if temporal_indicators:
            formatted_item += f" {' '.join(temporal_indicators)}"
        
        formatted_item += f"\n{content}\n"
        
        formatted_items.append(formatted_item)
    
    return "\n---\n".join(formatted_items)
