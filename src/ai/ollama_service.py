import logging
import os
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
from src.ai.protocol import AIServiceProtocol
from src.models import NewsDTO
from src.core.i18n import get_text

# Setup logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv(override=True)

class AIServiceError(Exception):
    """Base exception for all AI service related errors."""
    pass

class AIServiceConnectionError(AIServiceError):
    """Raised when the AI service (Ollama) is unreachable or times out."""
    pass

class OllamaAIService(AIServiceProtocol):
    """
    Implementation of AIServiceProtocol using the local Ollama API.
    
    This service treats the AI as 'eyes and ears only', focusing on factual
    processing and summarization without subjective analysis.
    """

    def __init__(self, model: str | None = None, host: str | None = None):
        """
        Initialize the Ollama AI service.
        
        Args:
            model: The name of the model to use (default: $OLLAMA_MODEL).
            host: The Ollama server URL (default: $OLLAMA_HOST).
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma4:E4B")
        host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = AsyncClient(host=host)

    async def _call(self, messages: list[dict[str, str]]) -> str:
        """
        Execute a chat call to Ollama with error handling.
        
        Args:
            messages: List of chat messages in Ollama format.
            
        Returns:
            The content of the AI response.
        """
        logger.debug(f"Calling Ollama (model={self.model}) with messages: {messages}")
        try:
            response = await self.client.chat(model=self.model, messages=messages)
            content = response.message.content or ""
            logger.debug(f"Ollama response: {content}")
            return content
        except ResponseError as e:
            logger.error(f"Ollama API error: {e.error}")
            raise AIServiceConnectionError(f"Ollama API error: {e.error}") from e
        except Exception as e:
            logger.error(f"Ollama connection failure: {str(e)}")
            raise AIServiceConnectionError(f"Ollama connection failed: {str(e)}") from e

    async def summarize_news(self, raw_content: str, language: str = "vi") -> str:
        """
        Summarize news content into a maximum of 2 sentences in the target language.
        """
        prompt = get_text("prompt_summarizer", language, content=raw_content)
        messages = [{"role": "user", "content": prompt}]
        return await self._call(messages)

    async def extract_search_queries(self, user_prompt: str, language: str = "vi") -> list[str]:
        """
        Extract search keywords from a user prompt.
        """
        prompt = get_text("prompt_query_designer", language, user_prompt=user_prompt)
        messages = [{"role": "user", "content": prompt}]
        response = await self._call(messages)
        
        # Post-processing: Split by comma and clean up
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        return keywords[:5]

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
        return await self._call(messages)
