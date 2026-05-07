import hashlib
import re
import logging
import asyncio
import aiohttp
from typing import List
from curl_cffi.requests import AsyncSession
import feedparser
from bs4 import BeautifulSoup

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
        # Handle the placeholder used in the briefing service
        if not feeds or feeds == ["default_rss"]:
            target_feeds = self.default_feeds
        else:
            target_feeds = feeds
            
        logger.info(f"Initiating news crawl from {len(target_feeds)} sources.")

        all_articles: List[NewsDTO] = []
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            tasks = [self._process_feed(session, url) for url in target_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, res in enumerate(results):
                if isinstance(res, list):
                    all_articles.extend(res)
                else:
                    logger.error(f"Error crawling feed {target_feeds[i]}: {res}")
        
        logger.info(f"Crawl completed. Found {len(all_articles)} total items.")
        return all_articles

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """Perform ad-hoc search via Google News RSS (Very stable)."""
        clean_query = query.replace("2026", "").strip()
        logger.info(f"Searching Google News RSS for: {clean_query}")
        
        # Google News RSS Search URL (Vietnamese Market)
        # hl=vi (Vietnamese), gl=VN (Vietnam), ceid=VN:vi
        rss_url = f"https://news.google.com/rss/search?q={clean_query.replace(' ', '+')}&hl=vi&gl=VN&ceid=VN:vi"
        
        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async with session.get(rss_url) as response:
                    if response.status != 200:
                        logger.error(f"Google News RSS failed with status {response.status}")
                        return []
                    xml_content = await response.text()

            feed = feedparser.parse(xml_content)
            entries = feed.entries[:limit]
            
            if not entries:
                logger.warning(f"No results in Google News RSS for: {clean_query}")
                return []

            # Collect URLs and fetch full contents
            urls = [e.get('link', '') for e in entries if e.get('link')]
            full_contents = await self.fetcher.fetch_contents(urls)
            content_map = dict(zip(urls, full_contents))

            results = []
            for entry in entries:
                url = entry.get('link', '')
                if not url: continue
                
                raw_content = content_map.get(url, "")
                # Google News RSS description is often just a snippet
                summary = entry.get('summary', entry.get('title', ''))

                results.append(NewsDTO(
                    article_id=self._generate_article_id(url),
                    title=entry.get('title', 'NO_TITLE'),
                    url=url,
                    source=entry.get('source', {}).get('title', 'Google News'),
                    summary=summary,
                    published_at=entry.get('published', 'TODAY'),
                    raw_content=raw_content if raw_content else summary
                ))
            return results

        except Exception as e:
            logger.error(f"Google News RSS Search failed: {e}")
            return []

