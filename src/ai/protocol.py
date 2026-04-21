from typing import Protocol
from src.models import NewsDTO

class AIServiceProtocol(Protocol):
    async def summarize_news(self, raw_content: str) -> str:
        """Summarize news content into a maximum of 2 sentences."""
        ...

    async def extract_search_queries(self, user_prompt: str) -> list[str]:
        """Extract search keywords from a user prompt."""
        ...

    async def synthesize_response(self, articles: list[NewsDTO], question: str) -> str:
        """Synthesize a factual response based on provided articles and a question."""
        ...
