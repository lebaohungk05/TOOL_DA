from typing import Protocol
from src.models import NewsDTO
class NewsRepositoryProtocol(Protocol):
    async def fetch_from_feeds(self, feeds: list[str], 
                               follow_keywords: list[str] = None, 
                               block_keywords: list[str] = None) -> list[NewsDTO]:
        """Fetch news from feeds with optional filtering."""
        ...

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """search and crawl full content of each return page"""
        ...
