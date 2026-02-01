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

def main():
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    
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
