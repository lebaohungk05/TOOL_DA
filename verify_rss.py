import asyncio
import sys
import os

# Ensure the project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.news.rss_crawler import RSSCrawler

async def test_clean_parallel_crawl():
    crawler = RSSCrawler()
    
    # Test with a mix of local and international feeds
    test_feeds = [
        "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ]
    
    print(f"--- STARTING CLEAN PARALLEL CRAWL TEST ---")
    
    # Fetch news (Now returns raw articles without internal filtering)
    articles = await crawler.fetch_from_feeds(test_feeds)
    
    print(f"Total articles found: {len(articles)}")
    print("-" * 60)
    
    # Display the first 3 articles to check for clean summary
    for i, article in enumerate(articles[:3]):
        print(f"Article {i+1}: [{article.source}] {article.title}")
        print(f"Summary: {article.summary[:300]}...") # Should be clean text now
        print(f"Link: {article.url}")
        print("-" * 30)

if __name__ == "__main__":
    # Check for dependencies
    try:
        import aiohttp
        import bs4
        import feedparser
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install: pip install aiohttp beautifulsoup4 feedparser")
        sys.exit(1)
        
    asyncio.run(test_clean_parallel_crawl())
