import asyncio
import logging
import hashlib
from typing import List

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from src.models import NewsDTO
from src.news.protocol import NewsRepositoryProtocol
from src.news.sources import get_all_feeds

logger = logging.getLogger(__name__)


class RSSCrawler(NewsRepositoryProtocol):
    """
    Crawler implementation for fetching news from RSS feeds and Web Search.
    Inherits from NewsRepositoryProtocol for architectural consistency.
    """

    def __init__(self):
        self.source_name = "Global News Engine"
        self.default_feeds = get_all_feeds()
        # Cap concurrent HTTP requests to avoid rate limits
        self._semaphore = asyncio.Semaphore(10)
        # Timeout for HTTP requests
        self._timeout = aiohttp.ClientTimeout(total=10)

    def _generate_article_id(self, url: str) -> str:
        """Create a unique MD5 hash from the article URL."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    async def _fetch_full_content(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        Fetch HTML page and extract main text content.
        Uses a semaphore to limit concurrent requests.
        """
        async with self._semaphore:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ""
                    html = await response.text()

                    # Parse HTML
                    soup = BeautifulSoup(html, "html.parser")

                    # Strip unwanted tags
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        tag.decompose()

                    # Try to find the main article tag, fallback to body
                    main_content = soup.find("article")
                    if not main_content:
                        main_content = soup.find("body")

                    if not main_content:
                        return ""

                    # Extract text and compress whitespace
                    text = main_content.get_text(separator=' ')
                    text = " ".join(text.split())

                    return text

            except Exception as e:
                logger.debug(f"Failed to fetch content for {url}: {e}")
                return ""

    async def _process_feed(self, session: aiohttp.ClientSession, url: str) -> List[NewsDTO]:
        """Fetch and parse a single RSS feed, extract full content for its entries."""
        articles = []
        try:
            # 1. Fetch RSS XML
            async with self._semaphore:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []
                    xml_content = await response.text()

            # 2. Parse XML (CPU bound, but fast enough for feedparser)
            feed = feedparser.parse(xml_content)
            source_title = feed.feed.get('title', 'UNKNOWN_SOURCE')

            # 3. Fetch full content for all entries concurrently
            entries = feed.entries

            async def process_entry(entry) -> NewsDTO | None:
                article_url = entry.get('link', '')
                if not article_url:
                    return None

                full_content = await self._fetch_full_content(session, article_url)
                summary = entry.get('summary', 'NO_SUMMARY')

                # Fallback to summary if full content fails
                raw_content = full_content if full_content else summary

                return NewsDTO(
                    article_id=self._generate_article_id(article_url),
                    title=entry.get('title', 'NO_TITLE'),
                    url=article_url,
                    source=source_title,
                    summary=summary,
                    published_at=entry.get('published', 'NO_DATE'),
                    raw_content=raw_content
                )

            # Gather all entries for this feed
            results = await asyncio.gather(*(process_entry(e) for e in entries), return_exceptions=True)
            for res in results:
                if isinstance(res, NewsDTO):
                    articles.append(res)

        except Exception as e:
            logger.debug(f"Failed to process feed {url}: {e}")

        return articles

    async def fetch_from_feeds(self, feeds: list[str]) -> list[NewsDTO]:
        """Fetch news from RSS feeds concurrently and extract full text."""
        target_feeds = feeds if feeds else self.default_feeds

        logger.info(
            f"Initiating news crawl from {len(target_feeds)} sources concurrently.")

        all_articles: List[NewsDTO] = []

        # Use a single ClientSession for connection pooling
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            # Gather all feed parsing tasks
            tasks = [self._process_feed(session, url) for url in target_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    all_articles.extend(res)

        return all_articles

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """Perform ad-hoc web search and optionally fetch full content."""
        results = []

        def ddg_sync():
            with DDGS() as ddgs:
                return list(ddgs.news(query, max_results=limit))

        try:
            # Run blocking DDGS in a thread
            search_results = await asyncio.to_thread(ddg_sync)

            # Fetch full content for the search results
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async def process_search_result(r) -> NewsDTO | None:
                    url = r.get('url', '')
                    if not url:
                        return None

                    full_content = await self._fetch_full_content(session, url)
                    summary = r.get('body', 'NO_SUMMARY')
                    raw_content = full_content if full_content else summary

                    return NewsDTO(
                        article_id=self._generate_article_id(url),
                        title=r.get('title', 'NO_TITLE'),
                        url=url,
                        source=r.get('source', 'DUCKDUCKGO'),
                        summary=summary,
                        published_at=r.get('date', 'NO_DATE'),
                        raw_content=raw_content
                    )

                tasks = [process_search_result(r) for r in search_results]
                gathered = await asyncio.gather(*tasks, return_exceptions=True)
                for res in gathered:
                    if isinstance(res, NewsDTO):
                        results.append(res)

        except Exception as e:
            logger.error(
                f"DuckDuckGo search failed for query '{query}': {str(e)}")

        return results
