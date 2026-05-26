import hashlib
import logging
import asyncio
import urllib.parse
from dataclasses import replace

import aiohttp
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

    async def _process_feed(self, session: aiohttp.ClientSession, url: str) -> list[NewsDTO]:
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

        all_articles: list[NewsDTO] = []
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

    def _parse_vietnamnet_search(self, html: str) -> list[NewsDTO]:
        """Parse search results from VietnamNet."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        posts = soup.select(".horizontalPost")
        for post in posts:
            title_a = post.select_one("h3.horizontalPost__main-title a") or post.select_one("h3.vnn-title a")
            if not title_a:
                continue
            title = title_a.get_text(strip=True)
            url = title_a.get("href", "").strip()
            if not url:
                continue
            
            # Extract summary
            desc_div = post.select_one(".horizontalPost__main-desc")
            summary = desc_div.get_text(strip=True) if desc_div else title
            
            results.append(NewsDTO(
                article_id=self._generate_article_id(url),
                title=title,
                url=url,
                source="VietnamNet",
                summary=summary,
                published_at="TODAY",
                raw_content=summary
            ))
        return results

    def _parse_vnexpress_search(self, html: str) -> list[NewsDTO]:
        """Parse search results from VnExpress."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        titles = soup.select(".title-news a")
        for t in titles:
            title = t.get_text(strip=True)
            url = t.get("href", "").strip()
            if not url:
                continue
            
            parent = t.find_parent("article")
            summary = title
            if parent:
                desc_el = parent.select_one(".description")
                if desc_el:
                    summary = desc_el.get_text(strip=True)
            
            results.append(NewsDTO(
                article_id=self._generate_article_id(url),
                title=title,
                url=url,
                source="VnExpress",
                summary=summary,
                published_at="TODAY",
                raw_content=summary
            ))
        return results

    def _parse_thanhnien_search(self, html: str) -> list[NewsDTO]:
        """Parse search results from Thanh Nien."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        items = soup.select(".box-category-item") or soup.select(".box-category-content")
        if not items:
            h3s = soup.select("h3.box-title-text")
            items = h3s if h3s else []
            
        for item in items:
            if item.name == "h3":
                title_a = item.select_one("a")
                parent_container = item.parent
            else:
                title_a = item.select_one("h3.box-title-text a") or item.select_one("a.box-category-link-title")
                parent_container = item
                
            if not title_a:
                continue
            title = title_a.get_text(strip=True)
            url = title_a.get("href", "").strip()
            if not url:
                continue
            if url.startswith("/"):
                url = f"https://thanhnien.vn{url}"
            
            summary = title
            if parent_container:
                sapo_el = parent_container.select_one(".box-category-sapo") or parent_container.select_one("p[class*='sapo']")
                if sapo_el:
                    summary = sapo_el.get_text(strip=True)
                    
            results.append(NewsDTO(
                article_id=self._generate_article_id(url),
                title=title,
                url=url,
                source="Thanh Niên",
                summary=summary,
                published_at="TODAY",
                raw_content=summary
            ))
        return results

    def _parse_tuoitre_search(self, html: str) -> list[NewsDTO]:
        """Parse search results from Tuoi Tre."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        items = soup.select(".box-category-item") or soup.select(".box-category-content")
        if not items:
            h3s = soup.select("h3.box-title-text")
            items = h3s if h3s else []
            
        for item in items:
            if item.name == "h3":
                title_a = item.select_one("a")
                parent_container = item.parent
            else:
                title_a = item.select_one("h3.box-title-text a") or item.select_one("a.box-category-link-title")
                parent_container = item
                
            if not title_a:
                continue
            title = title_a.get_text(strip=True)
            url = title_a.get("href", "").strip()
            if not url:
                continue
            if url.startswith("/"):
                url = f"https://tuoitre.vn{url}"
            
            summary = title
            if parent_container:
                sapo_el = parent_container.select_one(".box-category-sapo") or parent_container.select_one("p[class*='sapo']")
                if sapo_el:
                    summary = sapo_el.get_text(strip=True)
                    
            results.append(NewsDTO(
                article_id=self._generate_article_id(url),
                title=title,
                url=url,
                source="Tuổi Trẻ",
                summary=summary,
                published_at="TODAY",
                raw_content=summary
            ))
        return results

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """
        Perform ad-hoc search via native Vietnamese news search portals.
        Aggregates results in parallel and extracts full text.
        """
        logger.info(f"Searching native Vietnamese portals for: {query}")
        
        encoded_q = urllib.parse.quote(query)
        search_endpoints = [
            {
                "url": f"https://vietnamnet.vn/tim-kiem?bydaterang=1&q={encoded_q}",
                "parser": self._parse_vietnamnet_search,
            },
            {
                "url": f"https://timkiem.vnexpress.net/?search_q={encoded_q}&cate_code=&media_type=all&latest=&fromdate=&todate=&date_format=day&",
                "parser": self._parse_vnexpress_search,
            },
            {
                "url": f"https://thanhnien.vn/tim-kiem.htm?keywords={encoded_q}&author=0&time=2&zone=0&type=1&sort=0",
                "parser": self._parse_thanhnien_search,
            },
            {
                "url": f"https://tuoitre.vn/tim-kiem.htm?keywords={encoded_q}",
                "parser": self._parse_tuoitre_search,
            },
        ]
        
        all_results = []
        try:
            async with aiohttp.ClientSession(timeout=self._timeout, headers=self._headers) as session:
                async def fetch_and_parse(endpoint):
                    url = endpoint["url"]
                    parser = endpoint["parser"]
                    try:
                        async with session.get(url) as response:
                            if response.status != 200:
                                logger.debug(f"Search endpoint {url} returned status {response.status}")
                                return []
                            html = await response.text()
                            return parser(html)
                    except Exception as e:
                        logger.debug(f"Failed to fetch search page {url}: {e}")
                        return []
                
                tasks = [fetch_and_parse(ep) for ep in search_endpoints]
                parsed_lists = await asyncio.gather(*tasks, return_exceptions=True)
                for parsed in parsed_lists:
                    if isinstance(parsed, list):
                        all_results.extend(parsed)
        except Exception as e:
            logger.error(f"Error executing parallel web search: {e}")
            
        # Deduplicate results based on URL
        seen_urls = set()
        unique_results = []
        for doc in all_results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
                
        # Limit the results
        limited_results = unique_results[:limit]
        
        # Fetch full contents for the limited results using the fetcher
        if limited_results:
            urls = [doc.url for doc in limited_results]
            try:
                full_contents = await self.fetcher.fetch_contents(urls)
                updated_results = []
                for doc, raw_c in zip(limited_results, full_contents):
                    if raw_c:
                        updated_results.append(replace(doc, raw_content=raw_c))
                    else:
                        updated_results.append(doc)
                limited_results = updated_results
            except Exception as e:
                logger.error(f"Error fetching full contents for search results: {e}")
                
        return limited_results

