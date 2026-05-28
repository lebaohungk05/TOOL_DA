from typing import Protocol
from src.models import NewsDTO
class NewsRepositoryProtocol(Protocol):
    async def fetch_from_feeds(self, feeds: list[str]) -> list[NewsDTO]:
        """fetch new from feeds."""
        ...

    async def search_web(self, query: str, limit: int = 5) -> list[NewsDTO]:
        """search and crawl full content of each return page"""
        ...
