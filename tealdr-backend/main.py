import discord
from discord.ext import commands
import asyncio
import signal
import sys
from config import Config
from utils.logger import setup_logger, get_logger
from bot.events import setup_events
from bot.commands import setup_commands
from bot.dm_commands import register_dm_commands

setup_logger()
logger = get_logger(__name__)


async def _init_graph_rag(bot):
    """
    Initialize Neo4j schema and start Graph RAG background jobs.
    Designed to be idempotent and tolerant of schema/job failures.
    If any critical step fails, disables Graph RAG and logs the error,
    allowing the bot to continue operating with degraded functionality.
    """
    try:
        from graph.schema import setup_schema

        await setup_schema()
        logger.info("Neo4j schema initialized")
    except Exception as e:
        logger.error(f"Neo4j schema setup failed: {e} — Graph RAG will be disabled")
        Config.GRAPH_RAG_ENABLED = False
        return

    try:
        from jobs.chunker_job import start_chunker_job
        from jobs.decay_job import start_decay_job
        from jobs.summary_job import start_summary_job

        start_chunker_job(bot)
        start_decay_job(bot)
        start_summary_job(bot)
        logger.info("Graph RAG background jobs started")
    except Exception as e:
        logger.error(f"Failed to start Graph RAG jobs: {e}")


def main():
    """
    Bot entry point. Validates config, sets Discord intents, registers handlers,
    and starts the bot. Handles both startup errors (config, login) and runtime
    shutdown (signals) gracefully.
    """
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error(
            "Please check your .env file and ensure all required variables are set"
        )
        sys.exit(1)

    """
    Discord intents restrict which events the bot receives. message_content intent
    is required to read message text in message_create events (privileged intent).
    guilds/members/presences needed for full user tracking in Graph RAG.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
    intents.members = True
    intents.presences = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    setup_events(bot)
    setup_commands(bot)
    register_dm_commands(bot)

    @bot.event
    async def on_ready_graph_rag():
        if Config.GRAPH_RAG_ENABLED:
            logger.info("Graph RAG enabled — initializing Neo4j and background jobs...")
            await _init_graph_rag(bot)
        else:
            logger.info("Graph RAG disabled — using Gemini + pgvector only")

    """
    Hook Graph RAG init into Discord's on_ready lifecycle. setup_hook is called
    once when the bot connects; we wrap it to inject Graph RAG init without
    interfering with existing setup logic. Using create_task ensures Graph RAG
    init happens asynchronously without blocking bot readiness.
    """
    original_setup_hook = bot.setup_hook

    async def setup_hook():
        if original_setup_hook:
            await original_setup_hook()
        if Config.GRAPH_RAG_ENABLED:
            bot.loop.create_task(_init_graph_rag(bot))

    bot.setup_hook = setup_hook

    """
    Register signal handlers for graceful shutdown on SIGINT (Ctrl+C) or
    SIGTERM (systemd/Docker). asyncio.create_task ensures bot.close() runs
    on the event loop, avoiding deadlock from mixing sync signal handler
    with async bot lifecycle.
    """

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, closing bot...")
        asyncio.create_task(bot.close())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("Starting Discord bot...")
        bot.run(Config.DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to login. Please check your DISCORD_BOT_TOKEN")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
