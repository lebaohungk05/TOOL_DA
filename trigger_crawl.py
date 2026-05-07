import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.database.sqlite_storage import SQLiteStorage
from src.news.rss_crawler import RSSCrawler
from src.models import NewsDTO

async def manual_crawl_and_store():
    print("[*] ĐANG KÍCH HOẠT CRAWLER NẠP TIN VÀO DATABASE...")
    
    crawler = RSSCrawler()
    db = SQLiteStorage()
    await db.connect()
    
    # 1. Quét toàn bộ các nguồn mặc định (60+ nguồn)
    articles = await crawler.fetch_from_feeds(None)
    
    print(f"[v] Đã quét xong! Tìm thấy {len(articles)} tin mới.")
    
    # 2. Nạp vào Database
    print("[*] Đang lưu vào Database...")
    await db.archive_news_items(articles)
    
    print("[v] HOÀN TẤT! Bây giờ ông có thể vào Telegram để tìm kiếm thoải mái.")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(manual_crawl_and_store())
