import os
from src.ai.providers.protocol import LLMProviderProtocol
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.providers.groq_provider import GroqProvider

_PROVIDERS = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
}

def get_provider(name: str | None = None) -> LLMProviderProtocol:
    """Factory to get the configured LLM provider."""
    name = name or os.getenv("LLM_PROVIDER", "ollama")
    provider_class = _PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}. Available: {list(_PROVIDERS.keys())}")
    return provider_class()

__all__ = ["LLMProviderProtocol", "OllamaProvider", "GroqProvider", "get_provider"]

