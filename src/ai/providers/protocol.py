from typing import Protocol


class LLMProviderProtocol(Protocol):
    """
    Protocol defining the contract for generic Large Language Model providers.
    Adapters (Ollama, OpenAI, Gemini, etc.) must implement this interface
    to abstract network and SDK specifics away from the core AI service.
    """

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Send a conversation to the LLM and receive a text response.

        Args:
            messages: A list of message dictionaries following the ChatML format.
                      Standard keys: "role" (system, user, assistant) and "content".

        Returns:
            The raw text response from the LLM.

        Raises:
            AIProviderConnectionError: If network connection fails.
            AIProviderTimeoutError: If the request times out.
            AIGenerationError: If the model fails to generate a valid response.
        """
        ...
