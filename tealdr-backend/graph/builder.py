import logging
from datetime import datetime, timezone
from db.neo4j import get_driver
from config import Config

logger = logging.getLogger(__name__)


async def upsert_author(session, discord_id: int, username: str):
    await session.run(
        """
        MERGE (a:Author {discord_id: $discord_id})
        SET a.username = $username, a.last_seen = $now
        """,
        discord_id=discord_id,
        username=username,
        now=datetime.now(timezone.utc).isoformat(),
    )


async def upsert_server(session, server_id: int, server_name: str = None):
    await session.run(
        """
        MERGE (s:Server {id: $server_id})
        SET s.name = COALESCE($server_name, s.name)
        """,
        server_id=server_id,
        server_name=server_name,
    )


async def upsert_channel(session, channel_id: int, channel_name: str, server_id: int = None):
    if server_id:
        await session.run(
            """
            MERGE (c:Channel {id: $channel_id})
            SET c.name = $channel_name
            WITH c
            MATCH (s:Server {id: $server_id})
            MERGE (c)-[:IN_SERVER]->(s)
            """,
            channel_id=channel_id,
            channel_name=channel_name,
            server_id=server_id,
        )
    else:
        await session.run(
            """
            MERGE (c:Channel {id: $channel_id})
            SET c.name = $channel_name
            """,
            channel_id=channel_id,
            channel_name=channel_name,
        )


async def upsert_message(session, message: dict):
    await session.run(
        """
        MERGE (m:Message {id: $id})
        SET m.content   = $content,
            m.timestamp = $timestamp,
            m.channel   = $channel,
            m.author    = $author
        WITH m
        MATCH (a:Author  {discord_id: $author_id})
        MATCH (c:Channel {id: $channel_id})
        MERGE (a)-[:SENT]->(m)
        MERGE (m)-[:IN_CHANNEL]->(c)
        """,
        id=message["message_id"],
        content=message["content"],
        timestamp=str(message.get("created_at", "")),
        channel=message.get("channel_name", ""),
        author=message.get("author_name", ""),
        author_id=message["author_id"],
        channel_id=message["channel_id"],
    )


async def upsert_entity(session, name: str, entity_type: str, description: str = ""):
    now = datetime.now(timezone.utc).isoformat()
    await session.run(
        """
        MERGE (e:Entity {name: $name, type: $type})
        ON CREATE SET e.first_seen = $now, e.last_seen = $now, e.description = $description, e.mention_count = 1
        ON MATCH  SET e.last_seen  = $now, e.mention_count = e.mention_count + 1
        """,
        name=name,
        type=entity_type,
        description=description,
        now=now,
    )


async def upsert_relationship(session, from_name: str, from_type: str, to_name: str, to_type: str, rel_type: str):
    await session.run(
        f"""
        MATCH (a:Entity {{name: $from_name, type: $from_type}})
        MATCH (b:Entity {{name: $to_name,   type: $to_type}})
        MERGE (a)-[r:{rel_type}]->(b)
        ON CREATE SET r.weight = 1,    r.last_seen = $now
        ON MATCH  SET r.weight = r.weight + 1, r.last_seen = $now
        """,
        from_name=from_name,
        from_type=from_type,
        to_name=to_name,
        to_type=to_type,
        now=datetime.now(timezone.utc).isoformat(),
    )


async def link_message_to_entities(session, message_id: int, entities: list[dict]):
    for entity in entities:
        await session.run(
            """
            MATCH (m:Message {id: $message_id})
            MATCH (e:Entity  {name: $name, type: $type})
            MERGE (m)-[:MENTIONS]->(e)
            """,
            message_id=message_id,
            name=entity["name"],
            type=entity["type"],
        )


async def upsert_chunk(session, chunk_id: str, text: str, channel_id: int, channel_name: str,
                       guild_id: int, start_time: str, end_time: str, message_ids: list[int]):
    await session.run(
        """
        MERGE (ch:Chunk {id: $chunk_id})
        SET ch.text         = $text,
            ch.channel_id   = $channel_id,
            ch.channel_name = $channel_name,
            ch.guild_id     = $guild_id,
            ch.start_time   = $start_time,
            ch.end_time     = $end_time
        """,
        chunk_id=chunk_id,
        text=text,
        channel_id=channel_id,
        channel_name=channel_name,
        guild_id=guild_id,
        start_time=start_time,
        end_time=end_time,
    )
    for msg_id in message_ids:
        await session.run(
            """
            MATCH (ch:Chunk   {id: $chunk_id})
            MATCH (m:Message  {id: $msg_id})
            MERGE (ch)-[:CONTAINS]->(m)
            """,
            chunk_id=chunk_id,
            msg_id=msg_id,
        )


async def infer_expertise(session, author_id: int, threshold: int = None):
    """
    Create EXPERT_IN relationships when an author mentions an entity >= threshold times.
    
    P2 Enhancement: Adds confidence score based on:
    - Mention count (higher = more confident)
    - Recency of mentions (recent = more confident)
    - Entity type (technical topics = higher weight)
    """
    if threshold is None:
        threshold = Config.EXPERT_IN_THRESHOLD
    
    await session.run(
        """
        MATCH (a:Author {discord_id: $author_id})-[:SENT]->(m:Message)-[:MENTIONS]->(e:Entity)
        WITH a, e, count(m) AS mentions, max(m.timestamp) AS last_mention
        WHERE mentions >= $threshold
        
        // Calculate confidence score (0.0 to 1.0)
        // Base score from mention count (normalized)
        WITH a, e, mentions, last_mention,
             CASE 
                 WHEN mentions >= 20 THEN 0.5
                 WHEN mentions >= 10 THEN 0.4
                 WHEN mentions >= 5 THEN 0.3
                 ELSE 0.2
             END AS base_score
        
        // Bonus for technical entities
        WITH a, e, mentions, last_mention, base_score,
             CASE 
                 WHEN e.type IN ['technology', 'project'] THEN 0.2
                 WHEN e.type IN ['topic', 'decision'] THEN 0.1
                 ELSE 0.0
             END AS type_bonus
        
        // Recency bonus (last 30 days)
        WITH a, e, mentions, last_mention, base_score, type_bonus,
             CASE 
                 WHEN duration.between(datetime(last_mention), datetime()).days <= 7 THEN 0.3
                 WHEN duration.between(datetime(last_mention), datetime()).days <= 30 THEN 0.2
                 WHEN duration.between(datetime(last_mention), datetime()).days <= 90 THEN 0.1
                 ELSE 0.0
             END AS recency_bonus
        
        WITH a, e, mentions, last_mention,
             base_score + type_bonus + recency_bonus AS confidence_score
        
        MERGE (a)-[r:EXPERT_IN]->(e)
        SET r.mention_count = mentions,
            r.confidence_score = confidence_score,
            r.last_updated = datetime()
        """,
        author_id=author_id,
        threshold=threshold,
    )


async def get_experts_for_entity(session, entity_name: str, entity_type: str, min_confidence: float = 0.5):
    """
    Get experts for a specific entity, ordered by confidence score.
    
    Args:
        session: Neo4j session
        entity_name: Name of the entity
        entity_type: Type of the entity
        min_confidence: Minimum confidence score (default 0.5)
        
    Returns:
        List of expert dicts with author info and confidence scores
    """
    result = await session.run(
        """
        MATCH (a:Author)-[r:EXPERT_IN]->(e:Entity {name: $name, type: $type})
        WHERE r.confidence_score >= $min_confidence
        RETURN a.discord_id AS discord_id,
               a.username AS username,
               r.mention_count AS mention_count,
               r.confidence_score AS confidence_score,
               r.last_updated AS last_updated
        ORDER BY r.confidence_score DESC
        LIMIT 10
        """,
        name=entity_name,
        type=entity_type,
        min_confidence=min_confidence,
    )
    
    experts = []
    async for record in result:
        experts.append({
            "discord_id": record["discord_id"],
            "username": record["username"],
            "mention_count": record["mention_count"],
            "confidence_score": record["confidence_score"],
            "last_updated": record["last_updated"],
        })
    
    return experts


async def build_graph_from_extraction(extraction_result: dict, messages: list[dict]):
    """
    Top-level function: takes Claude extraction output and a list of raw messages,
    upserts everything into Neo4j.
    """
    driver = await get_driver()
    entities = extraction_result.get("entities", [])
    relationships = extraction_result.get("relationships", [])
    chunk_meta = extraction_result.get("chunk_metadata", {})

    async with driver.session() as session:
        # Upsert server, authors, and channels from raw messages
        author_ids_seen = set()
        for msg in messages:
            server_id = msg.get("server_id")
            if server_id:
                await upsert_server(session, server_id)
            await upsert_channel(session, msg["channel_id"], msg.get("channel_name", ""), server_id)
            await upsert_author(session, msg["author_id"], msg.get("author_name", ""))
            await upsert_message(session, msg)
            author_ids_seen.add(msg["author_id"])

        # Upsert extracted entities
        for entity in entities:
            await upsert_entity(session, entity["name"], entity["type"], entity.get("description", ""))

        # Upsert extracted relationships
        for rel in relationships:
            try:
                await upsert_relationship(
                    session,
                    rel["from_entity"], rel["from_type"],
                    rel["to_entity"],   rel["to_type"],
                    rel["relationship"],
                )
            except Exception as e:
                logger.warning(f"Skipping relationship {rel}: {e}")

        # Link messages to entities
        for msg in messages:
            await link_message_to_entities(session, msg["message_id"], entities)

        # Infer expertise for all authors seen in this batch
        for author_id in author_ids_seen:
            await infer_expertise(session, author_id)

    logger.info(
        f"Graph updated: {len(entities)} entities, {len(relationships)} relationships, "
        f"{len(messages)} messages (channel={chunk_meta.get('channel_name')})"
    )
