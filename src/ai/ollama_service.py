import logging
import os
from typing import Any
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
from src.ai.protocol import AIServiceProtocol
from src.models import NewsDTO

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
            model: The name of the model to use (default: $OLLAMA_MODEL or gemma4:E4B).
            host: The Ollama server URL (default: $OLLAMA_HOST or http://localhost:11434).
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
            
        Raises:
            AIServiceConnectionError: If connection fails or Ollama returns an error.
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
            # Catching generic exceptions from httpx or others as connection issues
            logger.error(f"Ollama connection failure: {str(e)}")
            raise AIServiceConnectionError(f"Ollama connection failed: {str(e)}") from e

    async def summarize_news(self, raw_content: str) -> str:
        """
        Summarize news content into a maximum of 2 sentences.
        """
        prompt = (
            "You are an objective news summarizer. "
            "Summarize the following content in EXACTLY 1 or 2 concise, factual sentences. "
            "Do NOT add any analysis, opinion, or introductory phrases (like 'This article is about').\n\n"
            f"Content: {raw_content}"
        )
        messages = [{"role": "user", "content": prompt}]
        return await self._call(messages)

    async def extract_search_queries(self, user_prompt: str) -> list[str]:
        """
        Extract search keywords from a user prompt.
        
        Returns a list of 3-5 concise search terms.
        """
        prompt = (
            "You are a search query designer. "
            "Extract 3 to 5 key search terms from the following user request that would help find relevant news articles. "
            "Return ONLY a comma-separated list of keywords. No numbering, no introductory text.\n\n"
            f"User Request: {user_prompt}"
        )
        messages = [{"role": "user", "content": prompt}]
        response = await self._call(messages)
        
        # Post-processing: Split by comma and clean up
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        return keywords[:5]  # Limit to 5

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

    async def synthesize_response(self, articles: list[NewsDTO], question: str) -> str:
        """
        Synthesize a factual response based on provided articles and a question.
        
        Ensures 'eyes and ears only' approach.
        """
        formatted_articles = self._format_articles(articles)
        prompt = (
            "You are a factual assistance tool (eyes and ears only). "
            "Answer the question based ONLY on the provided articles. "
            "If the information is not present in the articles, explicitly say 'I don't have enough information from the provided articles.' "
            "Do NOT add your own opinions, outside knowledge, or creative interpretations.\n\n"
            f"Articles:\n{formatted_articles}\n\n"
            f"Question: {question}"
        )
        messages = [{"role": "user", "content": prompt}]
        return await self._call(messages)
