import asyncio
import logging
import hashlib
from typing import List

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from ddgs import DDGS

from src.models import NewsDTO
from src.news.protocol import NewsRepositoryProtocol
from src.news.sources import get_all_feeds
from src.news.fetchers.protocol import ContentFetcherProtocol

logger = logging.getLogger(__name__)


class RSSCrawler(NewsRepositoryProtocol):
    """
    Crawler implementation for fetching news from RSS feeds and Web Search.
    Delegates raw fetching and extraction to a ContentFetcherProtocol.
    """

    def __init__(self, fetcher: ContentFetcherProtocol):
        self.source_name = "Global News Engine"
        self.default_feeds = get_all_feeds()
        self.fetcher = fetcher
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self._timeout = aiohttp.ClientTimeout(total=10)

    def _generate_article_id(self, url: str) -> str:
        """Create a unique MD5 hash from the article URL."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    async def _process_feed(self, session: aiohttp.ClientSession, url: str) -> List[NewsDTO]:
        """Fetch and parse a single RSS feed, extract full content via fetcher."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                xml_content = await response.text()

            feed = feedparser.parse(xml_content)
            source_title = feed.feed.get('title', 'UNKNOWN_SOURCE')
            entries = feed.entries

            # Collect all URLs and fetch in batch
            urls = [e.get('link', '') for e in entries if e.get('link')]
            full_contents = await self.fetcher.fetch_contents(urls)
            
            # Map contents back to entries
            content_map = dict(zip(urls, full_contents))
            
            articles = []
            for entry in entries:
                url = entry.get('link', '')
                if not url:
                    continue
                
                raw_content = content_map.get(url, "")
                summary = entry.get('summary', 'NO_SUMMARY')
                
                articles.append(NewsDTO(
                    article_id=self._generate_article_id(url),
                    title=entry.get('title', 'NO_TITLE'),
                    url=url,
                    source=source_title,
                    summary=summary,
                    published_at=entry.get('published', 'NO_DATE'),
                    raw_content=raw_content if raw_content else summary
                ))
            return articles

        except Exception as e:
            logger.debug(f"Failed to process feed {url}: {e}")
            return []

    async def fetch_from_feeds(self, feeds: list[str]) -> list[NewsDTO]:
        """Fetch news from RSS feeds concurrently."""
        target_feeds = feeds if feeds else self.default_feeds
        logger.info(f"Initiating news crawl from {len(target_feeds)} sources.")

        all_articles: List[NewsDTO] = []
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            tasks = [self._process_feed(session, url) for url in target_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    all_articles.extend(res)
        return all_articles

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """Perform ad-hoc web search and fetch full content via fetcher."""
        def ddg_sync():
            with DDGS() as ddgs:
                return list(ddgs.news(query, max_results=limit))

        try:
            search_results = await asyncio.to_thread(ddg_sync)
            urls = [r.get('url', '') for r in search_results if r.get('url')]
            
            # Fetch in batch
            full_contents = await self.fetcher.fetch_contents(urls)
            content_map = dict(zip(urls, full_contents))

            results = []
            for r in search_results:
                url = r.get('url', '')
                if not url:
                    continue
                
                raw_content = content_map.get(url, "")
                summary = r.get('body', 'NO_SUMMARY')

                results.append(NewsDTO(
                    article_id=self._generate_article_id(url),
                    title=r.get('title', 'NO_TITLE'),
                    url=url,
                    source=r.get('source', 'DUCKDUCKGO'),
                    summary=summary,
                    published_at=r.get('date', 'NO_DATE'),
                    raw_content=raw_content if raw_content else summary
                ))
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []

