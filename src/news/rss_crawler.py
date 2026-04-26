import asyncio
import logging
import hashlib
from typing import List, Optional

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from src.models import NewsDTO
from src.news.protocol import NewsRepositoryProtocol
from src.news.sources import get_all_feeds

logger = logging.getLogger(__name__)

class RSSCrawler(NewsRepositoryProtocol):
    """
    High-performance RSS Crawler.
    Fetches multiple feeds concurrently and extracts clean content.
    """
    
    def __init__(self):
        self.source_name = "RSS_Engine"
        self.default_feeds = get_all_feeds()
        # Limit concurrent connections to 20 to be polite to servers
        self._semaphore = asyncio.Semaphore(20)
        self._timeout = aiohttp.ClientTimeout(total=20)

    def _generate_article_id(self, url: str) -> str:
        """MD5 hash of URL for unique identification."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _clean_html(self, html_content: str) -> str:
        """Strip all HTML tags and return clean text."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=' ')
        return " ".join(text.split())

    async def _fetch_full_content(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch and extract main article text from a URL."""
        async with self._semaphore:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return ""
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Remove junk
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        tag.decompose()

                    # Focus on main content
                    content_node = soup.find("article") or soup.find("body")
                    if not content_node:
                        return ""
                        
                    return " ".join(content_node.get_text(separator=' ').split())[:5000]
            except Exception:
                return ""

    async def _process_single_feed(self, session: aiohttp.ClientSession, url: str) -> List[NewsDTO]:
        """Fetch and parse one RSS feed concurrently."""
        articles = []
        try:
            async with self._semaphore:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []
                    xml_data = await response.text()

            # Parse RSS structure
            feed = feedparser.parse(xml_data)
            source_title = feed.feed.get('title', 'UNKNOWN_SOURCE')
            
            # Create tasks for all entries in this feed
            for entry in feed.entries:
                link = entry.get('link', '')
                if not link:
                    continue
                
                summary_raw = entry.get('summary', '')
                clean_summary = self._clean_html(summary_raw)
                
                # Note: We are NOT fetching full content here for all 2000+ items 
                # to save bandwidth. Full content can be fetched on-demand (Deep-dive).
                articles.append(NewsDTO(
                    article_id=self._generate_article_id(link),
                    title=entry.get('title', 'NO_TITLE'),
                    url=link,
                    source=source_title,
                    summary=clean_summary,
                    published_at=entry.get('published', 'NO_DATE'),
                    raw_content=clean_summary # Initial content is the summary
                ))
        except Exception as e:
            logger.debug(f"Error processing feed {url}: {e}")
            
        return articles

    async def fetch_from_feeds(self, feeds: List[str]) -> List[NewsDTO]:
        """Main entry point: Fetch all feeds in parallel."""
        target_feeds = feeds if feeds else self.default_feeds
        all_results = []
        
        logger.info(f"Starting parallel fetch for {len(target_feeds)} feeds.")
        
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            # Gather all feed processing tasks
            tasks = [self._process_single_feed(session, url) for url in target_feeds]
            feed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in feed_results:
                if isinstance(res, list):
                    all_results.extend(res)
                    
        return all_results

    async def search_web(self, query: str, limit: int = 5) -> List[NewsDTO]:
        """
        Placeholder for web search. 
        Will implement local database search in Phase 4.
        """
        return []
