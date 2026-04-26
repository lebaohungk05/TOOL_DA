from src.news.rss_crawler import RSSCrawler
import asyncio
import sys
import os

# Ensure the project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


async def test_full_content_crawl():
    crawler = RSSCrawler()

    # Test with a few specific feeds for speed
    test_feeds = [
        "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ]

    print(f"--- STARTING FULL CONTENT TEST ---")

    # Fetch news
    articles = await crawler.fetch_from_feeds(test_feeds)

    print(f"Total articles found after filtering: {len(articles)}")
    print("-" * 60)

    # Display the first 3 articles with content info
    for i, article in enumerate(articles[:3]):
        print(f"Article {i+1}: [{article.source}] {article.title}")
        print(f"Link: {article.url}")

        # Check if full content was captured
        content_len = len(article.raw_content)
        print(f"Full Content Size: {content_len} characters")

        print(f"Raw content: {article.raw_content}")
        print(f"Summary: {article.summary}")

        print("-" * 30)

if __name__ == "__main__":
    # Check for missing dependencies
    try:
        import aiohttp
        import bs4
    except ImportError:
        print("Please install missing tools: pip install aiohttp beautifulsoup4")
        sys.exit(1)

    asyncio.run(test_full_content_crawl())
