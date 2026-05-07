import asyncio
import logging
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from src.news.fetchers.protocol import ContentFetcherProtocol

logger = logging.getLogger(__name__)

class BypassFetcher(ContentFetcherProtocol):
    """
    Advanced fetcher using curl_cffi to impersonate real browsers.
    This bypasses TLS fingerprints and other anti-bot protections.
    """

    def __init__(self, concurrent_limit: int = 5):
        self._semaphore = asyncio.Semaphore(concurrent_limit)
        # We use chrome impersonation to look like a real browser
        self._impersonate = "chrome110"
        self._timeout = 30
        self._blacklist = []

    async def fetch_contents(self, urls: list[str]) -> list[str]:
        """
        Fetch HTML from multiple URLs concurrently using browser impersonation.
        """
        async with AsyncSession() as session:
            tasks = [self._fetch_single(session, url) for url in urls]
            return list(await asyncio.gather(*tasks))

    async def _fetch_single(self, session: AsyncSession, url: str) -> str:
        """Helper to fetch a single URL with browser impersonation."""
        if any(domain in url for domain in self._blacklist):
            logger.debug(f"Skipping blacklisted domain: {url}")
            return ""

        async with self._semaphore:
            try:
                # curl_cffi handles headers and TLS fingerprints automatically
                response = await session.get(
                    url, 
                    impersonate=self._impersonate, 
                    timeout=self._timeout
                )
                
                if response.status_code != 200:
                    logger.debug(f"Source {url} returned status {response.status_code}")
                    return ""
                
                html = response.text
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
                    main_content = soup.find("div", class_="content-container") or soup.find("article")
                
                # Fallback to general selectors
                if not main_content:
                    main_content = soup.find("article") or soup.find("main")
                
                if not main_content:
                    candidates = soup.find_all(["div", "section"])
                    if candidates:
                        main_content = max(candidates, key=lambda d: len(d.get_text()), default=None)

                if not main_content:
                    return ""

                # Clean up the text
                text = " ".join(main_content.get_text(separator=' ').split())
                return text

            except Exception as e:
                logger.debug(f"Failed to fetch {url} via bypass: {e}")
                return ""
