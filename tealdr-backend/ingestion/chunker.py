import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from database.supabase_client import supabase_client
from extraction.entity_extractor import extract_entities_from_chunk, format_messages_for_extraction
from graph.builder import build_graph_from_extraction, upsert_chunk
from db.neo4j import get_driver
from config import Config
import uuid

logger = logging.getLogger(__name__)


def group_messages_into_windows(messages: list[dict], window_minutes: int = None) -> list[list[dict]]:
    """
    Group messages into time windows of `window_minutes` per channel.
    Returns a list of message groups (each group = one chunk).
    """
    if window_minutes is None:
        window_minutes = Config.CHUNK_WINDOW_MINUTES

    # Group by channel first
    by_channel: dict[int, list[dict]] = defaultdict(list)
    for msg in messages:
        by_channel[msg["channel_id"]].append(msg)

    chunks = []
    for channel_id, channel_msgs in by_channel.items():
        # Sort by time
        channel_msgs.sort(key=lambda m: str(m.get("created_at", "")))

        if not channel_msgs:
            continue

        window_start = None
        current_window = []

        for msg in channel_msgs:
            ts_raw = msg.get("created_at")
            if ts_raw is None:
                continue

            if isinstance(ts_raw, str):
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except ValueError:
                    continue
            else:
                ts = ts_raw

            if window_start is None:
                window_start = ts
                current_window = [msg]
            elif (ts - window_start).total_seconds() <= window_minutes * 60:
                current_window.append(msg)
            else:
                if current_window:
                    chunks.append(current_window)
                window_start = ts
                current_window = [msg]

        if current_window:
            chunks.append(current_window)

    logger.info(f"Grouped {len(messages)} messages into {len(chunks)} chunks")
    return chunks


async def process_chunk(messages: list[dict]):
    """
    Process a single chunk of messages:
    1. Format for extraction
    2. Call Claude for entity extraction
    3. Build graph from extraction
    4. Upsert chunk node into Neo4j
    """
    if not messages:
        return

    chunk_text = format_messages_for_extraction(messages)
    first_msg = messages[0]
    last_msg = messages[-1]

    chunk_metadata = {
        "channel_id": first_msg.get("channel_id"),
        "channel_name": first_msg.get("channel_name", str(first_msg.get("channel_id", ""))),
        "guild_id": first_msg.get("server_id"),
        "start_time": str(first_msg.get("created_at", "")),
        "end_time": str(last_msg.get("created_at", "")),
    }

    try:
        extraction = await extract_entities_from_chunk(chunk_text, chunk_metadata)
        await build_graph_from_extraction(extraction, messages)

        # Upsert chunk node in Neo4j
        driver = await get_driver()
        async with driver.session() as session:
            await upsert_chunk(
                session=session,
                chunk_id=str(uuid.uuid4()),
                text=chunk_text,
                channel_id=chunk_metadata["channel_id"],
                channel_name=chunk_metadata["channel_name"],
                guild_id=chunk_metadata["guild_id"],
                start_time=chunk_metadata["start_time"],
                end_time=chunk_metadata["end_time"],
                message_ids=[m["message_id"] for m in messages],
            )

        logger.info(f"Chunk processed: {len(messages)} messages, channel={chunk_metadata['channel_name']}")

    except Exception as e:
        logger.error(f"Failed to process chunk: {e}", exc_info=True)


async def run_chunker_for_server(server_id: int, since_minutes: int = None):
    """
    Fetch recent messages for a server, group into windows, and process each chunk.
    Called by the background chunker job.
    """
    if since_minutes is None:
        since_minutes = Config.CHUNK_WINDOW_MINUTES

    from datetime import datetime, timezone, timedelta
    start_time = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)

    messages = await supabase_client.get_messages_by_timerange(
        server_id=server_id,
        start_time=start_time,
        limit=500,
    )

    if not messages:
        logger.debug(f"No new messages to chunk for server {server_id}")
        return

    chunks = group_messages_into_windows(messages)
    for chunk in chunks:
        await process_chunk(chunk)

    logger.info(f"Chunker complete for server {server_id}: {len(chunks)} chunks processed")
