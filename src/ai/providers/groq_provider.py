import logging
import os
from dotenv import load_dotenv
from groq import AsyncGroq, APIError, APIConnectionError

from src.ai.providers.protocol import LLMProviderProtocol
from src.ai.exceptions import AIServiceError, AIServiceConnectionError

logger = logging.getLogger(__name__)

load_dotenv(override=True)


class GroqProvider(LLMProviderProtocol):
    """
    Adapter bridging the LLMProviderProtocol to the Groq SDK.
    Handles network requests, model configuration, and error translation.
    """

    def __init__(self, model: str | None = None, api_key: str | None = None):
        """
        Initialize the Groq provider.

        Args:
            model: The name of the model to use (default: $GROQ_MODEL or 'openai/gpt-oss-120b').
            api_key: The Groq API key (default: $GROQ_API_KEY).
        """
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY is not set in environment or passed to provider.")
            
        self.client = AsyncGroq(api_key=key)

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Send a conversation to Groq and return the text response.
        Translates Groq-specific exceptions into domain AIServiceError exceptions.
        """
        logger.debug(f"Calling Groq (model={self.model}) with messages: {messages}")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            content = ""
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if choice.message and choice.message.content:
                    content = choice.message.content
                    
            logger.debug(f"Groq response: {content}")
            return content
            
        except APIConnectionError as e:
            logger.error(f"Connection error to Groq: {e}")
            raise AIServiceConnectionError(f"Connection error: {e}") from e
        except APIError as e:
            logger.error(f"Groq API error: {e}")
            raise AIServiceError(f"Groq API error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error communicating with Groq: {e}")
            raise AIServiceError(f"Unexpected error: {e}") from e
