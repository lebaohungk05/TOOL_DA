import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.models import NewsDTO
from src.bot.formatter import TelegramFormatter
from src.bot.messenger import TelegramMessenger

async def test_formatter():
    print("Testing TelegramFormatter...")
    formatter = TelegramFormatter()
    
    news = [
        NewsDTO(
            article_id="1",
            title="Python 3.13 Released!",
            url="https://python.org",
            source="Official",
            summary="New features including a JIT compiler."
        ),
        NewsDTO(
            article_id="2",
            title="AI is evolving fast [News!]",
            url="https://ai.com/news?status=active",
            source="AI-Blog",
            summary="Large language models are getting better at reasoning."
        )
    ]
    
    briefing = formatter.format_briefing(news)
    print("--- Briefing Output ---")
    print(briefing)
    print("-----------------------")
    
    # Check for escaping
    assert "\\[News\\!\\]" in briefing
    assert "Official" in briefing
    print("✓ Formatter test passed!")

async def test_messenger():
    print("\nTesting TelegramMessenger (Mocked)...")
    mock_bot = AsyncMock()
    formatter = TelegramFormatter()
    messenger = TelegramMessenger(mock_bot, formatter)
    
    news_items = [
        NewsDTO(article_id="id1", title="Title 1", url="url1", source="src1", summary="sum1")
    ]
    
    await messenger.send_briefing(chat_id=123, news_items=news_items)
    
    # Verify bot.send_message was called
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert kwargs['chat_id'] == 123
    assert 'Title 1' in kwargs['text']
    assert kwargs['reply_markup'] is not None
    print("✓ Messenger mock test passed!")

async def main():
    await test_formatter()
    await test_messenger()

if __name__ == "__main__":
    asyncio.run(main())
