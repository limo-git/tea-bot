"""
Parameterized Cypher queries for each query intent type.
Never use string interpolation — all values go through parameters.
"""

# ── lookup ────────────────────────────────────────────────────────────────────
LOOKUP_QUERY = """
// Fuzzy match entity name (case-insensitive, partial match)
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
   OR toLower($entity_name) CONTAINS toLower(e.name)
OPTIONAL MATCH (m)<-[:SENT]-(a:Author)
WHERE m.timestamp IS NOT NULL
WITH e, collect({
           content:   m.content,
           timestamp: m.timestamp,
           channel:   c.name,
           author:    a.username
       }) AS all_messages
WITH e, all_messages
ORDER BY e.mention_count DESC
LIMIT 5
RETURN e.name        AS entity,
       e.type        AS entity_type,
       e.description AS description,
       all_messages[..20] AS messages
"""

# ── relational ────────────────────────────────────────────────────────────────
RELATIONAL_QUERY = """
// Find relationship path between two entities within the same server
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(a:Entity {name: $entity_a})
MATCH (s)<-[:IN_SERVER]-(c2:Channel)<-[:IN_CHANNEL]-(m2:Message)-[:MENTIONS]->(b:Entity {name: $entity_b})
WITH DISTINCT a, b
MATCH path = shortestPath((a)-[*1..5]-(b))
RETURN [node IN nodes(path) | {name: node.name, type: node.type}] AS nodes,
       [rel  IN relationships(path) | type(rel)]                   AS relationships,
       length(path)                                                 AS hops
LIMIT 5
"""

# ── evolutionary ──────────────────────────────────────────────────────────────
EVOLUTIONARY_QUERY = """
// Find entity evolution within the same server
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity {name: $entity_name})
WITH DISTINCT e
MATCH (e)-[r]->(related:Entity)
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
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity {name: $entity_name})
MATCH (m)<-[:SENT]-(a:Author)
WITH a, e, count(m) AS mention_count
RETURN a.username       AS expert,
       a.discord_id     AS discord_id,
       mention_count    AS mention_count,
       e.name           AS topic
ORDER BY mention_count DESC
LIMIT 10
"""

# ── summarization ─────────────────────────────────────────────────────────────
SUMMARIZATION_QUERY = """
// If entity is "server" or generic, return recent messages from all channels
CALL {
  WITH $entity_name AS entity, $time_filter AS time_filter, $server_id AS server_id
  MATCH (s:Server {id: server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)
  OPTIONAL MATCH (m)<-[:SENT]-(a:Author)
  WHERE m.timestamp IS NOT NULL
    AND toLower(entity) IN ['server', 'activity', 'recent', 'messages', 'events', 'happening', 'discussion']
    AND (time_filter IS NULL OR datetime(m.timestamp) >= datetime(time_filter))
  RETURN m.content AS content,
         m.timestamp AS timestamp,
         c.name AS channel,
         COALESCE(a.username, 'Unknown') AS author
  ORDER BY m.timestamp DESC
  LIMIT 50
  
  UNION
  
  WITH $entity_name AS entity, $time_filter AS time_filter, $server_id AS server_id
  MATCH (s:Server {id: server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)<-[:SENT]-(author:Author)
  WHERE toLower(author.username) CONTAINS toLower(entity)
    AND NOT toLower(entity) IN ['server', 'activity', 'recent', 'messages', 'events', 'happening', 'discussion']
    AND (time_filter IS NULL OR datetime(m.timestamp) >= datetime(time_filter))
  RETURN m.content AS content,
         m.timestamp AS timestamp,
         c.name AS channel,
         author.username AS author
  ORDER BY m.timestamp DESC
  LIMIT 25
  
  UNION
  
  WITH $entity_name AS entity, $time_filter AS time_filter, $server_id AS server_id
  MATCH (s:Server {id: server_id})<-[:IN_SERVER]-(c2:Channel)<-[:IN_CHANNEL]-(m2:Message)-[:MENTIONS]->(e:Entity)
  OPTIONAL MATCH (m2)<-[:SENT]-(a2:Author)
  WHERE toLower(e.name) CONTAINS toLower(entity)
    AND NOT toLower(entity) IN ['server', 'activity', 'recent', 'messages', 'events', 'happening', 'discussion']
    AND (time_filter IS NULL OR datetime(m2.timestamp) >= datetime(time_filter))
  RETURN m2.content AS content,
         m2.timestamp AS timestamp,
         c2.name AS channel,
         COALESCE(a2.username, 'Unknown') AS author
  ORDER BY m2.timestamp DESC
  LIMIT 25
}
RETURN content, timestamp, channel, author
ORDER BY timestamp DESC
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

# ── temporal context: find related discussions across time ───────────────────
TEMPORAL_CONTEXT_QUERY = """
// Find messages about the same entities/topics across different time periods within the same server
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c1:Channel)<-[:IN_CHANNEL]-(m1:Message)-[:MENTIONS]->(e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
  AND m1.timestamp IS NOT NULL

// Find related messages through entity connections
OPTIONAL MATCH (e)-[:RELATES_TO|CONTINUES*1..2]-(related_entity:Entity)
OPTIONAL MATCH (s)<-[:IN_SERVER]-(c2:Channel)<-[:IN_CHANNEL]-(m2:Message)-[:MENTIONS]->(related_entity)
WHERE m2.timestamp IS NOT NULL
  AND m2.id <> m1.id

// Get authors for context
OPTIONAL MATCH (m1)<-[:SENT]-(a1:Author)
OPTIONAL MATCH (m2)<-[:SENT]-(a2:Author)

WITH m1, m2, c1, c2, a1, a2, e, related_entity
WHERE m1 IS NOT NULL

RETURN DISTINCT
  m1.content AS content,
  m1.timestamp AS timestamp,
  c1.name AS channel,
  COALESCE(a1.username, 'Unknown') AS author,
  'primary' AS context_type,
  e.name AS related_entity,
  
  // Include related messages as additional context
  COLLECT(DISTINCT {
    content: m2.content,
    timestamp: m2.timestamp,
    channel: c2.name,
    author: COALESCE(a2.username, 'Unknown'),
    context_type: 'related',
    related_entity: related_entity.name,
    time_gap: CASE 
      WHEN m1.timestamp IS NOT NULL AND m2.timestamp IS NOT NULL 
      THEN abs(m1.timestamp - m2.timestamp) / 86400000  // Convert milliseconds to days
      ELSE 0 
    END
  }) AS related_discussions

ORDER BY timestamp DESC
LIMIT 30
"""

# ── conversation threads: find message sequences and continuations ───────────
CONVERSATION_THREADS_QUERY = """
// Find conversation threads around a topic within the same server
MATCH (s:Server {id: $server_id})<-[:IN_SERVER]-(c:Channel)<-[:IN_CHANNEL]-(m:Message)-[:MENTIONS]->(e:Entity)
WHERE toLower(e.name) CONTAINS toLower($entity_name)
  AND m.timestamp IS NOT NULL

// Find messages in temporal proximity (within 24 hours) in the same channel
MATCH (c)<-[:IN_CHANNEL]-(nearby:Message)
WHERE nearby.timestamp IS NOT NULL
  AND nearby.id <> m.id

// Get authors
OPTIONAL MATCH (m)<-[:SENT]-(author:Author)
OPTIONAL MATCH (nearby)<-[:SENT]-(nearby_author:Author)

// Find entities mentioned in nearby messages
OPTIONAL MATCH (nearby)-[:MENTIONS]->(nearby_entity:Entity)

// Calculate time gap in hours (simplified to avoid datetime parsing issues)
WITH m, nearby, c, author, nearby_author, e, 
     COLLECT(DISTINCT nearby_entity.name) AS nearby_entities,
     CASE 
       WHEN m.timestamp IS NOT NULL AND nearby.timestamp IS NOT NULL 
       THEN abs(m.timestamp - nearby.timestamp) / 3600000  // Convert milliseconds to hours
       ELSE 0 
     END AS time_gap

WHERE time_gap <= 24  // Filter to 24 hours

// Group by conversation threads
RETURN 
  m.content AS content,
  m.timestamp AS timestamp,
  c.name AS channel,
  COALESCE(author.username, 'Unknown') AS author,
  e.name AS primary_entity,
  
  // Collect thread context
  COLLECT(DISTINCT {
    content: nearby.content,
    timestamp: nearby.timestamp,
    author: COALESCE(nearby_author.username, 'Unknown'),
    time_gap_hours: time_gap,
    mentioned_entities: nearby_entities
  }) AS thread_context

ORDER BY timestamp DESC
LIMIT 20
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
        "temporal_context": TEMPORAL_CONTEXT_QUERY,
        "conversation_threads": CONVERSATION_THREADS_QUERY,
    }

    cypher = query_map.get(intent)
    if not cypher:
        return []

    result = await session.run(cypher, **params)
    records = [dict(record) async for record in result]
    return records
