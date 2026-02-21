import logging
from neo4j import AsyncGraphDatabase, AsyncDriver, NotificationMinimumSeverity
from config import Config

logger = logging.getLogger(__name__)

# Silence neo4j notification spam in logs
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

_driver: AsyncDriver | None = None


async def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
            notifications_min_severity=NotificationMinimumSeverity.OFF,
        )
        await _driver.verify_connectivity()
        logger.info("Neo4j driver connected")
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")
