"""
Parameterized Cypher queries for each query intent type.
Never use string interpolation — all values go through parameters.
"""

# ── lookup ────────────────────────────────────────────────────────────────────
LOOKUP_QUERY = """
MATCH (e:Entity {name: $entity_name})
OPTIONAL MATCH (e)<-[:MENTIONS]-(m:Message)-[:IN_CHANNEL]->(c:Channel)
OPTIONAL MATCH (m)<-[:SENT]-(a:Author)
RETURN e.name        AS entity,
       e.type        AS entity_type,
       e.description AS description,
       collect({
           content:   m.content,
           timestamp: m.timestamp,
           channel:   c.name,
           author:    a.username
       })[..10]       AS messages
ORDER BY e.mention_count DESC
LIMIT 1
"""

# ── relational ────────────────────────────────────────────────────────────────
RELATIONAL_QUERY = """
MATCH path = shortestPath(
    (a:Entity {name: $entity_a})-[*1..5]-(b:Entity {name: $entity_b})
)
RETURN [node IN nodes(path) | {name: node.name, type: node.type}] AS nodes,
       [rel  IN relationships(path) | type(rel)]                   AS relationships,
       length(path)                                                 AS hops
LIMIT 5
"""

# ── evolutionary ──────────────────────────────────────────────────────────────
EVOLUTIONARY_QUERY = """
MATCH (e:Entity {name: $entity_name})-[r]->(related:Entity)
RETURN e.name          AS entity,
       type(r)         AS relationship,
       related.name    AS related_entity,
       related.type    AS related_type,
       r.last_seen     AS last_seen,
       r.weight        AS weight
ORDER BY r.last_seen ASC
LIMIT 30
"""

# ── expert_finding ────────────────────────────────────────────────────────────
EXPERT_FINDING_QUERY = """
MATCH (a:Author)-[r:EXPERT_IN]->(e:Entity {name: $entity_name})
RETURN a.username       AS expert,
       a.discord_id     AS discord_id,
       r.mention_count  AS mention_count,
       e.name           AS topic
ORDER BY r.mention_count DESC
LIMIT 10
"""

# ── summarization ─────────────────────────────────────────────────────────────
SUMMARIZATION_QUERY = """
// Try to find by author first
OPTIONAL MATCH (author:Author)
WHERE toLower(author.username) CONTAINS toLower($entity_name)
WITH author
OPTIONAL MATCH (author)-[:SENT]->(m:Message)-[:IN_CHANNEL]->(c:Channel)
WITH collect({content: m.content, timestamp: m.timestamp, channel: c.name, author: author.username}) AS author_messages

// If no author found, search by entity mentions
OPTIONAL MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
WITH author_messages, e
OPTIONAL MATCH (e)<-[:MENTIONS]-(m2:Message)-[:IN_CHANNEL]->(c2:Channel)
OPTIONAL MATCH (m2)<-[:SENT]-(a2:Author)
WITH author_messages + collect({content: m2.content, timestamp: m2.timestamp, channel: c2.name, author: a2.username}) AS all_messages

UNWIND all_messages AS msg
WITH msg WHERE msg.content IS NOT NULL
RETURN msg.content AS content,
       msg.timestamp AS timestamp,
       msg.channel AS channel,
       msg.author AS author
ORDER BY msg.timestamp DESC
LIMIT 50
"""

# ── entity search (fuzzy name match) ─────────────────────────────────────────
ENTITY_SEARCH_QUERY = """
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS toLower($search_term)
RETURN e.name        AS name,
       e.type        AS type,
       e.description AS description,
       e.mention_count AS mention_count
ORDER BY e.mention_count DESC
LIMIT 10
"""

# ── related entities ──────────────────────────────────────────────────────────
RELATED_ENTITIES_QUERY = """
MATCH (e:Entity {name: $entity_name})-[r:RELATED_TO|SUGGESTED|FIXED_BY|DEPENDS_ON|DISCUSSED|WORKS_ON*1..2]-(related:Entity)
RETURN DISTINCT related.name AS name,
                related.type AS type,
                related.description AS description
LIMIT 15
"""

# ── decay: reduce weights of stale relationships ──────────────────────────────
DECAY_QUERY = """
MATCH ()-[r]-()
WHERE r.last_seen IS NOT NULL
  AND r.weight IS NOT NULL
  AND r.last_seen < $cutoff_date
  AND r.weight > 1
SET r.weight = r.weight - 1
RETURN count(r) AS decayed_count
"""

# ── daily summary: all chunks for a channel on a given day ───────────────────
DAILY_CHUNKS_QUERY = """
MATCH (ch:Chunk)
WHERE ch.channel_id IS NOT NULL
  AND ch.start_time IS NOT NULL
  AND ch.end_time   IS NOT NULL
  AND ch.channel_id = $channel_id
  AND ch.start_time >= $day_start
  AND ch.end_time   <= $day_end
RETURN ch.id        AS chunk_id,
       ch.text      AS text,
       ch.start_time AS start_time,
       ch.end_time   AS end_time
ORDER BY ch.start_time ASC
"""


async def run_intent_query(session, intent: str, params: dict) -> list[dict]:
    """
    Dispatch to the correct Cypher query based on intent classification.
    Returns a list of record dicts.
    """
    query_map = {
        "lookup":        LOOKUP_QUERY,
        "relational":    RELATIONAL_QUERY,
        "evolutionary":  EVOLUTIONARY_QUERY,
        "expert_finding": EXPERT_FINDING_QUERY,
        "summarization": SUMMARIZATION_QUERY,
    }

    cypher = query_map.get(intent)
    if not cypher:
        return []

    result = await session.run(cypher, **params)
    records = [dict(record) async for record in result]
    return records
