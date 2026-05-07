import asyncio
import sys
import os

# Ensure import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.database.sqlite_storage import SQLiteStorage
from src.news.rss_crawler import RSSCrawler
from src.models import NewsDTO

async def final_test():
    print("--- STARTING FINAL HYBRID SEARCH TEST ---")
    
    db = SQLiteStorage()
    await db.connect()
    crawler = RSSCrawler()
    
    # 1. TEST CASE 1: Search for something NOT in database (Forces Web Search)
    query = "giá vàng thế giới mới nhất"
    print(f"\n[*] Case 1: Searching for '{query}' (Likely web search)...")
    
    # Simulate the service logic
    local_results = await db.search_news(query, limit=5, max_age_days=1)
    
    if not local_results:
        print("[!] No local results. Triggering Brave Search...")
        web_results = await crawler.search_web(query, limit=3)
        if web_results:
            print(f"[v] FOUND {len(web_results)} results on the web!")
            for i, r in enumerate(web_results):
                print(f"  {i+1}. {r.title}")
                print(f"     URL: {r.url}")
        else:
            print("[x] Web search failed or found nothing.")
    else:
        print(f"[v] Found {len(local_results)} results in Database.")

    await db.disconnect()
    print("\n--- FINAL TEST COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(final_test())
