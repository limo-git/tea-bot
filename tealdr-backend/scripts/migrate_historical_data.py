"""
Script to extract and process historical messages from the last 2 weeks
for Graph RAG migration.

Usage:
    python scripts/migrate_historical_data.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import supabase_client
from db.neo4j import get_driver, close_driver
from graph.schema import setup_schema
from ingestion.chunker import group_messages_into_windows, process_chunk
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_messages_from_supabase(server_id: int, since_days: int = 21):
    """Fetch all messages from a server in the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    
    logger.info(f"Fetching messages from server {server_id} since {cutoff}")
    
    # Fetch in batches to avoid memory issues
    all_messages = []
    offset = 0
    batch_size = 500
    
    while True:
        response = supabase_client.client.table("messages").select("*").eq(
            "server_id", server_id
        ).gte("created_at", cutoff.isoformat()).order(
            "created_at", desc=False
        ).range(offset, offset + batch_size - 1).execute()
        
        if not response.data:
            break
        
        all_messages.extend(response.data)
        logger.info(f"Fetched {len(response.data)} messages (total: {len(all_messages)})")
        
        if len(response.data) < batch_size:
            break
        
        offset += batch_size
    
    return all_messages


async def migrate_server(server_id: int, since_days: int = 14):
    """Migrate historical data for a single server."""
    logger.info(f"Starting migration for server {server_id}")
    
    # Fetch messages
    messages = fetch_messages_from_supabase(server_id, since_days)
    
    if not messages:
        logger.warning(f"No messages found for server {server_id}")
        return
    
    logger.info(f"Processing {len(messages)} messages from server {server_id}")
    
    # Group into chunks
    chunks = group_messages_into_windows(messages)
    logger.info(f"Grouped into {len(chunks)} chunks")
    
    # Process each chunk
    processed = 0
    failed = 0
    
    for i, chunk in enumerate(chunks, 1):
        try:
            await process_chunk(chunk)
            processed += 1
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(chunks)} chunks processed")
        except Exception as e:
            logger.error(f"Failed to process chunk {i}: {e}")
            failed += 1
    
    logger.info(
        f"Migration complete for server {server_id}: "
        f"{processed} chunks processed, {failed} failed"
    )


async def main():
    """Main migration script."""
    logger.info("=" * 60)
    logger.info("Historical Data Migration Script")
    logger.info("=" * 60)
    
    # Get list of servers from environment or prompt
    print("\nEnter server IDs to migrate (comma-separated):")
    print("Example: 1131555356418523180,1099297370212159500")
    server_input = input("> ").strip()
    
    if not server_input:
        logger.error("No server IDs provided")
        return
    
    try:
        server_ids = [int(sid.strip()) for sid in server_input.split(",")]
    except ValueError:
        logger.error("Invalid server ID format")
        return
    
    # Confirm
    print(f"\nWill migrate data from {len(server_ids)} server(s) for the last 14 days.")
    print("This may take several minutes depending on message volume.")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != "y":
        logger.info("Migration cancelled")
        return
    
    # Initialize Neo4j
    try:
        await setup_schema()
        logger.info("Neo4j schema initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j: {e}")
        return
    
    # Migrate each server
    start_time = datetime.now()
    
    for server_id in server_ids:
        try:
            await migrate_server(server_id, since_days=14)
        except Exception as e:
            logger.error(f"Failed to migrate server {server_id}: {e}")
    
    # Cleanup
    await close_driver()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info(f"Migration complete in {elapsed:.1f} seconds")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
