import logging
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
from db.neo4j import get_driver
from graph.queries import DAILY_CHUNKS_QUERY

logger = logging.getLogger(__name__)


def start_summary_job(bot):
    """Create daily Summary nodes in Neo4j for each channel, runs once per day."""

    @tasks.loop(hours=24)
    async def summary_job():
        now = datetime.now(timezone.utc)
        day_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start.replace(hour=23, minute=59, second=59)

        try:
            driver = await get_driver()
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    async with driver.session() as session:
                        result = await session.run(
                            DAILY_CHUNKS_QUERY,
                            channel_id=channel.id,
                            day_start=day_start.isoformat(),
                            day_end=day_end.isoformat(),
                        )
                        chunks = [dict(r) async for r in result]

                        if not chunks:
                            continue

                        combined_text = "\n\n".join(c["text"] for c in chunks)

                        await session.run(
                            """
                            MERGE (s:Summary {channel_id: $channel_id, date: $date})
                            SET s.text       = $text,
                                s.guild_id   = $guild_id,
                                s.created_at = $now
                            """,
                            channel_id=channel.id,
                            date=day_start.date().isoformat(),
                            text=combined_text[:10000],
                            guild_id=guild.id,
                            now=now.isoformat(),
                        )
                        logger.info(f"Summary node created for #{channel.name} on {day_start.date()}")

        except Exception as e:
            logger.error(f"Summary job failed: {e}")

    @summary_job.before_loop
    async def before_summary():
        await bot.wait_until_ready()

    summary_job.start()
    logger.info("Summary job scheduled (runs every 24h)")
