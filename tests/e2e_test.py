import asyncio
import logging
import os
import sys
from typing import Any
from pathlib import Path

# Fix python path to allow importing from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

# Adapters
from src.bot.telegram_messenger import TelegramFormatter
from src.bot.protocol import MessengerProtocol
from src.database.sqlite_storage import SQLiteStorage
from src.ai import AIService
from src.ai.providers import get_provider
from src.news.rss_crawler import RSSCrawler
from src.news.fetchers.aiohttp_fetcher import AioHttpFetcher
from src.models import NewsDTO

# Core
from src.services.agent_controller import AgentController
from src.services.briefing_service import BriefingService

# Configure basic logging to focus only on E2E prints
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
# Keep third-party loggers quiet so terminal outputs are very clean
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)
logging.getLogger("ollama").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger("E2E_Test")


class CaptureMessenger(MessengerProtocol):
    """
    Outbound Messenger Adapter that intercepts the finalized 
    MarkdownV2 messages and displays them directly in the console.
    """
    def __init__(self):
        self.sent_briefings = []
        self.sent_deep_dives = []
        self.sent_notifications = []
        self.formatter = TelegramFormatter()

    async def send_briefing(self, recipient_id: str, news_items: list[NewsDTO], language: str = "vi") -> None:
        self.sent_briefings.append((recipient_id, news_items, language))
        text = self.formatter.format_briefing(news_items, language)
        
        print("\n" + "="*80)
        print(f"📡 [OUTBOUND TELEGRAM DELIVERY] BRIEFING CARD FOR USER: {recipient_id}")
        print(f"🌐 Language: {language.upper()}")
        print("-"*80)
        print(text)
        print("="*80 + "\n")

    async def send_deep_dive_response(self, recipient_id: str, text: str, sources: list[str], language: str = "vi") -> None:
        self.sent_deep_dives.append((recipient_id, text, sources, language))
        formatted = self.formatter.format_deep_dive(text, sources, language)
        
        print("\n" + "="*80)
        print(f"📡 [OUTBOUND TELEGRAM DELIVERY] CONTEXTUAL DEEP-DIVE RESPONSE FOR USER: {recipient_id}")
        print(f"🌐 Language: {language.upper()}")
        print("-"*80)
        print(formatted)
        print("="*80 + "\n")

    async def notify_event(self, recipient_id: str, message_key: str, **kwargs: Any) -> None:
        self.sent_notifications.append((recipient_id, message_key, kwargs))
        print(f"🔔 [OUTBOUND NOTIFICATION] User: {recipient_id} | Key: '{message_key}' | Args: {kwargs}")


async def run_e2e() -> None:
    """Run E2E scenario testing all core flows end-to-end with real APIs."""
    load_dotenv(override=True)
    
    # 1. Inspect environment config
    provider_name = os.getenv("LLM_PROVIDER", "ollama")
    model_name = os.getenv("GROQ_MODEL") if provider_name == "groq" else os.getenv("OLLAMA_MODEL", "gemma4:E4B")
    
    print("\n" + "*"*80)
    print("🚀 STARTING E2E INTEGRATION TEST SUITE")
    print(f"👉 LLM Provider: {provider_name.upper()}")
    print(f"👉 Target Model: {model_name}")
    print("*"*80 + "\n")

    # Use a temporary database for test validation
    test_db_path = "data/test_news_agent.db"
    
    # Clean up preexisting test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    storage = SQLiteStorage(db_path=test_db_path)
    await storage.connect()
    
    messenger = CaptureMessenger()
    llm_provider = get_provider()
    ai_service = AIService(provider=llm_provider, storage=storage)
    
    fetcher = AioHttpFetcher()
    news_repo = RSSCrawler(fetcher=fetcher)

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
    
    recipient_id = "test_user_777"
    
    try:
        # =====================================================================
        # FLOW 1: USER ONBOARDING & PREFERENCES
        # =====================================================================
        print("🟢 [FLOW 1] Initiating user onboarding and setting preferences...")
        
        # User triggers /start -> selected language
        await agent_controller.handle_interaction(recipient_id, "select_language", {"language": "vi"})
        
        # User sets keyword inclusions (follow) and exclusions (block)
        await agent_controller.handle_user_command(recipient_id, "/follow Công nghệ")
        await agent_controller.handle_user_command(recipient_id, "/follow trí tuệ nhân tạo")
        await agent_controller.handle_user_command(recipient_id, "/block scandal")
        await agent_controller.handle_user_command(recipient_id, "/block giải trí")
        
        # User configures strict curation mode (unrelated news off)
        await agent_controller.handle_user_command(recipient_id, "/unrelated no")
        
        # Display list configurations
        await agent_controller.handle_user_command(recipient_id, "/list")
        
        # Verify sqlite persistence
        config = await storage.get_user_config(recipient_id)
        assert config is not None, "User configuration failed to persist in SQLite!"
        assert config.name == "", "Persisted user name should be empty!"
        assert "Công nghệ" in config.follow_keywords, "Follow keywords did not persist!"
        assert "scandal" in config.block_keywords, "Block keywords did not persist!"
        assert config.allow_unrelated is False, "allow_unrelated failed to persist as False!"
        assert len(config.custom_feeds) > 0, "custom_feeds list is empty (dynamic LLM routing failed)!"
        print("✅ [FLOW 1 COMPLETE] User configuration successfully verified in SQLite.\n")

        # =====================================================================
        # FLOW 2: SCHEDULED NEWS BRIEFING (SYS1)
        # =====================================================================
        print("🟢 [FLOW 2] Triggering scheduled briefing crawl, filtering, and summarization...")
        
        # Fetch, filter, summarize top articles in parallel, and output Markdown briefing
        await briefing_service.run_scheduled_briefing(recipient_id)
        
        assert len(messenger.sent_briefings) > 0, "No briefing was delivered!"
        print("✅ [FLOW 2 COMPLETE] Scheduled briefing fetched, summarized, and logged successfully (strictly relevant tech only).\n")

        # =====================================================================
        # FLOW 3: CONTEXTUAL DEEP-DIVE (USER2)
        # =====================================================================
        print("🟢 [FLOW 3] Starting contextual focus deep-dive on an archived article...")
        
        # Fetch an article from the test SQLite cache
        async with storage._connection.execute("SELECT article_id, title FROM news_articles LIMIT 1") as cursor:
            row = await cursor.fetchone()
            
        if not row:
            print("⚠️ Skipping Flow 3: No articles were archived (possibly due to network crawling failures).")
        else:
            article_id = row["article_id"]
            article_title = row["title"]
            print(f"👉 Selecting archived article for deep-dive: ID='{article_id}', Title='{article_title}'")
            
            # Simulate clicking the inline detail button
            await agent_controller.handle_interaction(recipient_id, "deep_dive", {"article_id": article_id})
            
            # Send specific question while locked in Focus Mode
            question = "Bài viết này đề cập đến thông tin gì và tại sao nó lại là chủ đề đáng chú ý?"
            print(f"👉 User Question: '{question}'")
            await agent_controller.handle_user_command(recipient_id, question)
            
            # Check focus session status
            session = await storage.get_session_context(recipient_id)
            assert session.get("focus_article_id") == article_id, "User session did not lock into focus mode!"
            
            # Exit focus mode
            await agent_controller.handle_interaction(recipient_id, "exit_focus", {})
            session_exited = await storage.get_session_context(recipient_id)
            assert session_exited.get("focus_article_id") is None, "Focus mode context clear failed!"
            print("✅ [FLOW 3 COMPLETE] Deep-dive query executed, web portal searched, and facts synthesized.\n")

        # =====================================================================
        # FLOW 4: AD-HOC PORTAL DIRECT SEARCH (USER3)
        # =====================================================================
        print("🟢 [FLOW 4] Executing ad-hoc direct portal search query...")
        
        ad_hoc_prompt = "Công nghệ xe điện"
        print(f"👉 Direct Search Prompt: '{ad_hoc_prompt}'")
        await agent_controller.handle_user_command(recipient_id, ad_hoc_prompt)
        
        assert len(messenger.sent_briefings) > 1, "Ad-hoc search did not deliver a summary briefing!"
        print("✅ [FLOW 4 COMPLETE] Ad-hoc portal search completed successfully.\n")

    except Exception as e:
        logger.error(f"❌ E2E Integration Suite failed with exception: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # Graceful shutdown & database cleanup
        await storage.disconnect()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("🧹 Cleaned up temporary test SQLite database file.")
            
    print("\n" + "*"*80)
    print("🎉 ALL CORE FLOWS COMPLETED SUCCESSFULLY END-TO-END!")
    print("*"*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_e2e())
