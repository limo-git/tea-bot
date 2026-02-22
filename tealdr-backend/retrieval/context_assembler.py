import logging

logger = logging.getLogger(__name__)


def assemble_context(graph_results: list[dict], vector_results: list[dict], intent: str) -> list[dict]:
    """
    Merge graph traversal results and vector search results.
    Deduplicate by message content, rank by relevance.
    Returns a unified list of context items ready for the answer generator.
    """
    seen_contents = set()
    unified = []

    # Graph results get priority — they are structurally relevant
    for item in graph_results:
        messages = item.get("messages", [])
        if isinstance(messages, list):
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
            # Flat record (relational, evolutionary, expert_finding, summarization)
            content = (item.get("content") or item.get("text") or "").strip()
            if content and content not in seen_contents:
                seen_contents.add(content)
                unified.append({
                    "source": "graph",
                    "content": content,
                    "author": item.get("author", item.get("expert", "Unknown")),
                    "channel": item.get("channel", ""),
                    "timestamp": item.get("timestamp", item.get("last_seen", "")),
                    "relevance": 1.0,
                    "extra": {k: v for k, v in item.items() if k not in ("content", "author", "channel", "timestamp")},
                })

    # Vector results fill in semantic gaps
    for msg in vector_results:
        content = (msg.get("content") or "").strip()
        if content and content not in seen_contents:
            seen_contents.add(content)
            unified.append({
                "source": "vector",
                "content": content,
                "author": msg.get("author_name", "Unknown"),
                "channel": str(msg.get("channel_id", "")),
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
