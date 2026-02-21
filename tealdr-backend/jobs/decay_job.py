import logging
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
from db.neo4j import get_driver
from graph.queries import DECAY_QUERY
from config import Config

logger = logging.getLogger(__name__)


def start_decay_job(bot):
    """Reduce relationship weights for stale relationships once per day."""

    @tasks.loop(hours=24)
    async def decay_job():
        cutoff = datetime.now(timezone.utc) - timedelta(days=Config.RELATIONSHIP_DECAY_DAYS)
        cutoff_str = cutoff.isoformat()
        try:
            driver = await get_driver()
            async with driver.session() as session:
                result = await session.run(DECAY_QUERY, cutoff_date=cutoff_str)
                record = await result.single()
                count = record["decayed_count"] if record else 0
                logger.info(f"Decay job: reduced weight on {count} stale relationships (cutoff={cutoff_str})")
        except Exception as e:
            logger.error(f"Decay job failed: {e}")

    @decay_job.before_loop
    async def before_decay():
        await bot.wait_until_ready()

    decay_job.start()
    logger.info("Decay job scheduled (runs every 24h)")
