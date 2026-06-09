import asyncio
import os
import unittest
from src.database.sqlite_storage import SQLiteStorage
from src.services.briefing_service import BriefingService
from src.models import NewsDTO, UserConfigDTO
from unittest.mock import AsyncMock, MagicMock

class TestBriefingDeduplication(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the news briefing deduplication feature."""

    async def asyncSetUp(self) -> None:
        """Set up a test database."""
        self.db_path = "data/test_dedup.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.storage = SQLiteStorage(db_path=self.db_path)
        await self.storage.connect()

    async def asyncTearDown(self) -> None:
        """Clean up the test database."""
        await self.storage.disconnect()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_delivered_articles_persistence(self) -> None:
        """Verify that delivered articles are persisted and retrieved correctly."""
        user_id = "user_123"
        urls = ["https://example.com/art1", "https://example.com/art2"]
        
        # Initially empty
        delivered = await self.storage.get_delivered_urls(user_id)
        self.assertEqual(delivered, [])

        # Mark delivered
        await self.storage.mark_articles_delivered(user_id, urls)

        # Retrieve
        delivered = await self.storage.get_delivered_urls(user_id)
        self.assertEqual(set(delivered), set(urls))

        # Check duplicates ignore on mark
        await self.storage.mark_articles_delivered(user_id, ["https://example.com/art1"])
        delivered = await self.storage.get_delivered_urls(user_id)
        self.assertEqual(len(delivered), 2)

    async def test_delivered_articles_retention(self) -> None:
        """Verify the 2-day retention policy and automatic pruning."""
        user_id = "user_123"
        url_old = "https://example.com/old"
        url_new = "https://example.com/new"

        # Insert old article manually with backdated timestamp (e.g. 3 days ago)
        await self.storage._connection.execute(
            """
            INSERT INTO user_delivered_articles (user_id, url, delivered_at)
            VALUES (?, ?, datetime('now', '-3 days'))
            """,
            (user_id, url_old)
        )
        await self.storage._connection.execute(
            """
            INSERT INTO user_delivered_articles (user_id, url, delivered_at)
            VALUES (?, ?, datetime('now', '-1 hours'))
            """,
            (user_id, url_new)
        )
        await self.storage._connection.commit()

        # Query default window (within 2 days)
        delivered = await self.storage.get_delivered_urls(user_id)
        self.assertIn(url_new, delivered)
        self.assertNotIn(url_old, delivered)

        # Trigger prune by calling mark_articles_delivered
        await self.storage.mark_articles_delivered(user_id, ["https://example.com/brandnew"])
        
        # Verify old record is deleted from DB
        async with self.storage._connection.execute(
            "SELECT COUNT(*) as cnt FROM user_delivered_articles WHERE url = ?", (url_old,)
        ) as cursor:
            row = await cursor.fetchone()
            self.assertEqual(row["cnt"], 0)

    async def test_briefing_deduplication(self) -> None:
        """Verify that run_scheduled_briefing filters out previously delivered articles."""
        # Mock dependencies
        news_repo = MagicMock()
        ai_service = MagicMock()
        messenger = MagicMock()

        # Mock user config
        user_config = UserConfigDTO(
            user_id="user_123",
            recipient_id="user_123",
            follow_keywords=[],
            block_keywords=[],
            language="vi"
        )
        await self.storage.upsert_user_config("user_123", user_config)

        # Set up news items: art1 (already delivered), art2 (fresh)
        art1 = NewsDTO(article_id="id1", title="Title 1", url="https://example.com/art1", source="RSS")
        art2 = NewsDTO(article_id="id2", title="Title 2", url="https://example.com/art2", source="RSS")

        # Mark art1 as delivered
        await self.storage.mark_articles_delivered("user_123", ["https://example.com/art1"])

        briefing_service = BriefingService(
            news_repo=news_repo,
            ai_service=ai_service,
            storage=self.storage,
            messenger=messenger
        )

        news_repo.fetch_from_feeds = AsyncMock(return_value=[art1, art2])
        news_repo.fetch_full_contents = AsyncMock(side_effect=lambda items: items)
        ai_service.summarize_news = AsyncMock(side_effect=lambda content, lang: f"Summary of {content}")
        messenger.send_briefing = AsyncMock()
        messenger.notify_event = AsyncMock()
        
        # Run briefing
        await briefing_service.run_scheduled_briefing("user_123")

        # Verify: only art2 (fresh) was summarized and sent
        # fetch_full_contents should be called with only art2
        news_repo.fetch_full_contents.assert_called_once()
        called_args = news_repo.fetch_full_contents.call_args[0][0]
        self.assertEqual(len(called_args), 1)
        self.assertEqual(called_args[0].url, "https://example.com/art2")

        # Verify messenger sent briefing with only art2
        messenger.send_briefing.assert_called_once()
        sent_items = messenger.send_briefing.call_args[0][1]
        self.assertEqual(len(sent_items), 1)
        self.assertEqual(sent_items[0].url, "https://example.com/art2")

        # Verify art2 is now also marked as delivered in DB
        delivered = await self.storage.get_delivered_urls("user_123")
        self.assertIn("https://example.com/art2", delivered)
