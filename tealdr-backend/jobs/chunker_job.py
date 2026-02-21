import logging
import asyncio
from discord.ext import tasks
from ingestion.chunker import run_chunker_for_server
from config import Config

logger = logging.getLogger(__name__)


def start_chunker_job(bot):
    """Start the background chunker job that runs every CHUNK_WINDOW_MINUTES."""

    @tasks.loop(minutes=Config.CHUNK_WINDOW_MINUTES)
    async def chunker_job():
        logger.info("Chunker job started")
        for guild in bot.guilds:
            try:
                await run_chunker_for_server(server_id=guild.id)
            except Exception as e:
                logger.error(f"Chunker job failed for guild {guild.id}: {e}")

    @chunker_job.before_loop
    async def before_chunker():
        await bot.wait_until_ready()
        logger.info(f"Chunker job will run every {Config.CHUNK_WINDOW_MINUTES} minutes")

    chunker_job.start()
    logger.info("Chunker job scheduled")
