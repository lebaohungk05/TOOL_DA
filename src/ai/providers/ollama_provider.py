import logging
import os
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
import httpx

from src.ai.providers.protocol import LLMProviderProtocol
from src.ai.exceptions import AIServiceError, AIServiceConnectionError

logger = logging.getLogger(__name__)

load_dotenv(override=True)


class OllamaProvider(LLMProviderProtocol):
    """
    Adapter bridging the LLMProviderProtocol to the local Ollama SDK.
    Handles network requests, model configuration, and error translation.
    """

    def __init__(self, model: str | None = None, host: str | None = None):
        """
        Initialize the Ollama provider.

        Args:
            model: The name of the model to use (default: $OLLAMA_MODEL or 'gemma4:E4B').
            host: The Ollama server URL (default: $OLLAMA_HOST or 'http://localhost:11434').
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma4:E4B")
        host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = AsyncClient(host=host)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Send a conversation to Ollama and return the text response.
        Translates Ollama-specific exceptions into domain AIServiceError exceptions.
        """
        logger.debug(f"Calling Ollama (model={self.model}) with messages: {messages}")
        try:
            response = await self.client.chat(model=self.model, messages=messages)
            content = response.message.content or ""
            logger.debug(f"Ollama response: {content}")
            return content
        except ResponseError as e:
            logger.error(f"Ollama API error: {e.error}")
            raise AIServiceError(f"Ollama API error: {e.error}") from e
        except httpx.RequestError as e:
            logger.error(f"Connection error to Ollama: {e}")
            raise AIServiceConnectionError(f"Connection error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error communicating with Ollama: {e}")
            raise AIServiceError(f"Unexpected error: {e}") from e
