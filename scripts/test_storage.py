import asyncio
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.models import NewsDTO, UserConfigDTO
from src.database.sqlite_storage import SQLiteStorage

async def test_user_config(storage: SQLiteStorage):
    print("Testing User Configuration...")
    user_id = 999
    config = UserConfigDTO(
        user_id=user_id,
        chat_id=12345,
        follow_keywords=["Python", "AI"],
        block_keywords=["Spam"],
        briefing_times=["09:00", "21:00"]
    )
    
    await storage.upsert_user_config(user_id, config)
    retrieved = await storage.get_user_config(user_id)
    
    assert retrieved is not None
    assert retrieved.user_id == user_id
    assert retrieved.chat_id == 12345
    assert "Python" in retrieved.follow_keywords
    assert retrieved.briefing_times == ["09:00", "21:00"]
    print("✓ User Configuration test passed!")

async def test_news_archive(storage: SQLiteStorage):
    print("Testing News Archiving...")
    news = [
        NewsDTO(
            article_id="", # Test hash generation
            title="Tech News Today",
            url="https://example.com/tech",
            source="ExampleSource",
            summary="Something happened in tech."
        ),
        NewsDTO(
            article_id="manual_id_1",
            title="Manual News",
            url="https://example.com/manual",
            source="ManualSource",
            raw_content="Large text content here."
        )
    ]
    
    ids = await storage.archive_news_items(news)
    assert len(ids) == 2
    assert ids[1] == "manual_id_1"
    
    # Retrieve hashed one
    retrieved_hashed = await storage.get_article_by_id(ids[0])
    assert retrieved_hashed is not None
    assert retrieved_hashed.title == "Tech News Today"
    assert retrieved_hashed.url == "https://example.com/tech"
    
    # Retrieve manual one
    retrieved_manual = await storage.get_article_by_id("manual_id_1")
    assert retrieved_manual is not None
    assert retrieved_manual.raw_content == "Large text content here."
    print("✓ News Archiving test passed!")

async def main():
    db_file = "data/test_news_agent.db"
    
    # Clean up previous test db
    if os.path.exists(db_file):
        os.remove(db_file)
        
    storage = SQLiteStorage(db_path=db_file)
    try:
        await storage.connect()
        await test_user_config(storage)
        await test_news_archive(storage)
    finally:
        await storage.disconnect()
        if os.path.exists(db_file):
            os.remove(db_file)

if __name__ == "__main__":
    asyncio.run(main())
