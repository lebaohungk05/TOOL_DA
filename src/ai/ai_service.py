import logging

from src.ai.protocol import AIServiceProtocol
from src.ai.providers.protocol import LLMProviderProtocol
from src.models import NewsDTO
from src.core.i18n import get_text

logger = logging.getLogger(__name__)


class AIService(AIServiceProtocol):
    """
    Core AI Service implementation bridging domain use cases to generic LLM providers.
    
    This service treats the AI as 'eyes and ears only', focusing on factual
    processing and summarization without subjective analysis. Relies on the
    injected provider (Ollama, OpenAI, etc.) for actual LLM communication.
    """

    def __init__(self, provider: LLMProviderProtocol):
        """
        Initialize the AI service with a specific LLM Provider.
        
        Args:
            provider: Adaptive port implementation for the selected LLM.
        """
        self.provider = provider

    async def summarize_news(self, raw_content: str, language: str = "vi") -> str:
        """
        Summarize news content into a maximum of 2 sentences in the target language.
        """
        prompt = get_text("prompt_summarizer", language, content=raw_content)
        messages = [{"role": "user", "content": prompt}]
        return await self.provider.chat(messages)

    async def extract_search_queries(self, user_prompt: str, language: str = "vi") -> str:
        """
        Produce a single search-optimized string.
        """
        prompt = get_text("prompt_query_designer", language, user_prompt=user_prompt)
        messages = [{"role": "user", "content": prompt}]
        response = await self.provider.chat(messages)
        
        return response.strip().strip('"')

    def _format_articles(self, articles: list[NewsDTO]) -> str:
        """Format articles into a text block for the LLM."""
        formatted = []
        for i, art in enumerate(articles, 1):
            formatted.append(
                f"--- Article {i} ---\n"
                f"Title: {art.title}\n"
                f"Source: {art.source}\n"
                f"Content: {art.raw_content or art.summary}\n"
            )
        return "\n".join(formatted)

    async def synthesize_response(self, articles: list[NewsDTO], question: str, language: str = "vi") -> str:
        """
        Synthesize a factual response based on provided articles and a question.
        """
        formatted_articles = self._format_articles(articles)
        prompt = get_text(
            "prompt_synthesizer", 
            language, 
            articles=formatted_articles, 
            question=question
        )
        messages = [{"role": "user", "content": prompt}]
        return await self.provider.chat(messages)
