import logging

logger = logging.getLogger(__name__)


def assemble_context(graph_results: list[dict], vector_results: list[dict], intent: str) -> list[dict]:
    """
    Merge graph traversal results and vector search results.
    Deduplicate by message content, rank by relevance.
    Handles temporal context and cross-time discussion connections.
    Returns a unified list of context items ready for the answer generator.
    """
    seen_contents = set()
    unified = []

    # Graph results get priority — they are structurally relevant
    for item in graph_results:
        messages = item.get("messages", [])
        if isinstance(messages, list) and len(messages) > 0:
            for msg in messages:
                content = (msg.get("content") or "").strip()
                if content and content not in seen_contents:
                    seen_contents.add(content)
                    unified.append({
                        "source": "graph",
                        "content": content,
                        "author": msg.get("author", "Unknown"),
                        "channel": msg.get("channel", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "relevance": 1.0,
                    })
        else:
            # Flat record (relational, evolutionary, expert_finding, summarization, temporal_context, conversation_threads)
            content = (item.get("content") or item.get("text") or "").strip()
            if content and content not in seen_contents:
                seen_contents.add(content)
                
                # Build base context item
                context_item = {
                    "source": "graph",
                    "content": content,
                    "author": item.get("author", item.get("expert", "Unknown")),
                    "channel": item.get("channel", ""),
                    "timestamp": item.get("timestamp", item.get("last_seen", "")),
                    "relevance": 1.0,
                }
                
                # Add temporal context metadata if present
                if "related_discussions" in item:
                    context_item["temporal_context"] = {
                        "has_related_discussions": True,
                        "related_count": len(item["related_discussions"]),
                        "primary_entity": item.get("related_entity", ""),
                        "context_type": item.get("context_type", "primary")
                    }
                    
                    # Add related discussions as separate context items
                    for related in item["related_discussions"]:
                        related_content = (related.get("content") or "").strip()
                        if related_content and related_content not in seen_contents:
                            seen_contents.add(related_content)
                            unified.append({
                                "source": "graph",
                                "content": related_content,
                                "author": related.get("author", "Unknown"),
                                "channel": related.get("channel", ""),
                                "timestamp": related.get("timestamp", ""),
                                "relevance": 0.8,  # Slightly lower relevance for related discussions
                                "temporal_context": {
                                    "context_type": "related_discussion",
                                    "time_gap_days": related.get("time_gap", 0),
                                    "related_to_entity": item.get("related_entity", "")
                                }
                            })
                
                # Add conversation thread context if present
                if "thread_context" in item:
                    context_item["conversation_thread"] = {
                        "has_thread_context": True,
                        "thread_messages": len(item["thread_context"]),
                        "primary_entity": item.get("primary_entity", "")
                    }
                    
                    # Add thread messages as context
                    for thread_msg in item["thread_context"]:
                        thread_content = (thread_msg.get("content") or "").strip()
                        if thread_content and thread_content not in seen_contents:
                            seen_contents.add(thread_content)
                            unified.append({
                                "source": "graph",
                                "content": thread_content,
                                "author": thread_msg.get("author", "Unknown"),
                                "channel": item.get("channel", ""),
                                "timestamp": thread_msg.get("timestamp", ""),
                                "relevance": 0.9,  # High relevance for thread context
                                "conversation_thread": {
                                    "context_type": "thread_message",
                                    "time_gap_hours": thread_msg.get("time_gap_hours", 0),
                                    "mentioned_entities": thread_msg.get("mentioned_entities", [])
                                }
                            })
                
                # Add extra metadata for other fields
                extra_fields = {k: v for k, v in item.items() 
                              if k not in ("content", "author", "channel", "timestamp", "related_discussions", "thread_context")}
                if extra_fields:
                    context_item["extra"] = extra_fields
                
                unified.append(context_item)

    # Vector results fill in semantic gaps
    for msg in vector_results:
        content = (msg.get("content") or "").strip()
        if content and content not in seen_contents:
            seen_contents.add(content)
            
            # Get channel info from channel_id since no join relationship exists
            channel_info = msg.get("channel_id", "")
            if isinstance(channel_info, (int, float)):
                channel_info = f"#{channel_info}"
            
            unified.append({
                "source": "vector",
                "content": content,
                "author": msg.get("author_name", "Unknown"),
                "channel": str(channel_info),
                "timestamp": str(msg.get("created_at", "")),
                "relevance": float(msg.get("similarity", 0.5)),
            })

    # Sort: graph results first, then by timestamp descending (most recent first)
    def sort_key(x):
        source_priority = 0 if x["source"] == "graph" else 1
        # Parse timestamp for sorting, default to very old date if missing
        ts = x.get("timestamp", "")
        try:
            from datetime import datetime
            if isinstance(ts, str):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = ts
            timestamp_value = dt.timestamp()
        except:
            timestamp_value = 0
        return (source_priority, -timestamp_value)  # Negative for descending order
    
    unified.sort(key=sort_key)

    logger.info(f"Context assembled: {len(unified)} items ({sum(1 for x in unified if x['source']=='graph')} graph, {sum(1 for x in unified if x['source']=='vector')} vector)")
    return unified[:30]  # Cap at 30 context items to stay within token limits


def format_context_for_prompt(context_items: list[dict]) -> str:
    """Format assembled context into a readable string for the answer generator."""
    lines = []
    for i, item in enumerate(context_items, 1):
        ts = item.get("timestamp", "")
        author = item.get("author", "Unknown")
        channel = item.get("channel", "")
        content = item.get("content", "")
        source_tag = "[graph]" if item["source"] == "graph" else "[search]"
        channel_str = f"#{channel}" if channel else ""
        lines.append(f"{i}. {source_tag} [{ts}] {channel_str} {author}: {content}")

        # Include extra structural info for graph results (e.g. expert relationships)
        extra = item.get("extra", {})
        if extra:
            extra_str = ", ".join(f"{k}={v}" for k, v in extra.items() if v)
            if extra_str:
                lines.append(f"   → {extra_str}")

    return "\n".join(lines)
