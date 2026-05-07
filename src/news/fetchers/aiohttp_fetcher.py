import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from src.news.fetchers.protocol import ContentFetcherProtocol

logger = logging.getLogger(__name__)

class AioHttpFetcher(ContentFetcherProtocol):
    """
    Standard fetcher using aiohttp and BeautifulSoup for static HTML extraction.
    """

    def __init__(self, concurrent_limit: int = 10):
        self._semaphore = asyncio.Semaphore(concurrent_limit)
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._timeout = aiohttp.ClientTimeout(total=10)
        self._blacklist = ["msn.com"]

    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Fetch HTML from multiple URLs concurrently.
        """
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            tasks = [self._fetch_single(session, url) for url in urls]
            return list(await asyncio.gather(*tasks))

    async def _fetch_single(self, session: aiohttp.ClientSession, url: str) -> str:
        """Helper to fetch a single URL with semantic extraction."""
        if any(domain in url for domain in self._blacklist):
            logger.debug(f"Skipping blacklisted domain: {url}")
            return ""

        async with self._semaphore:
            try:
                async with session.get(url, headers=self._headers) as response:
                    if response.status != 200:
                        logger.debug(f"Source {url} returned status {response.status}")
                        return ""
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
                        tag.decompose()

                    main_content = soup.find("article") or soup.find("main")
                    if not main_content:
                        candidates = soup.find_all(["div", "section"])
                        if candidates:
                            main_content = max(candidates, key=lambda d: len(d.get_text()), default=None)

                    if not main_content:
                        return ""

                    text = " ".join(main_content.get_text(separator=' ').split())
                    return text

            except Exception as e:
                logger.debug(f"Failed to fetch {url}: {e}")
                return ""

