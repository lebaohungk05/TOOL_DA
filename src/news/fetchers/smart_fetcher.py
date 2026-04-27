import asyncio
import logging
from src.news.fetchers.protocol import ContentFetcherProtocol
from src.news.fetchers.aiohttp_fetcher import AioHttpFetcher
from src.news.fetchers.nodriver_fetcher import NodriverFetcher

logger = logging.getLogger(__name__)

class SmartFetcher(ContentFetcherProtocol):
    """
    Orchestrates multiple fetchers, choosing the best one based on domain.
    """

    def __init__(self):
        self.basic = AioHttpFetcher()
        self.browser = NodriverFetcher()
        # Domains known to block simple scraping
        self.hard_domains = ["reuters.com", "bloomberg.com", "nytimes.com"]

    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Split URLs into 'easy' and 'hard' categories and use appropriate fetchers.
        """
        hard_urls = []
        easy_urls = []
        
        # Track original indices to reassemble in order
        for url in urls:
            if any(domain in url for domain in self.hard_domains):
                hard_urls.append(url)
            else:
                easy_urls.append(url)
        
        # Fetch concurrently
        async def empty_list(): return []
        
        hard_task = self.browser.fetch_contents(hard_urls) if hard_urls else empty_list()
        easy_task = self.basic.fetch_contents(easy_urls) if easy_urls else empty_list()
        
        hard_results, easy_results = await asyncio.gather(hard_task, easy_task)
        
        # Reassemble
        results_map = {}
        for url, res in zip(hard_urls, hard_results):
            results_map[url] = res
        for url, res in zip(easy_urls, easy_results):
            results_map[url] = res
            
        return [results_map[url] for url in urls]
