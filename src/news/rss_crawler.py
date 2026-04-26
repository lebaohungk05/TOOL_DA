import asyncio
import logging
import hashlib
import re
from typing import List, Optional

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
    Supports high-concurrency fetching and dynamic Regex-based filtering.
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
        """Fetch HTML page and extract main text content using BeautifulSoup."""
        async with self._semaphore:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ""
                    html = await response.text()

                    soup = BeautifulSoup(html, "html.parser")
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        tag.decompose()

                    main_content = soup.find("article") or soup.find("body")
                    if not main_content:
                        return ""

                    text = main_content.get_text(separator=' ')
                    return " ".join(text.split())[:5000]

            except Exception as e:
                logger.debug(f"Failed to fetch content for {url}: {e}")
                return ""

    async def _process_feed(self, session: aiohttp.ClientSession, url: str) -> List[NewsDTO]:
        """Process a single RSS feed and fetch full content for entries."""
        articles = []
        try:
            async with self._semaphore:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []
                    xml_content = await response.text()

            feed = feedparser.parse(xml_content)
            source_title = feed.feed.get('title', 'UNKNOWN_SOURCE')
            
            async def process_entry(entry) -> NewsDTO | None:
                article_url = entry.get('link', '')
                if not article_url: return None
                    
                full_content = await self._fetch_full_content(session, article_url)
                summary = entry.get('summary', 'NO_SUMMARY')
                
                return NewsDTO(
                    article_id=self._generate_article_id(article_url),
                    title=entry.get('title', 'NO_TITLE'),
                    url=article_url,
                    source=source_title,
                    summary=summary,
                    published_at=entry.get('published', 'NO_DATE'),
                    raw_content=full_content if full_content else summary
                )

            results = await asyncio.gather(*(process_entry(e) for e in feed.entries), return_exceptions=True)
            for res in results:
                if isinstance(res, NewsDTO):
                    articles.append(res)
                
        except Exception as e:
            logger.debug(f"Failed to process feed {url}: {e}")
            
        return articles

    async def fetch_from_feeds(self, feeds: list[str], 
                               follow_keywords: list[str] = None, 
                               block_keywords: list[str] = None) -> list[NewsDTO]:
        """Fetch news from RSS feeds with high concurrency and apply filtering."""
        target_feeds = feeds if feeds else self.default_feeds
        logger.info(f"Initiating concurrent crawl from {len(target_feeds)} sources.")
        
        all_articles: List[NewsDTO] = []
        
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            tasks = [self._process_feed(session, url) for url in target_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    all_articles.extend(res)
                    
        # Apply dynamic filtering logic
        return self._filter_logic(all_articles, follow_keywords or [], block_keywords or [])

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """Perform ad-hoc web search using DuckDuckGo."""
        results = []
        def ddg_sync():
            with DDGS() as ddgs:
                return list(ddgs.news(query, max_results=limit))

        try:
            search_results = await asyncio.to_thread(ddg_sync)
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async def process_search_result(r) -> NewsDTO | None:
                    url = r.get('url', '')
                    if not url: return None
                    
                    full_content = await self._fetch_full_content(session, url)
                    summary = r.get('body', 'NO_SUMMARY')
                    
                    return NewsDTO(
                        article_id=self._generate_article_id(url),
                        title=r.get('title', 'NO_TITLE'),
                        url=url,
                        source=r.get('source', 'DUCKDUCKGO'),
                        summary=summary,
                        published_at=r.get('date', 'NO_DATE'),
                        raw_content=full_content if full_content else summary
                    )
                
                tasks = [process_search_result(r) for r in search_results]
                gathered = await asyncio.gather(*tasks, return_exceptions=True)
                for res in gathered:
                    if isinstance(res, NewsDTO):
                        results.append(res)
                        
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            
        return results

    def _filter_logic(self, articles: List[NewsDTO], follow: List[str], block: List[str]) -> List[NewsDTO]:
        """Filter articles based on block list and prioritize followed keywords using Regex."""
        if not follow and not block:
            return articles

        block_patterns = [re.compile(rf"\b{re.escape(kw.lower())}\b") for kw in block]
        follow_patterns = [re.compile(rf"\b{re.escape(kw.lower())}\b") for kw in follow]
        
        prioritized = []
        normal = []

        for article in articles:
            # Check both title and content/summary for keywords
            content_to_check = (article.title + " " + article.summary).lower()
            
            # Exclusion logic (Block)
            if any(p.search(content_to_check) for p in block_patterns):
                continue
            
            # Prioritization logic (Follow)
            if any(p.search(content_to_check) for p in follow_patterns):
                prioritized.append(article)
            else:
                normal.append(article)
                
        return prioritized + normal
