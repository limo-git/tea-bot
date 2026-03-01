import logging
from db.neo4j import get_driver

logger = logging.getLogger(__name__)

CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Message)  REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Author)   REQUIRE a.discord_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Server)   REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Channel)  REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (ch:Chunk)   REQUIRE ch.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name, e.type)",
    "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.type)",
    "CREATE INDEX IF NOT EXISTS FOR (m:Message) ON (m.timestamp)",
    "CREATE INDEX IF NOT EXISTS FOR (ch:Chunk) ON (ch.start_time)",
    "CREATE INDEX IF NOT EXISTS FOR (ch:Chunk) ON (ch.channel_id)",
    "CREATE INDEX IF NOT EXISTS FOR (a:Author) ON (a.username)",
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:CONTINUES]->() ON (r.time_gap)",
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:RELATES_TO]->() ON (r.strength)",
]


async def setup_schema():
    driver = await get_driver()
    async with driver.session() as session:
        for stmt in CONSTRAINTS:
            await session.run(stmt)
            logger.debug(f"Applied constraint: {stmt[:60]}...")

        for stmt in INDEXES:
            await session.run(stmt)
            logger.debug(f"Applied index: {stmt[:60]}...")

    logger.info("Neo4j schema setup complete")
