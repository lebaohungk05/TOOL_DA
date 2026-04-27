import asyncio
import logging
import nodriver as uc
from bs4 import BeautifulSoup
from src.news.fetchers.protocol import ContentFetcherProtocol

logger = logging.getLogger(__name__)

class NodriverFetcher(ContentFetcherProtocol):
    """
    High-stealth fetcher using 'nodriver' to bypass advanced anti-bot (DataDome).
    Succesor to undetected-chromedriver.
    """

    def __init__(self, concurrent_limit: int = 1):
        # Nodriver connects to real browser, keep concurrency low
        self._semaphore = asyncio.Semaphore(concurrent_limit)
        self._blacklist = ["msn.com"]

    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Fetch HTML from multiple URLs using a single browser instance.
        """
        if not urls:
            return []

        results = [""] * len(urls)
        
        async with self._semaphore:
            try:
                # Start browser
                browser = await uc.start()
                
                for i, url in enumerate(urls):
                    if any(domain in url for domain in self._blacklist):
                        continue
                        
                    try:
                        logger.debug(f"Nodriver: Fetching {url}")
                        page = await browser.get(url)
                        
                        # Wait for potential challenges and hydration
                        await asyncio.sleep(5)
                        
                        html = await page.get_content()
                        results[i] = self._extract_text(html)
                        
                    except Exception as e:
                        logger.error(f"Nodriver failed for {url}: {e}")

                try:
                    await browser.stop()
                except:
                    pass
                
            except Exception as e:
                logger.error(f"Nodriver browser error: {e}")
                
        return results

    def _extract_text(self, html: str) -> str:
        """Heuristic extraction of article body."""
        if not html:
            return ""
            
        soup = BeautifulSoup(html, "html.parser")
        
        # Strip unwanted
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
            tag.decompose()

        # Try common article containers
        main_content = soup.find("article") or soup.find("main")
        if not main_content:
            candidates = soup.find_all(["div", "section"])
            if candidates:
                main_content = max(candidates, key=lambda d: len(d.get_text()), default=None)

        if not main_content:
            return ""

        text = " ".join(main_content.get_text(separator=' ').split())
        return text
