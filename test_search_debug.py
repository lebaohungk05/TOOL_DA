import asyncio
import logging
import sys
from dotenv import load_dotenv

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

from src.news.rss_crawler import RSSCrawler
from src.news.fetchers.smart_fetcher import SmartFetcher

async def test_search():
    load_dotenv()
    
    print("\n--- TESTING WEB SEARCH (DuckDuckGo) ---")
    fetcher = SmartFetcher()
    crawler = RSSCrawler(fetcher=fetcher)
    
    query = "giá xăng dầu hôm nay"
    print(f"Searching for: {query}")
    
    try:
        results = await crawler.search_web(query, limit=3)
        print(f"Found {len(results)} results.")
        for i, res in enumerate(results, 1):
            print(f"\n{i}. {res.title}")
            print(f"   Source: {res.source}")
            print(f"   URL: {res.url}")
            print(f"   Content Length: {len(res.raw_content)}")
            if len(res.raw_content) < 50:
                print(f"   CONTENT TOO SHORT: {res.raw_content}")
    except Exception as e:
        print(f"SEARCH FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
