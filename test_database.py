import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'news_agent')))
from src.database.manager import DatabaseManager
from src.models import UserConfigDTO

async def test_db():
    db = DatabaseManager()
    await db.initialize()
    
    # New structure according to project models
    test_user = UserConfigDTO(
        user_id=12345,
        chat_id=67890,
        follow_keywords=["AI", "Python"],
        block_keywords=["Drama"],
        briefing_times=["08:00", "20:00"]
    )
    
    print("--- TESTING DATABASE SAVE ---")
    await db.save_user_config(test_user)
    
    print("--- TESTING DATABASE RETRIEVAL ---")
    config = await db.get_user_config(12345)
    
    if config:
        print(f"User ID: {config.user_id}")
        print(f"Follow: {config.follow_keywords}")
        print(f"Times: {config.briefing_times}")
    else:
        print("Failed to retrieve user!")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_db())
