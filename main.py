"""
Composition Root: Wires all Hexagonal Architecture components and starts the bot.

Usage:
    uv run main.py

Required environment variables (in .env):
    TELEGRAM_BOT_TOKEN  — Telegram Bot API token from @BotFather
    OLLAMA_MODEL        — (optional) Ollama model name, default: gemma4:E4B
    OLLAMA_HOST         — (optional) Ollama server URL, default: http://localhost:11434
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router

# Adapters
from src.bot.telegram_messenger import TelegramMessenger
from src.bot.telegram_handlers import register_handlers
from src.bot.scheduler import BriefingScheduler
from src.database.sqlite_storage import SQLiteStorage
from src.ai.ollama_service import OllamaAIService
from src.news.rss_crawler import RSSCrawler

# Core
from src.services.agent_controller import AgentController
from src.services.briefing_service import BriefingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Application entry point: wire components, start polling."""
    load_dotenv(override=True)

    # --- Validate required config ---
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN is not set. Add it to your .env file.")
        sys.exit(1)

    # --- Instantiate Outbound Adapters ---
    storage = SQLiteStorage(db_path="data/news_agent.db")
    await storage.connect()
    logger.info("SQLiteStorage connected")

    bot = Bot(token=token)
    messenger = TelegramMessenger(bot=bot)
    ai_service = OllamaAIService()  # reads OLLAMA_MODEL/HOST from env
    news_repo = RSSCrawler()

    # --- Instantiate Core ---
    briefing_service = BriefingService(
        news_repo=news_repo,
        ai_service=ai_service,
        storage=storage,
        messenger=messenger,
    )

    agent_controller = AgentController(
        briefing_service=briefing_service,
        storage=storage,
        messenger=messenger,
    )

    # --- Instantiate Inbound Adapters ---
    scheduler = BriefingScheduler(
        briefing_service=briefing_service,
        storage=storage,
    )

    # --- Wire Telegram Handlers ---
    router = Router()
    register_handlers(router, agent_controller)

    dp = Dispatcher()
    dp.include_router(router)

    # --- Start ---
    await scheduler.start()
    logger.info("Bot starting polling...")

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        await scheduler.stop()
        await storage.disconnect()
        await bot.session.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
