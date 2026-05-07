import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.database.sqlite_storage import SQLiteStorage
from src.models import NewsDTO

async def verify_search():
    db = SQLiteStorage()
    await db.connect()
    
    # 1. Thêm thử một số tin với thời gian khác nhau (giả lập)
    # Lưu ý: Hàm archive_news_items sẽ dùng timestamp hiện tại của hệ thống
    test_news = [
        NewsDTO(article_id="1", title="Tin rất mới về Bitcoin", url="u1", source="S1", summary="Nội dung mới"),
        NewsDTO(article_id="2", title="Tin cũ về AI", url="u2", source="S2", summary="Nội dung cũ")
    ]
    await db.archive_news_items(test_news)
    
    # 2. Thử tìm kiếm
    query = "Bitcoin"
    print(f"--- TESTING SMART SEARCH FOR: '{query}' ---")
    results = await db.search_news(query, limit=5, max_age_days=1)
    
    print(f"Found {len(results)} recent articles.")
    for n in results:
        print(f"- {n.title} (Source: {n.source})")
        
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_search())
