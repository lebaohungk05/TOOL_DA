from typing import Protocol
from src.models import NewsDTO

class AIServiceProtocol(Protocol):
    async def summarize_news(self, raw_content: str, language: str = "vi") -> str:
        """Summarize news content into a maximum of 2 sentences in the target language."""
        ...

    async def extract_search_queries(self, user_prompt: str, language: str = "vi") -> str:
        """Extract a single optimized search query from a user prompt."""
        ...

    async def synthesize_response(self, articles: list[NewsDTO], question: str, language: str = "vi") -> str:
        """Synthesize a factual response based on provided articles and a question in the target language."""
        ...
