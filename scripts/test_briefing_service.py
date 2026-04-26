import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.models import NewsDTO, UserConfigDTO
from src.services.briefing_service import BriefingService

async def test_scheduled_briefing_orchestration():
    print("Testing Scheduled Briefing Orchestration...")
    
    # Mocking dependencies
    mock_news = AsyncMock()
    mock_ai = AsyncMock()
    mock_storage = AsyncMock()
    mock_messenger = AsyncMock()
    
    service = BriefingService(mock_news, mock_ai, mock_storage, mock_messenger)
    
    # Setup mock returns
    # We specify language="en" here to verify propagation
    mock_storage.get_user_config.return_value = UserConfigDTO(
        user_id=123, 
        chat_id=123, 
        follow_keywords=[], 
        block_keywords=[], 
        language="en"
    )
    mock_news.fetch_from_feeds.return_value = [
        NewsDTO("", "Title 1", "url1", "src1", "raw1")
    ]
    mock_ai.summarize_news.return_value = "Summary 1"
    mock_storage.archive_news_items.return_value = ["id1"]
    
    # Execute
    await service.run_scheduled_briefing(chat_id=123)
    
    # Verify calls (propagation of lang="en")
    mock_news.fetch_from_feeds.assert_called_once()
    mock_ai.summarize_news.assert_called_once_with("raw1", "en")
    mock_storage.archive_news_items.assert_called_once()
    mock_messenger.send_briefing.assert_called_once_with(123, [NewsDTO("id1", "Title 1", "url1", "src1", "raw1", "Summary 1")], "en")
    
    print("✓ Scheduled briefing orchestration test passed!")

async def test_deep_dive_orchestration():
    print("\nTesting Deep-dive Orchestration...")
    
    mock_news = AsyncMock()
    mock_ai = AsyncMock()
    mock_storage = AsyncMock()
    mock_messenger = AsyncMock()
    
    service = BriefingService(mock_news, mock_ai, mock_storage, mock_messenger)
    
    # Setup mocks
    mock_storage.get_user_config.return_value = UserConfigDTO(123, 123, [], [], language="vi")
    mock_storage.get_article_by_id.return_value = NewsDTO("id1", "Title 1", "url1", "src1", "raw1")
    mock_ai.extract_search_queries.return_value = ["query1"]
    mock_news.search_web.return_value = [NewsDTO("sid1", "Web Result", "wurl1", "wsrc1", "wraw1")]
    mock_ai.synthesize_response.return_value = "Final Synthesis"
    
    # Execute
    await service.run_deep_dive(chat_id=123, article_id="id1", question="What's new?")
    
    # Verify sequence (propagation of lang="vi")
    mock_storage.get_article_by_id.assert_called_with("id1")
    mock_ai.extract_search_queries.assert_called_with("What's new?", "vi")
    mock_news.search_web.assert_called_with("query1")
    mock_ai.synthesize_response.assert_called_once_with([NewsDTO("id1", "Title 1", "url1", "src1", "raw1"), NewsDTO("sid1", "Web Result", "wurl1", "wsrc1", "wraw1")], "What's new?", "vi")
    mock_messenger.send_deep_dive_response.assert_called_once_with(123, "Final Synthesis", ["url1", "wurl1"], "vi")
    
    print("✓ Deep-dive orchestration test passed!")

async def main():
    await test_scheduled_briefing_orchestration()
    await test_deep_dive_orchestration()

if __name__ == "__main__":
    asyncio.run(main())
