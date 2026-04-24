import asyncio
import logging
from typing import Optional

from src.models import NewsDTO
from src.services.protocol import BriefingServiceProtocol
from src.ai.protocol import AIServiceProtocol
from src.news.protocol import NewsRepositoryProtocol
from src.database.protocol import StorageProtocol
from src.bot.protocol import MessengerProtocol

logger = logging.getLogger(__name__)

class BriefingService(BriefingServiceProtocol):
    """
    Orchestrator for the Personal News Agent Bot.
    Coordinates between News, AI, Storage, and Messaging layers.
    """

    def __init__(
        self,
        news_repo: NewsRepositoryProtocol,
        ai_service: AIServiceProtocol,
        storage: StorageProtocol,
        messenger: MessengerProtocol
    ):
        """
        Initialize the orchestrator with required protocols.
        
        Args:
            news_repo: Repository for fetching news.
            ai_service: Service for AI summarization and synthesis.
            storage: Database storage for configurations and archiving.
            messenger: Interface for interacting with users.
        """
        self.news_repo = news_repo
        self.ai_service = ai_service
        self.storage = storage
        self.messenger = messenger

    async def run_scheduled_briefing(self, chat_id: int) -> None:
        """Execute the full scheduled briefing workflow."""
        logger.info(f"Starting scheduled briefing for chat {chat_id}")
        
        try:
            # 1. Fetch user config to get preferences (not used for selection yet, but good for context)
            user_config = await self.storage.get_user_config(user_id=chat_id)
            feeds = ["default_rss"] # Mocked feed list for now
            
            # 2. Fetch fresh news
            raw_news = await self.news_repo.fetch_from_feeds(feeds)
            if not raw_news:
                await self.messenger.notify_system_event(chat_id, "No new news found for your briefing.")
                return

            # Keep top 5
            top_news = raw_news[:5]

            # 3. Parallelize AI Summarization
            async def summarize_task(item: NewsDTO) -> NewsDTO:
                try:
                    summary = await self.ai_service.summarize_news(item.raw_content or item.title)
                    return NewsDTO(
                        article_id=item.article_id,
                        title=item.title,
                        url=item.url,
                        source=item.source,
                        raw_content=item.raw_content,
                        summary=summary,
                        published_at=item.published_at
                    )
                except Exception as e:
                    logger.warning(f"AI Summarization failed for {item.url}: {e}")
                    # Return original item if AI fails
                    return item

            # Use asyncio.gather for parallel summarization
            summarized_news = await asyncio.gather(*(summarize_task(n) for n in top_news))

            # 4. Archive results
            # Note: archive_news_items returns a list of assigned article_ids
            article_ids = await self.storage.archive_news_items(list(summarized_news))
            
            # Reconstruct DTOs with confirmed IDs if they were missing
            final_news = []
            for i, item in enumerate(summarized_news):
                final_news.append(NewsDTO(
                    article_id=article_ids[i],
                    title=item.title,
                    url=item.url,
                    source=item.source,
                    raw_content=item.raw_content,
                    summary=item.summary,
                    published_at=item.published_at
                ))

            # 5. Push via Telegram
            await self.messenger.send_briefing(chat_id, final_news)
            logger.info(f"Successfully completed briefing for chat {chat_id}")

        except Exception as e:
            logger.error(f"Error during scheduled briefing workflow: {str(e)}")
            await self.messenger.notify_system_event(chat_id, "⚠️ A system error occurred while generating your briefing.")

    async def run_deep_dive(self, chat_id: int, article_id: str, question: str) -> None:
        """Execute the contextual deep-dive workflow."""
        logger.info(f"Starting deep-dive for chat {chat_id} on article {article_id}")

        try:
            # 1. Retrieve article context
            original_article = await self.storage.get_article_by_id(article_id)
            if not original_article:
                await self.messenger.notify_system_event(chat_id, "Sorry, I can't find the original article context.")
                return

            # 2. Extract Search Queries
            try:
                queries = await self.ai_service.extract_search_queries(question)
                if not queries:
                    queries = [original_article.title]
            except Exception as e:
                logger.warning(f"AI query extraction failed: {e}")
                queries = [original_article.title]

            # 3. Web Search for contextual enrichment
            web_results = []
            try:
                # Search for the top query
                web_results = await self.news_repo.search_web(queries[0])
            except Exception as e:
                logger.error(f"Web search failed: {e}")

            # 4. AI Synthesis
            try:
                # Combine original article with web results
                all_context = [original_article] + web_results
                answer = await self.ai_service.synthesize_response(all_context, question)
            except Exception as e:
                logger.error(f"AI synthesis failed: {e}")
                answer = "I'm sorry, I'm having trouble synthesizing a detailed answer right now."

            # 5. Push via Telegram
            source_urls = [original_article.url] + [r.url for r in web_results]
            await self.messenger.send_deep_dive_response(chat_id, answer, source_urls)
            logger.info(f"Successfully completed deep-dive for chat {chat_id}")

        except Exception as e:
            logger.error(f"Error during deep-dive workflow: {str(e)}")
            await self.messenger.notify_system_event(chat_id, "⚠️ Error processing your deep-dive request.")
