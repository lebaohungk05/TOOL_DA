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

    def __init__(self, concurrent_limit: int = 20):
        self._semaphore = asyncio.Semaphore(concurrent_limit)
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._timeout = aiohttp.ClientTimeout(total=10)
        self._blacklist = []  # Removed msn.com to allow fetching from MSN news links

    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Fetch HTML from multiple URLs concurrently.
        """
        if not urls:
            logger.debug("No URLs to fetch. Success rate: 0%")
            return []
        results = []
        batch_size = 20
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            for i in range(0, len(urls), batch_size):
                if i > 0:
                    logger.debug("Waiting 5 seconds before fetching next batch for same source...")
                    await asyncio.sleep(5)
                batch = urls[i:i + batch_size]
                tasks = [self._fetch_single(session, url) for url in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
            
            success_count = sum(1 for res in results if res)
            success_rate = (success_count / len(urls)) * 100
            logger.debug(f"Fetched {success_count}/{len(urls)} articles successfully ({success_rate:.2f}%)")
            return results

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

                    # Remove noise
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "button"]):
                        tag.decompose()

                    main_content = None
                    
                    # Site-specific selectors for Vietnamese News
                    if "vnexpress.net" in url:
                        main_content = soup.find("article", class_="fck_detail") or soup.find("div", class_="fck_detail")
                    elif "tuoitre.vn" in url:
                        main_content = soup.find("div", id="main-detail-body") or soup.find("div", class_="content-fck")
                    elif "thanhnien.vn" in url:
                        main_content = soup.find("div", class_="detail-content") or soup.find("div", id="abody")
                    elif "vietnamnet.vn" in url:
                        main_content = soup.find("div", class_="maincontent") or soup.find("div", id="contentDetailV1")
                    elif "msn.com" in url:
                        # MSN specific structure
                        main_content = soup.find("div", class_="content-container") or soup.find("article")
                    
                    # Fallback to general selectors
                    if not main_content:
                        main_content = soup.find("article") or soup.find("main")
                    
                    if not main_content:
                        # Find the div with the most text as a last resort
                        candidates = soup.find_all(["div", "section"])
                        if candidates:
                            # Filter out small divs and those that look like sidebars
                            main_content = max(candidates, key=lambda d: len(d.get_text()), default=None)

                    if not main_content:
                        return ""

                    # Clean up the text: remove extra whitespace and newlines
                    text = " ".join(main_content.get_text(separator=' ').split())
                    return text

            except Exception as e:
                logger.debug(f"Failed to fetch {url}: {e}")
                return ""

