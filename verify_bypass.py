import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.news.rss_crawler import RSSCrawler

async def test_full_bypass():
    crawler = RSSCrawler()
    
    # Thử lấy nội dung chi tiết một trang cực khó (Reuters)
    hard_url = "https://www.reuters.com/technology/ai-startups-race-develop-smarter-robots-2024-04-20/"
    
    print(f"--- TESTING ADVANCED BYPASS ENGINE ---")
    print(f"Target: {hard_url}")
    
    content = await crawler.get_full_content(hard_url)
    
    if content:
        print(f"\n[v] BYPASS SUCCESSFUL!")
        print(f"Content Length: {len(content)} chars")
        print(f"Snippet: {content[:500]}...")
    else:
        print("\n[x] Bypass failed. Site security might be too high for this IP.")

if __name__ == "__main__":
    asyncio.run(test_full_bypass())
