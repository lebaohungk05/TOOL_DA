import asyncio
import logging
import re
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

    def _filter_and_prioritize(
        self, articles: list[NewsDTO], follow: list[str], block: list[str]
    ) -> list[NewsDTO]:
        """Apply dynamic filtering using regex for exact word matching."""
        block_patterns = [re.compile(rf"\b{re.escape(kw.lower())}\b") for kw in block]
        follow_patterns = [re.compile(rf"\b{re.escape(kw.lower())}\b") for kw in follow]
        
        prioritized = []
        normal = []

        for article in articles:
            text = (article.title + " " + article.summary).lower()
            
            # Exclusion logic
            if any(p.search(text) for p in block_patterns):
                continue
            
            # Inclusion/Prioritization logic
            if any(p.search(text) for p in follow_patterns):
                prioritized.append(article)
            else:
                normal.append(article)
                
        return prioritized + normal

    async def run_scheduled_briefing(self, recipient_id: str) -> None:
        """
        Execute the full scheduled briefing workflow:
        1. Fetch fresh articles.
        2. Filter based on user preferences.
        3. Parallelize AI summarization.
        4. Archive results in the database.
        5. Push formatted briefing to the user.
        
        Args:
            recipient_id: The unique ID of the recipient to receive the briefing.
        """
        logger.info(f"Starting scheduled briefing for recipient {recipient_id}")
        
        # Default language for early fallbacks
        lang = "vi"
        
        try:
            # 1. Fetch user config to get preferences and language
            follow_keywords = []
            block_keywords = []
            user_config = await self.storage.get_user_config(user_id=recipient_id)
            if user_config:
                lang = user_config.language
                follow_keywords = user_config.follow_keywords
                block_keywords = user_config.block_keywords
                
            feeds = ["default_rss"] # Mocked feed list for now
            
            # 2. Fetch fresh news
            raw_news = await self.news_repo.fetch_from_feeds(feeds)
            if not raw_news:
                await self.messenger.notify_event(recipient_id, "no_news_found", language=lang)
                return

            # Apply filtering and prioritization based on user config
            filtered_news = self._filter_and_prioritize(raw_news, follow_keywords, block_keywords)

            # Keep top 5
            top_news = filtered_news[:5]

            # 3. Parallelize AI Summarization
            async def summarize_task(item: NewsDTO) -> NewsDTO:
                try:
                    summary = await self.ai_service.summarize_news(item.raw_content or item.title, lang)
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
            article_ids = await self.storage.archive_news_items(list(summarized_news))
            
            # Reconstruct DTOs with confirmed IDs
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
            await self.messenger.send_briefing(recipient_id, final_news, lang)
            logger.info(f"Successfully completed briefing for recipient {recipient_id} in {lang}")

        except Exception as e:
            logger.error(f"Error during scheduled briefing workflow: {str(e)}")
            await self.messenger.notify_event(recipient_id, "error_system", language=lang)

    async def run_deep_dive(self, recipient_id: str, article_id: str, question: str) -> None:
        """
        Execute the contextual deep-dive workflow:
        1. Retrieve original article from storage.
        2. Extract search queries using AI.
        3. Fetch additional context via web search.
        4. Synthesize final grounded answer via AI.
        5. Push detailed response to the user.
        
        Args:
            recipient_id: The unique ID of the recipient.
            article_id: The unique ID of the news article in focus.
            question: The specific question asked by the user.
        """
        logger.info(f"Starting deep-dive for recipient {recipient_id} on article {article_id}")
        
        lang = "vi"

        try:
            # 1. Fetch user config for language
            user_config = await self.storage.get_user_config(user_id=recipient_id)
            if user_config:
                lang = user_config.language

            # 2. Retrieve article context
            original_article = await self.storage.get_article_by_id(article_id)
            if not original_article:
                await self.messenger.notify_event(recipient_id, "error_context_not_found", language=lang)
                return

            # 3. Extract Search Queries
            try:
                # Wrap full article context into the user prompt for high-quality extraction
                context = f"Title: {original_article.title}\nSummary: {original_article.summary}"
                enriched_prompt = f"### CONTEXT ###\n{context}\n\n### USER QUESTION ###\n{question}"
                
                search_term = await self.ai_service.extract_search_queries(enriched_prompt, lang)
                if not search_term:
                    search_term = original_article.title
                logger.info(f"Deep-dive: AI generated search query for {recipient_id}: {search_term}")
            except Exception as e:
                logger.warning(f"AI query extraction failed: {e}")
                search_term = original_article.title

            # 4. Web Search for contextual enrichment
            web_results = []
            try:
                logger.info(f"Deep-dive: Searching web for {recipient_id} using term: {search_term}")
                web_results = await self.news_repo.search_web(search_term)
            except Exception as e:
                logger.error(f"Web search failed: {e}")

            # 5. AI Synthesis
            try:
                all_context = [original_article] + web_results
                answer = await self.ai_service.synthesize_response(all_context, question, lang)
            except Exception as e:
                logger.error(f"AI synthesis failed: {e}")
                answer = "I'm sorry, I'm having trouble synthesizing a detailed answer right now."

            # 6. Push via Telegram
            source_urls = [original_article.url] + [r.url for r in web_results]
            await self.messenger.send_deep_dive_response(recipient_id, answer, source_urls, lang)
            logger.info(f"Successfully completed deep-dive for recipient {recipient_id} in {lang}")

        except Exception as e:
            logger.error(f"Error during deep-dive workflow: {str(e)}")
            await self.messenger.notify_event(recipient_id, "error_deep_dive", language=lang)

    async def run_ad_hoc_query(self, recipient_id: str, query: str) -> None:
        """
        Execute a free-form search query requested by the user.
        
        Args:
            recipient_id: The unique ID of the recipient.
            query: The raw query from the user.
        """
        logger.info(f"Starting ad-hoc search for recipient {recipient_id}: {query}")
        lang = "vi"

        try:
            # 1. Fetch user config
            user_config = await self.storage.get_user_config(user_id=recipient_id)
            if user_config:
                lang = user_config.language

            # 2. Notify User
            await self.messenger.notify_event(recipient_id, "ad_hoc_searching", language=lang)

            # 3. Optimize queries and search web
            search_term = await self.ai_service.extract_search_queries(query, lang)
            if not search_term:
                search_term = query
            
            logger.info(f"Ad-hoc: Searching web for term: {search_term}")
            raw_results = await self.news_repo.search_web(search_term)
            
            if not raw_results:
                await self.messenger.notify_event(recipient_id, "error_system", language=lang)
                return
                
            # Limit to 3 for brevity
            articles = raw_results[:3]

            # 4. Summarize and Archive
            final_news = []
            import dataclasses
            for item in articles:
                ai_summary = await self.ai_service.summarize_news(item.summary, lang)
                new_item = dataclasses.replace(item, summary=ai_summary)
                final_news.append(new_item)
                
            await self.storage.archive_news_items(final_news)

            # 5. Push exact same briefing payload
            await self.messenger.send_briefing(recipient_id, final_news, lang)
            logger.info(f"Completed ad-hoc query for recipient {recipient_id}")

        except Exception as e:
            logger.error(f"Error during ad-hoc workflow: {str(e)}")
            await self.messenger.notify_event(recipient_id, "error_system", language=lang)

